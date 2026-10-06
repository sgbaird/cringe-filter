---
name: cringe-filter
description: Apply the measured AI-cringe filter and human-voice filter to drafted prose before it is sent, posted or committed. Use for GitHub replies, Discussions posts, issues in other people's repos, email, short messages, LinkedIn posts, docs pages and scientific prose. Run as a final pass, not while drafting.
---

# cringe-filter

A review pass after the draft exists. It is a separate step rather than a
standing rule list because a long list of rules degrades everything else
the agent is doing; the deterministic checks live in code and the judgment
calls are few.

Requires `pip install cringe-filter` (or `uvx cringe-filter ...`).

## Procedure

**1. Pick the context.** Where is the text going? `github` (your own
repos), `discussion`, `third-party` (someone else's repo), `email`,
`message` (DM, chat, comment), `linkedin`, `tutorial`, `paper`,
`proposal`. When you
have the destination URL, let it decide: `--url <url>`.

**2. Lint.** Write the draft to a temp file and run

```bash
cringe-filter lint --context <context> draft.md
```

Fix every `error`. Judge each `warn` and `info` on merit: `[15.2x, CI
9.7-23.9]` is a measured gap worth acting on; `[preventive, no corpus
support]` is a nudge.

**Drafts headed to review** (a manuscript, proposal, abstract, or a page
someone will read line by line): do not rewrite. Print the minimal-edit
filter and make only its edits:

```bash
cringe-filter prompt --minimal --context paper draft.tex
cringe-filter audit --context paper draft.tex    # the findings, by sentence
```

The audit lists each sentence to fix with its line and reason, and marks
the "X, not Y" hits as judgment calls: keep one only if Y is an
instruction, a real alternative, or something a reader would believe.

On drafts people later corrected, a full rewrite doubled the distance to
the reviewer's version, and the minimal edit did not
(`docs/voice/research/corrections.md`). After each revision round, lint
only what the round added, because agent revisions put the tells back:

```bash
cringe-filter lint --against previous.tex draft.tex
```

**3. Read the filter and apply it yourself.**

```bash
cringe-filter prompt --context <context> --system-only
```

That prints the filter: two real human-written passages, the register's
priorities, the measured tells in words and the register notes (the rates
behind them are in `--evidence`). Read the passages first. Then rewrite
your draft to match, keeping every fact, link and number. The five things
the linter cannot check:

- **Length.** The writer's median GitHub reply is 27 words; Claude's is 638. Cut to
  the shortest version that answers the question.
- **Stance.** Hedge where the fact is uncertain ("might be", "not sure
  if", "seems to") and nowhere else. The writer hedges 30 times more often than
  Claude does and asks 12 times more questions.
- **Audience.** Write for the reader. Delete defensive clauses about
  points nobody raised, replies to whoever last gave feedback, and any
  narration of the editing itself.
- **Small words.** The writer's replies talk to the people in a thread ("we could", "it
  might be", "can you", "this"); Claude reports to them in noun phrases.
  A held-out test found rewrites that removed every tell and matched the writer
  sentence length still read as Claude to a function-word model, because
  "we", "be" and "could" stayed at Claude's rates. The prompt names the writer's
  small words for each context; use them where they fit.
- **Sentence skeleton.** The same test, rerun with a parser, found the
  rewrites fixed the paragraphs and kept Claude's sentences: a thing as
  the subject ("The parser drops..."), a second idea packed in with a
  colon, dash or parenthesis. The writer's subject is usually a person ("I think",
  "we could", "can you"). Rebuild the sentences, not just the words, but
  do not turn a report into one "I did X" sentence after another
  (`docs/voice/research/structure.md`).

**4. Score, once.** `cringe-filter score --context <context> draft.md`
shows which features still pull the text toward Claude. Fix the top two or
three and stop. Do not iterate past that: repeated revision degrades text
that was already fine.

In a manuscript or proposal (`paper`, `proposal`, or any `.tex` file) the
score compares against Claude's own scientific prose (for a proposal, the
agents' proposals in the lab's repos), and the features that separate them
are "we" (Claude writes a fifth as many), colons and
semicolons carrying a second idea (four to five times the writer's rate), "critical" and
"key" (four times), and no hedge at all. The lab's corrections to Claude's
manuscripts were mostly not about words: claim only what was done, write
for the reader rather than as a reply to whoever asked for the edit, keep
issue and PR numbers out, define every abbreviation, and keep what a human
wrote intact. In proposals, add: name the method plainly rather than by
metaphor, meet the page limit by cutting content rather than compressing
sentences, and check that every citation exists. Leave long sentences long. Rewrite a manuscript draft only
when `score -c paper` reads it as Claude's: on drafts that already read as
the writer's, the paper prompt doubled "we" and removed the writer's semicolons
(`docs/voice/research/technical-writing.md`).

**5. Report what changed** in one sentence, outside the deliverable.

## When not to use this

Code, commit messages, config, and throwaway notes. A voice pass on a
one-line status update costs more than it saves. Detector evasion is not
the goal; sounding like the writer is.
