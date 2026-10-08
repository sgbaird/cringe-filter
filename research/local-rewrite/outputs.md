# Rewrites of six PR bodies Claude wrote in this repo

Context `github`. Each rewrite went through `cringe_filter.rewrite.rewrite()` (prompt, lint, at most one revision) with the model swapped for a local one, except the first, which is the frontier reference. The line under each rewrite is what the package itself measures; it does not check facts.

## Body of PR #13

````markdown
Adds `cringe-filter mcp`, an MCP server for the filter. Closes #11.

- Tools: lint, score, filter_prompt, audit and contexts. Prompts: rewrite and minimal_edit. Resources: cringe-filter://filter/{context} and cringe-filter://profile/{context}.
- stdio by default. `--transport streamable-http` serves /mcp statelessly, and the Dockerfile runs that on $PORT.
- An optional `mcp` extra (mcp>=2.2,<3, Python 3.10+), so the package keeps no dependencies.
- The CLI's context choice moves to `registers.pick`, which the server shares.
- 10 new tests. The MCP ones skip without the mcp package, as on Python 3.9.
````

Source: 85 words, score +2.94, 0 lint findings.

### Claude Opus 5.5, applying the same prompt by hand in one pass

````markdown
This adds `cringe-filter mcp`, so the filter can run as an MCP server. Closes #11.

It serves lint, score, filter_prompt, audit and contexts as tools, rewrite and minimal_edit as prompts, and cringe-filter://filter/{context} and cringe-filter://profile/{context} as resources.

It uses stdio by default. With `--transport streamable-http` it serves /mcp statelessly, and the Dockerfile runs that on $PORT.

I put the server behind an optional `mcp` extra (mcp>=2.2,<3, Python 3.10+) so the package itself still has no dependencies. The CLI's context choice moved to `registers.pick` so the server can share it.

There are 10 new tests. The MCP ones skip when the mcp package isn't installed, like on Python 3.9.
````

107 words, score -4.68, 0 lint findings, dropped: none.

### qwen3.5-2b

````markdown
I see the draft is very dense. It feels like a checklist from a commit message.

We could try to simplify this. The writer might have been too focused on listing features. I think it's better to explain the result first.

1. Adds `cringe-filter mcp`, which is an MCP server for the filter. This closes #11.
2. Tools include lint, score, filter_prompt, audit, and contexts. The prompts are rewrite and minimal_edit.
3. Resources are cringe-filter://filter/{context} and cringe-filter://profile/{context}.
4. Stdio is the default. `--transport streamable-http` serves /mcp statelessly, and the Dockerfile runs that on $PORT.
5. An optional `mcp` extra (mcp>=2.2,<3, Python 3.10+) keeps the package with no dependencies.
6. The CLI's context choice moves to `registers.pick`, which the server shares.
7. 10 new tests exist. The MCP ones skip without the mcp package, which is on Python 3.9.

We could have been more direct. The writer might have felt that listing everything was too much.

We could try to add a bit more context. The writer might have felt that this was too technical. I think it's better to say what the result is.

I think the writer should have been clearer. The writer might have felt that the list was too long.

We could have been more concise. The writer might have felt that the list was too long.

I think the writer should have been clearer. The writer might have felt that the list was too long.

We could have been more concise. The writer might have felt that the list was too long.

I think the writer should have been clearer. The
````

265 words, score -114.27, 1 lint findings, dropped: none.

### qwen3.5-4b

````markdown
I've added `cringe-filter mcp`, an MCP server that closes #11. It includes tools like lint, score, filter_prompt, audit, and contexts, plus prompts for rewrite and minimal_edit. The server runs on stdio by default, but you can enable `--transport streamable-http` for stateless /mcp access, which the Dockerfile exposes on $PORT. I've added an optional `mcp` extra (mcp>=2.2,<3, Python 3.10+) so the package stays dependency-free. The CLI's context choice now uses `registers.pick` to share context selection with the server. I also added 10 new tests; the MCP tests skip without the mcp package on Python 3.9.
````

94 words, score -7.42, 2 lint findings, dropped: none.

### gemma-4-e4b, reply capped at about twice the draft

````markdown
### Plan:
1.  **Analyze the previous attempt:** Identify and remove any instances of bold emphasis, the "X, not Y" correction, and ensure all specific code spans, numbers, and names are present.
2.  **Re-incorporate missing elements:** Reintegrate `cringe-filter mcp`, `--transport streamable-http`, `mcp`, `registers.pick`, `2.2`, `3.10`, and `3.9` into the text.
3.  **Apply writing style constraints:** Maintain a conversational, human, and non-report-like tone, using verbs and hedges where appropriate.
4.  **Review constraints:** Ensure the final output is only the rewritten text, is under 110 words, and follows all style guidelines.

### Execution:
*(Self-Correction during drafting: The original draft was very list-heavy and technical. I need to turn this into a human-sounding GitHub update while keeping the density of information.)*

### Final Output Generation.
````

121 words, score +3.72, 8 lint findings, dropped: none.

### gemma-4-e4b, with 1200 more tokens of room

````markdown
I need to rewrite the original draft while strictly adhering to all the provided constraints. I must address the specific violations flagged in the previous review (bold emphasis, 'X, not Y' phrasing, and ensuring the tone is conversational and directed at the team).

**Original Draft:**
Adds `cringe-filter mcp`, an MCP server for the filter. Closes #11.

- Tools: lint, score, filter_prompt, audit and contexts. Prompts: rewrite and minimal_edit. Resources: cringe-filter://filter/{context} and cringe-filter://profile/{context}.
- stdio by default. `--transport streamable-http` serves /mcp statelessly, and the Dockerfile runs that on $PORT.
- An optional `mcp` extra (mcp>=2.2,<3, Python 3.10+), so the package keeps no dependencies.
- The CLI's context choice moves to `registers.pick`, which the server shares.
- 10 new tests. The MCP ones skip without the mcp package, as on Python 3.9.

**Refining the rewrite based on feedback:**
1.  **Tone:** Must sound like a person talking to the team.
2.  **Structure:** Lead with the action/answer.
3.  **Formatting:** No bolding, no excessive punctuation.
4.  **Content:** Keep all facts (tools, prompts, URLs, versions, commands, test notes).

**Drafting the final response.**
````

176 words, score +8.20, 8 lint findings, dropped: none.

### lfm2.5-8b-a1b

````markdown
Adds `cringe-filter mcp`, an MCP server for the filter. Closes #11.

- Tools: lint, score, filter_prompt, audit, contexts. Prompts: rewrite, minimal_edit.  
- Resources: `cringe-filter://filter/{context}` and `cringe-filter://profile/{context}`.  
- stdio by default. `--transport streamable-http` serves /mcp statelessly, and the Dockerfile runs that on $PORT.  
- Optional `mcp` extra (mcp>=2.2,<3, Python 3.10+); package keeps no dependencies.  
- CLI's context choice moves to `registers.pick`, which the server shares.  
- 10 new tests. The MCP ones skip without the mcp package, as on Python 3.9.
````

80 words, score +3.69, 0 lint findings, dropped: none.

### qwen3.5-9b

````markdown
I've added `cringe-filter mcp`, an MCP server for the filter. This closes #11.

The server includes tools for lint, score, filter_prompt, audit, and contexts, plus rewrite and minimal_edit prompts. Resources expose the filter and profile contexts at `cringe-filter://filter/{context}` and `cringe-filter://profile/{context}`.

By default, it uses stdio. You can also serve statelessly over `/mcp` with `--transport streamable-http`, which the Dockerfile runs on `$PORT`.

I added an optional `mcp` extra requiring MCP>=2.2,<3 and Python 3.10+. This keeps the package dependency-free otherwise. The CLI's context choice now moves to `registers.pick`, which the server shares.

I also added 10 new tests. The MCP ones skip without the mcp package, as on Python 3.9.
````

108 words, score -9.33, 0 lint findings, dropped: none.

### gpt-oss-20b

````markdown
Added the `cringe-filter mcp` command, an MCP server for the filter, and closed issue #11.

- It uses the existing tools: lint, score, filter_prompt, audit, and contexts.  
- Prompts available: rewrite and minimal_edit.  
- Resources are exposed at cringe-filter://filter/{context} and cringe-filter://profile/{context}.  
- By default it writes to stdio; with `--transport streamable-http` it serves `/mcp` statelessly, and the Dockerfile runs that on `$PORT`.  
- An optional `mcp` extra (`mcp>=2.2,<3`, Python 3.10+) keeps the base package dependency‑free.  
- The CLI’s context picker now uses `registers.pick`, which the server also exposes, allowing users to select contexts from the same registry.  
- Ten new tests were added; the MCP tests are skipped when the `mcp` package is unavailable, such as on Python 3.9.
````

119 words, score +5.98, 2 lint findings, dropped: none.

## Body of PR #12

````markdown
Rewrites the README by running cringe-filter on it in the tutorial context, following SKILL.md (lint, read the prompt, rewrite, score once).

- README before: 26 findings (1 error), 2146 words, score +4.51 (reads like Claude). After: 3 info findings, 1457 words, score -77.67 (reads human).
- New docs/methods.md holds the measurement details moved out of the README.
- lint: suppression comments inside code blocks no longer apply. The README's own disable-file example had switched the linter off for the whole file. A new test keeps the README free of errors and warnings under its own linter.

Addresses #10. Package suggestions from the process are in the issue comment.
````

Source: 108 words, score +1.17, 0 lint findings.

### Claude Opus 5.5, applying the same prompt by hand in one pass

````markdown
I rewrote the README by running cringe-filter on it in the tutorial context, the way SKILL.md says to (lint, read the prompt, rewrite, score once).

Before, the README had 26 findings (1 error), 2146 words and a score of +4.51, which reads like Claude. Now it has 3 info findings, 1457 words and a score of -77.67, which reads human.

The measurement details moved out of the README into a new docs/methods.md.

I also fixed lint so suppression comments inside code blocks no longer apply. The README's own disable-file example had switched the linter off for the whole file. A new test keeps the README free of errors and warnings under its own linter.

Addresses #10. My package suggestions from the process are in the issue comment.
````

127 words, score -3.97, 1 lint findings, dropped: none.

### qwen3.5-4b

````markdown
I fixed the README by running the cringe-filter in tutorial context as SKILL.md suggests. It went from 26 findings and +4.51 score to just 3 info findings and -77.67 score, reading more human. The word count dropped from 2146 to 1457. I moved measurement details to docs/methods.md. Also, lint suppression comments in code blocks don't work anymore; the README's disable-file example now turns off the linter for the whole file. I added a test to keep the README clean. The package suggestions are in the issue comment for #10.
````

89 words, score -10.76, 0 lint findings, dropped: none.

## Body of PR #3

````markdown
Removes the references to Sterling ("his median", "reads like Sterling", "Real passages Sterling wrote", "the way Sterling Baird would write it") and describes each context by the task it is tuned for.

- **Wording:** "the human median/rate", "reads human", "Examples of human writing", context labels like "GitHub reply in your own repos"; corrections credited to "a reviewer"
- **Unchanged:** quoted exemplar passages (byte-identical), English word lists and regexes that contain "he"/"his" as data, author metadata in `pyproject.toml`/`LICENSE`, and the internal `sterling` key in `profile.json` (the build pipeline writes it)
- 48 tests pass; docs build clean with `sphinx -W`

Heads-up: the private build pipeline still generates the old wording, so the next profile rebuild needs the same changes upstream or it will reintroduce them.
````

Source: 124 words, score +6.93, 5 lint findings.

### Claude Opus 5.5, applying the same prompt by hand in one pass

````markdown
This removes the references to Sterling ("his median", "reads like Sterling", "Real passages Sterling wrote", "the way Sterling Baird would write it") and describes each context by the task it's tuned for.

The new wording is "the human median/rate", "reads human" and "Examples of human writing", with context labels like "GitHub reply in your own repos". Corrections are credited to "a reviewer".

I left a few things alone: the quoted exemplar passages (byte-identical), the English word lists and regexes that contain "he"/"his" as data, the author metadata in `pyproject.toml`/`LICENSE`, and the internal `sterling` key in `profile.json`, since the build pipeline writes it.

48 tests pass and the docs build clean with `sphinx -W`.

The private build pipeline still generates the old wording, so we need the same changes upstream before the next profile rebuild, or it will bring them back.
````

140 words, score -5.34, 2 lint findings, dropped: none.

### qwen3.5-4b

````markdown
I rebuilt the figure and pushed it. I removed the Sterling references so the context is defined by its task instead of by the author.

I kept the quoted exemplar passages, the English word lists, the regexes, and the internal `sterling` key in `profile.json`.

- Wording: "the human median/rate", "reads human", "Examples of human writing", context labels like "GitHub reply in your own repos"
- Unchanged: quoted exemplar passages, English word lists and regexes that contain "he"/"his" as data, author metadata in `pyproject.toml`/`LICENSE`, and the internal `sterling` key in `profile.json`
- 48 tests pass; docs build clean with `sphinx -W`

The private build pipeline still generates the old wording, so the next profile rebuild needs the same changes upstream or it will reintroduce them.
````

124 words, score -7.10, 1 lint findings, dropped: none.

## Body of PR #4

````markdown
A bare `@claude` (no `+model` tag) passed `--model claude-opus` straight to the CLI, which rejects it ("There's an issue with the selected model (claude-opus)"), so every untagged ping failed in under a minute. Only `@claude+opus`-style tags worked, because only the tag went through `resolve_model`.

Fix: resolve `PRIMARY_MODEL` the same way, so it reaches the CLI as the alias `opus`. Tagged pings resolve exactly as before:

| trigger | before | after |
| --- | --- | --- |
| `@claude` | `--model claude-opus` (fails) | `--model opus` |
| `@claude+opus` | `--model opus` | `--model opus` |
| `@claude+opus-4.8` | `--model claude-opus-4-8` | `--model claude-opus-4-8` |

Found from the failed run https://github.com/sgbaird/byu-finances/actions/runs/36251978652 (execution log: `claude-opus` "may not exist or you may not have access to it").
````

Source: 127 words, score +9.69, 5 lint findings.

### Claude Opus 5.5, applying the same prompt by hand in one pass

````markdown
A bare `@claude` (no `+model` tag) passed `--model claude-opus` straight to the CLI, which rejects it ("There's an issue with the selected model (claude-opus)"). So every untagged ping failed in under a minute. Only `@claude+opus`-style tags worked, because only the tag went through `resolve_model`.

This resolves `PRIMARY_MODEL` the same way, so it reaches the CLI as the alias `opus`. A bare `@claude` now passes `--model opus` instead of `--model claude-opus`. Tagged pings resolve exactly as before: `@claude+opus` still gives `--model opus`, and `@claude+opus-4.8` still gives `--model claude-opus-4-8`.

I found it from the failed run https://github.com/sgbaird/byu-finances/actions/runs/36251978652, where the execution log says `claude-opus` "may not exist or you may not have access to it".
````

112 words, score -2.35, 0 lint findings, dropped: none.

### qwen3.5-2b

````markdown
I rebuilt the figure and pushed it to the repo. I added back the code span for `+model`, `--model claude-opus`, `--model opus`, `--model opus-4-8`, `--model claude-opus-4-8`, `--model opus`, `@claude`, `@claude+opus`, `@claude+opus-4.8`, `PRIMARY_MODEL`, and `claude-opus`. I also restored the link to the action run. I removed the emoji and the table to keep it simple. I kept the facts and the log message. I used short sentences and kept "we" as the subject where appropriate. I asked you to check the log. I didn't add any new claims or explanations.

Does this sound pretentious to someone who already knows what they are doing? If yes, cut a third and put the honest hedges back. Then check silently that every fact, number, link, code span and command is still there and that nothing new was claimed.
````

134 words, score -34.99, 1 lint findings, dropped: code: resolve_model; urls: https://github.com/sgbaird/byu-finances/actions/runs/36251978652.

### qwen3.5-4b

````markdown
I can't change the behavior; only `@claude+model` tags worked. I'm fixing `resolve_model` to resolve `PRIMARY_MODEL` to `opus` so the CLI alias matches. The run failed because the CLI rejected `--model claude-opus`.

Here's how it will behave now:

- `@claude` will send `--model opus`
- `@claude+opus` stays `--model opus`
- `@claude+opus-4.8` stays `--model claude-opus-4-8`

I'll push the fix when I have time. Can you check the logs if this doesn't work? Found from the failed run https://github.com/sgbaird/byu-finances/actions/runs/36251978652
````

76 words, score -17.83, 0 lint findings, dropped: none.

### lfm2.5-8b-a1b

````markdown
@claude
--model claude-opus (fails)
Only @claude+opus-style tags worked, because only the tag went through resolve_model.

Fix: resolve PRIMARY_MODEL the same way, so it reaches the CLI as the alias opus. Tagged pings resolve exactly as before:

| trigger | before | after |
|---|---|---|
| @claude | --model claude-opus (fails) | --model opus |
| @claude+opus | --model opus | --model opus |
| @claude+opus-4.8 | --model claude-opus-4-8 | --model claude-opus-4-8 |

The failed run (https://github.com/sgbaird/byu-finances/actions/runs/36251978652) showed claude-opus “may not exist or you may not have access to it”.
````

89 words, score +8.07, 5 lint findings, dropped: code: +model.

### qwen3.5-9b

````markdown
I'm fixing `PRIMARY_MODEL` so it resolves to the alias `opus` for the CLI, which stops untagged pings from failing.

Before, `@claude` passed `--model claude-opus` and got rejected because the CLI doesn't see that alias. `@claude+model-opus` worked because the tag alone went through `resolve_model`. Now tagged pings resolve exactly as before:

- `@claude` passes `--model opus`
- `@claude+model-opus` passes `--model opus`
- `@claude+model-opus-4.8` passes `--model claude-opus-4-8`

The issue came from https://github.com/sgbaird/byu-finances/actions/runs/36251978652, where the log said `claude-opus` "may not exist or you may not have access to it."
````

86 words, score -6.16, 0 lint findings, dropped: code: @claude+opus, @claude+opus-4.8.

### gpt-oss-20b

````markdown
`@claude` without a `+model` tag passed `--model claude-opus` to the CLI, which rejects it with “There's an issue with the selected model (claude-opus)”. Every untagged ping therefore failed in under a minute. Only `@claude+opus`‑style tags worked because the tag is resolved via `resolve_model` to the alias `opus` before the CLI sees it.

The fix is to resolve `PRIMARY_MODEL` the same way, so the CLI receives `--model opus`. After the change, tagged pings resolve exactly as before:

- `@claude` now sends `--model opus` instead of `--model claude-opus`.
- `@claude+opus` still sends `--model opus`.
- `@claude+opus-4.8` still sends `--model claude-opus-4-8`.

The issue was identified in the failed run https://github.com/sgbaird/byu-finances/actions/runs/36251978652, where the log said `claude-opus` “may not exist or you may not have access to it”.
````

123 words, score +0.63, 0 lint findings, dropped: none.

## Body of PR #1

````markdown
Sets up `@claude` in this repo using the same workflow and token fix as the other lab repos (e.g. `borysgroup/aurora-cloud-infra`, `vertical-cloud-lab/caliber`).

**1. `claude.yml`.** This is the primary/fallback template with both models set to `claude-opus`, which the CLI reads as the alias `opus`, i.e. the latest Opus. The `@claude+<model>[:<effort>]` selector works, and effort defaults to max. Since this repo is public, full output, the step-summary report, and the log upload are off.

**2. The one-hour GitHub token expiry.** `scripts/refresh_github_app_token.py` mints a fresh token once the session's original one expires at minute 60. The new CLAUDE.md section tells the agent when and how to use it. Both come from gist [31e88e2](https://gist.github.com/sgbaird/31e88e2484545af735541fca9773ad08) and gist [9725299](https://gist.github.com/sgbaird/972529991768c5dce469f013f490567e).

**Before this can run:** the repo has no `CLAUDE_CODE_OAUTH_TOKEN` secret yet (`claude setup-token`, then `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R sgbaird/cringe-filter`). The Claude GitHub App also needs access to this repo.

Files:
- `.github/workflows/claude.yml`
- `CLAUDE.md`
- `scripts/refresh_github_app_token.py`
````

Source: 149 words, score +10.47, 5 lint findings.

### Claude Opus 5.5, applying the same prompt by hand in one pass

````markdown
This sets up `@claude` here with the same workflow and token fix as the other lab repos, like `borysgroup/aurora-cloud-infra` and `vertical-cloud-lab/caliber`.

`claude.yml` is the primary/fallback template with both models set to `claude-opus`, which the CLI reads as the alias `opus`, the latest Opus. The `@claude+<model>[:<effort>]` selector works, and effort defaults to max. Since this repo is public, I turned off the full output, the step-summary report and the log upload.

The GitHub token expires after an hour, so `scripts/refresh_github_app_token.py` mints a fresh one once the session's original token expires at minute 60. The new CLAUDE.md section tells the agent when and how to use it. Both come from gist [31e88e2](https://gist.github.com/sgbaird/31e88e2484545af735541fca9773ad08) and gist [9725299](https://gist.github.com/sgbaird/972529991768c5dce469f013f490567e).

Before this can run, the repo needs a `CLAUDE_CODE_OAUTH_TOKEN` secret (`claude setup-token`, then `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R sgbaird/cringe-filter`), and the Claude GitHub App needs access to this repo.

It changes `.github/workflows/claude.yml`, `CLAUDE.md` and `scripts/refresh_github_app_token.py`.
````

148 words, score -2.46, 1 lint findings, dropped: none.

### qwen3.5-4b

````markdown
I set up `@claude` in this repo using the same workflow and token fix as `borysgroup/aurora-cloud-infra` and `vertical-cloud-lab/caliber`. I configured `claude.yml` with both models defaulting to `claude-opus`, so the selector `@claude+<model>[:<effort>]` works with effort set to max. I'm turning off full output, step-summary reports, and log uploads since the repo is public. I also added the one-hour GitHub token expiry script to mint a fresh token once the session's original one expires at minute 60, and updated `CLAUDE.md` with instructions from gist [31e88e2](https://gist.github.com/sgbaird/31e88e2484545af735541fca9773ad08) and gist [9725299](https://gist.github.com/sgbaird/972529991768c5dce469f013f490567e). Before this can run, the repo needs `CLAUDE_CODE_OAUTH_TOKEN` secret set via `claude setup-token` then `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R sgbaird/cringe-filter`, and the Claude GitHub App needs access to this repo.
````

116 words, score -15.52, 1 lint findings, dropped: code: .github/workflows/claude.yml, scripts/refresh_github_app_token.py.

## Body of PR #8

````markdown
Follow-up to #3. The rates come from one researcher's corpus, but #3 worded them as facts about human writing in general ("Human writing hedges 30 times more often than Claude", "the human median is 27"). This says "the writer" instead, defined once in the README as the single researcher whose writing was measured, without naming them.

- **Not "reference":** the package already uses that for Claude's side (the `references` rates, "the reference for most contexts is Claude's GitHub prose"), so it would have read backwards.
- **Kept where literal:** "human-written passages", "a careful human writer" in the rewrite prompt, "Examples of human writing", and the verdict "reads human".
- **Output:** `score` prints "the writer's median here is 27", "closer to the writer", and a `writer/1k` column, now one character wider so its header no longer runs into `yours/1k`.
- **Scope:** hand-maintained files only. The profile cards and exemplar headers are generated, so the build pipeline has to switch them too, or the next rebuild brings "the human median" back.

48 tests pass; docs build clean with `sphinx -W`.
````

Source: 178 words, score +18.70, 9 lint findings.

### Claude Opus 5.5, applying the same prompt by hand in one pass

````markdown
This follows up on #3. The rates come from one researcher's corpus, but #3 worded them as facts about human writing in general ("Human writing hedges 30 times more often than Claude", "the human median is 27"). This says "the writer" instead, defined once in the README as the single researcher whose writing was measured, without naming them.

I didn't use "reference" because the package already uses that for Claude's side (the `references` rates, "the reference for most contexts is Claude's GitHub prose"), so it would have read backwards.

I kept the literal uses: "human-written passages", "a careful human writer" in the rewrite prompt, "Examples of human writing", and the verdict "reads human".

`score` now prints "the writer's median here is 27", "closer to the writer", and a `writer/1k` column. The column is one character wider so its header no longer runs into `yours/1k`.

This only covers the hand-maintained files. The profile cards and exemplar headers are generated, so the build pipeline has to switch them too, or the next rebuild brings "the human median" back.

48 tests pass and the docs build clean with `sphinx -W`.
````

187 words, score -6.03, 1 lint findings, dropped: none.

### qwen3.5-2b

````markdown
The output shows the writer's median here is 27, with a `writer/1k` column. I'm not sure if this means the same thing as "human-written passages," but the verdict "reads human" is clear. I think the build pipeline needs switching for the profile cards and exemplar headers, otherwise the next rebuild brings "the human median" back.

48 tests pass; docs build clean with `sphinx -W`.

**Note:** I kept the phrase "human-written passages" from the prompt since it's a specific term used in the rewrite. I also kept the number 27 and the command `sphinx -W`. I didn't add anything the draft didn't contain.

- **Bold-run:** Bold emphasis. (uild clean with `sphinx -W`)
- **References:** code span
- **Score:** code span
- **Yours/1k:** code span
- **3:** number
````

126 words, score +1.84, 12 lint findings, dropped: code: references, score, yours/1k; numbers: 30.

### qwen3.5-4b

````markdown
I switched the rates to reference "the writer" from the README. The package already uses that for Claude's side (`references`), so the rewrite kept "human-written passages" and "a careful human writer" literal. The `score` prints the writer's median (27) and a wider `writer/1k` column avoids header collision with `yours/1k`.

We only hand-maintain files now. The profile cards and exemplar headers are generated, so the build pipeline needs to switch them too.

48 tests pass; docs build clean with `sphinx -W`.
````

80 words, score -3.84, 0 lint findings, dropped: numbers: 3, 30.

### lfm2.5-8b-a1b

````markdown
Follow-up to #3. The rates come from one researcher's corpus, but human writing hedges 30 times more often than Claude, and the human median is 27. I might be unsure if this is the case, but it reads the writer's median here is 27, closer to the writer, and a writer/1k column, now one character wider so its header no longer runs into yours/1k. Hand‑maintained files only. The profile cards and exemplar headers are generated, so the build pipeline must switch them, or the next rebuild brings the human median back. All 48 tests pass; docs build clean with sphinx -W.
````

101 words, score -7.94, 0 lint findings, dropped: code: references, score.

### qwen3.5-9b

````markdown
I'll update the text to clarify that the rates come from one researcher's corpus. I'll keep "the writer" in the output and notes, since that's defined in the README as the single researcher whose writing was measured.

I changed the terminology so it doesn't conflict with the existing `references` label for Claude's side—the package already uses `references` for Claude's rates, so calling this "reference" would read backwards.

I kept the literal phrases "human-written passages", "a careful human writer", "Examples of human writing", and the verdict "reads human". The output now prints "the writer's median here is 27", says "closer to the writer", and adds a `writer/1k` column that's one character wider so its header doesn't run into `yours/1k`.

This scope covers hand-maintained files only. The profile cards and exemplar headers are generated, so the build pipeline needs to switch them too, or the next rebuild brings "the human median" back.

Follow-up to #3. 48 tests pass; docs build clean with `sphinx -W`.
````

162 words, score -10.26, 2 lint findings, dropped: code: score; numbers: 30.

### gpt-oss-20b

````markdown
The follow‑up to issue #3 notes that the rates come from a single researcher’s corpus. Issue #3 framed them as general facts (“Human writing hedges 30 times more often than Claude”, “the human median is 27”), but the README defines “the writer” as that researcher, so we refer to them instead.

The package already uses the label reference for Claude’s side (the `references` rates, “the reference for most contexts is Claude's GitHub prose”), so using it for the human side would read backwards.
* Literal terms such as “human‑written passages”, “a careful human writer”, and the verdict “reads human” are preserved.
* The `score` output now prints “the writer's median here is 27”, “closer to the writer”, and adds a `writer/1k` column. The header is one character wider so it no longer overlaps `yours/1k`.

Only hand‑maintained files changed; the profile cards and exemplar headers are generated, so the build pipeline must update them too, or the next rebuild will restore “the human median”.

All 48 tests pass and the documentation builds cleanly with `sphinx -W`.
````

175 words, score -2.21, 1 lint findings, dropped: none.
