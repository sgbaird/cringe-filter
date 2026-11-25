"""Collect every draft and each model's rewrite into one Markdown file."""
import json, os

from cringe_filter.lint import lint_text
from cringe_filter.preserve import check
from cringe_filter.score import score_text

DRAFTS = {"pr13-body": "#13", "pr12-body": "#12", "pr3-body": "#3",
          "pr4-body": "#4", "pr1-body": "#1", "pr8-body": "#8"}
MODELS = ["opus-self", "qwen3.5-2b", "qwen3.5-4b", "gemma-4-e4b-capped", "gemma-4-e4b", "lfm2.5-8b-a1b",
          "qwen3.5-9b", "gpt-oss-20b"]
LABEL = {"opus-self": "Claude Opus 5.5, applying the same prompt by hand in one pass",
         "gemma-4-e4b-capped": "gemma-4-e4b, reply capped at about twice the draft",
         "gemma-4-e4b": "gemma-4-e4b, with 1200 more tokens of room"}


def fence(text):
    return "````markdown\n" + text.strip() + "\n````\n"


out = ["# Rewrites of six PR bodies Claude wrote in this repo", "",
       "Context `github`. Each rewrite went through `cringe_filter.rewrite.rewrite()` "
       "(prompt, lint, at most one revision) with the model swapped for a local one, "
       "except the first, which is the frontier reference. The line under each "
       "rewrite is what the package itself measures; it does not check facts.", ""]
for d, pr in DRAFTS.items():
    src = open(f"drafts/{d}.md").read()
    s = score_text(src, "github")
    out += [f"## Body of PR {pr}", "", fence(src),
            f"Source: {len(src.split())} words, score {s['log_odds']:+.2f}, "
            f"{len(lint_text(src, 'github'))} lint findings.", ""]
    for m in MODELS:
        p = f"out/{m}/{d}.md"
        if not os.path.exists(p):
            continue
        t = open(p).read()
        s2 = score_text(t, "github")
        kept = check(src, t)
        miss = "; ".join(f"{k}: {', '.join(v)}" for k, v in kept["missing"].items()) or "none"
        out += [f"### {LABEL.get(m, m)}", "", fence(t),
                f"{len(t.split())} words, score {s2['log_odds']:+.2f}, "
                f"{len(lint_text(t, 'github'))} lint findings, dropped: {miss}.", ""]
open("outputs.md", "w").write("\n".join(out))
print("wrote outputs.md", sum(1 for _ in open("outputs.md")), "lines")
