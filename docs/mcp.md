# MCP server

`cringe-filter mcp` serves the filter over the Model Context Protocol.
Install the extra, which needs Python 3.10 or later, and add the server
to Claude Code:

```bash
pip install 'cringe-filter[mcp]'
claude mcp add cringe-filter -- uvx --from 'cringe-filter[mcp]' cringe-filter mcp
```

## Other clients

A client configured in JSON (Claude Desktop, Cursor, a project's
`.mcp.json`) takes the same command:

```json
{
  "mcpServers": {
    "cringe-filter": {
      "command": "uvx",
      "args": ["--from", "cringe-filter[mcp]", "cringe-filter", "mcp"]
    }
  }
}
```

## Tools, prompts and resources

The tools `lint`, `score`, `audit` and `contexts` match the commands of
the same name; `lint` takes `against` for the old version, and `score`
reports the top features only (`top`, default 12). `filter_prompt` is
`prompt --system-only`, with `minimal` and `evidence` as in `prompt`. The
prompts `rewrite` and `minimal_edit` put a draft under the filter for the
client's own model to edit, and the resources
`cringe-filter://filter/{context}` and `cringe-filter://profile/{context}`
serve a context's filter and its measured rates.

Each tool takes `context` (a name or alias) or `url`, as the commands do.
`lint` and `score` answer with the report the command prints, a third to
half the length of the JSON, and carry the JSON as structured content for
programs. There is no rewrite tool, because the
agent calling the server is already a model. `audit`
consults a model only when the call names one, at the endpoint
`CRINGE_FILTER_LLM_ENDPOINT` sets where the server runs. The server also
sends a short form of the `SKILL.md` procedure as its instructions, which
clients such as Claude Code pass to the model.

## Hosting it

Over streamable HTTP the same server can be hosted for clients that cannot
start a local process. It keeps no state between calls, so any number of
copies can serve it, but every draft sent to it passes through that host.

```bash
cringe-filter mcp --transport streamable-http --port 8000   # http://127.0.0.1:8000/mcp
docker build -t cringe-filter-mcp . && docker run -p 8000:8000 cringe-filter-mcp
```

The container listens on `$PORT` when the platform sets one.
