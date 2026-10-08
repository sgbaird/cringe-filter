Adds `cringe-filter mcp`, an MCP server for the filter. Closes #11.

- Tools: lint, score, filter_prompt, audit, contexts. Prompts: rewrite, minimal_edit.  
- Resources: `cringe-filter://filter/{context}` and `cringe-filter://profile/{context}`.  
- stdio by default. `--transport streamable-http` serves /mcp statelessly, and the Dockerfile runs that on $PORT.  
- Optional `mcp` extra (mcp>=2.2,<3, Python 3.10+); package keeps no dependencies.  
- CLI's context choice moves to `registers.pick`, which the server shares.  
- 10 new tests. The MCP ones skip without the mcp package, as on Python 3.9.
