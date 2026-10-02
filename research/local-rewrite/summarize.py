"""Aggregate results/*.jsonl into one line per model."""
import glob, json, re, statistics as st

from cringe_filter.lint import lint_text
from cringe_filter.prompt import build_prompt


def shingles(t, n=4):
    w = re.findall(r"[a-z0-9']+", t.lower())
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def leaked(draft, label):
    """4-word runs in the output that come from the prompt, not the draft."""
    src = open(f"drafts/{draft}.md").read()
    out = open(f"out/{label}/{draft}.md").read()
    system, _ = build_prompt(src, "github")
    return sorted((shingles(out) & shingles(system)) - shingles(src))

order = ["opus-self", "qwen3.5-2b", "qwen3.5-4b", "gemma-4-e4b-capped", "gemma-4-e4b", "lfm2.5-8b-a1b", "qwen3.5-9b", "gpt-oss-20b"]
rows = {}
for p in glob.glob("results/*.jsonl"):
    for line in open(p):
        r = json.loads(line)
        rows.setdefault(r["model"], []).append(r)

print(f"{'model':15s} {'n':>2s} {'score in>out (median)':>22s} {'writer side':>11s} {'errors':>6s} {'warns*':>6s} "
      f"{'dropped':>7s} {'recall':>6s} {'words':>9s} {'2nd pass':>8s} {'leak':>4s} {'s/draft':>7s} {'read t/s':>8s} {'write t/s':>9s}")
for m in order + sorted(set(rows) - set(order)):
    rs = rows.get(m)
    if not rs:
        continue
    n = len(rs)
    s_in = st.median(r["score_in"] for r in rs)
    s_out = st.median(r["score_out"] for r in rs)
    writer = sum(r["score_out"] < 0 for r in rs)
    found = [f for r in rs for f in lint_text(open(f"out/{m}/{r['draft']}.md").read(), "github")]
    errs = sum(f["severity"] == "error" for f in found)
    # warnings other than length, which the pipeline never revises against
    warns = sum(f["severity"] == "warn" and f["rule"] != "too-long" for f in found)
    dropped = sum(r["missing"] for r in rs)
    imm = sum(r["immutables"] for r in rs)
    recall = st.mean(r["content_recall"] for r in rs)
    w_in = sum(r["words_in"] for r in rs)
    w_out = sum(r["words_out"] for r in rs)
    passes = sum(r.get("passes", 1) == 2 for r in rs)
    leaks = sum(bool(leaked(r["draft"], m)) for r in rs)
    secs = st.mean(r["secs"] for r in rs) if "secs" in rs[0] else 0
    calls = [c for r in rs for c in r.get("calls", [])]
    pp = st.median(c["prompt_tps"] for c in calls if c["prompt_n"] and c["prompt_n"] > 200) if calls else 0
    tg = st.median(c["gen_tps"] for c in calls if c["gen_n"]) if calls else 0
    print(f"{m:15s} {n:2d} {s_in:+9.2f} > {s_out:+9.2f}  {writer:>5d} of {n} {errs:6d} {warns:6d} "
          f"{dropped:3d}/{imm:<3d} {recall:6.2f} {w_in:4d}>{w_out:<4d} {passes:5d}/{n} {leaks:4d} {secs:7.0f} {pp:8.1f} {tg:9.1f}")

if __name__ == "__main__":
    import sys
    if "--leaks" in sys.argv:
        for m, rs in rows.items():
            for r in rs:
                l = leaked(r["draft"], m)
                if l:
                    print(m, r["draft"], l[:8])
