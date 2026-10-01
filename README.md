# cringe-filter

cringe-filter checks a draft for the habits that make text read as if
Claude wrote it: em dashes, the `it isn't X, it's Y` frame, bold lead-ins,
status emoji, and replies five times longer than they need to be. You tell
it where the text is going, and it tells you what to fix and how much more
often Claude does each thing than a person writing in that place.

The rules come from measurement. We compared 570k words that one
researcher (called "the writer" below) wrote in GitHub replies, issues and
reviews with 1.35M words Claude wrote in the same threads. The writer's
Discussions posts, LinkedIn posts, email, messages, papers and tutorials
cover the other contexts. The `lint` rules describe Claude's
habits, so they work on anyone's draft. `score` and `prompt` also pull a
draft toward how the writer handles that kind of text, which is one
careful person's practice.

It needs Python 3.9 or later and nothing else. The optional `rewrite`
command also needs the `anthropic` package.

## Install

```bash
pip install cringe-filter
```

Or run it without installing:

```bash
uvx cringe-filter contexts
```

## Quick start

Here is a GitHub reply with four of Claude's habits in it, saved as
`reply.md`:

```markdown
The parser now handles empty rows — it isn't a hack, it's the real fix.

**Key changes:**
- ✅ Added a guard for empty rows
```

Lint it for the place it is going:

```console
$ cringe-filter lint -c github reply.md
reply.md:1: error em-dash [10.2x, CI 7.13-16.66]: Em dash. Use a period, a colon, or commas.
    parser now handles empty rows — it isn't a hack, it's the rea
reply.md:1: warn isnt-x-its-y [3.49x, CI 1.71-12.05]: The 'it isn't X, it's Y' frame. State Y and stop.
    r now handles empty rows — it isn't a hack, it's the real fix. **Key changes:
reply.md:3: warn bold-run [7.22x, CI 5.29-9.98]: Bold emphasis.
    t a hack, it's the real fix. **Key changes:** - ✅ Added a guard for empty r
reply.md:4: warn emoji-status [14.66x, CI 8.15-33.65]: Status emoji.
    real fix. **Key changes:** - ✅ Added a guard for empty rows

4 findings, 1 errors  (context: github)
```

`[10.2x, CI 7.13-16.66]` means Claude used em dashes 10.2 times as often
as the writer did in GitHub replies, with a family-wise bootstrap
interval. An `error` makes the command exit with code 1, so you can run it
in CI or a pre-commit hook. The `warn` and `info` findings are yours to
judge.

The writer would have written something closer to this, which passes:

```markdown
I think the parser was dropping empty rows. Could you check whether a
guard there fixes it for you?
```

## Contexts

You write differently in a GitHub reply and in a paper, so every command
takes a context, each with its own length budget, formatting rules and
example passages:

```console
$ cringe-filter contexts
context     label                                            docs    words  median  budget
github      GitHub reply in your own repos                   7235   378991      27     110
discussion  GitHub Discussions post                           456    56929      51     297
third-party Issue or comment in someone else's repo          2269   136266      30     126
email       Email                                             144    11972      57     170
message     Short message (DM, chat reply, comment)           757    23572      22      65
linkedin    LinkedIn post                                      89     9784      54     283
tutorial    Tutorial or docs page                             161    54974     357    1500
paper       Scientific prose                                  206    70341     359    6000
proposal    Proposal                                           39    13272     359    6000
any         Unspecified                                      9960   572186      28   10000
```

`median` is the writer's median length in words (per section for papers
and proposals), and `lint` warns past `budget`. Aliases such as `dm`,
`docs`, `bug-report`, `pr` and `grant` work too. With `--url`, the
destination picks the context:

```bash
cringe-filter lint --url https://github.com/pytorch/pytorch/issues/1 draft.md
```

`profile -c <context>` prints the rate of each surface marker for the
writer and for Claude in one context.

## Commands

### lint

`lint` makes no model calls, so you can run it on every file you touch:

```bash
cringe-filter lint --context github draft.md
git diff --name-only | grep '\.md$' | xargs cringe-filter lint -c tutorial --quiet
```

Revisions tend to put the tells back. When agents in the lab's repos
revised paragraphs after a reviewer's comment, em dashes went from 261 to
329 and semicolons from 371 to 470. `--against` shows only what the new
version added:

```bash
cringe-filter lint -c paper --against draft-v1.tex draft-v2.tex
```

A finding tagged `[preventive, no corpus support]` is a pattern that never
separated the two authors in that context, and it stays at `info`. Where
the writer uses a pattern as often as Claude, the rule is off. The writer
uses "ensure", "leverage", "comprehensive" and "streamline" more than
Claude does, so `lint` never flags them.

To silence a false positive, add a comment. `disable-line` covers its own
line, `disable-next-line` the line after it, and `disable-file` the whole
file:

```markdown
<!-- cringe-filter: disable-line em-dash -->
<!-- cringe-filter: disable-next-line bold-run, md-header -->
<!-- cringe-filter: disable-file -->
```

In LaTeX, write `% cringe-filter: disable-line em-dash`. `lint` reads a
`.tex` file as the prose in the PDF. It skips the preamble, comments,
math, tables, footnotes and the keys of `\cite`, `\ref` and `\label`,
treats `---` as an em dash and `--` as an en dash, and keeps the line
numbers. A `.tex` file with no context is linted as `paper`.

### score

`score` adds up how far each feature pulls the draft toward Claude or
toward the writer. On the reply from the quick start:

```console
$ cringe-filter score -c github reply.md
context: github (GitHub reply in your own repos)   words: 25   sentences: 2, longest 15
style score: +11.83 log-odds, reads like Claude (a ranking of what to fix, not a calibrated probability)
length: 25 words; the writer's median here is 27, p90 110, budget 110
Burrows' Delta over the 150 most frequent words: 0.39 to the writer's register, 0.42 to Claude (closer to the writer)
feature                                        n  yours/1k writer/1k  Claude/1k  log-odds
(per 1000 words; structure rows per 1000 sentences or prose paragraphs)
status emoji                                   1     40.00      0.03       1.21     +3.60
em dashes                                      1     40.00      1.83      18.43     +1.90
dashes between words                           1    500.00     36.20     349.60     +1.64
bold runs                                      1     40.00      2.93      21.47     +1.53
isn't X it's Y                                 1     40.00      0.03       0.12     +1.34
...
```

Positive reads like Claude. The writer's version scores -21.12. Each row
is a log-likelihood ratio of Claude's rate against the writer's, and the
rows overlap, so use the total to decide what to fix first. It is not a
probability, and the JSON output says `calibrated: false`.

The Delta line compares the draft's 150 most common words, mostly
function words, with each author's average. The rows counted per 1000
sentences describe how the sentences are built, such as how often the
subject is a person or a sentence opens on "The". Email and tutorials
have no rows of that kind.

### prompt

`prompt` turns the measurements into instructions any model can follow:

```bash
cringe-filter prompt --context linkedin draft.txt        # the full prompt, with your draft
cringe-filter prompt --context linkedin --system-only    # the filter alone
cringe-filter prompt -c github --evidence draft.md       # plus the numbers behind it
cringe-filter prompt -c github --json draft.md           # {system, user, evidence}
```

The prompt starts with two real passages that match your draft's length
and break none of the rules. Then it lists priorities for the context,
the tells to avoid and a few notes. It leaves out the rates, because
models follow numeric rules badly, and `--evidence` prints them for you.
One priority covers sentence structure, such as making a person the
subject. `--no-structure` leaves it out.

### rewrite

`rewrite` sends the prompt to Claude and lints the result:

```bash
pip install 'cringe-filter[rewrite]'
export ANTHROPIC_API_KEY=...
cringe-filter rewrite --context email draft.txt
cringe-filter rewrite -c github --model claude-sonnet-5 --effort low draft.md
cringe-filter rewrite -c github --dry-run draft.md      # print the prompt instead
cringe-filter rewrite -c paper --minimal draft.tex      # edit, do not rewrite
```

If the result still has lint errors or measured warnings, or it dropped a
number, link, code span or path (in LaTeX, also a citation, reference or
math span), `rewrite` makes one more pass. It stops
at two model calls, because repeated self-revision makes good text worse.
Length alone does not trigger the second pass. In a held-out test, each
revision made for length cut about 6% of the source's content words and
moved no classifier toward the writer.

The default model is `claude-opus-5` with adaptive thinking at medium
effort. A declined request
is re-run on the server-side fallback model unless you pass
`--no-fallback`. The rewrite goes to stdout, and the pass count, scores
and remaining findings go to stderr.

Use `--minimal`, on `rewrite` or `prompt`, for a draft headed to review,
like a manuscript or a proposal. It asks for the smallest edit a reviewer
would make, from the draft's lint findings and a short checklist of what
the lab's reviewers asked agents to change. On 74 agent drafts that
people later corrected, a full rewrite moved the text away from the
reviewer's version. The minimal edit did not.

### audit

`audit` turns the lint findings into an edit spec: each sentence to fix,
with its line and the reason, and the flagged sentences to leave alone.
Give the spec and the draft to any model along with `prompt --minimal`:

```bash
cringe-filter audit -c paper draft.tex > spec.md
```

Some findings are judgment calls, because the writer also uses the
`X, not Y` contrast and the `X is what did Y` cleft, mostly to give
instructions. With `--model`, `audit` asks a model to score each one from
0 to 100 for how likely it is that Y was set up only to be knocked down.
Hits under `--threshold` (30 by default) move to the leave-alone list.
Without `--model`, nothing is dropped and you decide. The model can be
anything with an OpenAI-compatible endpoint. The default is Ollama on your
own machine, so a private draft stays private. `--endpoint` points it at
llama.cpp's `llama-server`, LM Studio or vLLM instead:

```bash
ollama pull qwen2.5:14b
cringe-filter audit -c github --model qwen2.5:14b draft.md
```

A frontier model separated Claude's contrasts from the writer's on this
question. The 1.5B and 3B models that fit on two CPU cores did worse.

### instructions

`instructions` writes a GitHub Copilot instruction file for each context
into `.github/instructions/`, or the folder you pass to `--dir`:

```bash
cringe-filter instructions paper proposal tutorial
cringe-filter instructions paper --apply-to "manuscript/**"
```

Copilot's cloud agent and code review apply each file to the paths its
`applyTo` globs match. By default these are `.tex` and `.bib` files for
`paper`, folders named for a proposal or grant for `proposal`, and
Markdown, RST and notebooks for `tutorial`. `--apply-to` replaces the
globs, and `--exclude-agent code-review` keeps code review from reading a
file. Replies are not files, so for those contexts put the output of
`prompt -c <context> --system-only` in `.github/copilot-instructions.md`
instead.

## Inside a coding agent

An agent that drafts prose is already a model, so it does not need
`rewrite`. [SKILL.md](https://github.com/sgbaird/cringe-filter/blob/main/SKILL.md) is a Claude Code skill that has the agent
run `lint` and `prompt` and then fix its own draft. Copy it to
`.claude/skills/cringe-filter/SKILL.md` in any repository where this
package is installed.

## Where the numbers come from

The corpus and the pipeline that builds `cringe_filter/data/profile.json`
live in a private repository, because the corpus includes mail and direct
messages. Each rebuild opens a pull request here, so the rules follow the
data without anyone editing them. The example passages in the package
come only from public repositories and public LinkedIn posts. Mail and
messages contribute counts and nothing else.

To use your own profile, point `CRINGE_FILTER_PROFILE` at it. An
`exemplars/` folder next to it replaces the packaged passages that have
the same file names:

```bash
export CRINGE_FILTER_PROFILE=~/private/voice/profile.json
```

[How it was measured](https://github.com/sgbaird/cringe-filter/blob/main/docs/methods.md) covers the statistics, the
held-out tests and what is in the profile. To run the tests:

```bash
python -m unittest discover -s tests
```

## Limits

- Most contexts are scored against Claude's GitHub replies, because that
  is the only place both authors wrote about the same work. Scoring an
  email that way asks whether it reads like the model or like the
  writer's email, which is useful, but the two are different genres.
- Papers and proposals are scored against Claude's own manuscripts and
  agents' proposals. The writer's side of `proposal` rests on two
  proposals, so treat that score as a hint.
- Small contexts carry little signal for rare phrases. LinkedIn has 89
  posts, and where a context has no verdict for a phrase, `lint` falls
  back to the verdict for the whole corpus.
- A low score proves nothing, and getting past AI detectors is not the
  goal. The better test: would this sound pretentious to someone who
  already knows what they are doing?
