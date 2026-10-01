"""Apply the voice filter with Claude, then lint what came back.

One rewrite, at most one revision against concrete lint findings, and no
further loop: the operational survey behind this project found that
repeated self-revision degrades text that was already fine, and that an
external deterministic check is what makes a revision pass worth having.

Requires the `anthropic` package (optional extra `cringe-filter[rewrite]`) and
credentials the SDK can find (ANTHROPIC_API_KEY, or an `ant auth login`
profile). The client can be injected, which is how the tests run without
a network.
"""
from .lint import lint_text
from .preserve import check as preservation, report as preservation_report
from .prompt import build_minimal_prompt, build_prompt
from .registers import resolve
from .score import score_text

DEFAULT_MODEL = "claude-opus-5"
NO_REVISE = {"too-long"}
FALLBACK_BETA = "server-side-fallback-2026-07-01"


def make_client():
    try:
        import anthropic
    except ImportError as e:  # pragma: no cover
        raise SystemExit("rewrite needs the anthropic package: "
                         "pip install 'cringe-filter[rewrite]'") from e
    return anthropic.Anthropic()


def _text_of(message):
    if getattr(message, "stop_reason", None) == "refusal":
        raise RuntimeError("the model declined this request (stop_reason=refusal)")
    parts = [b.text for b in message.content if getattr(b, "type", "") == "text"]
    return "\n".join(parts).strip()


def _call(client, model, system, messages, fallbacks=True, effort="medium"):
    kwargs = dict(model=model, max_tokens=16000, system=system,
                  messages=messages, thinking={"type": "adaptive"},
                  extra_body={"output_config": {"effort": effort}})
    if fallbacks:
        # Server-side refusal fallback: if a safety classifier declines the
        # request, the API re-runs it on a fallback model in the same call.
        kwargs["extra_headers"] = {"anthropic-beta": FALLBACK_BETA}
        kwargs["extra_body"]["fallbacks"] = "default"
    with client.messages.stream(**kwargs) as stream:
        return _text_of(stream.get_final_message())


def rewrite(text, context="any", model=DEFAULT_MODEL, client=None,
            revise=True, fallbacks=True, effort="medium", structure=None,
            minimal=False):
    ctx = resolve(context)
    client = client or make_client()
    if minimal:
        # The smallest edit a reviewer would make; no revision pass, since
        # a second turn is one more chance to rewrite what should stay.
        system, user = build_minimal_prompt(text, ctx)
        revise = False
    else:
        system, user = build_prompt(text, ctx, **({} if structure is None
                                                  else {"structure": structure}))
    messages = [{"role": "user", "content": user}]
    draft = _call(client, model, system, messages, fallbacks, effort)
    findings = lint_text(draft, ctx)
    kept = preservation(text, draft)
    passes = 1
    # Revise against errors and against measured warnings: bold, headers,
    # tables and arrows are the dominant Claude features and they are
    # warnings, so a pass that only looked at errors would miss them. The
    # same pass asks for any number, link, code span or path the rewrite
    # dropped, which a style check alone would never notice. The length
    # budget is reported but never revised against on its own: in the
    # held-out experiment every revision it triggered cut about 6% of the
    # source's content words, moved none of the three classifiers toward
    # the writer, and left 22 of 24 drafts over budget anyway
    # (docs/voice/research/rewrite-experiment.md).
    errors = [f for f in findings if f["rule"] not in NO_REVISE
              and (f["severity"] == "error"
                   or (f["severity"] == "warn" and f.get("evidence") == "measured"))]
    if (errors or kept["n_missing"]) and revise:
        messages += [{"role": "assistant", "content": draft},
                     {"role": "user", "content":
                      revision_request(errors, kept)}]
        draft = _call(client, model, system, messages, fallbacks, effort)
        findings = lint_text(draft, ctx)
        kept = preservation(text, draft)
        passes = 2
    return {
        "context": ctx, "model": model, "passes": passes, "text": draft,
        "findings": findings, "preservation": kept,
        "score_before": score_text(text, ctx),
        "score_after": score_text(draft, ctx),
    }


def revision_request(errors, kept):
    """The second turn: concrete lint findings and dropped content."""
    parts = []
    if errors:
        parts.append("A deterministic check found these in your rewrite. "
                     "Fix each one:\n" + "\n".join(
                         f"- line {f['line']}: {f['rule']}: {f['message']}"
                         + (f" ({f['snippet']})" if f.get("snippet") else "")
                         for f in errors[:20]))
    if kept["n_missing"]:
        parts.append("The rewrite dropped these from the draft. Put each "
                     "one back where it belongs:\n" + preservation_report(kept))
    parts.append("Return the complete text again, with nothing else changed.")
    return "\n\n".join(parts)
