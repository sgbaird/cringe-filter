The follow‑up to issue #3 notes that the rates come from a single researcher’s corpus. Issue #3 framed them as general facts (“Human writing hedges 30 times more often than Claude”, “the human median is 27”), but the README defines “the writer” as that researcher, so we refer to them instead.

The package already uses the label reference for Claude’s side (the `references` rates, “the reference for most contexts is Claude's GitHub prose”), so using it for the human side would read backwards.
* Literal terms such as “human‑written passages”, “a careful human writer”, and the verdict “reads human” are preserved.
* The `score` output now prints “the writer's median here is 27”, “closer to the writer”, and adds a `writer/1k` column. The header is one character wider so it no longer overlaps `yours/1k`.

Only hand‑maintained files changed; the profile cards and exemplar headers are generated, so the build pipeline must update them too, or the next rebuild will restore “the human median”.

All 48 tests pass and the documentation builds cleanly with `sphinx -W`.
