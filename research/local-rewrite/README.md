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
