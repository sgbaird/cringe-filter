I switched the rates to reference "the writer" from the README. The package already uses that for Claude's side (`references`), so the rewrite kept "human-written passages" and "a careful human writer" literal. The `score` prints the writer's median (27) and a wider `writer/1k` column avoids header collision with `yours/1k`.

We only hand-maintain files now. The profile cards and exemplar headers are generated, so the build pipeline needs to switch them too.

48 tests pass; docs build clean with `sphinx -W`.
