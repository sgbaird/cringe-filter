This adds `cringe-filter mcp`, so the filter can run as an MCP server. Closes #11.

It serves lint, score, filter_prompt, audit and contexts as tools, rewrite and minimal_edit as prompts, and cringe-filter://filter/{context} and cringe-filter://profile/{context} as resources.

It uses stdio by default. With `--transport streamable-http` it serves /mcp statelessly, and the Dockerfile runs that on $PORT.

I put the server behind an optional `mcp` extra (mcp>=2.2,<3, Python 3.10+) so the package itself still has no dependencies. The CLI's context choice moved to `registers.pick` so the server can share it.

There are 10 new tests. The MCP ones skip when the mcp package isn't installed, like on Python 3.9.
