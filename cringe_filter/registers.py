"""Contexts: the situations a piece of text is written for.

A context names a register in the profile. The same person writes very
differently in each, which is the whole reason the toolset takes a context
argument: a rule that is right for a GitHub reply is wrong for a paper.
"""
import re

from .bundle import profile

ALIASES = {
    "github": ("github", "gh", "github-own", "own-repo", "issue", "pr",
               "pull-request", "issue-comment", "review", "github-reply"),
    "discussion": ("discussion", "discussions", "github-discussion",
                   "lab", "announcement"),
    "third-party": ("third-party", "third_party", "thirdparty", "bug-report",
                    "bug", "upstream", "issue-elsewhere", "external-repo"),
    "email": ("email", "mail", "e-mail", "outlook"),
    "message": ("message", "dm", "chat", "slack", "teams", "text", "sms",
                "comment", "linkedin-comment", "note"),
    "linkedin": ("linkedin", "post", "social", "announcement-post"),
    "tutorial": ("tutorial", "docs", "doc", "readme", "documentation",
                 "guide", "course", "lesson", "wiki"),
    "paper": ("paper", "manuscript", "report", "abstract", "thesis",
              "scientific", "science", "journal", "preprint"),
    "proposal": ("proposal", "grant", "grant-proposal", "funding",
                 "nsf", "doe", "white-paper"),
    "any": ("any", "unknown", "default", "none"),
}


def resolve(name):
    """Canonical context for a name or alias; raises on unknown."""
    key = (name or "any").strip().lower().replace("_", "-")
    for ctx, names in ALIASES.items():
        if key == ctx or key in names:
            if ctx in profile()["registers"]:
                return ctx
            # A profile built before proposals had a register of their own
            # still serves them, with the paper card.
            if ctx == "proposal" and "paper" in profile()["registers"]:
                return "paper"
            return "any"
    raise ValueError(f"unknown context {name!r}; one of: "
                     + ", ".join(ALIASES))


OWN_ACCOUNTS = {"sgbaird", "sparks-baird", "accelerationconsortium",
                "vertical-cloud-lab", "sgbaird-alt", "ac-bo-hackathon",
                "borysgroup", "sgbaird-yolo"}


def infer_context(url_or_path):
    """Guess the context from where the text is going."""
    s = (url_or_path or "").strip().lower()
    if not s:
        return "any"
    if "linkedin.com" in s:
        return "message" if "/comment" in s else "linkedin"
    if "mailto:" in s or "outlook" in s or s.endswith(".eml"):
        return "email"
    m = re.search(r"github\.com/([^/]+)/([^/]+)(/([^/]+))?", s)
    if m:
        owner, section = m.group(1), m.group(4) or ""
        if section == "discussions":
            return "discussion"
        if section in ("issues", "pull", "pulls", "compare", ""):
            return "github" if owner in OWN_ACCOUNTS else "third-party"
        if section in ("blob", "tree", "wiki"):
            return "tutorial"
        return "github" if owner in OWN_ACCOUNTS else "third-party"
    if "proposal" in s or "grant" in s:
        return "proposal"
    if re.search(r"\.(tex|bib)$", s) or "manuscript" in s or "paper" in s:
        return "paper"
    if re.search(r"\.(md|rst|ipynb)$", s) or "docs/" in s or "readme" in s:
        return "tutorial"
    return "any"


def register(ctx):
    return profile()["registers"][resolve(ctx)]


def contexts():
    """Every context the bundle can serve, with its label and budget."""
    regs = profile()["registers"]
    return [{"context": c, "aliases": list(ALIASES.get(c, ())),
             "label": r["label"], "n_docs": r["n_docs"],
             "n_words": r["n_words"], "median_words": r["doc_words_median"],
             "budget_words": r["doc_words_budget"],
             "carried_forward": r["carried_forward"]}
            for c, r in regs.items()]
