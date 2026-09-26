"""Load the compiled profile and the exemplar banks that ship in the package."""
import functools
import json
import os
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def profile_dir():
    """Where the profile lives. CRINGE_FILTER_PROFILE points at a profile kept
    outside the package, and its exemplars/ folder, if any, comes with it."""
    path = os.environ.get("CRINGE_FILTER_PROFILE")
    return os.path.dirname(os.path.abspath(path)) if path else DATA_DIR


@functools.lru_cache(maxsize=1)
def profile():
    path = os.environ.get("CRINGE_FILTER_PROFILE",
                          os.path.join(DATA_DIR, "profile.json"))
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def reference(ctx):
    """Claude's rates to contrast a context with. Claude's GitHub prose by
    default; a context whose genre Claude also writes in (a manuscript, a
    proposal) can carry its own, so the contrast is author, not genre."""
    p = profile()
    name = (p.get("registers", {}).get(ctx) or {}).get("reference")
    return (p.get("references") or {}).get(name) or p["reference"]


HEADING = re.compile(r"^## (.+)$")


@functools.lru_cache(maxsize=None)
def exemplars(bank):
    """Passages from one bank: list of {heading, text, words}. A bank next
    to an outside profile wins over the packaged one of the same name."""
    path = os.path.join(profile_dir(), "exemplars", bank)
    if not os.path.exists(path):
        path = os.path.join(DATA_DIR, "exemplars", bank)
    if not os.path.exists(path):
        return []
    out, heading, quote = [], None, []

    def flush():
        if heading and quote:
            text = "\n".join(quote).strip()
            if text:
                out.append({"heading": heading, "text": text,
                            "words": len(text.split())})

    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    for line in lines:
        m = HEADING.match(line)
        if m:
            flush()
            heading, quote = m.group(1).strip(), []
        elif line.startswith(">"):
            quote.append(line[1:].lstrip(" "))
        elif heading and not line.strip() and quote:
            quote.append("")
    flush()
    return out
