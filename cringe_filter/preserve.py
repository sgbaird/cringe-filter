"""Content preservation: what a rewrite has to carry over from its source.

The rewrite prompt promises to keep every number, link, code span and
command, and until now nothing checked the promise (Edison review,
2026-09-23: "a fluent factual deletion can pass"). This module lists the
tokens in a draft that a style rewrite has no business changing and
reports which of them a rewrite dropped, so the revision pass can ask for
them back and an evaluation can count them.

It is deliberately literal. A rewrite that turns "3 repos" into "three
repos" is fine, so single digits are matched against their word form too;
everything else has to appear verbatim.
"""
import re

from . import latex

CODE_BLOCK = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`([^`\n]+)`")
URL = re.compile(r"https?://[^\s)>\]]+")
NUMBER = re.compile(r"(?<![\w./-])[+-]?\d[\d,]*(?:\.\d+)?%?(?![\w/-])")
PATH = re.compile(r"(?<![\w/:])(?:[\w.-]+/)+[\w.-]+")

_WORDS = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
          "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
          "10": "ten", "11": "eleven", "12": "twelve"}

# Slash-joined words are usually prose, not paths: "at/under 20 mm",
# "argon/atmosphere" and "page/RSS/oEmbed" all became plain words in
# held-out rewrites, and the check asked for each "path" back (rewrite
# experiment, 2026-09-25). A match is a path only if it looks like one: a
# file extension, or a digit, hyphen or underscore somewhere in it.
_PATHLIKE = re.compile(r"\.\w+$|[\d_-]")


def _norm(s):
    return " ".join(s.split())


def immutables(text):
    """The tokens a rewrite must keep, by kind."""
    blocks = [_norm(m.group(0)) for m in CODE_BLOCK.finditer(text)]
    prose = CODE_BLOCK.sub(" ", text)
    code = {_norm(m.group(1)) for m in INLINE_CODE.finditer(prose)}
    prose = INLINE_CODE.sub(" ", prose)
    urls = {u.rstrip(".,;:") for u in URL.findall(prose)}
    prose = URL.sub(" ", prose)
    # A path that ends a sentence carries the period in the match, and the
    # rewrite is free to move it mid-sentence.
    paths = {p for p in (m.rstrip(".,;:") for m in PATH.findall(prose))
             if _PATHLIKE.search(p)}
    numbers = {n.replace(",", "") for n in NUMBER.findall(prose)}
    out = {"blocks": blocks, "code": sorted(code), "urls": sorted(urls),
           "paths": sorted(paths), "numbers": sorted(numbers)}
    if latex.looks_like_latex(text):
        # A rewrite of a LaTeX draft that drops a \cite or a \ref loses a
        # claim's support without changing a single number.
        out.update(latex.immutables(text))
    return out


def _present(token, kind, haystack, haystack_words):
    if kind == "numbers":
        if token in haystack_words or token in haystack:
            return True
        return _WORDS.get(token.rstrip("%"), "\0") in haystack_words
    return token in haystack


def check(source, rewrite):
    """What the rewrite dropped: {kind: [missing...]}, plus a retention rate."""
    want = immutables(source)
    hay = _norm(rewrite)
    # "1,234" and "1234" are the same number.
    hay_numbers = re.sub(r"(?<=\d),(?=\d)", "", hay.lower())
    hay_words = set(re.findall(r"[\w%.]+", hay_numbers))
    missing, total = {}, 0
    for kind in ("code", "urls", "paths", "numbers", "citations", "refs", "math"):
        if kind not in want:
            continue
        lost = [t for t in want[kind]
                if not _present(t, kind,
                                hay_numbers if kind == "numbers" else hay,
                                hay_words)]
        total += len(want[kind])
        if lost:
            missing[kind] = lost
    have_blocks = {_norm(m.group(0)) for m in CODE_BLOCK.finditer(rewrite)}
    lost_blocks = [b for b in want["blocks"] if b not in have_blocks]
    total += len(want["blocks"])
    if lost_blocks:
        missing["blocks"] = [b[:80] for b in lost_blocks]
    n_missing = sum(len(v) for v in missing.values())
    return {"missing": missing, "n_immutables": total, "n_missing": n_missing,
            "retained": round(1 - n_missing / total, 3) if total else 1.0}


def report(result, limit=12):
    """One line per dropped token, for a revision request."""
    lines = []
    for kind, items in result["missing"].items():
        for t in items[:limit]:
            label = {"code": "code span", "math": "math span",
                     "citations": "citation key", "refs": "reference or label key"
                     }.get(kind, kind[:-1])
            lines.append(f"- dropped {label}: {t}")
    return "\n".join(lines)
