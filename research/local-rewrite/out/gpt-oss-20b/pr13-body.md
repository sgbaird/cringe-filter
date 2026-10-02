Added the `cringe-filter mcp` command, an MCP server for the filter, and closed issue #11.

- It uses the existing tools: lint, score, filter_prompt, audit, and contexts.  
- Prompts available: rewrite and minimal_edit.  
- Resources are exposed at cringe-filter://filter/{context} and cringe-filter://profile/{context}.  
- By default it writes to stdio; with `--transport streamable-http` it serves `/mcp` statelessly, and the Dockerfile runs that on `$PORT`.  
- An optional `mcp` extra (`mcp>=2.2,<3`, Python 3.10+) keeps the base package dependency‑free.  
- The CLI’s context picker now uses `registers.pick`, which the server also exposes, allowing users to select contexts from the same registry.  
- Ten new tests were added; the MCP tests are skipped when the `mcp` package is unavailable, such as on Python 3.9.
