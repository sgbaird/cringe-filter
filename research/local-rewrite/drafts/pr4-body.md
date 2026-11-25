A bare `@claude` (no `+model` tag) passed `--model claude-opus` straight to the CLI, which rejects it ("There's an issue with the selected model (claude-opus)"), so every untagged ping failed in under a minute. Only `@claude+opus`-style tags worked, because only the tag went through `resolve_model`.

Fix: resolve `PRIMARY_MODEL` the same way, so it reaches the CLI as the alias `opus`. Tagged pings resolve exactly as before:

| trigger | before | after |
| --- | --- | --- |
| `@claude` | `--model claude-opus` (fails) | `--model opus` |
| `@claude+opus` | `--model opus` | `--model opus` |
| `@claude+opus-4.8` | `--model claude-opus-4-8` | `--model claude-opus-4-8` |

Found from the failed run https://github.com/sgbaird/byu-finances/actions/runs/36251978652 (execution log: `claude-opus` "may not exist or you may not have access to it").
