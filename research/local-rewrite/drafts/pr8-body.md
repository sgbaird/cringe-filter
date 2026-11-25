Follow-up to #3. The rates come from one researcher's corpus, but #3 worded them as facts about human writing in general ("Human writing hedges 30 times more often than Claude", "the human median is 27"). This says "the writer" instead, defined once in the README as the single researcher whose writing was measured, without naming them.

- **Not "reference":** the package already uses that for Claude's side (the `references` rates, "the reference for most contexts is Claude's GitHub prose"), so it would have read backwards.
- **Kept where literal:** "human-written passages", "a careful human writer" in the rewrite prompt, "Examples of human writing", and the verdict "reads human".
- **Output:** `score` prints "the writer's median here is 27", "closer to the writer", and a `writer/1k` column, now one character wider so its header no longer runs into `yours/1k`.
- **Scope:** hand-maintained files only. The profile cards and exemplar headers are generated, so the build pipeline has to switch them too, or the next rebuild brings "the human median" back.

48 tests pass; docs build clean with `sphinx -W`.
