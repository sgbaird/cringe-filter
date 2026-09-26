"""Sentence-level audit with an optional local model, compiled into an edit spec.

`cringe-filter audit` lints a draft, groups the findings by sentence, and can ask
a model one narrow question per judgment-call finding: how likely is it
that this "X, not Y" rejects a reading nobody offered, rather than giving
an instruction or a real alternative? The output is a Markdown spec for a
frontier model doing a minimal edit (`prompt --minimal`): which sentences
to fix, where they are, why, and which flagged sentences to leave alone.

Any OpenAI-compatible chat endpoint works (Ollama, llama.cpp's llama-server,
LM Studio, vLLM). The default is Ollama on localhost, so a private draft
never leaves the machine.

Measured on sentences from three held-out repositories whose authors are
known (docs/voice/research/local-models.md): a frontier model asked for
this score separated Claude's contrasts from his; the 1.5B and 3B models
that fit on two CPU cores did not do as well. Without --model the
judgment-call findings are listed for the editor to decide, and nothing is
dropped.
"""
import json
import os
import re
import urllib.request

from .lint import lint_text
from .registers import resolve
from .structure import sentences

ENDPOINT = os.environ.get("CRINGE_FILTER_LLM_ENDPOINT", "http://localhost:11434/v1")
# Findings whose rule cannot decide alone: his own uses of the frame are
# mostly instructions ("an assert, not an if statement"), Claude's mostly
# reject a reading nobody offered.
JUDGED = {"x-not-y", "dash-not-y", "is-what-cleft"}

JUDGE_SYSTEM = (
    "You audit one sentence from a draft. It contains a contrast such as "
    "'X, not Y', 'not Y' after a dash or semicolon, or a cleft such as 'X is "
    "what did Y'. Give a number from 0 to 100: how likely it is that the "
    "'not Y' part rejects a reading nobody offered, that is, Y was set up "
    "only to be knocked down to make X sound sharper, rather than carrying "
    "information (an instruction, a real alternative the reader might "
    "choose, an answer to a question, or a correction of something someone "
    "said or would plausibly assume). 0 means clearly informative, 50 "
    "means you can't tell, 100 means clearly set up to be knocked down. "
    "Reply with the number only.")
# Asked for a verdict, the frontier judge kept all 59 test contrasts;
# asked for this score it ranked Claude's above his at AUC 0.83, and at 30
# flagged 11 of Claude's 32 and 1 of his 27 (local-models.md). The
# threshold was chosen on those same 59, so it is a starting point.
THRESHOLD = 30


# Lines that hold markup rather than prose: LaTeX sectioning and
# environments, comments, Markdown headings.
MARKUP_LINE = re.compile(r"\s*(%|#|\\(sub)*section\b|\\(begin|end|label|caption|"
                         r"chapter|paragraph)\b)")


def _chat(model, system, user, endpoint=ENDPOINT):
    body = json.dumps({"model": model, "temperature": 0, "max_tokens": 5,
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode()
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("CRINGE_FILTER_LLM_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions",
                                 data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]


def _sentence_at(text, finding):
    """The sentence a finding sits in, and the two before it for context."""
    lines = text.split("\n")
    ln = max(1, min(finding["line"], len(lines)))
    para_start = ln
    while para_start > 1 and lines[para_start - 2].strip():
        para_start -= 1
    para = " ".join(l.strip() for l in lines[para_start - 1:ln + 2]
                    if l.strip() and not MARKUP_LINE.match(l))
    sents = sentences(para) or [para]
    needle = (finding.get("match") or "").lower()
    for i, s in enumerate(sents):
        if needle and needle[:40] in " ".join(s.split()).lower():
            return s.strip(), " ".join(sents[max(0, i - 2):i]).strip()
    return lines[ln - 1].strip(), ""


def judge(sentence, context, model, endpoint=ENDPOINT):
    """The model's 0-100 score, or None when the reply has no number."""
    user = (f"Earlier text: {context or '(none)'}\n"
            f"Sentence: {sentence}\nScore (0-100):")
    m = re.search(r"\b(\d{1,3})\b", _chat(model, JUDGE_SYSTEM, user, endpoint))
    return min(100, int(m.group(1))) if m else None


def audit(text, context="any", path="<text>", model=None, endpoint=None,
          threshold=THRESHOLD):
    """Lint findings grouped by sentence, with judgment calls adjudicated.

    Returns {"context", "model", "fix": [...], "keep": [...], "document": [...]}
    where each fix/keep entry is {"line", "sentence", "findings", "score"}."""
    ctx = resolve(context)
    endpoint = endpoint or ENDPOINT
    fix, keep, document = {}, {}, []
    for f in lint_text(text, ctx, path):
        if f["rule"] == "too-long" or not f.get("snippet"):
            document.append(f)
            continue
        sentence, before = _sentence_at(text, f)
        score = None
        if f["rule"] in JUDGED and model:
            score = judge(sentence, before, model, endpoint)
        # A low score clears only the judged finding; an em dash in the
        # same sentence still needs fixing.
        cleared = score is not None and score < threshold
        bucket = keep if cleared else fix
        entry = bucket.setdefault((f["line"], sentence), {
            "line": f["line"], "sentence": sentence, "findings": [], "score": None})
        entry["findings"].append(f)
        if score is not None and (cleared or bucket is fix):
            entry["score"] = score
    order = lambda d: sorted(d.values(), key=lambda e: e["line"])  # noqa: E731
    return {"context": ctx, "model": model, "path": path, "threshold": threshold,
            "fix": order(fix), "keep": order(keep), "document": document}


def _tag(f):
    if f.get("lean") and f.get("ci_familywise"):
        lo, hi = f["ci_familywise"]
        return f"{f['severity']}, {f['lean']}x Claude's rate (CI {lo}-{hi})"
    return f["severity"]


def render_spec(result):
    """The audit as a Markdown spec for a frontier model's minimal edit."""
    out = [f"# Edit spec: {result['path']} ({result['context']})", "",
           "Change as little as possible. Fix the sentences listed under "
           "\"Fix\" and leave every other sentence exactly as written. Keep "
           "every claim, number, name, link, citation, label and math span. "
           "Where a fix needs a fact the draft does not give, leave the "
           "sentence and add a note after the text.", ""]
    if result["fix"]:
        out += ["## Fix", ""]
        for i, e in enumerate(result["fix"], 1):
            out.append(f"{i}. Line {e['line']}: \"{e['sentence']}\"")
            for f in e["findings"]:
                out.append(f"   - {f['rule']} ({_tag(f)}): {f['message']}")
            if e["score"] is not None:
                out.append(f"   - {result['model']} scored the contrast "
                           f"{e['score']}/100 for rejecting a reading nobody "
                           "offered: state X and stop.")
            elif any(f["rule"] in JUDGED for f in e["findings"]) and not result["model"]:
                out.append("   - Judgment call: keep the contrast only if Y "
                           "is an instruction, a real alternative, or "
                           "something a reader would believe.")
        out.append("")
    if result["keep"]:
        out += ["## Leave as written", ""]
        for e in result["keep"]:
            rules = ", ".join(f["rule"] for f in e["findings"])
            out.append(f"- Line {e['line']} ({rules}): {result['model']} "
                       f"scored the contrast {e['score']}/100, informative. "
                       f"\"{e['sentence']}\"")
        out.append("")
    if result["document"]:
        out += ["## Whole draft", ""]
        out += [f"- {f['rule']} ({f['severity']}): {f['message']}"
                for f in result["document"]]
        out.append("")
    if not (result["fix"] or result["document"]):
        out.append("No findings. Leave the draft as it is.")
    return "\n".join(out).rstrip() + "\n"
