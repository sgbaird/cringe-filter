I'll update the text to clarify that the rates come from one researcher's corpus. I'll keep "the writer" in the output and notes, since that's defined in the README as the single researcher whose writing was measured.

I changed the terminology so it doesn't conflict with the existing `references` label for Claude's side—the package already uses `references` for Claude's rates, so calling this "reference" would read backwards.

I kept the literal phrases "human-written passages", "a careful human writer", "Examples of human writing", and the verdict "reads human". The output now prints "the writer's median here is 27", says "closer to the writer", and adds a `writer/1k` column that's one character wider so its header doesn't run into `yours/1k`.

This scope covers hand-maintained files only. The profile cards and exemplar headers are generated, so the build pipeline needs to switch them too, or the next rebuild brings "the human median" back.

Follow-up to #3. 48 tests pass; docs build clean with `sphinx -W`.
