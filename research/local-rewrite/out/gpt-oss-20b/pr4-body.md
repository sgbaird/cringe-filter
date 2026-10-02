`@claude` without a `+model` tag passed `--model claude-opus` to the CLI, which rejects it with “There's an issue with the selected model (claude-opus)”. Every untagged ping therefore failed in under a minute. Only `@claude+opus`‑style tags worked because the tag is resolved via `resolve_model` to the alias `opus` before the CLI sees it.

The fix is to resolve `PRIMARY_MODEL` the same way, so the CLI receives `--model opus`. After the change, tagged pings resolve exactly as before:

- `@claude` now sends `--model opus` instead of `--model claude-opus`.
- `@claude+opus` still sends `--model opus`.
- `@claude+opus-4.8` still sends `--model claude-opus-4-8`.

The issue was identified in the failed run https://github.com/sgbaird/byu-finances/actions/runs/36251978652, where the log said `claude-opus` “may not exist or you may not have access to it”.
