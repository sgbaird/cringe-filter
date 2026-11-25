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
