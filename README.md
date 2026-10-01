# cringe-filter

Strip the AI tells out of prose: the em dashes, the "it's not X, it's Y",
the bolded preambles and the rest. A linter, a scorer and a prompt
builder, all measured rather than guessed: 570k words one researcher wrote
in GitHub replies, issues and reviews, contrasted against 1.35M words Claude wrote
in the same threads, plus Discussions posts, LinkedIn posts and comments,
direct-message counts, sent-mail counts, first-author manuscripts and
tutorial pages. The rates and intervals are measured; the thresholds,
severities and budgets are declared in code and listed in this file, and a
corpus rebuild changes the rules without anyone editing them.

It is tuned per task: a GitHub reply, a bug report in someone else's repo,
a Discussions post, an email, a short message, a LinkedIn post, a docs
page, a paper or a proposal each get their own length budget, formatting
rules and exemplars. The `lint` tells are about Claude's prose and apply
to anyone's; `score` and `prompt` pull toward the measured writer's habits
for that task. Every rate below is that one writer's ("the writer"), so
read it as one careful human's practice, not a law of human writing.

No dependencies. Python 3.9 or later. The optional `rewrite` command needs
the `anthropic` package, and the MCP server needs `mcp` and Python 3.10.

## Install

```bash
pip install cringe-filter
uvx cringe-filter contexts            # or run it without installing

# Drop SKILL.md into a project's .claude/skills/cringe-filter/ so a coding
# agent applies the filter to its own drafts (see below)
```

The corpus and the pipeline that compiles it into
`cringe_filter/data/profile.json` live in a private repository, because the
corpus includes mail and messages. Paths below under `scripts/voice/` and
`docs/voice/` refer to that repository.

## Contexts

Every command takes a context, because the same person writes very
differently in each. `cringe-filter contexts` prints the table. Aliases are
accepted (`dm`, `docs`, `bug-report`, `pr`, `grant`), and `--url` infers
the context from where the text is going:

| Context | What it is | Writer's median | Budget |
| --- | --- | ---: | ---: |
| `github` | Reply in your own repos | 27 words | 110 |
| `discussion` | GitHub Discussions post | 51 | 297 |
| `third-party` | Issue or comment in someone else's repo | 30 | 126 |
| `email` | Sent mail | 57 | 170 |
| `message` | DM, chat reply, comment on a post | 22 | 65 |
| `linkedin` | LinkedIn post | 54 | 283 |
| `tutorial` | Docs and teaching pages | 357 | 1500 |
| `paper` | Scientific prose, the writer's papers before 2023 | 359 per section | 6000 |
| `proposal` | Grant and research proposals | 359 per section | 6000 |

## Commands

**`lint`**: the cringe filter. Deterministic, zero tokens, exit code 1 on
any error.

```bash
cringe-filter lint --context github draft.md
cringe-filter lint --url https://github.com/pytorch/pytorch/issues/1 draft.md
git diff --name-only | grep '\.md$' | xargs cringe-filter lint -c tutorial --quiet
# only what a revision added
cringe-filter lint -c paper --against draft-v1.tex draft-v2.tex
```

`--against OLD` reports the findings the new version has that the old one
did not (same rule on the same text, wherever it moved). In the lab's
repos, paragraphs an agent revised after a reviewer's comment came back
with more em dashes (261 to 329) and semicolons (371 to 470) than they
had, so a review round can reopen what the last one closed.

Each finding says what backs it. `[15.2x, CI 9.7-23.9]` means Claude used
the pattern 15 times as often as the writer did in that register, with the
family-wise bootstrap interval. `[preventive, no corpus support]` means the
pattern never separated the two authors there; those never rise above
`info`. A rule the corpus contradicts (the writer uses "ensure", "leverage",
"comprehensive" and "streamline" more than Claude does) is switched off,
per register, from the data. Suppress a real false positive inline:

```markdown
<!-- cringe-filter: disable-line em-dash -->
<!-- cringe-filter: disable-next-line bold-run, md-header -->
<!-- cringe-filter: disable-file -->
```

LaTeX is read as the prose a reader of the PDF sees (`latex.py`): the
preamble, comments, math, tables, footnotes and `\cite`/`\ref`/`\label`
keys are masked, `---` counts as an em dash and `--` as an en dash, and
findings keep their line numbers. A `.tex` file given without a context is
linted as `paper`, and `rewrite` checks that every citation key, reference
key and inline math span survives. In LaTeX the suppression comment is
`% cringe-filter: disable-line em-dash`.

**`score`**: the voice filter as a measurement. Each feature is scored by
the Poisson log-likelihood ratio of Claude's rate against the writer's rate in the
chosen context, and the sum is one style score with the features that
produced it. The features overlap and the rates were measured on the same
corpus, so the score is a ranking of what to fix, not a calibrated
probability; the JSON carries `calibrated: false` and the review in
`docs/voice/research/` says what a calibrated version needs.

```bash
cringe-filter score --context email draft.txt
cringe-filter score -c github --text "Not sure this is right. Could you check?"
```

```
context: github (GitHub reply in your own repos)   words: 143   sentences: 7, longest 31
style score: +3.41 log-odds, reads like Claude (a ranking of what to fix, not a calibrated probability)
length: 143 words; the writer's median here is 27, p90 110, budget 110  [over budget]
Burrows' Delta over the 150 most frequent words: 1.31 to the writer's register, 1.12 to Claude (closer to Claude)
feature                       n  yours/1k   writer/1k  Claude/1k  log-odds
bold runs                     4     28.0     2.93      21.47     +2.13
hedges (might, maybe, ...)    0      0.0    10.58       0.33     +1.46
```

The Delta line is Burrows' Delta over the 150 most frequent words of the
pooled corpus (mostly function words, by construction, not a curated
function-word list), z-scored against the per-document spread: the draft's
distance to the register's centroid and to Claude's. Function words carry
authorship in the stylometry literature, and this is the standard
implementation of that idea. It is a second signal, though not an
independent one: its centroids come from the same corpus as the tells.

The structure rows (marked per 1000 sentences or paragraphs) measure how
the sentences are built rather than which words they use: how often the
subject is I, we or you, how often a sentence opens on "The", a number, a
conjunction or a lead-in like "Also,", modal and "to" verbs per sentence,
colons, dashes, semicolons and parentheses inside a sentence, and the share
of one-sentence paragraphs. `structure.py` counts them without a parser;
each was checked against a dependency parse of the corpus
(`docs/voice/research/structure.md`). Registers whose text never reaches
the build (email, tutorials, manuscripts) have no structure rows.

It is not a detector. It says where a draft sits between two measured
writers and which features put it there, which is what you need to fix it.

**`prompt`**: the voice filter as a prompt, for any model. Two real
passages first, matched to the target length and free of anything the
rules forbid; then five plain constraints derived from the register's
measurements; then the measured tells in plain words; then a few notes from
the register card. No rates or intervals reach the model, because numeric
constraints are what models follow worst; `--evidence` appends them for a
person.

```bash
cringe-filter prompt --context linkedin draft.txt        # full prompt
cringe-filter prompt --context linkedin --system-only    # the filter alone
cringe-filter prompt -c github --evidence draft.md       # plus the numbers
cringe-filter prompt -c github --json draft.md           # {system, user, evidence}
cringe-filter prompt -c github --structure draft.md      # with the sentence-structure priority
```

The prompt carries one priority written from the register's structure
rates: make a person the subject, open few sentences on "The" or a
number, carry plans in verbs, ask where the draft leaves a choice open,
one idea per sentence, one point per paragraph. Each clause appears only
where the register's own rates put it on the writer's side by a clear margin.
It is on by default: on 36 fresh held-out comments it moved every
grammar judge toward the writer, at a cost of about 1.5 points of the source's
content words. `--no-structure` leaves it out, and `build_prompt(...,
structure=1)` rebuilds the wording that test used
(`docs/voice/research/structure.md`).

**`rewrite`**: apply the prompt with Claude, lint the result, and make one
revision pass against lint errors and measured warnings (bold, headers,
tables and arrows are warnings, and they are the dominant Claude
features), and against any number, link, code span or path the rewrite
dropped (`preserve.py`). The length budget is reported but does not
trigger a revision by itself: in the held-out rewrite experiment every
length-driven revision cut about 6% of the source's content words without
moving any classifier toward the writer. Never more than two model calls:
repeated self-revision degrades text that was already fine.

```bash
pip install 'cringe-filter[rewrite]'      # or: pip install anthropic
export ANTHROPIC_API_KEY=...
cringe-filter rewrite --context email draft.txt
cringe-filter rewrite -c github --model claude-sonnet-5 --effort low draft.md
cringe-filter rewrite -c github --dry-run draft.md      # print the prompt
cringe-filter rewrite -c paper --minimal draft.tex      # edit, do not rewrite
```

`--minimal` (also on `prompt`) is for a draft headed to review. It asks
for the smallest edit a reviewer would make: a nine-line checklist of what
the lab's reviewers asked agents to change (claim only what was done,
plain words, defined abbreviations, concrete detail, no process talk, no
em dashes or "X, not Y"), the draft's own lint findings, and no revision
pass. On 74 agent drafts that people later corrected, the full rewrite
moved the text away from the version the reviewer wrote, and the minimal
edit did not (`docs/voice/research/corrections.md`).

Defaults to `claude-opus-5` with adaptive thinking at medium effort, and
requests the server-side refusal fallback so a declined request is re-run
on a fallback model inside the same call (`--no-fallback` to turn that
off). Output goes to stdout; the pass count, before-and-after score and
any remaining findings go to stderr.

**`audit`** turns the lint findings into an edit spec: each sentence that
needs work, its line, and why, plus the flagged sentences to leave alone.
Hand the spec and the draft to any frontier model with `prompt --minimal`.
The "X, not Y" family and the "X is what did Y" cleft are judgment calls
(the writer's own uses are mostly instructions), so `--model` puts each one to a
model as a single question: score from 0 to 100 how likely it is that Y
was set up only to be knocked down. Hits under `--threshold` (default 30)
move to "leave as written". Any OpenAI-compatible endpoint works: Ollama
on localhost by default, so a private draft stays on the machine, or
llama.cpp's `llama-server`, LM Studio or vLLM through `--endpoint`. A
frontier model asked for this score separated Claude's contrasts from the writer's;
the 1.5B and 3B models that fit on two CPU cores did worse
(`docs/voice/research/local-models.md`). Without `--model` nothing is
dropped and the editor decides.

```bash
cringe-filter audit -c paper draft.tex > spec.md
ollama pull qwen2.5:14b
cringe-filter audit -c github --model qwen2.5:14b draft.md
```

**`instructions <context>...`** writes path-scoped instruction files for
GitHub Copilot, one per context, into `.github/instructions/` (`--dir` to
change it). Copilot's cloud agent and its code review apply each file to
the paths its `applyTo` globs match: `**/*.tex,**/*.bib` for `paper`,
folders named for a proposal or grant for `proposal`, Markdown, RST and
notebooks for `tutorial`. `--apply-to` replaces the globs and
`--exclude-agent code-review` keeps review from reading a file. Replies are
not files, so for `github` and the other reply contexts put
`prompt -c <context> --system-only` in `.github/copilot-instructions.md`.

```bash
cringe-filter instructions paper proposal tutorial
cringe-filter instructions paper --apply-to "manuscript/**"
```

**`contexts`** and **`profile -c <context>`** print what the bundle knows.

## Inside a coding agent

An agent that drafts prose is itself the model, so it does not need
`rewrite`. `SKILL.md` in this folder is a Claude Code skill that runs
`lint` and `prompt` and has the agent apply the filter to its own draft.
Copy it to `.claude/skills/cringe-filter/SKILL.md` in any repository that has
this package on its path.

## As an MCP server

`cringe-filter mcp` serves the same checks to any client that speaks the
Model Context Protocol, such as Claude Code, Claude Desktop, VS Code and
Cursor. An agent can then lint and score a draft without a shell or a
skill file. It runs on the machine that starts it, over stdio, so a
private draft stays there.

```bash
pip install 'cringe-filter[mcp]'
claude mcp add cringe-filter -- uvx --from 'cringe-filter[mcp]' cringe-filter mcp
```

A client configured in JSON (Claude Desktop, Cursor, a project's
`.mcp.json`) takes the same command:

```json
{
  "mcpServers": {
    "cringe-filter": {
      "command": "uvx",
      "args": ["--from", "cringe-filter[mcp]", "cringe-filter", "mcp"]
    }
  }
}
```

The tools `lint`, `score`, `audit` and `contexts` match the commands of
the same name; `lint` takes `against` for the old version, and `score`
reports the top features only (`top`, default 12). `filter_prompt` is
`prompt --system-only`, with `minimal` and `evidence` as in `prompt`. The
prompts `rewrite` and `minimal_edit` put a draft under the filter for the
client's own model to edit, and the resources
`cringe-filter://filter/{context}` and `cringe-filter://profile/{context}`
serve a context's filter and its measured rates.

Each tool takes `context` (a name or alias) or `url`, as the commands do.
`lint` and `score` answer with the report the command prints, which costs
the model a third of the tokens the JSON would, and carry the JSON as
structured content for programs. There is no rewrite tool, for the reason
in the section above: the agent calling the server is the model. `audit`
consults a model only when the call names one, at the endpoint
`CRINGE_FILTER_LLM_ENDPOINT` sets where the server runs. The server also
sends a short form of the `SKILL.md` procedure as its instructions, which
clients such as Claude Code pass to the model.

Over streamable HTTP the same server can be hosted for clients that cannot
start a local process. It keeps no state between calls, so any number of
copies can serve it, but every draft sent to it passes through that host.

```bash
cringe-filter mcp --transport streamable-http --port 8000   # http://127.0.0.1:8000/mcp
docker build -t cringe-filter-mcp . && docker run -p 8000:8000 cringe-filter-mcp
```

The container listens on `$PORT` when the platform sets one.

## What is in the bundle

`profile.json` carries, per context: document and sentence length
statistics, per-1000-word rates for 31 surface markers, the register's own
rate for each of 104 candidate tells, the Claude-over-register ratio for
each with its family-wise interval, the register card, and which exemplar
banks to read. Plus Claude's reference rates, the corpus-wide verdicts, and
the Holm-surviving bigrams on each side, limited in the published build
to function-word pairs so project vocabulary stays out. The exemplar
banks are real passages from public repositories and public LinkedIn posts only; sent
mail and direct messages never leave the machine that harvested them, and
only their counts are here.

The private repository rebuilds it after the pipeline runs
(`scripts/voice/build_voicekit.py`) and opens a pull request here with
the new profile. Tests:

```bash
python -m unittest discover -s tests
```

A profile can also live outside the package. Point `CRINGE_FILTER_PROFILE` at
it, and an `exemplars/` folder beside it replaces the packaged banks of
the same name:

```bash
export CRINGE_FILTER_PROFILE=~/private/voice/profile.json   # + ~/private/voice/exemplars/*.md
```

`python scripts/voice/privacy_audit.py` reports what the package would
reveal if it were published: whether every quoted passage is public,
any private repository name, email or phone number, which numbers come
from private text, and which word lists carry project vocabulary.

## Limits

- The reference for most contexts is Claude's GitHub prose, because that
  is the only place both authors wrote about the same work. Scoring an
  email against it asks "does this read like the model or like the writer's email",
  which is the useful question, but the two are not the same genre.
- `paper` is scored against Claude's own scientific prose instead: the
  manuscripts claude[bot] wrote in the lab's repos (`references` in the
  profile). With one of the writer's papers and one of Claude's repositories held
  out at a time, `score -c paper` reads 253 of 291 chunks of the writer's earlier
  papers as the writer's and 17 as Claude's, and 66 of 79 chunks of Claude's
  manuscripts as Claude's and 3 as the writer's. Before, it read every one of
  Claude's drafts of the writer's sections as the writer's.
- `proposal` is scored against the coding agents' proposals in the lab's
  public and private repos, 15k words, most of them the Copilot agent
  running Claude Opus models. Semicolons, mid-sentence colons,
  significance words and "we" separate them from the writer's proposals. Held out,
  it reads 32 of 40 of the writer's chunks as the writer's and 38 of 49 of the agents' as
  Claude's, against 33 and 34 with Claude's manuscripts as the reference.
  The writer's side rests on two proposals, 13k words, so treat the score as a hint
  and the card as the rules (`docs/voice/research/technical-writing.md`).
- Small registers carry little signal for rare phrases. LinkedIn is 89
  posts; the linter falls back to the corpus-wide verdict when a register
  has none of its own for a phrase.
- The scorer treats features as independent, which they are not; read
  the log-odds as a ranking of what to fix, not as a probability with
  guarantees.
- Detector evasion is not the objective, and a low score is not proof of
  anything. The one-question test still applies: does this sound
  pretentious to someone who already knows what they are doing?
