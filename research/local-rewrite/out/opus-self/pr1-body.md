This sets up `@claude` here with the same workflow and token fix as the other lab repos, like `borysgroup/aurora-cloud-infra` and `vertical-cloud-lab/caliber`.

`claude.yml` is the primary/fallback template with both models set to `claude-opus`, which the CLI reads as the alias `opus`, the latest Opus. The `@claude+<model>[:<effort>]` selector works, and effort defaults to max. Since this repo is public, I turned off the full output, the step-summary report and the log upload.

The GitHub token expires after an hour, so `scripts/refresh_github_app_token.py` mints a fresh one once the session's original token expires at minute 60. The new CLAUDE.md section tells the agent when and how to use it. Both come from gist [31e88e2](https://gist.github.com/sgbaird/31e88e2484545af735541fca9773ad08) and gist [9725299](https://gist.github.com/sgbaird/972529991768c5dce469f013f490567e).

Before this can run, the repo needs a `CLAUDE_CODE_OAUTH_TOKEN` secret (`claude setup-token`, then `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R sgbaird/cringe-filter`), and the Claude GitHub App needs access to this repo.

It changes `.github/workflows/claude.yml`, `CLAUDE.md` and `scripts/refresh_github_app_token.py`.
