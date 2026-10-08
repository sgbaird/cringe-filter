A bare `@claude` (no `+model` tag) passed `--model claude-opus` straight to the CLI, which rejects it ("There's an issue with the selected model (claude-opus)"). So every untagged ping failed in under a minute. Only `@claude+opus`-style tags worked, because only the tag went through `resolve_model`.

This resolves `PRIMARY_MODEL` the same way, so it reaches the CLI as the alias `opus`. A bare `@claude` now passes `--model opus` instead of `--model claude-opus`. Tagged pings resolve exactly as before: `@claude+opus` still gives `--model opus`, and `@claude+opus-4.8` still gives `--model claude-opus-4-8`.

I found it from the failed run https://github.com/sgbaird/byu-finances/actions/runs/36251978652, where the execution log says `claude-opus` "may not exist or you may not have access to it".
