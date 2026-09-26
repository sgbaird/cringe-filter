"""LaTeX input: the prose a reader of the typeset paper would see.

The rules and rates were measured on prose, and manuscripts reached the
corpus as detexed text (scripts/voice/fetch_manuscripts.py). A .tex file
handed to the linter as it is reads differently: `---` is an em dash in
the PDF but not to a pattern looking for the glyph, a `%` comment reads
as a sentence, and `\\cite{...}` keys count as words. On the .tex files
of his first-author papers the linter found 15 em dashes, all typed as
the glyph, against 96 once `---` counts, and reported commented-out
paragraphs as long sentences (docs/voice/research/technical-writing.md).

`mask` keeps every character position, so a finding still names the right
line: markup becomes spaces, `---` becomes an em dash and `--` an en dash,
and a section title gets a full stop so it does not run into the next
sentence. What it drops follows the corpus detex: the preamble, comments,
math, tables, code listings, footnotes and reference commands; the
text of formatting commands and captions stays.
"""
import re

_COMMANDS = re.compile(
    r"\\(documentclass|begin\{document\}|section\*?\{|subsection\*?\{|"
    r"cite[pt]?\{|citep?\*?\{|ref\{|cref\{|eqref\{|label\{|textbf\{|emph\{|"
    r"begin\{(itemize|enumerate|equation|figure|table|abstract)\}|item\b)")

# Environments whose content is not prose.
_DROP_ENVS = ("equation", "align", "alignat", "gather", "multline", "eqnarray",
              "displaymath", "math", "tabular", "tabularx", "longtable",
              "tikzpicture", "lstlisting", "verbatim", "minted", "algorithm",
              "algorithmic", "thebibliography", "filecontents")

# Commands whose arguments are keys, paths or settings rather than prose.
_KEYED = (r"cite\w*|parencite|textcite|autocite|footcite|ref|eqref|autoref|"
          r"cref|Cref|pageref|nameref|label|url|includegraphics|input|include|"
          r"bibliography|bibliographystyle|addbibresource|usepackage|"
          r"RequirePackage|documentclass|newcommand|renewcommand|providecommand|"
          r"DeclareMathOperator|setlength|addtolength|vspace|hspace|"
          r"graphicspath|hypersetup|newacronym|newglossaryentry|"
          r"setcounter|bibitem")

_HEADING = re.compile(r"\\(part|chapter|section|subsection|subsubsection|"
                      r"paragraph|subparagraph)\*?(\[[^\]]*\])?\{([^{}]*)\}")


def looks_like_latex(text, path=None):
    """True for a .tex path, or text with enough LaTeX markup to be one."""
    if path and str(path).lower().endswith((".tex", ".ltx")):
        return True
    return len(_COMMANDS.findall(text or "")) >= 3


def _blank(s):
    return re.sub(r"[^\n]", " ", s)


def mask(text):
    """LaTeX source to prose, character positions unchanged."""
    def sub(pattern, repl, s, flags=0):
        return re.sub(pattern, repl, s, flags=flags)

    blank = lambda m: _blank(m.group(0))  # noqa: E731

    # The preamble is packages and metadata.
    m = re.search(r"\\begin\{document\}", text)
    if m:
        text = _blank(text[:m.end()]) + text[m.end():]
    text = sub(r"(?<!\\)%[^\n]*", blank, text)                     # comments
    for env in _DROP_ENVS:
        text = sub(r"\\begin\{" + env + r"\*?\}.*?\\end\{" + env + r"\*?\}",
                   blank, text, re.S)
    text = sub(r"(?<!\\)\$\$.*?(?<!\\)\$\$", blank, text, re.S)     # display math
    text = sub(r"\\\[.*?\\\]", blank, text, re.S)
    text = sub(r"\\\(.*?\\\)", blank, text, re.S)
    text = sub(r"(?<!\\)\$(?:[^$\n]|\n(?!\s*\n)){1,400}?(?<!\\)\$", blank, text)
    # \href{url}{text}: the url goes, the text stays.
    text = sub(r"\\href\{[^{}]*\}", blank, text)
    text = sub(r"\\(" + _KEYED + r")\*?(\s*\[[^\]]*\])*(\s*\{[^{}]*\})+", blank, text)
    # A footnote read in place would run into its host sentence; the corpus
    # detex dropped them too. Twice, for one level of nested braces.
    for _ in range(2):
        text = sub(r"\\footnote(mark|text)?(\[[^\]]*\])?\{[^{}]*\}", blank, text)
    # A heading keeps its words and ends like a sentence.
    text = _HEADING.sub(lambda m: _blank(m.group(0)[:m.start(3) - m.start(0)])
                        + m.group(3) + ".", text)
    text = sub(r"(?<!-)---(?!-)", "\u2014  ", text)
    text = sub(r"(?<![-!])--(?![->])", "\u2013 ", text)
    text = sub(r"\\\\(\[[^\]]*\])?", blank, text)                   # line breaks
    text = sub(r"\\([%&$#_{}])", r" \1", text)                      # escaped chars
    text = sub(r"\\[,;:! ]", "  ", text)                            # spacing
    text = sub(r"\\(begin|end)\{[^{}]*\}(\[[^\]]*\]|\{[^{}]*\})*", blank, text)
    text = sub(r"\\[A-Za-z@]+\*?(\[[^\]]*\])?", blank, text)        # other commands
    text = sub(r"[{}~]", " ", text)
    return text


def to_prose(text):
    """Compact prose for counting: the mask with its padding collapsed."""
    out = mask(text)
    out = re.sub(r"[ \t]+", " ", out)
    out = re.sub(r" +([.,;:!?])", r"\1", out)
    out = re.sub(r"\n[ \t]*\n\s*", "\n\n", out)
    return out.strip()


_CITE = re.compile(r"\\(?:cite\w*|parencite|textcite|autocite|footcite)\*?"
                   r"(?:\s*\[[^\]]*\])*\s*\{([^{}]*)\}")
_REF = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref|pageref|nameref|label)\*?"
                  r"\s*\{([^{}]*)\}")
_MATH = re.compile(r"(?<!\\)\$(?:[^$\n]|\n(?!\s*\n)){1,400}?(?<!\\)\$")


def immutables(text):
    """Citation keys, reference and label keys, and inline math spans: what
    a style rewrite of a LaTeX draft has no business changing."""
    def keys(rx):
        out = set()
        for m in rx.finditer(text):
            out.update(k.strip() for k in m.group(1).split(",") if k.strip())
        return sorted(out)

    return {"citations": keys(_CITE), "refs": keys(_REF),
            "math": sorted({" ".join(m.group(0).split()) for m in _MATH.finditer(text)})}
