I've added `cringe-filter mcp`, an MCP server for the filter. This closes #11.

The server includes tools for lint, score, filter_prompt, audit, and contexts, plus rewrite and minimal_edit prompts. Resources expose the filter and profile contexts at `cringe-filter://filter/{context}` and `cringe-filter://profile/{context}`.

By default, it uses stdio. You can also serve statelessly over `/mcp` with `--transport streamable-http`, which the Dockerfile runs on `$PORT`.

I added an optional `mcp` extra requiring MCP>=2.2,<3 and Python 3.10+. This keeps the package dependency-free otherwise. The CLI's context choice now moves to `registers.pick`, which the server shares.

I also added 10 new tests. The MCP ones skip without the mcp package, as on Python 3.9.
