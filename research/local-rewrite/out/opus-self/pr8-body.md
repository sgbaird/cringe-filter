This follows up on #3. The rates come from one researcher's corpus, but #3 worded them as facts about human writing in general ("Human writing hedges 30 times more often than Claude", "the human median is 27"). This says "the writer" instead, defined once in the README as the single researcher whose writing was measured, without naming them.

I didn't use "reference" because the package already uses that for Claude's side (the `references` rates, "the reference for most contexts is Claude's GitHub prose"), so it would have read backwards.

I kept the literal uses: "human-written passages", "a careful human writer" in the rewrite prompt, "Examples of human writing", and the verdict "reads human".

`score` now prints "the writer's median here is 27", "closer to the writer", and a `writer/1k` column. The column is one character wider so its header no longer runs into `yours/1k`.

This only covers the hand-maintained files. The profile cards and exemplar headers are generated, so the build pipeline has to switch them too, or the next rebuild brings "the human median" back.

48 tests pass and the docs build clean with `sphinx -W`.
