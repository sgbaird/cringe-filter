"""The filter as an MCP server, for agents that speak the Model Context Protocol.

    cringe-filter mcp                                       # stdio, local
    cringe-filter mcp --transport streamable-http --host 0.0.0.0   # hosted

Each tool makes the same deterministic call as the CLI command of the same
name, so the server keeps no state and needs no credentials, and any
replica can answer any request. There is no rewrite tool: an agent that
calls these tools is already a model and applies the filter itself
(SKILL.md), and a hosted rewrite would spend the host's API key on every
caller's drafts. `audit` reaches a model only when the caller names one,
and only at the endpoint the server's environment sets
(CRINGE_FILTER_LLM_ENDPOINT), so a caller cannot point a hosted server at
an address of its choosing.

Lint and score answer with the report the CLI prints, since SKILL.md
teaches an agent to read that form and it costs a third of the tokens of
the JSON. The JSON comes along as structured content for programs.

Needs the mcp package, which needs Python 3.10 or later:
pip install 'cringe-filter[mcp]'.
"""
import functools
import json
import os
from typing import Annotated, Any

from . import __version__
from .audit import THRESHOLD, audit as run_audit, render_spec
from .bundle import profile
from .lint import format_finding, introduced, lint_text
from .prompt import build_minimal_prompt, build_prompt, render
from .registers import contexts as list_contexts, pick, resolve
from .score import format_score, score_text

INSTRUCTIONS = (
    "A final pass over prose drafted for a person to read: a GitHub reply, "
    "an issue in someone else's repo, a Discussions post, an email, a short "
    "message, a LinkedIn post, a docs page, a paper or a proposal. Use it "
    "once the draft exists; skip code, commit messages and config. Pass "
    "the context, or the destination URL to infer it. Call lint and fix "
    "every error; judge each warn and info on its evidence. Call "
    "filter_prompt and rewrite the draft to match it, keeping every fact, "
    "link and number. Call score once, fix the top two or three features "
    "and stop: repeated revision degrades text that was already fine. A "
    "draft headed to review (a paper, proposal or abstract) gets the "
    "smallest edit instead: filter_prompt with minimal=true, and audit for "
    "the sentences to fix.")


def build_server():
    """The MCPServer with every tool, prompt and resource registered."""
    try:
        from mcp.server.mcpserver import MCPServer
        from mcp.server.mcpserver.exceptions import (ResourceNotFoundError,
                                                     ToolError)
        from mcp.shared.exceptions import MCPError
        from mcp.types import (INVALID_PARAMS, CallToolResult, TextContent,
                               ToolAnnotations)
        from pydantic import Field
    except ImportError as e:
        raise SystemExit("the MCP server needs the mcp package, which needs "
                         "Python 3.10 or later: "
                         "pip install 'cringe-filter[mcp]'") from e

    server = MCPServer(
        "cringe-filter", title="cringe-filter", version=__version__,
        instructions=INSTRUCTIONS,
        website_url="https://github.com/sgbaird/cringe-filter")
    offline = ToolAnnotations(read_only_hint=True, idempotent_hint=True,
                              open_world_hint=False)

    Text = Annotated[str, Field(
        description="The draft: Markdown, plain text or LaTeX.")]
    Context = Annotated[str | None, Field(
        description="Where the text is going: github, discussion, "
                    "third-party, email, message, linkedin, tutorial, "
                    "paper, proposal or any. Aliases such as dm, docs, "
                    "bug-report, pr and grant work. Default any.")]
    Url = Annotated[str | None, Field(
        description="The destination URL or path, to infer the context "
                    "from instead (a GitHub issue, a LinkedIn post, a .tex "
                    "file). Wins over context.")]
    Filename = Annotated[str | None, Field(
        description="The name of the file the text came from, if any. "
                    "Nothing is read from it; a .tex name means LaTeX and, "
                    "without a context, a paper.")]

    def report(text, data):
        return CallToolResult(content=[TextContent(type="text", text=text)],
                              structured_content=data)

    def guard(register, error):
        """Register a function so that a ValueError (an unknown context, a
        missing draft) reaches the client as `error` with its message, as
        the CLI prints it. The SDK withholds the text of anything else.
        The docstring, which the client shows, goes out on one line."""
        def decorate(fn):
            @functools.wraps(fn)
            def run(*args, **kwargs):
                try:
                    return fn(*args, **kwargs)
                except ValueError as e:
                    raise error(str(e)) from e
            run.__doc__ = " ".join((fn.__doc__ or "").split())
            return register(run)
        return decorate

    def tool(**kw):
        return guard(server.tool(**kw), ToolError)

    def prompt(**kw):
        return guard(server.prompt(**kw),
                     lambda m: MCPError(code=INVALID_PARAMS, message=m))

    def resource(uri, **kw):
        return guard(server.resource(uri, **kw), ResourceNotFoundError)

    @tool(annotations=offline)
    def lint(text: Text, context: Context = None, url: Url = None,
             filename: Filename = None,
             against: Annotated[str | None, Field(
                 description="The version before a revision. Only findings "
                             "the new text added are reported.")] = None,
             errors_only: bool = False):
        """Find the AI tells in a draft: em dashes, bold runs, headers,
        "X, not Y" contrasts, inflated vocabulary, status-report scaffolding,
        length over the context's budget. Deterministic and free. Each
        finding gives its line, severity and the evidence behind the rule:
        [15.2x, CI 9.7-23.9] means Claude used the pattern 15 times as often
        as the measured writer in that context; [preventive, no corpus
        support] is a nudge. Fix every error."""
        ctx = pick(context, url, filename)
        path = filename or "<text>"
        found = (introduced(against, text, ctx, path) if against is not None
                 else lint_text(text, ctx, path))
        if errors_only:
            found = [f for f in found if f["severity"] == "error"]
        n_err = sum(1 for f in found if f["severity"] == "error")
        lines = [format_finding(f, color=False) for f in found]
        lines.append(f"{len(found)} findings, {n_err} errors  (context: {ctx})")
        return report("\n".join(lines), {"context": ctx, "errors": n_err,
                                         "findings": found})

    @tool(annotations=offline)
    def score(text: Text, context: Context = None, url: Url = None,
              filename: Filename = None,
              top: Annotated[int, Field(
                  ge=1, description="How many features to report, largest "
                                    "first.")] = 12):
        """Where a draft sits between Claude and the measured writer in a
        context, feature by feature: one log-odds style score (positive
        reads like Claude), the length against the writer's median and
        budget, and the features that pull it each way. A ranking of what
        to fix, not a calibrated probability or a detector. Score once, fix
        the top two or three features, and stop."""
        r = score_text(text, pick(context, url, filename))
        r["n_features"] = len(r["features"])
        r["features"] = r["features"][:top]
        return report(format_score(r, top), r)

    @tool(annotations=offline, structured_output=False)
    def filter_prompt(
            context: Context = None, url: Url = None,
            text: Annotated[str, Field(
                description="Your draft, if one exists yet. It picks "
                            "examples of a matching length, and minimal=true "
                            "needs it. It is not echoed back.")] = "",
            minimal: Annotated[bool, Field(
                description="For a draft headed to review: the smallest "
                            "edit a reviewer would make, with the draft's "
                            "lint findings, in place of a rewrite.")] = False,
            evidence: Annotated[bool, Field(
                description="Append the measured rates and intervals "
                            "behind the filter, for a person.")] = False) -> str:
        """The voice filter for a context, as instructions to apply to your
        own draft: real passages from the writer where the context has them,
        the priorities, the measured tells in plain words and the register's
        notes. Read the passages first, then rewrite the draft to match,
        keeping every fact, link and number."""
        ctx = pick(context, url)
        if minimal:
            if not text.strip():
                raise ValueError("minimal=true needs the draft: its lint "
                                 "findings go into the prompt")
            return build_minimal_prompt(text, ctx)[0]
        system, _, appendix = build_prompt(text, ctx, with_evidence=True)
        return system + ("\n\n" + appendix if evidence else "")

    @tool(annotations=ToolAnnotations(read_only_hint=True,
                                      open_world_hint=True),
          structured_output=False)
    def audit(text: Text, context: Context = None, url: Url = None,
              filename: Filename = None,
              model: Annotated[str | None, Field(
                  description="A model at the server's OpenAI-compatible "
                              "endpoint (Ollama by default) to judge each "
                              "'X, not Y' contrast. Without one, those are "
                              "left to the editor.")] = None,
              threshold: Annotated[int, Field(
                  ge=0, le=100, description="Judged contrasts scoring "
                                            "below this are kept as "
                                            "written.")] = THRESHOLD) -> str:
        """The lint findings as an edit spec, for the smallest edit to a
        draft headed to review: each sentence to fix with its line and
        reason, and the flagged sentences to leave alone."""
        ctx = pick(context, url, filename)
        return render_spec(run_audit(text, ctx, filename or "<text>",
                                     model=model, threshold=threshold))

    @tool(annotations=offline)
    def contexts() -> dict[str, Any]:
        """The contexts the filter knows, with their aliases, the writer's
        median length and the length budget for each."""
        return {"contexts": list_contexts()}

    Draft = Annotated[str, Field(description="The text to filter.")]
    Name = Annotated[str, Field(description="Where the text is going: github, "
                                            "email, message, linkedin, paper "
                                            "and so on, or an alias.")]

    @prompt(title="Rewrite a draft in the writer's voice")
    def rewrite(draft: Draft, context: Name = "any") -> str:
        """The voice filter for a context with the draft under it, for the
        model to rewrite."""
        return render(*build_prompt(draft, pick(context)))

    @prompt(title="Smallest edit before review")
    def minimal_edit(draft: Draft, context: Name = "paper") -> str:
        """The minimal-edit filter with the draft's lint findings, for a
        manuscript, proposal or page someone will read line by line."""
        return render(*build_minimal_prompt(draft, pick(context)))

    @resource("cringe-filter://filter/{context}", name="filter",
              mime_type="text/markdown")
    def filter_resource(context: str) -> str:
        """The voice filter for a context, without a draft."""
        return build_prompt("", resolve(context))[0]

    @resource("cringe-filter://profile/{context}", name="profile",
              mime_type="application/json")
    def profile_resource(context: str) -> str:
        """Everything the profile measured for a context."""
        return json.dumps(profile()["registers"][resolve(context)], indent=1)

    return server


def serve(transport="stdio", host="127.0.0.1", port=None):
    server = build_server()
    if transport == "stdio":
        server.run("stdio")
        return
    # Stateless JSON responses: no tool keeps anything between calls, so a
    # platform can start, stop and load-balance replicas freely.
    server.run("streamable-http", host=host,
               port=port or int(os.environ.get("PORT", 8000)),
               stateless_http=True, json_response=True)
