"""Surface markers, counted the same way the corpus was measured.

These patterns are a copy of the ones in scripts/voice/analyze_corpus.py.
They have to be identical, because the rates in the profile were produced
by them; a test in the repository asserts the two sets match.
"""
import re

CODE_BLOCK = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`\n]+`")
HTML_TAG = re.compile(r"<[^>]{1,200}>", re.S)
QUOTED = re.compile(r"^\s*>.*$", re.M)
URL = re.compile(r"https?://\S+")
IMG_MD = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK_MD = re.compile(r"\[([^\]]*)\]\([^)]*\)")
MENTION = re.compile(r"@[\w-]+")
BOILERPLATE = re.compile(
    r"(View job run|Generated with \[Claude Code\]|Co-Authored-By|"
    r"Create a PR|branch `claude/|\[View job run\])", re.I)


def clean(text):
    """Reduce a document to the prose its author composed."""
    text = CODE_BLOCK.sub(" ", text)
    text = QUOTED.sub(" ", text)
    text = IMG_MD.sub(" ", text)
    text = LINK_MD.sub(r"\1", text)
    text = URL.sub(" ", text)
    text = HTML_TAG.sub(" ", text)
    text = INLINE_CODE.sub(" ", text)
    text = MENTION.sub(" ", text)
    lines = [l for l in text.split("\n") if not BOILERPLATE.search(l)]
    return "\n".join(lines)


SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

PATTERNS = {
    "em_dash": re.compile(r"—"),
    "en_dash": re.compile(r"–"),
    "not_just_x_but_y": re.compile(r"\bnot (just|only|merely)\b[^.\n]{0,60}\b(but|it'?s)\b", re.I),
    "isnt_x_its_y": re.compile(r"\b(is|it'?s|this is) not\b[^.\n]{0,50}\bit'?s\b", re.I),
    "rule_of_three": re.compile(r"\b\w+, \w+,? and \w+\b"),
    "delve": re.compile(r"\bdelve[sd]?\b", re.I),
    "crucial_vital": re.compile(r"\b(crucial|vital|pivotal|paramount|essential)\b", re.I),
    "leverage_verb": re.compile(r"\bleverag(e|es|ed|ing)\b", re.I),
    "robust": re.compile(r"\brobust\b", re.I),
    "seamless": re.compile(r"\bseamless(ly)?\b", re.I),
    "comprehensive": re.compile(r"\bcomprehensive(ly)?\b", re.I),
    "its_worth_noting": re.compile(r"\b(it'?s worth noting|it is worth noting|it'?s important to note|notably,)", re.I),
    "in_the_realm_of": re.compile(r"\b(in the realm of|in the world of|when it comes to|in today'?s)\b", re.I),
    "landscape_journey": re.compile(r"\b(landscape|journey|tapestry|realm|testament)\b", re.I),
    "furthermore": re.compile(r"\b(furthermore|moreover|additionally|in conclusion)\b", re.I),
    "ensure": re.compile(r"\bensur(e|es|ed|ing)\b", re.I),
    "utilize": re.compile(r"\butiliz(e|es|ed|ing|ation)\b", re.I),
    "facilitate": re.compile(r"\bfacilitat(e|es|ed|ing)\b", re.I),
    "bold_md": re.compile(r"\*\*[^*\n]+\*\*"),
    "header_md": re.compile(r"^#{1,6} ", re.M),
    "bullet_md": re.compile(r"^\s*[-*+] ", re.M),
    "table_md": re.compile(r"^\s*\|.*\|\s*$", re.M),
    "checkbox_md": re.compile(r"^\s*- \[[ x]\]", re.M),
    "emoji_check": re.compile(r"[✅❌⚠\U0001F680\U0001F389✨\U0001F4A1]"),
    "contraction": re.compile(r"\b\w+'(s|t|re|ve|ll|d|m)\b", re.I),
    "first_person_sg": re.compile(r"\bI\b"),
    "first_person_pl": re.compile(r"\bwe\b", re.I),
    "you": re.compile(r"\byou\b", re.I),
    "hedge": re.compile(r"\b(might|maybe|perhaps|probably|I think|I'd say|seems|likely)\b", re.I),
    "question": re.compile(r"\?"),
    "exclaim": re.compile(r"!"),
}


def mechanical(texts):
    """Per-1000-word rates for each marker, plus shape statistics."""
    joined = "\n\n".join(texts)
    words = len(joined.split())
    if words == 0:
        return {}
    stats = {f"{k}_per_1k": round(1000 * len(p.findall(joined)) / words, 3)
             for k, p in PATTERNS.items()}
    stats.update({f"{k}_n": len(p.findall(joined)) for k, p in PATTERNS.items()})
    sents = [s for s in SENT_SPLIT.split(re.sub(r"\s+", " ", joined)) if s.strip()]
    slens = sorted(len(s.split()) for s in sents)
    dlens = sorted(len(t.split()) for t in texts if t.strip())

    def pct(xs, q):
        return xs[int(q * (len(xs) - 1))] if xs else 0

    stats.update({
        "n_docs": len(texts), "n_words": words,
        "sent_len_mean": round(sum(slens) / len(slens), 2) if slens else 0,
        "sent_len_median": pct(slens, 0.5), "sent_len_p90": pct(slens, 0.9),
        "doc_len_mean": round(sum(dlens) / len(dlens), 2) if dlens else 0,
        "doc_len_median": pct(dlens, 0.5), "doc_len_p90": pct(dlens, 0.9),
    })
    return stats
