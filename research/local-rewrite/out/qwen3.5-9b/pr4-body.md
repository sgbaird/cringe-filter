I'm fixing `PRIMARY_MODEL` so it resolves to the alias `opus` for the CLI, which stops untagged pings from failing.

Before, `@claude` passed `--model claude-opus` and got rejected because the CLI doesn't see that alias. `@claude+model-opus` worked because the tag alone went through `resolve_model`. Now tagged pings resolve exactly as before:

- `@claude` passes `--model opus`
- `@claude+model-opus` passes `--model opus`
- `@claude+model-opus-4.8` passes `--model claude-opus-4-8`

The issue came from https://github.com/sgbaird/byu-finances/actions/runs/36251978652, where the log said `claude-opus` "may not exist or you may not have access to it."
