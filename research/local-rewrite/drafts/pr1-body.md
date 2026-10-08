Sets up `@claude` in this repo using the same workflow and token fix as the other lab repos (e.g. `borysgroup/aurora-cloud-infra`, `vertical-cloud-lab/caliber`).

**1. `claude.yml`.** This is the primary/fallback template with both models set to `claude-opus`, which the CLI reads as the alias `opus`, i.e. the latest Opus. The `@claude+<model>[:<effort>]` selector works, and effort defaults to max. Since this repo is public, full output, the step-summary report, and the log upload are off.

**2. The one-hour GitHub token expiry.** `scripts/refresh_github_app_token.py` mints a fresh token once the session's original one expires at minute 60. The new CLAUDE.md section tells the agent when and how to use it. Both come from gist [31e88e2](https://gist.github.com/sgbaird/31e88e2484545af735541fca9773ad08) and gist [9725299](https://gist.github.com/sgbaird/972529991768c5dce469f013f490567e).

**Before this can run:** the repo has no `CLAUDE_CODE_OAUTH_TOKEN` secret yet (`claude setup-token`, then `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R sgbaird/cringe-filter`). The Claude GitHub App also needs access to this repo.

Files:
- `.github/workflows/claude.yml`
- `CLAUDE.md`
- `scripts/refresh_github_app_token.py`
