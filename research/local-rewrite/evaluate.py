"""Score finished rewrites in out/<label>/ with the same metrics as bench.py.

Usage: python evaluate.py <label> [--findings]
For rewrites written without a model call (the frontier baseline).
"""
import json, sys

from cringe_filter.lint import lint_text
from cringe_filter.preserve import check
from cringe_filter.score import score_text
from bench import content_words, sev

label = sys.argv[1]
show = "--findings" in sys.argv
drafts = ["pr13-body", "pr12-body", "pr3-body", "pr4-body", "pr1-body", "pr8-body"]
rows = []
for d in drafts:
    src = open(f"drafts/{d}.md").read()
    out = open(f"out/{label}/{d}.md").read().strip()
    f_out = lint_text(out, "github")
    kept = check(src, out)
    s_in, s_out = score_text(src, "github"), score_text(out, "github")
    row = {"model": label, "draft": d, "words_in": len(src.split()), "words_out": len(out.split()),
           "lint_in": sev(lint_text(src, "github")), "lint_out": sev(f_out),
           "score_in": s_in["log_odds"], "score_out": s_out["log_odds"],
           "delta_in": s_in["delta"]["closer_to"], "delta_out": s_out["delta"]["closer_to"],
           "immutables": kept["n_immutables"], "missing": kept["n_missing"],
           "missing_detail": kept["missing"],
           "content_recall": round(len(content_words(src) & content_words(out)) / max(1, len(content_words(src))), 3)}
    rows.append(row)
    print(json.dumps({k: row[k] for k in ("draft", "words_in", "words_out", "lint_in", "lint_out", "score_in",
                                          "score_out", "delta_out", "missing", "missing_detail", "content_recall")}))
    if show:
        for f in f_out:
            print("   ", f["severity"], f["rule"], f.get("evidence"), "|", f.get("snippet", "")[:80])
with open(f"results/{label}.jsonl", "w") as fh:
    for r in rows:
        fh.write(json.dumps(r) + "\n")
