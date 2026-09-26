"""The voice filter as a prompt.

Two things the research behind this project says about getting a model to
write like a person, and one thing the Edison review of this toolset
added. Real examples beat descriptions, and long rule lists degrade
compliance; and numeric rates and intervals are not instructions a model
can act on for one short rewrite, so they belong in an appendix for
people. The prompt therefore leads with two real passages matched to the
target length and free of anything the rules forbid, follows with five
plain constraints and a short list of tells in plain words, and keeps the
numbers out. `build_prompt(..., with_evidence=True)` also returns the
appendix with every rate and interval.

Any model can apply it. rewrite.py applies it with Claude; inside a coding
agent the agent applies it to its own draft.
"""
import re

from . import latex
from .bundle import exemplars, profile, reference
from .lint import lint_text, rules_for
from .registers import resolve

_HAS_DIGIT = re.compile(r"\d")
_ENDS_SENTENCE = re.compile(r"[.!?][\"')\]]*$")
_BACKREF = re.compile(r"\b(it|this|that|these|those|they|them)\b", re.I)


def _sentences(text):
    """Split on sentence ends, never inside a quotation."""
    out, buf, quotes = [], [], 0
    for tok in re.split(r"(\s+)", text):
        buf.append(tok)
        quotes += tok.count('"')
        if quotes % 2 == 0 and _ENDS_SENTENCE.search(tok):
            out.append("".join(buf).strip())
            buf = []
    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return [s for s in out if s]


def plain_note(note, min_words=2):
    """A register-card rule with its measurements removed.

    The cards in registers.md are written for a person and quote the rates
    behind each rule ("25.4 per 1000 words, nearly double the writer's rate in your
    own repos"). Numbers are not instructions a model can act on for one
    short rewrite, and the Edison review found them in the emitted prompt,
    so every sentence that carries a figure is dropped here. A sentence
    that follows a dropped one and opens on a pronoun ("Do not use it.")
    is dropped with it, since its referent is gone. The full text, numbers
    included, stays in the profile for `prompt --evidence`.
    """
    kept, dropped_prev = [], False
    for s in _sentences(note.strip()):
        if _HAS_DIGIT.search(s) or ".py" in s or "--" in s:
            dropped_prev = True
            continue
        if dropped_prev and _BACKREF.search(" ".join(s.split()[:5])):
            continue
        kept.append(s)
        dropped_prev = False
    text = " ".join(kept).strip()
    return text if len(text.split()) >= min_words else ""


def _trim(text, max_words):
    words = text.split()
    if len(words) <= max_words:
        return text
    cut = " ".join(words[:max_words])
    for stop in (". ", "? ", "! "):
        i = cut.rfind(stop)
        if i > len(cut) * 0.6:
            return cut[:i + 1]
    return cut + " [...]"


def pick_exemplars(reg, ctx, n=2, target_words=None, max_words=300):
    """Two passages near the target length that contradict none of the rules.

    The banks were selected for typicality; this picks from them by length
    band rather than taking the longest, and drops any passage the linter
    would flag in this context, so the examples never argue with the
    constraints that follow them.
    """
    pool = []
    for bank in reg.get("exemplars", []):
        pool.extend(exemplars(bank))
    if not pool:
        return []
    clean = [e for e in pool
             if e["words"] >= 25 and not fragmented(e["text"])
             and not any(f["severity"] in ("error", "warn")
                         and f["rule"] not in ("too-long",)
                         for f in lint_text(e["text"], ctx))]
    if not clean:
        clean = pool
    median = reg.get("doc_words_median") or 60
    p90 = reg.get("doc_words_p90") or median * 3
    target = target_words or int(median * 1.5)
    target = max(median, min(target, p90))
    clean.sort(key=lambda e: abs(e["words"] - target))
    return [_trim(e["text"], max_words) for e in clean[:n]]


def fragmented(text):
    """A passage whose links and code were stripped at bank-building time
    reads as a list of stubs; it teaches nothing about voice."""
    raw = text.split("\n")
    lines = [l.strip() for l in raw if l.strip()]
    if len(lines) < 3:
        return False
    if len(raw) - len(lines) >= len(lines):
        return True  # more blank lines than text: stripped links and code
    short = sum(1 for l in lines if len(l.split()) < 5)
    return short / len(lines) > 0.3


def _formatting_line(m):
    def level(key, none=0.5, normal=3.0):
        v = m.get(key, 0) or 0
        return "none" if v < none else "normal" if v >= normal else "rare"

    h, b, u, t = (level("header_md_per_1k"), level("bold_md_per_1k"),
                  level("bullet_md_per_1k", 1.0), level("table_md_per_1k"))
    parts = []
    if h == "none" and b == "none" and t == "none":
        parts.append("Short prose paragraphs without headers, tables or bold")
    else:
        parts.append("Headers are normal here" if h == "normal" else
                     "Headers only where a template supplies them" if h == "rare"
                     else "No headers")
        parts.append("bold is normal here" if b == "normal" else
                     "bold sparingly" if b == "rare" else "no bold")
        parts.append("tables are fine" if t == "normal" else "no tables")
    parts.append("bullets are fine but few" if u == "normal" else
                 "bullets rarely" if u == "rare" else "no bullet lists")
    return "; ".join(parts) + "."


def _stance_line(m):
    out = []
    hedge = m.get("hedge_per_1k", 0) or 0
    if hedge >= 5:
        out.append("The writer hedges freely here (\"might be\", \"not sure if\", "
                   "\"seems to\"): hedge whatever is uncertain")
    elif hedge < 2:
        out.append("The writer commits to positions here: hedge only genuine uncertainty")
    else:
        out.append("Hedge only what is uncertain")
    if (m.get("question_per_1k", 0) or 0) >= 5:
        out.append("questions back to the reader are normal")
    if (m.get("first_person_sg_per_1k", 0) or 0) >= 15:
        out.append("first person singular, as a person")
    elif (m.get("first_person_sg_per_1k", 0) or 0) < 1:
        out.append("no \"I\"")
    if (m.get("first_person_pl_per_1k", 0) or 0) >= 5:
        out.append("\"we\" for shared work")
    ex = m.get("exclaim_per_1k", 0) or 0
    if ex >= 5:
        out.append("exclamation marks are normal here")
    elif ex < 1:
        out.append("no exclamation marks")
    return "; ".join(out) + "."


# Closed-class words and the few stance verbs that carry them ("I think",
# "we need"). Only these are eligible for the small-words line, so topic
# words and the action harness's vocabulary ("job", "branch") never are.
SMALL_WORDS = set("""
i me my we us our you your he she it its they them their this that these
those here there a an the some any every each all both no nothing none
and but or so if because since though although while when whether
to of in on at by for with from into about after before over than as
be is are was were been being am have has had do does did done
can could will would shall should may might must i'm i'd i've i'll we're
we'd we've we'll you're you'd let's it's that's there's what's
also just only even still already maybe probably perhaps actually really
exactly quite very too not think guess need want seems seem like
""".split())


CONVERSATIONAL = {"github", "discussion", "third-party", "message", "email"}
# Written for the record rather than to a person: no answer to lead with,
# no one to ask, and the length is set by the content.

# The corrective-contrast rules, stated to the model as one move.
CONTRAST_KEYS = ("x-not-y", "dash-not-y", "isnt-x-its-y")
CONTRAST_LINE = ("Correct a reading nobody offered ('X, not Y', 'X; not Y', "
                 "'it isn't X, it's Y'). Say what it is; name the alternative "
                 "only if someone in the thread proposed it.")

FORMAL = {"paper", "proposal"}


def _small_words_line(reg, ref, mfw, conversational=True, n_his=12, n_claude=5):
    """The function words that separate the writer from Claude in this register.

    Read from the Burrows' Delta profile the bundle already carries: the
    register's mean rate for each of the most frequent words against
    Claude's. The held-out rewrite experiment found that rewrites fixed
    sentence length and every named tell while keeping Claude's small
    words: "we", "be", "could", "might" stayed at Claude's rates, and
    "the" rose past them (docs/voice/research/rewrite-experiment.md)."""
    if not mfw or not reg.get("mfw_mean") or not ref.get("mfw_mean"):
        return None
    writer, claude = reg["mfw_mean"], ref["mfw_mean"]
    lean = [(w, (writer[j] + 0.5) / (claude[j] + 0.5), writer[j], claude[j])
            for j, w in enumerate(mfw["words"]) if w in SMALL_WORDS]
    mine = [w for w, r, a, _ in sorted(lean, key=lambda x: -x[1])
            if r >= 3 and a >= 2][:n_his]
    theirs = [w for w, r, _, b in sorted(lean, key=lambda x: x[1])
              if r <= 1 / 3 and b >= 1][:n_claude]
    if len(mine) < 3:
        return None
    line = ("Small words the writer uses far more than Claude here: "
            + ", ".join(f'"{w}"' for w in mine) + ".")
    if theirs:
        line += (" Claude leans on " + ", ".join(f'"{w}"' for w in theirs) + ".")
    if not conversational:
        return line
    return ("Talk to the people in the thread instead of reporting to them. "
            + line + " Put plans and doubts in verbs (\"we could\", \"it might "
            "be\", \"I think\") rather than in noun phrases, colons or parentheses.")


STRUCTURE_WORDING = 2


def _structure_line(reg, ref, wording=STRUCTURE_WORDING, formal=False, draft=None):
    """How the writer's sentences are built here, against Claude's, in plain words.

    Read from the parser-free structure rates the profile carries
    (cringe_filter.structure, docs/voice/data/structure-profile.json). The held-out
    rewrite test found that rewrites fixed the formatting, the dashes and the
    colons, and kept Claude's sentence skeleton: a noun-phrase subject, a
    past-tense or "is" verb, a statement; the writer's subject is usually a person,
    the writer's plans sit in modal and infinitive verbs, and it asks
    (docs/voice/research/structure.md). Each clause below appears only when
    the register's own rates put it on the writer's side by a clear margin, so a
    rebuild changes the wording without anyone editing it.

    Wording 1 is the one round two tested on fresh held-out comments. It
    moved every grammar judge toward the writer and overcorrected in two places:
    its example ("I ran it on the Pi") turned reports into one "I did X"
    sentence after another, and "no parenthesis" removed nearly all of them
    where the writer uses half Claude's rate. Wording 2 changes only those two
    clauses."""
    writer = (reg.get("structure") or {}).get("rates")
    cl = (ref.get("structure") or {}).get("rates")
    if not writer or not cl:
        return None

    def lean(k):
        a, b = writer.get(k), cl.get(k)
        if a is None or b is None:
            return 1.0
        return (a + 1e-3) / (b + 1e-3)

    if formal:
        return _formal_structure_line(writer, lean, draft)
    out = []
    if lean("person_open") >= 2 and wording == 1:
        out.append("Make a person the subject: what I, we or you did, think or "
                   "should do (\"I ran it on the Pi\", \"we could try a smaller "
                   "batch\"), not what a thing did (\"The run completed\").")
    elif lean("person_open") >= 2:
        out.append("Make a person the subject: what I, we or you think, plan or "
                   "need (\"I think it's the loader\", \"we could try a smaller "
                   "batch\", \"can you check the log?\") instead of what a thing "
                   "did (\"The run completed\"). Where the draft lists steps that were "
                   "done, say them once (\"I rebuilt the figure and pushed it\") "
                   "rather than one \"I did X\" sentence after another.")
    if lean("determiner_open") <= 0.5 or lean("number_open") <= 0.5:
        out.append("Open few sentences on \"The ...\", \"This ...\" or a number.")
    if lean("modal") >= 1.5 or lean("to_verb") >= 1.5:
        out.append("Put plans, doubts and next steps in verbs (could, might, "
                   "should, need to, want to) instead of past-tense summaries "
                   "or \"is\" sentences.")
    if lean("question") >= 3:
        out.append("Where the draft leaves a choice or a doubt open, ask it as a "
                   "question to the person.")
    packed = [k for k in ("colon", "dash", "semicolon", "paren") if lean(k) <= 0.67]
    if len(packed) >= 2 and wording == 1:
        out.append("One idea per sentence: no colon, dash, semicolon or "
                   "parenthesis carrying a second one.")
    elif len(packed) >= 2:
        names = {"colon": "colons", "dash": "dashes", "semicolon": "semicolons",
                 "paren": "parentheses"}
        marks = [names[k] for k in packed]
        marks = ", ".join(marks[:-1]) + " and " + marks[-1]
        out.append(f"Fewer {marks}: give a second idea its own sentence.")
    if (writer.get("one_sentence_paragraphs") or 0) >= 0.4 and lean("one_sentence_paragraphs") >= 1.3:
        out.append("One point per paragraph, often a single sentence.")
    if len(out) < 2:
        return None
    return " ".join(out)


def _formal_structure_line(writer, lean, draft=None):
    """The same measures, worded for a manuscript or a proposal, where
    the contrast is Claude's own scientific prose (paper_registers.py):
    in the lab's manuscripts Claude opens on a noun phrase and packs a
    second idea behind a colon or a semicolon, at four to five times the writer's
    rate in their papers before 2023, and writes "we" a fifth as often.

    Given unconditionally, the clauses overshot on Claude's one-pass
    drafts of the writer's sections, which were already at the writer's rates: "we"
    doubled, every semicolon went, sentences shrank from 22 words to 18
    (docs/voice/research/technical-writing.md, second pass). So with a
    draft in hand a clause appears only where the draft sits on Claude's
    side of the writer's rate, and without one each clause says not to overdo it.
    """
    mine = None
    if draft:
        from . import structure as shape
        mine = shape.rates(shape.measure(draft))

    def off(k, direction):
        """Is the draft on Claude's side of the writer's rate for k?"""
        if mine is None or mine.get(k) is None or writer.get(k) is None:
            return True
        return mine[k] < 0.5 * writer[k] if direction < 0 else mine[k] > 1.5 * writer[k] + 0.01

    out = []
    if lean("person_open") >= 1.5 and off("person_open", -1):
        out.append("Where a sentence reports what the authors did, let \"we\" "
                   "be its subject (\"We trained ...\") instead of the method or "
                   "the result (\"This approach enables ...\"); leave the other "
                   "sentences as they are.")
    if lean("determiner_open") <= 0.67 and off("determiner_open", 1):
        out.append("Open fewer sentences on \"The ...\" or \"This ...\".")
    packed = [k for k in ("colon", "semicolon", "dash") if lean(k) <= 0.67 and off(k, 1)]
    if packed:
        names = {"colon": "colon", "dash": "dash", "semicolon": "semicolon"}
        marks = [names[k] for k in packed]
        marks = (", ".join(marks[:-1]) + " or " + marks[-1]) if len(marks) > 1 else marks[0]
        out.append(f"Where a {marks} carries a second idea, give that idea its "
                   f"own sentence; the writer still uses them, so do not remove every one.")
    return " ".join(out) if out else None


def build_prompt(text, context="any", n_exemplars=2, max_exemplar_words=300,
                 max_rules=8, with_evidence=False, small_words=True,
                 structure=True, standing=False):
    """(system, user) for a rewrite, plus the evidence appendix on request.

    `standing` frames the filter as standing instructions for an agent that
    edits files (`cringe-filter instructions`) instead of a one-off rewrite.

    `small_words` adds a priority naming the function words that separate
    the writer from Claude in the register (see `_small_words_line`). On by
    default since the held-out experiment: against the same prompt without
    it, it moved the topic-masked model by +0.04 (32 of 36 rewrites up) and
    Delta toward the writer, with no loss on the other judges or in content. That
    condition was added after the first round, so the gain is exploratory.

    `structure` adds a priority on how sentences are built (see
    `_structure_line`); False leaves it out, 1 or 2 picks a wording. On by
    default since round two of the held-out test: on 36 fresh comments,
    wording 1 beat the prompt without it on every grammar judge (parts of
    speech +0.14, 34 of 36 up) and on the topic-masked model (+0.10), and
    overshot into "I did X" narration; wording 2, written after that and so
    exploratory, halved the overshoot and kept about two thirds of the
    gain (parts of speech +0.09, topic-masked +0.06, 33 of 36 up). Both
    cost about 1.5 points of the source's content words
    (docs/voice/research/structure.md)."""
    ctx = resolve(context)
    p = profile()
    reg = p["registers"][ctx]
    ref = reference(ctx)
    m = reg["mechanical"]
    draft_words = len(text.split()) if text else None

    out = [
        f"Rewrite the draft the way a careful human writer would write it here. Context: "
        f"{reg['label']}. "
        f"Preserve every factual claim, number, name, link, code span, command "
        f"and stated uncertainty. Do not add an answer the draft does not "
        f"contain, and do not report that you edited it. If style conflicts "
        f"with fidelity, keep the facts. Output only the rewrite.",
    ]
    if standing:
        out[0] = (
            f"When you write or edit prose in these files (text a reader sees; "
            f"leave code alone), write it the way a careful human writer would. "
            f"Context: {reg['label']}. Keep every factual claim, number, name, "
            f"link, code span, command and stated uncertainty. If style "
            f"conflicts with fidelity, keep the facts.")
        if ctx in ("paper", "proposal"):
            out[0] += (" In LaTeX, keep every \\cite, \\ref, \\label, math span "
                       "and environment exactly as written.")
    if text and latex.looks_like_latex(text):
        out[0] += (" The draft is LaTeX: keep every \\cite, \\ref, \\label, math "
                   "span and environment exactly as written, and change only "
                   "the prose between them.")
    ex = pick_exemplars(reg, ctx, n_exemplars, draft_words, max_exemplar_words)
    if ex:
        out += ["", "## Examples of human writing in this situation"]
        for e in ex:
            out += ["", "> " + e.replace("\n", "\n> ")]
    elif ctx == "email":
        out += ["", "## Examples", "",
                "No examples ship for email, because the sent mail in the corpus is "
                "private. The nearest public register is the short message:"]
        for e in pick_exemplars({"exemplars": ["message.md"],
                                 "doc_words_median": 21, "doc_words_p90": 66},
                                "message", 2, None, 120):
            out += ["", "> " + e.replace("\n", "\n> ")]
    elif ctx in FORMAL:
        what = ("proposals, because the writer's proposals are private"
                if ctx == "proposal" else "scientific prose in this profile")
        out += ["", "## Examples", "",
                f"No examples ship for {what}. Defer to the scientific "
                f"communication style guide where one exists."]

    budget = reg.get("doc_words_budget")
    # A manuscript section has no "answer or requested action" to lead
    # with, and cutting a third of it cuts content; what the paper card
    # and the style guide ask for instead is reporting over selling.
    first = ("Report what was done and found; cut any sentence that sells "
             "the work instead." if ctx in FORMAL else
             "Lead with the answer or the requested action.")
    length = (f"Keep it under {budget} words unless the content needs more; "
              f"the writer's median here is {reg['doc_words_median']}, and when more "
              f"room is needed, add sentences and keep each one short.")
    if ctx in FORMAL:
        # A section's length is set by its content, and the line above
        # made the model split the writer's sentences: 17 words against their 26 on
        # eight human-written sections (docs/voice/research/technical-writing.md).
        length = ("Keep the draft's length and its sentences whole; split a "
                  "sentence only when it carries two ideas.")
    out += ["", "## Priorities, in order",
            f"1. {first}",
            f"2. {length}",
            f"3. {_formatting_line(m)}",
            f"4. {_stance_line(m)}",
            "5. Remove status-report scaffolding, hype, and any narration of "
            "the edit."]
    extra = []
    small = (_small_words_line(reg, ref, p.get("mfw"), ctx in CONVERSATIONAL)
             if small_words else None)
    if small:
        extra.append(small)
    # structure=True takes the current wording; an int picks one, so the
    # round-two prompts can be rebuilt exactly.
    shape = (_structure_line(reg, ref, structure if isinstance(structure, int)
                             and not isinstance(structure, bool) else STRUCTURE_WORDING,
                             formal=ctx in FORMAL, draft=text)
             if structure else None)
    if shape:
        extra.append(shape)
    if reg.get("greetings"):
        g = ", ".join(k.capitalize() for k in list(reg["greetings"])[:3])
        sgn = ", ".join(k.capitalize() for k in list(reg["signoffs"])[:3])
        extra.append(f"Open with {g}; close with {sgn}.")
    for i, line in enumerate(extra, 6):
        out.append(f"{i}. {line}")

    measured = [r for r in rules_for(ctx) if r.evidence == "measured"]
    measured.sort(key=lambda r: -(r.lean or 0))
    if ctx in FORMAL:
        # The paper ratios compare the writer's detexed manuscripts with Claude's
        # GitHub comments, so the formatting rules top the ranking only
        # because detex stripped the \section, \textbf and \item; ranked
        # that way the em dash, which the linter fails a paper on, fell off
        # the list. Errors first here.
        measured.sort(key=lambda r: r.severity != "error")
    # The corrective contrast goes in as one line ahead of the ranked
    # rules: ranked by ratio, "X, not Y" fell below the glyphs, and it is
    # the member Claude writes most (1.5 per 1000 words against the writer's 0.4),
    # the one the rewrites kept at Claude's rate (contrast-family.json).
    contrast = [r for r in measured if r.key in CONTRAST_KEYS]
    listed = [r for r in measured if r.key not in CONTRAST_KEYS]
    if listed or contrast:
        out += ["", "## Do not"]
        if contrast:
            out.append(f"- {CONTRAST_LINE}")
        for r in listed[:max_rules]:
            out.append(f"- {r.message}")

    card = reg.get("card") or {}
    notes = [n for n in (plain_note(r) for r in card.get("rules", [])) if n][:4]
    if notes:
        out += ["", "## Notes for this register"] + [f"- {n}" for n in notes]
    q = p.get("one_question") or []
    if q:
        cut = ("cut the sentences that sell rather than report" if ctx in FORMAL
               else "cut a third")
        out += ["", f"Before returning, ask: {q[0]} If yes, {cut} and put "
                    f"the honest hedges back. Then check silently that every "
                    f"fact, number, link, code span and command is still there "
                    f"and that nothing new was claimed."]
    else:
        out += ["", "Before returning, check silently that every fact, number, "
                    "link, code span and command is still there and that "
                    "nothing new was claimed."]

    system = "\n".join(out)
    user = "Rewrite this draft:\n\n" + text.strip()
    if not with_evidence:
        return system, user
    return system, user, evidence_appendix(ctx, reg, ref, p, measured)


MINIMAL_INTRO = (
    "You are editing a draft that a reviewer is about to read. Change as "
    "little as possible: copy every word you are not asked to change exactly "
    "as it is, keep the same markup (LaTeX or Markdown), and keep every fact, "
    "number, citation and link. Return only the edited draft, with no comment.")

# What the lab's reviewers asked agents to change in manuscripts,
# proposals and abstracts, most frequent first (the rule groups in
# docs/voice/data/manuscript-threads.json and proposal-threads.json).
# scripts/voice/correction_experiment.py tests exactly this list.
REVIEW_CHECKLIST = [
    "Claim only what was done. Remove embellishment, extrapolation and "
    "anything the work did not show.",
    "Use plain words where the draft uses jargon, and define each "
    "abbreviation or coined term at first use.",
    "Be concrete: numbers, examples and named things in place of general "
    "claims.",
    "Cut words and details the reader does not need.",
    "Write for the reader of the document. No process talk, no references "
    "to issues, pull requests or whoever asked for the text.",
    "Keep one frame and do not overemphasize: drop 'critical', 'key', "
    "'novel' and the like unless the sentence earns them.",
    "Name things plainly and use one term for one thing.",
    "No em dashes or dash-set asides. Use a semicolon or a colon only "
    "where a period will not do, and fewer parenthetical asides.",
    "Do not correct a reading nobody offered ('X, not Y').",
]


def build_minimal_prompt(text, context="any"):
    """The smallest edit a reviewer would make, for a draft headed to review.

    A full rewrite moves a draft away from the version its reviewer ends up
    writing: on 74 drafts people corrected in the lab repos and the course
    repo, the cringe-filter rewrite took the median word-level distance to the
    reviewer's version from 0.24 to 0.42, while an edit told to change as
    little as possible, with this checklist and the draft's lint findings,
    stayed at 0.24, and 39% of its word changes were the reviewer's
    against the rewrite's 27% (docs/voice/research/corrections.md).
    Returns (system, user)."""
    from .lint import lint_text
    ctx = resolve(context)
    found = [f for f in lint_text(text, ctx)
             if f["rule"] not in ("too-long", "long-sentence")]
    out = [MINIMAL_INTRO, "",
           "Make only the edits a careful reviewer would make. What reviewers "
           "have asked for in drafts like this:"]
    out += [f"- {c}" for c in REVIEW_CHECKLIST]
    if found:
        out += ["", "A style linter also flagged these; fix each one unless it "
                    "is a false alarm:"]
        out += [f"- {f['rule']}: {f['message']} (at: \"{f['snippet']}\")"
                for f in found]
    out += ["", "If nothing needs to change, return the draft unchanged."]
    return "\n".join(out), "Edit this draft:\n\n" + text.strip()


def evidence_appendix(ctx, reg, ref, p, measured):
    """The numbers behind the prompt, for a person reviewing it."""
    m, rm = reg["mechanical"], ref["mechanical"]
    lines = [f"## Evidence for {ctx} ({reg['n_docs']:,} documents, "
             f"{reg['n_words']:,} words; Claude reference {ref['n_docs']:,} "
             f"documents)",
             f"- Length: median {reg['doc_words_median']}, p90 "
             f"{reg['doc_words_p90']}, budget {reg['doc_words_budget']}; "
             f"Claude's median {ref['doc_words_median']}.",
             f"- Sentences: median {reg['sent_words_median']}, p90 "
             f"{reg['sent_words_p90']}."]
    for label, key in (("headers", "header_md_per_1k"), ("bold", "bold_md_per_1k"),
                       ("bullets", "bullet_md_per_1k"), ("tables", "table_md_per_1k"),
                       ("hedges", "hedge_per_1k"), ("questions", "question_per_1k"),
                       ('"I"', "first_person_sg_per_1k"), ('"we"', "first_person_pl_per_1k"),
                       ('"you"', "you_per_1k"), ("exclamation marks", "exclaim_per_1k")):
        lines.append(f"- {label}: {m.get(key, 0) or 0:.2f} per 1k; Claude "
                     f"{rm.get(key, 0) or 0:.2f}")
    lines.append("- Measured tells, Claude's rate over the writer's rate, family-wise interval:")
    for r in measured:
        ci = f", CI {r.ci[0]}-{r.ci[1]}" if r.ci else ""
        lines.append(f"  - {r.key}: {r.lean}x{ci}")
    allow = []
    own = reg.get("candidate_per_1k") or {}
    for phrase, t in p["tells"].items():
        if t.get("significant") and t.get("lean") and t["lean"] < 1 \
                and own.get(phrase, t["sterling_per_1k"]) > 0:
            allow.append((phrase, t["lean"]))
    allow.sort(key=lambda r: r[1])
    if allow:
        lines.append("- Phrases the corpus says are the writer's (the writer's rate over Claude's): "
                     + ", ".join(f"\"{ph}\" ({1 / max(lean, 1e-3):.0f}x)"
                                 for ph, lean in allow[:12]))
    if not reg.get("candidate_rates_measured", True):
        lines.append("- This register has no measured phrase rates of its own; "
                     "phrase verdicts fall back to the GitHub-wide corpus.")
    return "\n".join(lines)


def render(system, user):
    return system + "\n\n## Draft\n\n" + user.split("\n\n", 1)[-1]
