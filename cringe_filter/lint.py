"""The AI-cringe filter: deterministic tells, each labelled with its evidence.

Every rule names the candidate phrase it was measured as, and at lint time
the verdict for the requested context is read from the profile:

    measured    Claude's rate over Sterling's is significantly above 1 in
                this register (family-wise bootstrap interval excludes 1)
    preventive  no support in this register's data; kept because the
                registers the corpus covers thinly are where a model
                reaches for it; never rises above info severity
    contra      Sterling uses it as much or more; the rule is switched off

The verdicts come from the register's own measurements when it has any
signal for the phrase, and from the whole GitHub corpus otherwise, so a
word that is his in manuscripts and Claude's in replies is treated
differently in the two contexts without anyone hand-listing exceptions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import latex
from .bundle import profile
from .registers import resolve

# Below this ratio the point estimate says he uses it more than Claude,
# and there is no evidence for the rule even before significance is asked.
CONTRA_BELOW = 0.8
# Formatting rules only apply where his own rate for the marker is low;
# above this rate the structure is part of how he writes that register
# (headers in tutorials, bullets in his own repos, template headers in a
# bug report).
FORMAT_OWN_RATE_MAX = 3.0

# Formatting rule -> the mechanical marker that carries his own rate.
FORMAT_MARKER = {"bold-run": "bold_md_per_1k", "bold-lead-in": "bold_md_per_1k",
                 "md-header": "header_md_per_1k",
                 "bullet-line": "bullet_md_per_1k", "md-table": "table_md_per_1k",
                 "checkbox": "checkbox_md_per_1k"}


@dataclass
class Spec:
    key: str
    pattern: str
    family: str
    severity: str
    message: str
    candidate: str | None = None
    contexts: tuple | None = None
    flags: int = re.M


I = re.M | re.I

# Words after ", not" that make a concession or a hedge, not a correction.
_NOT_OK = (r"sure|yet|to mention|that|bad|necessarily|really|quite|much|"
           r"many|all|every|everything|always|entirely|exactly|too|so|as|"
           r"ideal|great|terrible|perfect|ready|urgent|required|needed|"
           r"working|sure yet|now|anymore|a big deal|a problem|an issue")
CONTRAST = {
    "X, not Y": (rf",\s+not\s+(?!(?:{_NOT_OK})\b)[^,.;:!?\n]{{1,60}}"
                 r"(?=[.;:!?)\n]|$)"),
    "dash/semicolon not Y": (r"(?:\s[—–]\s?|[—–]|\s-{1,2}\s|;\s)not\s+"
                             r"(?!(?:sure|yet|to mention)\b)\w"),
    "is what (cleft)": (r"\b(is|was|are|were|'s) what\s+"
                        r"(?!I\b|you\b|we\b|they\b|he\b|she\b|it\b|i\b)\w+"),
}

# Two patterns from the ME-EN-372 course repo's cringe filter that also
# separate Claude from him in the GitHub threads (contrast_family.py,
# COURSE). The others in that filter do not transfer: "in other words,"
# and "don't worry" are his in replies, whatever they are on a course page.
COURSE = {
    "heading then bold lead-in": r"^#{1,6} [^\n]+\n+\*\*[^*\n]{3,60}\*\*",
    "invented precision": (r"\b(?:takes? (?:about|roughly|only|just)?\s*(?:a|one|two|three|five|ten|\d+) (?:minute|second|hour)s?|"
                           r"a one-(?:sentence|line|paragraph) \w+)\b"),
}

# The rules Sterling and Kelvin Chow wrote for the Copilot coding agent in
# 2025 ("avoid sycophancy, favor objectiveness", "avoid patting yourself on
# the back", "comments should not leave a trace of the development
# process", "emoji and special symbols sparingly, if at all"), as the
# regexes scripts/voice/contrast_family.py measures (AGENT). Each is judged
# against Claude in the same threads and, where Claude gives no signal,
# against Copilot's replies in his repos.
AGENT = {
    "you're right (opener)": (r"(?:^|(?<=[.!?]\s))(?:Thanks[^.!?\n]{0,40}[.!]\s+)?"
                              r"(?:You'?re|You are|You were) (?:absolutely |completely |"
                              r"totally |exactly |quite |entirely )?(?:right|correct)\b"),
    "absolutely right": r"\b(?:absolutely|completely|totally|entirely) (?:right|correct)\b",
    "good catch / great question": r"\b(?:good|great|nice|excellent) (?:catch|question|point|call)\b",
    "acknowledged (opener)": r"(?:^|(?<=[.!?]\s))(?:Acknowledged|Understood)(?:[.!,:]|\s+-)",
    "apology": r"\b(?:I apologi[sz]e|(?:my )?apologies|I'?m sorry|sorry (?:for|about))\b",
    "promise (I will never/always)": r"\bI(?: will|'ll) (?:never|always|make sure|ensure|be sure)\b",
    "successfully": r"\bsuccessfully\b",
    "production-ready / fully verified": (r"\b(?:production[- ]ready|fully (?:functional|tested|verified|"
                                          r"working|operational|implemented)|thoroughly (?:tested|verified)|"
                                          r"works (?:perfectly|flawlessly))\b"),
    "significantly improved (own work)": (r"\b(?:significantly|greatly|dramatically|substantially) "
                                          r"(?:improved|expanded|enhanced|simplified)\b"),
    "Done. (opener)": r"(?:^|(?<=[.!?]\s))Done[.!](?=\s|$)",
    "per instructions / as requested": (r"\b(?:(?:as )?per|following) (?:your|the user'?s|custom|the custom|"
                                        r"my|the) (?:request|instructions?|guidelines)\b|"
                                        r"\bas (?:you )?(?:requested|instructed)\b"),
    "now + verb (change trace)": (r"\bnow (?:uses|includes|properly|correctly|focuses|contains|supports|"
                                  r"reads|matches|follows|fails|checks|asks|says|returns)\b"),
    "commit hash in parentheses": r"\((?:commit\s+)?[0-9a-f]{7,40}\)",
    "different approach": (r"\b(?:let me|let'?s|I'?ll|I will|I) (?:try|take|use) (?:a |an )?"
                           r"(?:different|another|alternative|simpler) approach\b"),
    "check glyph": r"[✓✔✗✘☑]",
    "spaced hyphen as dash": r"(?<=[A-Za-z0-9)\]'\"]) - (?=[A-Za-z(\"'])",
    "ALL-CAPS imperative": r"(?-i:\b(?:IMPORTANT|CRITICAL|NEVER|ALWAYS|MUST)\b)",
}
FAMILY_MESSAGE = {
    "claude5": "Claude 5-era tell (model-prose survey, 2026-09).",
    "significance": "Inflated-significance word. Say what it does instead.",
    "latinate": "Latinate verb where a plain one exists (use, help, start, "
                "try, show, cover).",
    "metaphor": "Metaphor noun that reads as generated prose.",
    "scaffold": "Discourse scaffolding. Delete it or start the sentence.",
}

SPECS = [
    Spec("em-dash", "—", "glyph", "error",
         "Em dash. Use a period, a colon, or commas.", "em dash"),
    Spec("en-dash", "–", "glyph", "error",
         "En dash. Write 'to' in prose, a plain hyphen in a label.", "en dash"),
    Spec("emoji-status", "[✅❌⚠\U0001F680\U0001F389✨\U0001F4A1\U0001F50D"
                         "\U0001F4CA\U0001F527\U0001F4E6]", "glyph", "error",
         "Status emoji.", "emoji status"),
    Spec("arrow-glyph", "→", "glyph", "warn",
         "Arrow glyph. Write the relation as words.", "arrow glyph"),

    # Not in proposals: his use \textbf and \emph at 2.5 to 3 times his
    # papers' rate, and the grant-writing slides he kept say to bold the
    # standout sentence of a section (registers.md, Proposal).
    Spec("bold-run", r"\*\*[^*\n]{1,80}\*\*", "formatting", "warn",
         "Bold emphasis.", "bold run",
         contexts=("github", "discussion", "third-party", "email", "message",
                   "linkedin", "tutorial", "paper", "any")),
    Spec("md-table", r"^[ \t]*\|.*\|[ \t]*$", "formatting", "warn",
         "Markdown table.", "markdown table",
         contexts=("github", "discussion", "third-party", "email",
                   "linkedin", "message", "any")),
    Spec("checkbox", r"^[ \t]*[-*] \[[ xX]\]", "formatting", "warn",
         "Checkbox list.", "checkbox list",
         contexts=("discussion", "email", "linkedin", "message", "tutorial",
                   "paper")),
    Spec("md-header", r"^#{2,3} ", "formatting", "warn",
         "Header in a short reply.", "H2/H3 header"),
    Spec("bullet-line", r"^[ \t]*[-*+] ", "formatting", "info",
         "Bullet list where he writes prose.", "bullet line"),
    Spec("bold-lead-in", r"^[ \t]*[-*] \*\*[^*\n]{1,60}\*\*:?", "formatting",
         "warn", "Bold lead-in bullet ('- **Label:** text').",
         "bold lead-in bullet"),

    Spec("isnt-x-its-y",
         r"\b(isn'?t|is not|it'?s not|that'?s not)\b[^.\n]{1,60}\bit'?s\b",
         "frame", "error", "The 'it isn't X, it's Y' frame. State Y and stop.",
         "isn't X it's Y"),
    Spec("no-x-no-y", r"\bno [a-z]+, no [a-z]+\b", "frame", "error",
         "The 'no X, no Y' cadence.", "no X, no Y"),
    Spec("what-makes", r"\bwhat makes (it|this|that|the)\b", "frame", "warn",
         "'What makes X ...' sets up a claim about significance.",
         "what makes X"),
    Spec("defn-frame", r"\b(This|That|It) is the\b(?! (same|only|one|first|"
                       r"last|case|file|repo|reason|link|list))", "frame",
         "info", "Definitional pronouncement frame.", "X is the Y (defn)"),
    Spec("here-is-the", r"\bhere'?s (the thing|what'?s|why|how it works)\b",
         "frame", "warn", "Explainer-voice opener.", "here's the thing"),
    Spec("not-just-but", r"\bnot (just|only|merely)\b[^.\n]{1,70}\b(but|it'?s)\b",
         "frame", "warn", "The 'not just X, but Y' frame. Say the thing once.",
         "not just X but Y"),
    # The corrective contrast, measured as a family in the same threads
    # (scripts/voice/contrast_family.py; patterns must stay identical).
    # He writes "X, not Y" too, mostly as an instruction ("an assert, not
    # an if"); Claude writes it to correct a reading nobody offered.
    Spec("x-not-y", CONTRAST["X, not Y"], "frame", "warn",
         "The 'X, not Y' correction. Keep it only if Y is something the "
         "reader actually believes; otherwise say what it is and stop.",
         "X, not Y", flags=I),
    Spec("dash-not-y", CONTRAST["dash/semicolon not Y"], "frame", "warn",
         "A dash or semicolon before 'not Y'. The same correction frame; "
         "state X and stop.", "dash/semicolon not Y", flags=I),
    Spec("heading-bold-lead-in", COURSE["heading then bold lead-in"],
         "formatting", "warn",
         "A heading followed by a bold lead-in that restates it.",
         "heading then bold lead-in"),
    Spec("invented-precision", COURSE["invented precision"], "frame", "warn",
         "Invented precision ('takes about a minute', 'a one-line summary'). "
         "Give the real figure or drop it.", "invented precision", flags=I),
    Spec("is-what-cleft", CONTRAST["is what (cleft)"], "frame", "warn",
         "'X is what did Y'. Put the doer first: 'the referrer unlocked it'.",
         "is what (cleft)", flags=I),
    Spec("rhetorical-q", r"^[ \t]*\*{0,2}(The (result|upshot|catch|problem|answer)|"
                         r"Why\b[^?\n]{0,40})\?", "frame", "info",
         "Rhetorical question as a section hook.", "the result?"),
    Spec("think-of-it-as", r"\bthink of it as\b", "frame", "warn",
         "Explainer metaphor opener.", "think of it as", flags=I),
    Spec("lets-dive-in", r"\b(let'?s|we'?ll) (dive|dig) in(to)?\b", "frame",
         "warn", "'Let's dive in.' Start with the content.", "let's dive in",
         flags=I),

    Spec("orders-of-magnitude",
         r"\b(thousands|millions|orders of magnitude|years (of|to)|overnight)"
         r"\b[^.\n]{0,50}\b(instead of|rather than|compared to|versus|vs\.?)\b",
         "overstatement", "info",
         "Magnitude comparison. He has walked these back by hand "
         "('Thousands is probably an overstatement').", None, flags=I),

    Spec("youre-right", AGENT["you're right (opener)"], "sycophancy", "error",
         "Agreement opener. Start with the answer or the change.",
         "you're right (opener)", flags=I),
    Spec("absolutely-right", AGENT["absolutely right"], "sycophancy", "error",
         "'Absolutely right'. Say what was wrong and what changed.",
         "absolutely right", flags=I),
    Spec("good-catch", AGENT["good catch / great question"], "sycophancy",
         "warn", "Praise for the question. Answer it.",
         "good catch / great question", flags=I),
    Spec("acknowledged", AGENT["acknowledged (opener)"], "sycophancy", "warn",
         "'Acknowledged.' Say what you did about it.",
         "acknowledged (opener)", flags=I),
    Spec("apology", AGENT["apology"], "sycophancy", "warn",
         "Apology. Name the mistake and the fix.", "apology", flags=I),
    Spec("promise", AGENT["promise (I will never/always)"], "sycophancy",
         "warn", "A promise about future behaviour. Show the fix.",
         "promise (I will never/always)", flags=I),
    Spec("successfully", AGENT["successfully"], "self-report", "warn",
         "'Successfully'. Say what ran and what it returned.", "successfully",
         flags=I),
    Spec("production-ready", AGENT["production-ready / fully verified"],
         "self-report", "error",
         "Readiness claim. Say what was tested, on what, and what was not.",
         "production-ready / fully verified", flags=I),
    Spec("praises-own-change", AGENT["significantly improved (own work)"],
         "self-report", "warn", "Praise for a change. Say what changed.",
         "significantly improved (own work)", flags=I),
    Spec("done-opener", AGENT["Done. (opener)"], "self-report", "info",
         "'Done.' opener. Lead with the result.", "Done. (opener)", flags=I),
    Spec("per-instructions", AGENT["per instructions / as requested"],
         "trace", "warn",
         "Trace of the request. Write for a reader who never saw it.",
         "per instructions / as requested", flags=I),
    Spec("change-trace", AGENT["now + verb (change trace)"], "trace", "warn",
         "Describes the text against an earlier version. Say what it does.",
         "now + verb (change trace)", flags=I),
    Spec("commit-in-parens", AGENT["commit hash in parentheses"], "trace",
         "warn", "Bare commit hash. Link it, or leave it out of a document.",
         "commit hash in parentheses", flags=I),
    Spec("different-approach", AGENT["different approach"], "trace", "warn",
         "Narrates a change of plan. Report what worked.",
         "different approach", flags=I),
    Spec("check-glyph", AGENT["check glyph"], "glyph", "error",
         "Check-mark glyph. Say it in words.", "check glyph"),
    Spec("spaced-hyphen", AGENT["spaced hyphen as dash"], "glyph", "warn",
         "Spaced hyphen used as a dash. Use a period, a colon, or commas.",
         "spaced hyphen as dash"),
    Spec("all-caps", AGENT["ALL-CAPS imperative"], "glyph", "warn",
         "All-caps emphasis.", "ALL-CAPS imperative"),
]

SCAFFOLD = [
    ("notably", "notably,", r"\bnotably,"),
    ("crucially", "crucially,", r"\bcrucially,"),
    ("importantly", "importantly,", r"\bimportantly,"),
    ("that-said", "that said,", r"\bthat said,"),
    ("ultimately", "ultimately,", r"\bultimately,"),
    ("overall", "overall,", r"\boverall,"),
    ("furthermore", "furthermore", r"\bfurthermore\b"),
    ("moreover", "moreover", r"\bmoreover\b"),
    ("additionally", "additionally", r"\badditionally\b"),
    ("in-conclusion", "in conclusion", r"\bin conclusion\b"),
    ("in-summary", "in summary", r"\bin summary\b"),
    ("in-essence", "in essence", r"\bin essence\b"),
    ("at-its-core", "at its core", r"\bat its core\b"),
    ("when-it-comes-to", "when it comes to", r"\bwhen it comes to\b"),
    ("in-the-realm-of", "in the realm of", r"\bin the (realm|world) of\b"),
    ("in-todays", "in today's", r"\bin today'?s\b"),
    ("the-key-is", "the key is", r"\bthe key (is|to)\b"),
    ("worth-noting", "it's worth noting", r"\bit'?s worth noting\b"),
    ("important-to", "it is important to", r"\bit is important to\b"),
    ("its-important-to", "it's important to", r"\bit'?s important to\b"),
]
SIGNIFICANCE = [
    ("crucial", "crucial", r"\bcrucial(ly)?\b"), ("vital", "vital", r"\bvital(ly)?\b"),
    ("pivotal", "pivotal", r"\bpivotal\b"), ("paramount", "paramount", r"\bparamount\b"),
    ("essential", "essential", r"\bessential(ly)?\b"),
    ("critical", "critical(adj)", r"\bcritical\b"),
    ("significant", "significant", r"\bsignificant(ly)?\b"),
    ("profound", "profound", r"\bprofound(ly)?\b"),
    ("remarkable", "remarkable", r"\bremarkable\b"),
    ("notable", "notable", r"\bnotabl[ey]\b"), ("powerful", "powerful", r"\bpowerful\b"),
    ("seamless", "seamless", r"\bseamless(ly)?\b"), ("robust", "robust", r"\brobust\b"),
    ("comprehensive", "comprehensive", r"\bcomprehensive(ly)?\b"),
    ("cutting-edge", "cutting-edge", r"\bcutting[- ]edge\b"),
    ("state-of-the-art", "state-of-the-art", r"\bstate[- ]of[- ]the[- ]art\b"),
    ("game-changer", "game-changer", r"\bgame[- ]chang(er|ing)\b"),
    ("revolutionize", "revolutionize", r"\brevolutioni[sz]e"),
    ("unlock", "unlock", r"\bunlock(s|ed|ing)?\b"),
    ("empower", "empower", r"\bempower(s|ed|ing)?\b"),
    ("harness", "harness(v)", r"\bharness(ed|ing)\b|\bharness(es)? (the|its|their|our|your|this|that|these|those|ai|llms?|machine)\b"),
    ("elevate", "elevate", r"\belevat(e|es|ed|ing)\b"),
    ("unparalleled", "unparalleled", r"\bunparalleled\b"),
    ("meticulous", "meticulous", r"\bmeticulous(ly)?\b"),
]
LATINATE = [
    ("utilize", "utilize", r"\butiliz(e|es|ed|ing|ation)\b"),
    ("leverage", "leverage(v)", r"\bleverag(e|es|ed|ing)\b"),
    ("facilitate", "facilitate", r"\bfacilitat(e|es|ed|ing|ion)\b"),
    ("ensure", "ensure", r"\bensur(e|es|ed|ing)\b"),
    ("enable", "enable", r"\benabl(e|es|ed|ing)\b"),
    ("commence", "commence", r"\bcommenc(e|es|ed|ing)\b"),
    ("endeavor", "endeavor", r"\bendeavou?r"), ("delve", "delve", r"\bdelve[sd]?\b"),
    ("underscore", "underscore", r"\bunderscor(e|es|ed|ing)\b"),
    ("showcase", "showcase", r"\bshowcas(e|es|ed|ing)\b"),
    ("streamline", "streamline", r"\bstreamlin(e|es|ed|ing)\b"),
    ("encompass", "encompass", r"\bencompass(es|ed|ing)?\b"),
]
METAPHOR = [(w, w, rf"\b{w}\b") for w in
            ("landscape", "realm", "journey", "tapestry", "testament",
             "cornerstone", "beacon", "gateway", "backbone", "ecosystem")]
# Claude 5-era vocabulary from the model-prose survey; measured, not assumed.
CLAUDE5 = [
    ("load-bearing", "load-bearing", r"\bload[- ]bearing\b"),
    ("seam", "seam(n)", r"\bseams?\b"), ("plainly", "plainly", r"\bplainly\b"),
    ("quietly", "quietly", r"\bquietly\b"),
    ("genuinely", "genuinely", r"\bgenuinely\b"),
    ("honestly", "honestly", r"\bhonestly\b"),
    ("vacuous", "vacuous", r"\bvacuous\b"),
    ("straightforward", "straightforward", r"\bstraightforward\b"),
    ("honest-take", "honest take", r"\bhonest take\b"),
    ("synthesize", "synthesize", r"\bsynthesi[sz]e[sd]?\b"),
]

for _family, _rows, _sev in (("scaffold", SCAFFOLD, "warn"),
                             ("significance", SIGNIFICANCE, "warn"),
                             ("latinate", LATINATE, "warn"),
                             ("metaphor", METAPHOR, "warn"),
                             ("claude5", CLAUDE5, "warn")):
    for _key, _cand, _pat in _rows:
        SPECS.append(Spec(_key, _pat, _family, _sev,
                          f"'{_cand}'. {FAMILY_MESSAGE[_family]}", _cand,
                          flags=I))


@dataclass
class Rule:
    key: str
    pattern: str
    severity: str
    message: str
    family: str
    candidate: str | None
    evidence: str
    lean: float | None
    ci: list | None
    flags: int


def verdict(spec, ctx):
    """(evidence, lean, ci) for one rule in one context."""
    p = profile()
    reg = p["registers"][ctx]
    if spec.candidate is None:
        return "preventive", None, None
    local = reg.get("vs_claude", {}).get(spec.candidate)
    own_rate = (reg.get("candidate_per_1k") or {}).get(spec.candidate, 0) or 0
    global_ = p["tells"].get(spec.candidate)
    if local and (local["significant"] or own_rate > 0):
        lean, ci, sig = local["lean"], local["ci"], local["significant"]
    elif global_:
        lean, ci, sig = global_["lean"], global_["ci"], global_["significant"]
    else:
        return copilot_verdict(spec)
    if lean is not None and lean <= CONTRA_BELOW:
        # Significantly his: off, whatever Copilot does. A lean his way
        # that the interval cannot tell from 1 lets Copilot's evidence
        # decide ("production-ready": 7 uses each for him and Claude,
        # 8.5 times his rate for Copilot).
        if not (ci and ci[1] < 1):
            cv = copilot_verdict(spec)
            if cv[0] == "copilot":
                return cv
        return "contra", lean, ci
    if sig and lean and lean > 1:
        return "measured", lean, ci
    return copilot_verdict(spec, lean, ci)


def copilot_verdict(spec, lean=None, ci=None):
    """Second reference: Copilot's replies in the same threads of his repos.

    Only consulted where Claude gives no signal either way. A pattern that
    Claude's text does not carry but Copilot's does is still a tell of an
    agent's draft; it is labelled as Copilot's and capped at warn."""
    cop = (profile().get("tells_copilot") or {}).get(spec.candidate)
    if cop and cop["significant"] and cop["lean"] and cop["lean"] > 1:
        return "copilot", cop["lean"], cop["ci"]
    return "preventive", lean, ci


def severity_overrides(ctx):
    """Severities set by the calibration step, if the bundle carries one.

    A rule's declared severity is a starting point; where the corpus has
    been linted document by document (scripts/voice/calibrate_linter.py),
    the measured false-positive rate on Sterling's own writing decides,
    and the profile records the result per context."""
    return (profile().get("severity_overrides") or {}).get(ctx, {})


def rules_for(context):
    """The rules that apply in a context, with their evidence resolved."""
    ctx = resolve(context)
    reg = profile()["registers"][ctx]
    overrides = severity_overrides(ctx)
    out = []
    for spec in SPECS:
        if spec.contexts and ctx not in spec.contexts:
            continue
        marker = FORMAT_MARKER.get(spec.key)
        if marker and (reg["mechanical"].get(marker) or 0) >= FORMAT_OWN_RATE_MAX:
            continue
        evidence, lean, ci = verdict(spec, ctx)
        if evidence == "contra":
            continue
        severity = spec.severity if evidence == "measured" else "info"
        if evidence == "measured":
            severity = overrides.get(spec.key, severity)
        elif evidence == "copilot":
            severity = "info" if spec.severity == "info" else "warn"
        out.append(Rule(spec.key, spec.pattern, severity, spec.message,
                        spec.family, spec.candidate, evidence,
                        round(lean, 2) if lean else None,
                        [round(x, 2) for x in ci] if ci else None, spec.flags))
    return out


DISABLE_FILE = re.compile(r"(cringe-lint|cringe-filter|voicekit):\s*disable-file")
KEYLIST = r"(?:\s+([\w-]+(?:\s*,\s*[\w-]+)*))?"
DISABLE_LINE = re.compile(r"(?:cringe-lint|cringe-filter|voicekit):\s*disable-line" + KEYLIST)
DISABLE_NEXT = re.compile(r"(?:cringe-lint|cringe-filter|voicekit):\s*disable-next-line" + KEYLIST)
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
CODE_BLOCK = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`\n]+`")
URL = re.compile(r"https?://\S+")
FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)


def maskable(text, is_latex=False):
    """Blank out code, URLs and front matter, preserving line positions.

    LaTeX gets its own mask instead of the Markdown one: its opening quotes
    are backticks, which the inline-code pattern would eat, and its em
    dashes are `---`, which only the LaTeX mask turns into the glyph the
    rules look for."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    text = URL.sub(blank, text)
    if is_latex:
        return latex.mask(text)
    text = FRONTMATTER.sub(blank, text)
    text = CODE_BLOCK.sub(blank, text)
    text = INLINE_CODE.sub(blank, text)
    return text


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def suppressions(text):
    out = {}
    for i, line in enumerate(text.split("\n"), start=1):
        for rx, target in ((DISABLE_LINE, i), (DISABLE_NEXT, i + 1)):
            m = rx.search(line)
            if m:
                keys = ({k.strip() for k in m.group(1).split(",")}
                        if m.group(1) else {"*"})
                out.setdefault(target, set()).update(keys)
    return out


def lint_text(text, context="any", path="<text>", budget_only=False):
    """Findings for one document: list of dicts, errors first."""
    if DISABLE_FILE.search(text):
        return []
    ctx = resolve(context)
    reg = profile()["registers"][ctx]
    masked = maskable(text, latex.looks_like_latex(text, path))
    supp = suppressions(text)
    findings = []

    if not budget_only:
        for rule in rules_for(ctx):
            for m in re.finditer(rule.pattern, masked, rule.flags):
                ln = line_of(text, m.start())
                at = supp.get(ln, set())
                if "*" in at or rule.key in at:
                    continue
                snippet = text[max(0, m.start() - 30):m.end() + 30]
                findings.append({
                    "file": path, "line": ln, "rule": rule.key,
                    "severity": rule.severity, "family": rule.family,
                    "message": rule.message, "lean": rule.lean,
                    "ci_familywise": rule.ci, "evidence": rule.evidence,
                    "match": " ".join(text[m.start():m.end()].split()).lower(),
                    "snippet": " ".join(snippet.split())[:110]})

    overrides = severity_overrides(ctx)
    words = len(masked.split())
    budget = reg["doc_words_budget"]
    if budget and words > budget:
        findings.append({
            "file": path, "line": 1, "rule": "too-long",
            "severity": overrides.get("too-long", "warn"),
            "family": "length", "evidence": "measured", "lean": None,
            "ci_familywise": None,
            "message": (f"{words} words. His median {reg['label'].lower()} "
                        f"is {reg['doc_words_median']} words and the budget "
                        f"is {budget}."),
            "snippet": ""})

    sent_p90 = reg.get("sent_words_p90") or 45
    prose_lines = [l for l in masked.split("\n")
                   if l.strip() and not re.match(r"\s*([-*+>|#]|\d+[.)])\s", l)]
    prose = re.sub(r"\s+", " ", " ".join(prose_lines))
    for s in SENT_SPLIT.split(prose):
        n = len(s.split())
        if n > sent_p90:
            idx = text.find(s.strip()[:40])
            findings.append({
                "file": path, "line": line_of(text, idx) if idx > 0 else 1,
                "rule": "long-sentence",
                "severity": overrides.get("long-sentence", "info"), "family": "length",
                "evidence": "measured", "lean": None, "ci_familywise": None,
                "message": f"{n}-word sentence; his p90 in this register is "
                           f"{sent_p90}.",
                "snippet": " ".join(s.split())[:110]})

    order = {"error": 0, "warn": 1, "info": 2}
    findings.sort(key=lambda f: (order[f["severity"]], f["line"]))
    return findings


def introduced(old_text, new_text, context="any", path="<text>"):
    """Findings in new_text that old_text did not already have.

    Agent revisions put the tells back: in the lab's repos, paragraphs an
    agent revised after a reviewer's comment came back with more em dashes
    (261 to 329), semicolons (371 to 470) and parentheses than they had
    (docs/voice/data/correction-pairs.json). Linting only what a revision
    added keeps a review round from reopening what the last one closed.
    A finding counts as old when the same rule matched the same text in
    the old version, however many lines it moved."""
    seen = {}
    for f in lint_text(old_text, context, path):
        k = (f["rule"], f.get("match") or f["snippet"])
        seen[k] = seen.get(k, 0) + 1
    out = []
    for f in lint_text(new_text, context, path):
        k = (f["rule"], f.get("match") or f["snippet"])
        if seen.get(k):
            seen[k] -= 1
            continue
        out.append(f)
    return out


def format_finding(f, color=True):
    colors = {"error": "\033[31m", "warn": "\033[33m", "info": "\033[36m"}
    c = colors[f["severity"]] if color else ""
    r = "\033[0m" if color else ""
    who = "Copilot " if f.get("evidence") == "copilot" else ""
    if f.get("lean") and f.get("ci_familywise"):
        lo, hi = f["ci_familywise"]
        tag = f" [{who}{f['lean']}x, CI {lo}-{hi}]"
    elif f.get("lean"):
        tag = f" [{f['lean']}x]"
    elif f.get("evidence") == "preventive":
        tag = " [preventive, no corpus support]"
    else:
        tag = ""
    line = (f"{f['file']}:{f['line']}: {c}{f['severity']}{r} "
            f"{f['rule']}{tag}: {f['message']}")
    if f.get("snippet"):
        line += f"\n    {f['snippet']}"
    return line
