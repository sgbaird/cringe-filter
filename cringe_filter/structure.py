"""Sentence and paragraph shape, without a parser.

The parsed comparison of the two writers (scripts/voice/structure.py,
docs/voice/research/structure.md) found that the gap is not only in which
words each uses but in how the sentences are built. Even in plain
statements, with requests and questions set aside, the writer's subject is
usually a person ("I", "we", "you") and the writer's plans sit in modal and
infinitive verbs ("we could try", "want to check"); Claude's subject is
usually a noun phrase ("The parser drops ..."), and it packs a second idea
into the same sentence with a colon, a dash, a semicolon, an appositive or
a parenthesis. And half of Claude's words sit in lists, tables, headers
and checkboxes, where nine tenths of the writer's are prose.

This module counts the parts of that a regular expression can see, so the
toolset stays free of dependencies. Each measure was checked against the
parser on the corpus before it was used (see the research note). Counts
come with their denominator (sentences, prose paragraphs or words), so the
profile can carry pooled rates and score.py can weigh a short draft
fairly.
"""
import re

from .markers import clean

# Formatting that turns a line into something other than prose.
_HEADER = re.compile(r"^\s{0,3}#{1,6}\s")
_ITEM = re.compile(r"^\s*(?:[-*+]|\d{1,3}[.)])\s")
_TABLE = re.compile(r"^\s*\|.*\|\s*$")
_RULE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
_EMPHASIS = re.compile(r"\*\*|__|~~")
_SENT_END = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[\"'(\[]?[A-Za-z0-9@`])")
_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*|\d[\d.,]*")

PERSON = {"i", "i'm", "i've", "i'd", "i'll", "we", "we're", "we've", "we'd", "we'll",
          "let's", "you", "you're", "you've", "you'd", "you'll"}
# Words that can stand before the subject without changing who it is:
# "Also, I think", "So we could", "Thanks, I'll".
LEAD_IN = {"also", "so", "and", "but", "then", "now", "maybe", "actually", "honestly",
           "ok", "okay", "yes", "yeah", "no", "thanks", "hmm", "well", "still", "just",
           "otherwise", "anyway", "probably", "perhaps", "hopefully", "btw", "fyi",
           "alternatively", "additionally", "unfortunately", "separately", "oh"}
DETERMINER = {"the", "a", "an", "each", "every", "all", "both", "most", "many",
              "several", "no", "any", "some", "another", "its", "their", "his", "her"}
NUMBER_WORDS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                "ten", "eleven", "twelve", "twenty", "thirty", "forty", "fifty",
                "hundred", "half", "none", "zero"}
CONJUNCTION = {"and", "but", "so", "or", "yet", "plus"}
MODAL = re.compile(r"\b(?:can|could|would|should|might|may|must|shall|will)\b|'ll\b|'d\b", re.I)
# "to" before a verb: anything but a determiner, a pronoun or a number
# follows it. Crude, but it tracks the parser's infinitive complements.
NOT_VERB = ("the|a|an|this|that|these|those|my|your|our|his|her|their|its|me|you|him|them|"
            "us|it|which|what|whom|each|every|all|both|some|any|no|one|two|three|four|five|"
            "six|seven|eight|nine|ten|about|around|date|do|be|get|have|see")
TO_VERB = re.compile(r"\bto\s+(?!(?:%s)\b)[a-z]{2,}\b" % NOT_VERB)
TO_COMMON = re.compile(r"\bto\s+(?:do|be|get|have|see)\b", re.I)
_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


def colon_blocks(text):
    """(blocks, how many of them a colon introduces), from the raw text.

    A block is a fenced code block, a list or a table, counted once. It is
    introduced by a colon when the last line of text before it ends in one
    ("Run this:", "**Changes:**"). The share measures the habit itself; the
    "colon before block" tell counts the same lines per 1000 words, which
    mostly measures how many blocks a page has, so a docs page with few
    code blocks read as Claude's."""
    blocks = colon = 0
    prev, kind, fence = "", None, None
    for line in text.split("\n"):
        if fence:
            if line.strip().startswith(fence):
                fence, prev = None, line
            continue
        if not line.strip():
            kind = None if kind == "table" else kind
            continue
        m = _FENCE.match(line)
        new = ("code" if m else "table" if _TABLE.match(line)
               else "list" if _ITEM.match(line) else None)
        if new and new != kind:
            blocks += 1
            colon += prev.rstrip(" \t*_").endswith(":")
        if m:
            fence, new = m.group(1), None
        elif not new and kind == "list" and line[:1] in (" ", "\t"):
            new = "list"  # a wrapped list item
        kind, prev = new, line
    return blocks, colon


def blocks(text):
    """Paragraphs as lists of (kind, text) lines, kind prose/list/header/table."""
    out = []
    for block in re.split(r"\n\s*\n", text):
        lines = [l for l in block.split("\n") if l.strip() and not _RULE.match(l)]
        units, prose = [], []
        for line in lines:
            kind = ("header" if _HEADER.match(line) else "table" if _TABLE.match(line)
                    else "list" if _ITEM.match(line) else None)
            if kind:
                if prose:
                    units.append(("prose", " ".join(prose)))
                    prose = []
                units.append((kind, line.strip()))
            elif units and units[-1][0] == "list" and not prose and line[:1] in (" ", "\t"):
                units[-1] = ("list", units[-1][1] + " " + line.strip())
            else:
                prose.append(line.strip())
        if prose:
            units.append(("prose", " ".join(prose)))
        if units:
            out.append(units)
    return out


def sentences(text):
    text = _EMPHASIS.sub("", " ".join(text.split()))
    return [s for s in _SENT_END.split(text) if _WORD.search(s)]


def _first_words(sent, n=3):
    return [w.lower().replace("’", "'") for w in _WORD.findall(sent)[:n]]


def openers(sent):
    """What a sentence opens on, as a set of feature keys.

    A lead-in word ("Also,", "So", "Thanks,") and the subject after it
    are counted separately, so "Also, we could" is both an adverb opener
    and a person subject. A determiner or a number only counts when it is
    the first word."""
    words = _first_words(sent, 4)
    if not words:
        return set()
    first, out = words[0], set()
    if first in CONJUNCTION:
        out.add("conjunction_open")
    elif first in LEAD_IN:
        out.add("adverb_open")
    head = words[1] if out and len(words) > 1 else first
    if head in PERSON:
        out.add("person_open")
    elif not out and head in DETERMINER:
        out.add("determiner_open")
    elif not out and (head in NUMBER_WORDS or head[:1].isdigit()):
        out.add("number_open")
    return out


def measure(text):
    """Counts and denominators for one text.

    Returns {"sentences", "prose_paragraphs", "words", "list_words",
    "blocks", and a count per feature}. Features are counted over prose
    sentences only; list items, headers and table rows count toward
    list_words. Blocks are read from the text before code is stripped."""
    cleaned = clean(text)
    paras = blocks(cleaned)
    c = {"sentences": 0, "prose_paragraphs": 0, "one_sentence_paragraphs": 0,
         "words": 0, "list_words": 0, "person_open": 0, "determiner_open": 0,
         "number_open": 0, "conjunction_open": 0, "adverb_open": 0, "question": 0,
         "modal": 0, "to_verb": 0, "colon": 0, "semicolon": 0, "dash": 0, "paren": 0,
         "sentence_words": 0}
    c["blocks"], c["colon_block"] = colon_blocks(text)
    for units in paras:
        prose_only = all(k == "prose" for k, _ in units)
        n_in_para = 0
        for kind, line in units:
            n = len(line.split())
            c["words"] += n
            if kind != "prose":
                c["list_words"] += n
                continue
            for s in sentences(line):
                n_in_para += 1
                c["sentences"] += 1
                c["sentence_words"] += len(s.split())
                for key in openers(s):
                    c[key] += 1
                c["question"] += s.rstrip(" )\"'").endswith("?")
                c["modal"] += len(MODAL.findall(s))
                c["to_verb"] += len(TO_VERB.findall(s)) + len(TO_COMMON.findall(s))
                # A colon inside a sentence, not one that ends a line
                # introducing a list or a code block.
                c["colon"] += len(re.findall(r":(?=\s+\S)", s))
                c["semicolon"] += s.count(";")
                c["dash"] += len(re.findall(r"\s[-–—]{1,2}\s|—|–", s))
                c["paren"] += len(re.findall(r"\(\s*[A-Za-z0-9]", s))
        if prose_only and n_in_para:
            c["prose_paragraphs"] += 1
            c["one_sentence_paragraphs"] += n_in_para == 1
    return c


# Each feature: its count key, its denominator, and how it reads.
FEATURES = {
    "person_open": ("sentences", "sentences whose subject is I, we or you"),
    "determiner_open": ("sentences", "sentences opening on \"The\", \"A\", \"Each\" and the like"),
    "number_open": ("sentences", "sentences opening on a number"),
    "conjunction_open": ("sentences", "sentences opening on And, But or So"),
    "adverb_open": ("sentences", "sentences opening on Also, Maybe, Thanks and the like"),
    "question": ("sentences", "questions"),
    "modal": ("sentences", "modal verbs (could, might, would, should) per sentence"),
    "to_verb": ("sentences", "\"to\" + verb (want to, need to, good to) per sentence"),
    "colon": ("sentences", "colons inside a sentence"),
    "semicolon": ("sentences", "semicolons"),
    "dash": ("sentences", "dashes between words"),
    "paren": ("sentences", "parentheses"),
    "sentence_words": ("sentences", "words per sentence"),
    "one_sentence_paragraphs": ("prose_paragraphs", "one-sentence paragraphs"),
    "list_words": ("words", "words in lists, tables and headers"),
    "colon_block": ("blocks", "lists, tables and code blocks a colon introduces"),
}


def rates(counts):
    """Pooled rate per feature: a share or a count per denominator unit."""
    out = {}
    for key, (den, _) in FEATURES.items():
        d = counts.get(den, 0)
        out[key] = round(counts.get(key, 0) / d, 4) if d else None
    return out


def pool(texts):
    total = {}
    for t in texts:
        for k, v in measure(t).items():
            total[k] = total.get(k, 0) + v
    return total
