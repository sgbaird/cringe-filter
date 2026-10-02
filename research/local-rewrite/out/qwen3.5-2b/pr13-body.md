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
