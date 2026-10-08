# Local models in the rewrite step

The question in #14 was which open models fit on the Actions runner and
whether a small one could do the rewriting. This folder holds what I ran
to answer it, so the numbers in the issue can be checked and rerun.

Each model went through the package's own `cringe_filter.rewrite.rewrite()`
(the `github` prompt, lint, at most one revision pass) with a client that
talks to llama.cpp's `llama-server` in place of the Anthropic SDK. Nothing
else changed. The drafts are six PR bodies Claude wrote in this repo: #1,
#3, #4, #8, #12 and #13. The frontier reference (`opus-self`) is Claude
Opus 5.5 applying the same prompt by hand in one pass, the way `SKILL.md`
has an agent do it.

`outputs.md` has every draft and every rewrite side by side. Read those
before trusting the summary: the package scores style, and it does not
check facts.

## Results

Speed on the runner (llama.cpp b11342, 4 threads, 4-bit weights). "Reads"
is prompt processing and "writes" is generation, both in tokens per second.
Per draft includes the revision pass when it ran.

```
model            weights   reads   writes   per draft
Qwen3.5-2B        1.3 GB    95     15.2      35 s
Qwen3.5-4B        2.7 GB    35      6.5      77 s
Gemma 4 E4B       5.2 GB    27      6.5      no rewrite
LFM2.5-8B-A1B     5.2 GB    56     18.5      39 s
Qwen3.5-9B        5.7 GB    20      3.9     148 s
Gemma 4 12B       7.0 GB    11      3.0      speed test only (llama-bench)
gpt-oss-20b      12.1 GB    15      7.0     167 s, 2.5 GB of swap in use
```

Quality on the three drafts every model got (#4, #8, #13). Score is the
median `score` log-odds, negative on the writer's side; the drafts
themselves have a median of +9.69. Dropped counts the code spans, URLs,
paths and numbers `preserve.py` tracks. Content kept is the share of the
draft's content words that survive. Wrong is my read of each rewrite
against its draft: a claim the draft doesn't make, a renamed identifier,
or text too garbled to send.

```
model             score   writer side   lint errors   dropped   content kept   wrong
Opus 5.5 (me)     -4.68   3 of 3        0             0 of 31   94%            0 of 3
Qwen3.5-2B       -34.99   2 of 3        5             6         52%            3 of 3
Qwen3.5-4B        -7.42   3 of 3        0             2         58%            2 of 3
Gemma 4 E4B       +8.20   0 of 1        0             0         (copied)       1 of 1
LFM2.5-8B-A1B     +3.69   1 of 3        0             3         74%            2 of 3
Qwen3.5-9B        -9.33   3 of 3        1             4         77%            2 of 3
gpt-oss-20b       +0.63   1 of 3        0             0         77%            1 of 3
```

On all six drafts, Qwen3.5-4B got four wrong and the reference none. Gemma
4 E4B never produced a rewrite of #13. With thinking on it spent the whole
budget thinking, and with thinking off it wrote a plan, the second time
with the draft pasted in, which is why its content kept reads 100%.

## Rerun

On a runner like the one in the issue (4 vCPU, 16 GB, no GPU):

```bash
pip install -e .
cd research/local-rewrite
# llama.cpp b11342 CPU build, then a GGUF, e.g. unsloth/Qwen3.5-4B-GGUF
./run_model.sh qwen3.5-4b Qwen3.5-4B-Q4_K_M.gguf "--reasoning-budget 0" -- \
    pr13-body pr12-body pr3-body pr4-body pr1-body pr8-body
python summarize.py              # one line per model
python make_outputs_md.py        # outputs.md
```

`run_model.sh` expects the llama.cpp release under `bin/llama-b11342/` and
the GGUF under `models/`. Sampling is the same for every model:
temperature 0.7, top-p 0.9, seed 1, and a reply capped at about twice the
draft's length so a model that loops stops. Gemma 4, LFM2.5 and Qwen3.5
think by default, so they run with `--reasoning-budget 0`; gpt-oss cannot
switch it off, so it runs at low reasoning effort with 1500 extra tokens.

## Files

- `bench.py`: the client shim and the per-draft metrics
- `evaluate.py`: the same metrics for rewrites written without a model call
- `summarize.py`: the table, plus `--leaks` for 4-word runs a rewrite took
  from the prompt rather than the draft
- `make_outputs_md.py`: `outputs.md`
- `drafts/`: the six PR bodies, as the action posted them
- `results/*.jsonl`: one row per model and draft, with timings
