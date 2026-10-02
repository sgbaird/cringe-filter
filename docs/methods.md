# How it was measured

This page collects the measurements behind the rules, in case you want to
check them. The corpus and the pipeline live in a private repository,
because the corpus includes mail and direct messages. Paths below under
`scripts/voice/` and `docs/voice/` refer to that repository.

## The corpus

The core comparison is 570k words one researcher ("the writer") wrote in
GitHub replies, issues and reviews, against 1.35M words Claude wrote in
the same threads. The other contexts add the writer's Discussions posts,
LinkedIn posts and comments, first-author manuscripts and tutorial pages,
plus counts from direct messages and sent mail. The `paper` context uses
the writer's papers from before 2023.

The rates and intervals are measured. The thresholds, severities and
length budgets are declared in code, so a rebuild of the corpus changes
the rules without anyone editing them. `scripts/voice/build_voicekit.py`
rebuilds the profile and opens a pull request here with it.

## How a rule gets its severity

Every rule names the phrase it was measured as, and `lint` reads the
verdict for the requested context from the profile:

- `measured`: Claude's rate over the writer's is above 1, and the
  family-wise bootstrap interval excludes 1. The rule keeps its declared
  severity.
- `preventive`: the context's data does not support the rule. It stays
  at `info`.
- `contra`: the writer uses the pattern as often as Claude or more. The
  rule is off in that context.

When a context has any signal of its own for a phrase, that decides.
Otherwise the verdict for the whole GitHub corpus applies. Where Claude
gives no signal either way, Copilot's replies in the same threads are a
second reference, and a rule backed only by them is capped at `warn`.
Where the profile carries a calibration step
(`scripts/voice/calibrate_linter.py`), the false-positive rate on the
writer's own text sets the severity of a measured rule.

## What lint reads

`lint` skips code, URLs and front matter, and keeps every line number.
The rules also skip the inside of a short span in double quotes (up to
80 characters), because a page about writing quotes the patterns it
describes. Single quotes are read, since they double as apostrophes.
Suppression comments count only outside code.

Three checks look at the whole text. `too-long` compares the word count
with the context's budget. `long-sentence` flags a sentence longer than
the writer's 90th percentile for the context. A blank line ends a
sentence, so a heading or a line that introduces a code block never joins
the next one. `repeated-phrase` flags a run of seven or more words that
repeats an earlier one. No measurement backs it, so it stays at `info`.
At seven words it fires on none of the 83 passages in the example banks,
and at six on three.

## The score

`score` treats each feature as a Poisson count. It compares Claude's rate
with the writer's rate in the chosen context and adds the log-likelihood
ratios into one style score. Shares, such as the share of one-sentence
paragraphs, use a binomial ratio instead. The features overlap, and the
rates were measured on the same corpus the score describes. So the score
ranks what to fix, and the JSON output carries `calibrated: false`. The
review in `docs/voice/research/` says what a calibrated version would
need.

The Delta line is Burrows' Delta over the 150 most frequent words of the
pooled corpus. Those are mostly function words because of how they were
picked, with no hand-made word list. Each word is z-scored against the
spread between documents, and the line reports how far the draft is from
the centroid for the context and from Claude's. Function words carry authorship
in the stylometry literature, and this is the standard way to use them.
The centroids come from the same corpus as the tells, so Delta is a
second signal and not an independent one.

In contexts with structure rates, you also get rows that count how
sentences are built. They cover how often
the subject is I, we or you, and how often a sentence opens on "The", a
number, a conjunction or a lead-in like "Also,". They also count modal
and "to" verbs per sentence, the colons, dashes, semicolons and
parentheses inside a sentence, and the share of one-sentence paragraphs.
`structure.py` counts them without a parser, and each was checked against
a dependency parse of the corpus (`docs/voice/research/structure.md`).
Email and tutorials have no structure rates, because their text never
reaches the build.

`structure.py` also counts lists, tables and code blocks, and the share
of them a colon introduces. The "colon before block" tell counts those
colons per 1000 words, so it mostly measures how many blocks a page has.
Once a rebuild carries the share for the context and for Claude, `score`
uses it in place of the per-word row.

## The prompt

The prompt leads with two real passages, matched to the target length
and free of anything the rules forbid. A few plain priorities follow,
written from the context's measurements, then the measured tells in plain
words and some notes from the card for that context. No rates or intervals reach
the model, because models follow numeric constraints worst of all.

One priority is written from the structure rates: make a person the
subject, open few sentences on "The" or a number, carry plans in verbs,
ask where the draft leaves a choice open, and keep one idea per sentence
and one point per paragraph. Each clause appears only where the rates for
that context favor the writer by a clear margin. On 36 fresh held-out
comments it moved every grammar judge toward the writer, at a cost of
about 1.5 points of the source's content words. `build_prompt(...,
structure=1)` rebuilds the wording that test used
(`docs/voice/research/structure.md`).

## Rewrite, minimal edit and audit

The revision pass in `rewrite` looks at lint errors and at measured
warnings, because bold, headers, tables and arrows are warnings and they
are the strongest Claude features. It also asks for any number, link,
code span or path the rewrite dropped (`preserve.py`). In the held-out
rewrite experiment, every revision made only for length cut about 6% of
the source's content words and moved none of the three classifiers toward
the writer (`docs/voice/research/rewrite-experiment.md`).

The minimal edit uses a nine-line checklist of what the lab's reviewers
asked agents to change. It asks the model to claim only what was done,
use plain words, define abbreviations, give concrete detail, and drop
process talk, em dashes and the `X, not Y` frame. On 74 agent drafts that
people later corrected, the full rewrite moved the text away from the
version the reviewer wrote, and the minimal edit did not
(`docs/voice/research/corrections.md`).

For the judgment calls in `audit`, a frontier model asked the one
question separated Claude's contrasts from the writer's. The 1.5B and 3B
models that fit on two CPU cores did worse
(`docs/voice/research/local-models.md`).

## Papers and proposals

`paper` is scored against the manuscripts claude[bot] wrote in the lab's
repos (`references` in the profile). With one of the writer's papers and
one of Claude's repositories held out at a time, `score -c paper` reads
253 of 291 chunks of the writer's earlier papers as the writer's and 17 as
Claude's. It reads 66 of 79 chunks of Claude's manuscripts as Claude's and
3 as the writer's. When it was scored against Claude's GitHub prose, it
read every one of Claude's drafts of the writer's sections as the
writer's.

`proposal` is scored against 15k words of proposals by coding agents in
the lab's public and private repos, most of them from the Copilot agent
running Claude Opus models. Semicolons, mid-sentence colons, significance
words and "we" separate them from the writer's proposals. Held out, it
reads 32 of 40 of the writer's chunks as the writer's and 38 of 49 of the
agents' chunks as Claude's. With Claude's manuscripts as the reference,
those counts were 33 and 34. The writer's side rests on two proposals and
13k words, so treat the score as a hint and the card as the rules
(`docs/voice/research/technical-writing.md`).

## What is in the profile

For each context, `profile.json` carries document and sentence length
statistics and per-1000-word rates for 31 surface markers. It has the
writer's rate for each of 116 candidate tells, and Claude's rate over the
writer's for each one with its family-wise interval. It also has the
card for each context and the names of its example banks. Across contexts, it
carries Claude's reference rates, the corpus-wide verdicts, and the word
pairs that survive a Holm correction on each side. The published build
keeps only pairs of function words, so project vocabulary stays out.

The example passages come from public repositories and public LinkedIn
posts only. Sent mail and direct messages never leave the machine that
collected them, and only their counts are here.
`scripts/voice/privacy_audit.py` reports what the package would reveal if
published. It checks whether every quoted passage is public, and lists
any private repository name, email address or phone number, the numbers
that come from private text, and the word lists that carry project
vocabulary.
