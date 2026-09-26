"""The voice filter as a measurement: does this read like the writer, here?

For each feature the profile carries two rates per 1000 words: the writer's
in the requested register and Claude's in its GitHub prose (the reference
the whole profile is built against). A draft of N words with n occurrences
of the feature is scored by the Poisson log-likelihood ratio of those two
rates, and the per-feature ratios add up to one log-odds figure: positive
reads like Claude, negative reads like the writer. Features are markers of
stance and formatting plus every candidate tell that separated the two
authors after the family-wise correction, in either direction.

This is a stylometric summary, not a detector, and it says nothing about
whether a text is good. It says where a draft sits between two measured
writers, and which features put it there.
"""
import math

from . import latex
from .bundle import profile, reference
from .markers import PATTERNS, SENT_SPLIT, clean, mechanical
from .registers import resolve
from . import structure as shape
import re

FLOOR = 0.02  # per 1k; keeps a zero rate from producing an infinite ratio

STANCE = [("hedge", "hedges (might, maybe, probably, seems, I think)"),
          ("question", "question marks"), ("exclaim", "exclamation marks"),
          ("first_person_sg", '"I"'), ("first_person_pl", '"we"'),
          ("you", '"you"'), ("contraction", "contractions")]
FORMAT = [("bold_md", "bold runs"), ("header_md", "headers"),
          ("bullet_md", "bullet lines"), ("table_md", "table rows"),
          ("checkbox_md", "checkbox items"), ("emoji_check", "status emoji"),
          ("em_dash", "em dashes"), ("en_dash", "en dashes")]
# Candidate tells already covered by the formatting markers above.
COVERED = {"em dash", "en dash", "bold run", "checkbox list", "markdown table",
           "H2/H3 header", "emoji status", "bullet line"}


def llr(n, words, rate_s, rate_c):
    ls = max(rate_s, FLOOR) * words / 1000.0
    lc = max(rate_c, FLOOR) * words / 1000.0
    return n * math.log(lc / ls) - (lc - ls)


def score_text(text, context="any"):
    ctx = resolve(context)
    p = profile()
    reg = p["registers"][ctx]
    ref = reference(ctx)
    if latex.looks_like_latex(text):
        text = latex.to_prose(text)
    cleaned = clean(text)
    m = mechanical([cleaned])
    words = m.get("n_words", 0)
    if words == 0:
        return {"context": ctx, "words": 0, "features": [], "log_odds": 0.0,
                "p_claude": 0.5, "verdict": "empty"}

    feats = []
    for key, label in STANCE + FORMAT:
        n = m.get(f"{key}_n", 0)
        s = reg["mechanical"].get(f"{key}_per_1k", 0) or 0
        c = ref["mechanical"].get(f"{key}_per_1k", 0) or 0
        feats.append({"feature": label, "n": n,
                      "per_1k": round(1000 * n / words, 2),
                      "sterling_per_1k": s, "claude_per_1k": c,
                      "log_odds": round(llr(n, words, s, c), 3),
                      "kind": "stance" if (key, label) in STANCE else "format"})

    own = reg.get("candidate_per_1k") or {}
    for phrase, t in p["tells"].items():
        if phrase in COVERED or not t.get("significant"):
            continue
        rx = re.compile(t["pattern"], re.I | re.M)
        n = len(rx.findall(cleaned))
        s = own.get(phrase, t["sterling_per_1k"])
        c = (ref.get("candidate_per_1k") or {}).get(phrase, t["claude_per_1k"])
        if n == 0 and abs(llr(0, words, s, c)) < 0.05:
            continue
        feats.append({"feature": phrase, "n": n,
                      "per_1k": round(1000 * n / words, 2),
                      "sterling_per_1k": s, "claude_per_1k": c,
                      "log_odds": round(llr(n, words, s, c), 3),
                      "kind": "tell"})

    feats += structure_features(text, reg, ref)
    delta = burrows_delta(cleaned, reg, ref, p.get("mfw"))

    total = sum(f["log_odds"] for f in feats)
    # A logistic transform of this sum is not a calibrated probability:
    # the features overlap and depend on each other, there is no class
    # prior, and the rates were selected on the corpus being described
    # (Edison review, 2026-09-23). It is kept only as a bounded display.
    logistic = 1.0 / (1.0 + math.exp(-max(min(total, 40), -40)))
    if total > 2:
        verdict = "reads like Claude"
    elif total < -2:
        verdict = "reads human"
    else:
        verdict = "in between"
    feats.sort(key=lambda f: -abs(f["log_odds"]))

    sents = [s for s in SENT_SPLIT.split(re.sub(r"\s+", " ", cleaned)) if s.strip()]
    slens = [len(s.split()) for s in sents]
    return {
        "context": ctx, "label": reg["label"], "words": words,
        "sentences": len(sents), "longest_sentence": max(slens) if slens else 0,
        "length": {"median_words": reg["doc_words_median"],
                   "p90_words": reg["doc_words_p90"],
                   "budget_words": reg["doc_words_budget"],
                   "over_budget": bool(reg["doc_words_budget"]
                                       and words > reg["doc_words_budget"]),
                   "ratio_to_median": round(words / max(reg["doc_words_median"] or 1, 1), 2)},
        "log_odds": round(total, 3),
        "logistic_of_log_odds": round(logistic, 3),
        "calibrated": False,
        "candidate_rates_measured": bool(reg.get("candidate_rates_measured", True)),
        "verdict": verdict, "features": feats, "delta": delta,
        "note": ("Style score: Poisson log-likelihood ratio of Claude's GitHub "
                 "rates over the writer's rates in this register, summed over "
                 "features. Positive reads like Claude. Features overlap, so "
                 "this is a ranking of what to fix, not a calibrated "
                 "probability, and not a detector."),
    }


# Structure features the stance and format markers above do not already
# count: questions are a stance marker, list words are bullets and tables.
STRUCTURE = ("person_open", "determiner_open", "number_open", "conjunction_open",
             "adverb_open", "modal", "to_verb", "colon", "semicolon", "dash",
             "paren", "one_sentence_paragraphs")
SHARES = {"person_open", "determiner_open", "number_open", "conjunction_open",
          "adverb_open", "one_sentence_paragraphs"}


def structure_features(text, reg, ref):
    """How the draft's sentences are built, against both writers.

    A share (sentences opening on a person, one-sentence paragraphs) is
    scored as a binomial log-likelihood ratio over the draft's sentences or
    paragraphs, and a count per sentence (modals, colons) as a Poisson one,
    the same way the word markers are. Registers without structure rates
    (email, tutorials, manuscripts) score nothing here."""
    writer = (reg.get("structure") or {}).get("rates")
    cl = (ref.get("structure") or {}).get("rates")
    if not writer or not cl:
        return []
    counts = shape.measure(text)
    out = []
    for key in STRUCTURE:
        den_key, label = shape.FEATURES[key]
        d = counts.get(den_key, 0)
        s_rate, c_rate = writer.get(key), cl.get(key)
        if not d or s_rate is None or c_rate is None:
            continue
        n = counts.get(key, 0)
        if key in SHARES:
            ps = min(max(s_rate, 0.005), 0.995)
            pc = min(max(c_rate, 0.005), 0.995)
            lo = n * math.log(pc / ps) + (d - n) * math.log((1 - pc) / (1 - ps))
        else:
            ls, lc = max(s_rate, 0.005), max(c_rate, 0.005)
            lo = n * math.log(lc / ls) - d * (lc - ls)
        out.append({"feature": label, "n": n, "of": d,
                    "per_1k": round(1000 * n / d, 2),
                    "sterling_per_1k": round(1000 * s_rate, 2),
                    "claude_per_1k": round(1000 * c_rate, 2),
                    "log_odds": round(lo, 3), "kind": "structure",
                    "unit": "per 1000 " + ("paragraphs" if den_key == "prose_paragraphs"
                                           else "sentences")})
    return out


WORD = re.compile(r"[a-z][a-z'-]+")


def burrows_delta(cleaned, reg, ref, mfw):
    """Burrows' Delta from the draft to the register centroid and to Claude's.

    Each of the most frequent words is z-scored against the pooled
    per-document spread, and Delta is the mean absolute z difference. A
    smaller Delta to the register than to Claude means the draft's
    function-word profile sits nearer the writer's. Short drafts are noisy here;
    read the margin, not the third decimal.
    """
    if not mfw or not reg.get("mfw_mean") or not ref.get("mfw_mean"):
        return None
    toks = WORD.findall(cleaned.lower())
    n = max(len(toks), 1)
    counts = {}
    for t in toks:
        counts[t] = counts.get(t, 0) + 1
    words, mean, std = mfw["words"], mfw["pooled_mean"], mfw["pooled_std"]
    zd = [(1000.0 * counts.get(w, 0) / n - mean[j]) / std[j]
          for j, w in enumerate(words)]

    def dist(centroid):
        return sum(abs(zd[j] - (centroid[j] - mean[j]) / std[j])
                   for j in range(len(words))) / len(words)

    to_reg = dist(reg["mfw_mean"])
    to_claude = dist(ref["mfw_mean"])
    return {"to_register": round(to_reg, 3), "to_claude": round(to_claude, 3),
            "margin": round(to_claude - to_reg, 3),
            "closer_to": "register" if to_reg < to_claude else "claude",
            "n_features": len(words), "n_tokens": len(toks)}


def format_score(r, top=12):
    lines = [f"context: {r['context']} ({r.get('label', '')})   words: {r['words']}"
             f"   sentences: {r.get('sentences', 0)}, longest {r.get('longest_sentence', 0)}",
             f"style score: {r['log_odds']:+.2f} log-odds, {r['verdict']} "
             f"(a ranking of what to fix, not a calibrated probability)"]
    if not r.get("candidate_rates_measured", True):
        lines.append("note: this register has no measured phrase rates of its "
                     "own; phrase rows use the GitHub-wide rates")
    L = r.get("length")
    if L:
        flag = "  [over budget]" if L["over_budget"] else ""
        lines.append(f"length: {r['words']} words; the writer's median here is "
                     f"{L['median_words']}, p90 {L['p90_words']}, budget "
                     f"{L['budget_words']}{flag}")
    d = r.get("delta")
    if d:
        who = "the writer" if d["closer_to"] == "register" else "Claude"
        lines.append(f"Burrows' Delta over the {d['n_features']} most frequent "
                     f"words: {d['to_register']:.2f} to the writer's register, "
                     f"{d['to_claude']:.2f} to Claude (closer to {who})")
    lines.append(f"{'feature':44s}{'n':>4s}{'yours/1k':>10s}{'writer/1k':>10s}"
                 f"{'Claude/1k':>11s}{'log-odds':>10s}")
    lines.append("(per 1000 words; structure rows per 1000 sentences or prose paragraphs)")
    for f in r["features"][:top]:
        lines.append(f"{f['feature'][:43]:44s}{f['n']:4d}{f['per_1k']:10.2f}"
                     f"{f['sterling_per_1k']:10.2f}{f['claude_per_1k']:11.2f}"
                     f"{f['log_odds']:+10.2f}")
    return "\n".join(lines)
