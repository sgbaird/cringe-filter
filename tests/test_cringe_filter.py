"""Smoke tests. Run with `python -m unittest discover tests`
or `pytest tests`."""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from cringe_filter import lint_text, rules_for, score_text, build_prompt  # noqa: E402
from cringe_filter.registers import infer_context, resolve, contexts  # noqa: E402
from cringe_filter.bundle import profile, exemplars  # noqa: E402
from cringe_filter import markers  # noqa: E402

CLAUDE_ISH = """## Summary

**Done** — the pipeline now runs end to end. Here's what changed:

- ✅ Added the parser — it isn't a hack, it's the real fix
- ✅ Updated the docs

| Step | Status |
| --- | --- |
| parse | done |

This is the cornerstone of the new approach → leverage it comprehensively."""

STERLING_ISH = ("Hmm, not sure this is the right call. Could you check whether "
                "the parser might be dropping the last row? I think it's "
                "probably fine for now, but let me know what you find.")


class Lint(unittest.TestCase):
    def test_em_dash_is_error_everywhere(self):
        for ctx in ("github", "email", "linkedin", "paper", "tutorial"):
            f = lint_text("A thing — another thing.", ctx)
            self.assertTrue(any(x["rule"] == "em-dash" and
                                x["severity"] == "error" for x in f), ctx)

    def test_headers_scoped_by_register(self):
        text = "## Results\n\nSome prose here."
        self.assertTrue(any(x["rule"] == "md-header" for x in lint_text(text, "github")))
        self.assertFalse(any(x["rule"] == "md-header" for x in lint_text(text, "tutorial")))
        self.assertFalse(any(x["rule"] == "md-header" for x in lint_text(text, "third-party")))

    def test_lint_flags_the_tables_the_prompt_forbids(self):
        for ctx in ("github", "discussion", "third-party", "email", "message",
                    "linkedin", "tutorial"):
            system, _ = build_prompt("x", ctx)
            if "no tables" in system or "without headers, tables" in system:
                self.assertIn("md-table", {r.key for r in rules_for(ctx)}, ctx)

    def test_suppression(self):
        text = "A thing — another. <!-- cringe-filter: disable-line em-dash -->"
        self.assertFalse(any(x["rule"] == "em-dash" for x in lint_text(text, "github")))
        text = "<!-- cringe-lint: disable-file -->\nA thing — another."
        self.assertEqual(lint_text(text, "github"), [])

    def test_suppression_shown_in_code_does_not_apply(self):
        # A README that documents the syntax must still be linted.
        text = ("Skip a file with:\n\n```markdown\n"
                "<!-- cringe-filter: disable-file -->\n```\n\nA thing — another.")
        self.assertTrue(any(x["rule"] == "em-dash" for x in lint_text(text, "tutorial")))
        text = "Use `<!-- cringe-filter: disable-line -->`. A thing — another."
        self.assertTrue(any(x["rule"] == "em-dash" for x in lint_text(text, "tutorial")))
        text = "A thing --- another. % cringe-filter: disable-line em-dash"
        self.assertFalse(any(x["rule"] == "em-dash"
                             for x in lint_text(text, "paper", "draft.tex")))

    def test_readme_passes_its_own_linter(self):
        root = os.path.dirname(HERE)
        with open(os.path.join(root, "README.md"), encoding="utf-8") as f:
            text = f.read()
        found = lint_text(text, "tutorial", "README.md")
        self.assertEqual([x for x in found if x["severity"] != "info"], [])
        # Linted, not skipped: a tell added at the end is still found.
        found = lint_text(text + "\nA thing — another.\n", "tutorial", "README.md")
        self.assertTrue(any(x["rule"] == "em-dash" for x in found))

    def test_long_sentence_stays_in_its_paragraph(self):
        words = " ".join(["word"] * 34)  # the tutorial p90 is 35
        # A heading, or a line that introduces a code block, is not part of
        # the sentence after it.
        text = (f"## A heading of six words\n\n{words}.\n\n"
                f"Run this:\n\n```\nls\n```\n\n{words}.")
        self.assertFalse([x for x in lint_text(text, "tutorial")
                          if x["rule"] == "long-sentence"])
        # Masked inline code does not lose the line.
        text = f"Short.\n\nThen `run it` and {words} {words}."
        f = [x for x in lint_text(text, "tutorial") if x["rule"] == "long-sentence"]
        self.assertEqual([x["line"] for x in f], [3])
        self.assertIn("`run it`", f[0]["snippet"])

    def test_quoted_pattern_is_a_mention(self):
        text = ("Avoid the \"it isn't X, it's Y\" frame and the “X, not Y” "
                "correction.")
        rules = {x["rule"] for x in lint_text(text, "tutorial")}
        self.assertFalse(rules & {"isnt-x-its-y", "x-not-y"}, rules)
        rules = {x["rule"] for x in lint_text("It isn't a hack, it's the real fix.",
                                              "tutorial")}
        self.assertIn("isnt-x-its-y", rules)

    def test_repeated_phrase(self):
        text = ("The score is a ranking of what to fix, not a probability. "
                "Read it as a ranking of what to fix, not as a verdict.")
        f = [x for x in lint_text(text, "tutorial") if x["rule"] == "repeated-phrase"]
        self.assertEqual([(x["match"], x["severity"]) for x in f],
                         [("a ranking of what to fix, not", "info")])
        # Six words, or seven with a sentence end inside, are not a repeat.
        text = ("We ran it on the Pi today. We ran it on the Pi. Then "
                "it failed. Then it failed again and again.")
        self.assertFalse([x for x in lint_text(text, "tutorial")
                          if x["rule"] == "repeated-phrase"])
        # A repeat that overlaps itself is one finding, not one per word.
        f = [x for x in lint_text("ha " * 30, "tutorial") if x["rule"] == "repeated-phrase"]
        self.assertEqual(len(f), 1)

    def test_length_budget(self):
        long = " ".join(["word"] * 400) + "."
        self.assertTrue(any(x["rule"] == "too-long" for x in lint_text(long, "github")))
        self.assertFalse(any(x["rule"] == "too-long" for x in lint_text(long, "tutorial")))

    def test_contra_rules_are_off(self):
        # "ensure" runs higher in the writer's prose than in Claude's; it must not fire.
        keys = {r.key for r in rules_for("github")}
        self.assertNotIn("ensure", keys)
        self.assertIn("em-dash", keys)

    def test_preventive_never_above_info(self):
        for r in rules_for("github"):
            if r.evidence == "preventive":
                self.assertEqual(r.severity, "info", r.key)

    def test_code_is_masked(self):
        f = lint_text("Run `a — b` and\n```\nx — y\n```\n", "github")
        self.assertFalse(any(x["rule"] == "em-dash" for x in f))

    def test_list_findings_name_the_item_line(self):
        # A blank line before a list used to be reported as the item's line.
        text = "Intro.\n\n- **Label:** text\n\n| a | b |\n"
        lines = {(x["rule"], x["line"]) for x in lint_text(text, "github")}
        self.assertIn(("bold-lead-in", 3), lines)
        self.assertIn(("md-table", 5), lines)


class Score(unittest.TestCase):
    def test_direction(self):
        c = score_text(CLAUDE_ISH, "github")
        s = score_text(STERLING_ISH, "github")
        self.assertGreater(c["log_odds"], 0)
        self.assertLess(s["log_odds"], 0)
        self.assertGreater(c["log_odds"], s["log_odds"])
        self.assertFalse(c["calibrated"])

    def test_exemplars_read_like_him(self):
        n_like = 0
        bank = exemplars("github-short.md")
        for e in bank:
            if score_text(e["text"], "github")["log_odds"] < 0:
                n_like += 1
        self.assertGreaterEqual(n_like, len(bank) * 0.7)

    def test_delta_direction_on_banks(self):
        from cringe_filter.bundle import profile
        if not profile().get("mfw"):
            self.skipTest("bundle built without the MFW profile")
        bank = exemplars("github-long.md")
        closer = sum(1 for e in bank
                     if score_text(e["text"], "github")["delta"]["closer_to"] == "register")
        self.assertGreaterEqual(closer, len(bank) * 0.6)
        d = score_text(CLAUDE_ISH, "github")["delta"]
        self.assertEqual(d["n_features"], 150)
        self.assertGreater(d["n_tokens"], 10)

    def test_empty(self):
        self.assertEqual(score_text("", "github")["verdict"], "empty")

    def test_delta_tie_and_writer_wording(self):
        from cringe_filter.score import burrows_delta, format_score
        mfw = {"words": ["the"], "pooled_mean": [0.0], "pooled_std": [1.0]}
        d = burrows_delta("the cat", {"mfw_mean": [490.0]}, {"mfw_mean": [510.0]}, mfw)
        self.assertEqual((d["to_register"], d["to_claude"], d["closer_to"]),
                         (10.0, 10.0, "tie"))
        r = score_text(STERLING_ISH, "github")
        self.assertEqual(r["verdict"], "reads like the writer")
        self.assertNotIn("sterling", json.dumps(r))
        r["delta"] = d
        self.assertIn("(a tie)", format_score(r))


class Prompt(unittest.TestCase):
    def test_contains_exemplar_and_label(self):
        system, user = build_prompt("Some text.", "github")
        self.assertIn("Examples of human writing", system)
        self.assertIn("em dash", system.lower())
        self.assertIn("Rewrite this draft", user)
        # Examples come before the rules, and the model prompt carries no
        # rates or intervals (those go in the evidence appendix).
        self.assertLess(system.index("Examples of human writing"), system.index("Priorities"))
        self.assertNotRegex(system, r"CI \d")
        self.assertLess(len(system.split()), 1200)
        _, _, evidence = build_prompt("Some text.", "github", with_evidence=True)
        self.assertIn("em-dash", evidence)

    def test_paper_has_no_latinate_rule(self):
        system, _ = build_prompt("x", "paper")
        self.assertNotIn("'leverage'", system)

    def test_small_words_line(self):
        from cringe_filter.prompt import build_prompt
        s, _ = build_prompt("x", "github")
        line = next(l for l in s.split("\n") if "Small words" in l)
        self.assertIn("Talk to the people in the thread", line)
        self.assertIn('"we"', line)
        self.assertNotRegex(line.split(". ", 1)[1], r"\d")  # no rates
        s, _ = build_prompt("x", "paper")
        self.assertNotIn("Talk to the people", s)
        s, _ = build_prompt("x", "github", small_words=False)
        self.assertNotIn("Small words", s)

    def test_notes_are_whole_sentences_without_rates(self):
        from cringe_filter.prompt import plain_note
        self.assertEqual(plain_note("First person, heavily. 25.4 per 1000 "
                                    "words. Do not write as a lab."),
                         "First person, heavily. Do not write as a lab.")
        # A pronoun whose referent was the dropped sentence goes with it.
        self.assertEqual(plain_note("Sign-offs: Thanks (21). Do not use it."), "")
        # Never split inside a quotation.
        self.assertEqual(plain_note('Few bullets. "Tone it down. They stay." '
                                    '5.2 per 1000 words.'),
                         'Few bullets. "Tone it down. They stay."')
        for ctx in ("github", "third-party", "email", "linkedin", "tutorial"):
            system, _ = build_prompt("Some text.", ctx)
            notes = system.split("## Notes for this register")[-1].split("\n\n")[0]
            for line in notes.split("\n"):
                if line.startswith("- "):
                    self.assertRegex(line, r"[.!?\"')]$", (ctx, line))
                    self.assertNotIn("per 1000", line, (ctx, line))


class Structure(unittest.TestCase):
    TEXT = ("I think we could try a smaller batch. The parser drops the last "
            "row: see the log. Can you check it?\n\n"
            "Also, we need to rerun it.\n\n"
            "- first item\n- second item\n\n"
            "## Results\n\nThree runs passed; one failed (timeout).")

    def test_measure(self):
        from cringe_filter.structure import measure
        c = measure(self.TEXT)
        self.assertEqual(c["sentences"], 5)         # lists and headers are not prose
        self.assertEqual(c["person_open"], 2)       # "I think", "Also, we"
        self.assertEqual(c["determiner_open"], 1)   # "The parser"
        self.assertEqual(c["number_open"], 1)       # "Three runs"
        self.assertEqual(c["adverb_open"], 1)       # "Also,"
        self.assertEqual(c["question"], 1)
        self.assertEqual(c["modal"], 2)             # could, can
        self.assertEqual(c["to_verb"], 1)           # to rerun
        self.assertEqual(c["colon"], 1)
        self.assertEqual(c["semicolon"], 1)
        self.assertEqual(c["paren"], 1)
        self.assertEqual(c["prose_paragraphs"], 3)
        self.assertEqual(c["one_sentence_paragraphs"], 2)
        self.assertEqual(c["list_words"], 8)        # two items and a header, markers included

    def test_colon_blocks(self):
        from cringe_filter.structure import colon_blocks, measure, rates
        text = ("Run this:\n\n```bash\nls\n```\n\n**Changes:**\n- one\n- two\n"
                "  wrapped\n\nSome prose.\n\n| a | b |\n| - | - |\n")
        self.assertEqual(colon_blocks(text), (3, 2))
        self.assertEqual(rates(measure(text))["colon_block"], 0.6667)

    def test_colon_share_replaces_the_per_word_row(self):
        import copy
        from cringe_filter import bundle
        text = "Run this:\n\n```\nls\n```\n\nThen check the log.\n\n- one\n- two\n"
        before = {f["feature"] for f in score_text(text, "github")["features"]}
        self.assertIn("colon before block", before)
        # A rebuild that measures the share carries it for both sides.
        p = bundle.profile()
        saved = copy.deepcopy(p)
        try:
            p["registers"]["github"]["structure"]["rates"]["colon_block"] = 0.5
            p["reference"]["structure"]["rates"]["colon_block"] = 0.9
            feats = {f["feature"]: f for f in score_text(text, "github")["features"]}
        finally:
            p.clear()
            p.update(saved)
        self.assertNotIn("colon before block", feats)
        row = feats["lists, tables and code blocks a colon introduces"]
        self.assertEqual((row["n"], row["of"], row["unit"]), (1, 2, "per 1000 blocks"))

    def test_prompt_line_is_default_and_data_driven(self):
        s, _ = build_prompt("x", "github", structure=False)
        self.assertNotIn("Make a person the subject", s)
        s, _ = build_prompt("x", "github")
        line = next(l for l in s.split("\n") if "Make a person the subject" in l)
        self.assertNotRegex(line, r"\d\.\d")  # no rates
        self.assertNotIn("I ran it on the Pi", line)  # wording 2 is the default
        s, _ = build_prompt("x", "github", structure=1)
        self.assertIn("I ran it on the Pi", s)  # round two's tested wording, kept
        # No structure rates for email (its text never reaches the runner),
        # so no structure line.
        s, _ = build_prompt("x", "email", structure=True)
        self.assertNotIn("Make a person the subject", s)

    def test_score_reads_structure(self):
        c = score_text("The parser drops the last row: see the log. The fix is "
                       "in the second commit. Three files changed.", "github")
        s = score_text("I think we could try a smaller batch. Can you check "
                       "whether we need to rerun it?", "github")
        cs = sum(f["log_odds"] for f in c["features"] if f["kind"] == "structure")
        ss = sum(f["log_odds"] for f in s["features"] if f["kind"] == "structure")
        self.assertGreater(cs, 0)
        self.assertLess(ss, 0)
        e = score_text("The parser drops the last row.", "email")
        self.assertFalse([f for f in e["features"] if f["kind"] == "structure"])


class Contexts(unittest.TestCase):
    def test_aliases(self):
        self.assertEqual(resolve("dm"), "message")
        self.assertEqual(resolve("docs"), "tutorial")
        self.assertEqual(resolve("bug-report"), "third-party")
        with self.assertRaises(ValueError):
            resolve("nonsense-context")

    def test_infer(self):
        self.assertEqual(infer_context("https://github.com/sgbaird/cringe-filter/issues/1"), "github")
        self.assertEqual(infer_context("https://github.com/pytorch/pytorch/issues/1"), "third-party")
        self.assertEqual(infer_context("https://github.com/AccelerationConsortium/x/discussions/3"), "discussion")
        self.assertEqual(infer_context("https://www.linkedin.com/posts/x"), "linkedin")
        self.assertEqual(infer_context("docs/index.md"), "tutorial")

    def test_bundle_is_complete(self):
        p = profile()
        for ctx in ("github", "discussion", "third-party", "email", "message",
                    "linkedin", "tutorial", "paper", "any"):
            self.assertIn(ctx, p["registers"], ctx)
        self.assertGreater(len(p["tells"]), 90)
        self.assertTrue(contexts())

    def test_outside_profile_brings_its_exemplars(self):
        import shutil
        import tempfile
        from cringe_filter import bundle
        tmp = tempfile.mkdtemp()
        try:
            shutil.copy(os.path.join(bundle.DATA_DIR, "profile.json"), tmp)
            os.mkdir(os.path.join(tmp, "exemplars"))
            with open(os.path.join(tmp, "exemplars", "github-short.md"), "w") as f:
                f.write("## mine\n\n> Could you check the second run?\n")
            os.environ["CRINGE_FILTER_PROFILE"] = os.path.join(tmp, "profile.json")
            bundle.profile.cache_clear()
            bundle.exemplars.cache_clear()
            self.assertEqual([e["heading"] for e in exemplars("github-short.md")], ["mine"])
            # A bank the outside profile does not carry falls back to the package.
            self.assertTrue(exemplars("github-long.md"))
        finally:
            os.environ.pop("CRINGE_FILTER_PROFILE", None)
            bundle.profile.cache_clear()
            bundle.exemplars.cache_clear()
            shutil.rmtree(tmp)


class Preserve(unittest.TestCase):
    def test_dropped_tokens_are_named(self):
        from cringe_filter.preserve import check, immutables
        src = ("See https://example.com/a and `foo_bar` in src/x.py; 3 runs, "
               "42% done, 1,234 rows.\n```\npip install x\n```\n")
        im = immutables(src)
        self.assertIn("https://example.com/a", im["urls"])
        self.assertIn("foo_bar", im["code"])
        self.assertIn("src/x.py", im["paths"])
        self.assertIn("1234", im["numbers"])
        good = ("Three runs are 42% done with 1,234 rows; see "
                "https://example.com/a, `foo_bar` and src/x.py.\n```\npip install x\n```")
        self.assertEqual(check(src, good)["n_missing"], 0)
        bad = "Some runs are done. See src/x.py."
        r = check(src, bad)
        self.assertIn("urls", r["missing"])
        self.assertIn("blocks", r["missing"])
        self.assertLess(r["retained"], 0.6)

    def test_slashed_words_are_not_paths(self):
        from cringe_filter.preserve import check, immutables
        src = ("Every diameter at/under 20 mm, under argon/atmosphere, and/or "
               "plug stock from sgbaird/cringe-filter, per docs/voice/README.md "
               "and the page/RSS/oEmbed routes.")
        self.assertEqual(immutables(src)["paths"],
                         ["docs/voice/README.md", "sgbaird/cringe-filter"])
        ok = ("Per docs/voice/README.md and the page, RSS and oEmbed routes, every "
              "diameter at or under 20 mm, in an argon atmosphere, or plug stock "
              "from sgbaird/cringe-filter")
        self.assertEqual(check(src, ok)["n_missing"], 0)


LATEX = r"""\documentclass{article}
\usepackage{amsmath}
\begin{document}
\section{Introduction}
We compare three interpolation methods---GPR, IDW and
barycentric---against prior work \cite{baird2021,banadaki2016}.
% An old draft sentence---it should never be linted.
The error drops by 12\% for $n = 50000$ points (\cref{fig:parity}).
\begin{equation}
  a -- b --- c
\end{equation}
\end{document}
"""


class Latex(unittest.TestCase):
    def test_mask_keeps_positions_and_finds_dashes(self):
        from cringe_filter import latex
        m = latex.mask(LATEX)
        self.assertEqual(len(m), len(LATEX))
        self.assertEqual(m.count("\n"), LATEX.count("\n"))
        self.assertNotIn("baird2021", m)
        self.assertNotIn("old draft", m)
        self.assertNotIn("usepackage", m)
        self.assertIn("—", m)

    def test_lint_sees_latex_em_dashes_on_their_lines(self):
        f = lint_text(LATEX, "paper", "draft.tex")
        dashes = [x["line"] for x in f if x["rule"] == "em-dash"]
        # Two in the prose on lines 5 and 6; none from the comment or the
        # equation.
        self.assertEqual(sorted(dashes), [5, 6])

    def test_tex_path_implies_paper(self):
        from cringe_filter.cli import main
        import tempfile
        import io
        import contextlib
        with tempfile.NamedTemporaryFile("w", suffix=".tex", delete=False) as fh:
            fh.write(LATEX)
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                main(["lint", "--no-color", fh.name])
        finally:
            os.unlink(fh.name)
        self.assertIn("(context: paper)", out.getvalue())

    def test_dropped_citations_and_refs_are_named(self):
        from cringe_filter.preserve import check
        rewrite = ("We compare GPR, IDW and barycentric interpolation against "
                   "prior work. Error drops by 12% for $n = 50000$ points.")
        r = check(LATEX, rewrite)
        self.assertEqual(r["missing"].get("citations"), ["baird2021", "banadaki2016"])
        self.assertEqual(r["missing"].get("refs"), ["fig:parity"])
        kept = (r"We compare GPR, IDW and barycentric interpolation against prior "
                r"work \cite{baird2021, banadaki2016}. Error drops by 12\% for "
                r"$n = 50000$ points (\cref{fig:parity}).")
        self.assertEqual(check(LATEX, kept)["n_missing"], 0)

    def test_score_ignores_markup(self):
        r = score_text(LATEX, "paper")
        self.assertLess(r["words"], 45)

    def test_prompt_asks_to_keep_latex(self):
        system, _ = build_prompt(LATEX, "paper")
        self.assertIn(r"\cite", system)


class Rewrite(unittest.TestCase):
    def test_with_fake_client(self):
        from cringe_filter.rewrite import rewrite

        class Block:
            type = "text"

            def __init__(self, t):
                self.text = t

        class Msg:
            stop_reason = "end_turn"

            def __init__(self, t):
                self.content = [Block(t)]

        class Stream:
            def __init__(self, t):
                self.t = t

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def get_final_message(self):
                return Msg(self.t)

        class Messages:
            calls = []

            def stream(self, **kw):
                Messages.calls.append(kw)
                # First answer keeps an em dash so the revision pass runs.
                return Stream("Fixed — done." if len(Messages.calls) == 1
                              else "Fixed. Done.")

        class Client:
            messages = Messages()

        r = rewrite("**Bold** — text", "github", client=Client())
        self.assertEqual(r["passes"], 2)
        self.assertEqual(r["text"], "Fixed. Done.")
        self.assertIn("preservation", r)
        # The revision turn names the lint finding.
        self.assertIn("em-dash", Messages.calls[1]["messages"][-1]["content"])
        self.assertEqual(Messages.calls[0]["model"], "claude-opus-5")
        self.assertIn("anthropic-beta", Messages.calls[0]["extra_headers"])


    def test_length_alone_does_not_trigger_a_revision(self):
        from cringe_filter.rewrite import rewrite

        long_answer = "Checked the link. " * 80

        class Block:
            type = "text"
            text = long_answer

        class Msg:
            stop_reason = "end_turn"
            content = [Block()]

        class Stream:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def get_final_message(self):
                return Msg()

        class Messages:
            calls = 0

            def stream(self, **kw):
                Messages.calls += 1
                return Stream()

        class Client:
            messages = Messages()

        r = rewrite("Checked the link.", "github", client=Client())
        self.assertEqual(r["passes"], 1)
        self.assertEqual(Messages.calls, 1)
        self.assertIn("too-long", {f["rule"] for f in r["findings"]})

class FormalContexts(unittest.TestCase):
    """Papers and proposals are contrasted with Claude's scientific prose,
    not with its GitHub comments, and proposals have a register of their
    own (docs/voice/research/technical-writing.md, second pass)."""

    def test_proposal_is_its_own_context(self):
        self.assertEqual(resolve("proposal"), "proposal")
        self.assertEqual(resolve("grant"), "proposal")
        self.assertEqual(resolve("manuscript"), "paper")
        self.assertEqual(infer_context("drafts/proposal.tex"), "proposal")
        self.assertEqual(infer_context("paper/main.tex"), "paper")

    def test_formal_contexts_use_the_scientific_reference(self):
        from cringe_filter.bundle import reference
        self.assertEqual(reference("paper").get("name"), "claude_paper")
        self.assertEqual(reference("proposal").get("name"), "bot_proposals")
        self.assertEqual(reference("github").get("name"), "claude_github")

    def test_paper_prompt_is_not_conversational(self):
        system, _ = build_prompt("We trained the model.", "paper")
        self.assertNotIn("Lead with the answer", system)
        self.assertNotIn("ask it as a question", system)
        self.assertIn("## Examples of human writing", system)


class Sync(unittest.TestCase):
    def test_markers_match_pipeline(self):
        """The bundled patterns must equal the pipeline's, or rates drift."""
        root = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
        src = os.path.join(root, "scripts", "voice", "analyze_corpus.py")
        if not os.path.exists(src):
            self.skipTest("not running inside the repository")
        sys.path.insert(0, os.path.dirname(src))
        import analyze_corpus  # noqa: E402
        a = {k: (p.pattern, p.flags) for k, p in analyze_corpus.PATTERNS.items()}
        b = {k: (p.pattern, p.flags) for k, p in markers.PATTERNS.items()}
        self.assertEqual(a, b)

    def test_contrast_rules_match_measurement(self):
        """The contrast rules must be the patterns contrast_family.py measured."""
        root = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
        src = os.path.join(root, "scripts", "voice", "contrast_family.py")
        if not os.path.exists(src):
            self.skipTest("not running inside the repository")
        sys.path.insert(0, os.path.dirname(src))
        import contrast_family  # noqa: E402
        from cringe_filter.lint import CONTRAST, COURSE
        for k, pat in CONTRAST.items():
            self.assertEqual(pat, contrast_family.FAMILY[k], k)
        for k, pat in COURSE.items():
            self.assertEqual(pat, contrast_family.COURSE[k], k)
        from cringe_filter.lint import AGENT
        self.assertEqual(AGENT, contrast_family.AGENT)


class Contrast(unittest.TestCase):
    def rules(self, text, ctx="github"):
        return {f["rule"] for f in lint_text(text, ctx)}

    def test_corrective_contrast_is_flagged(self):
        got = self.rules("Most errors happen here, not in the algebra. The "
                         "referrer is what unlocked it.")
        self.assertIn("x-not-y", got)
        self.assertIn("is-what-cleft", got)
        self.assertIn("dash-not-y", self.rules("The unit was the problem; not "
                                               "the count."))

    def test_concessions_and_hedges_are_not(self):
        got = self.rules("Not sure, but I think it works. It runs, not yet on "
                         "the Pi though. That's what I meant.")
        self.assertFalse(got & {"x-not-y", "dash-not-y", "is-what-cleft"}, got)

    def test_against_reports_only_what_a_revision_added(self):
        from cringe_filter.lint import introduced
        old = "It rose \u2014 sharply. We checked it twice."
        new = ("We checked it twice. It rose \u2014 sharply. The fix was the "
               "cable, not the adapter.")
        got = [f["rule"] for f in introduced(old, new, "github")]
        self.assertEqual(got.count("em-dash"), 0)
        self.assertIn("x-not-y", got)

    def test_minimal_prompt_carries_checklist_and_findings(self):
        from cringe_filter import build_minimal_prompt
        from cringe_filter.prompt import REVIEW_CHECKLIST
        system, user = build_minimal_prompt(
            "The fix was upstream, not in our code. It rose \u2014 sharply.", "paper")
        self.assertIn(REVIEW_CHECKLIST[0], system)
        self.assertIn("em-dash", system)
        self.assertIn("x-not-y", system)
        self.assertTrue(user.endswith("It rose \u2014 sharply."))

    def test_measured_in_github(self):
        r = {x.key: x for x in rules_for("github")}
        for k in ("x-not-y", "dash-not-y", "is-what-cleft"):
            self.assertEqual(r[k].evidence, "measured", k)
            self.assertGreater(r[k].ci[0], 1, k)


class AgentInstructions(unittest.TestCase):
    """The rules written for Copilot in 2025."""

    def test_patterns(self):
        import re
        from cringe_filter.lint import AGENT
        yes = {"you're right (opener)": "Thanks for the clarification! You're absolutely right - I misread it.",
               "acknowledged (opener)": "Acknowledged - I will never expose secrets.",
               "per instructions / as requested": "Removed the wrapper per custom instructions.",
               "commit hash in parentheses": "Fixed the step names (cfe26cc).",
               "spaced hyphen as dash": "Aligned with the docs - now uses the client.",
               "production-ready / fully verified": "Integration is production-ready.",
               "check glyph": "Parser \u2713"}
        no = {"you're right (opener)": "If you're right about the cause, it works.",
              "spaced hyphen as dash": "- a bullet line, and x = a - 1",
              "ALL-CAPS imperative": "It is important to never print it."}
        for k, t in yes.items():
            self.assertTrue(re.search(AGENT[k], t, re.I | re.M), k)
        for k, t in no.items():
            self.assertFalse(re.search(AGENT[k], t, re.I | re.M), k)

    def test_copilot_evidence_never_above_warn(self):
        for ctx in ("github", "tutorial", "paper"):
            for r in rules_for(ctx):
                if r.evidence == "copilot":
                    self.assertIn(r.severity, ("warn", "info"), r.key)

    def test_verdicts_follow_the_measurement(self):
        r = {x.key: x for x in rules_for("github")}
        self.assertEqual(r["youre-right"].evidence, "measured")
        self.assertEqual(r["change-trace"].evidence, "measured")
        self.assertEqual(r["absolutely-right"].evidence, "copilot")
        # The writer's: politeness, apologies, "successfully" and the spaced hyphen.
        for k in ("good-catch", "apology", "successfully", "spaced-hyphen"):
            self.assertNotIn(k, r)

    def test_bold_is_his_in_proposals(self):
        self.assertNotIn("bold-run", {r.key for r in rules_for("proposal")})


class Instructions(unittest.TestCase):
    def test_writes_path_scoped_files(self):
        import tempfile
        from cringe_filter.cli import main
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(main(["instructions", "paper", "proposal", "--dir", d]), 0)
            text = open(os.path.join(d, "cringe-filter-paper.instructions.md")).read()
            self.assertTrue(text.startswith('---\napplyTo: "**/*.tex,**/*.bib"\n---\n'))
            self.assertIn("When you write or edit prose in these files", text)
            self.assertNotIn("Output only the rewrite", text)
            self.assertTrue(os.path.exists(os.path.join(d, "cringe-filter-proposal.instructions.md")))
            self.assertEqual(main(["instructions", "github", "--dir", d]), 2)


class Audit(unittest.TestCase):
    DRAFT = ("The bottleneck is the parser, not the network.\n\n"
             "Use an assert, not an if statement.\n\n"
             "The fix is what made it work \u2014 and it shipped.\n")

    def test_without_a_model_nothing_is_dropped(self):
        from cringe_filter.audit import audit, render_spec
        r = audit(self.DRAFT, "github")
        self.assertEqual([e["line"] for e in r["fix"]], [1, 3, 5])
        self.assertEqual(r["keep"], [])
        self.assertIn("Judgment call", render_spec(r))

    def test_a_verdict_clears_only_the_judged_finding(self):
        import cringe_filter.audit as a
        real = a._chat
        a._chat = lambda model, system, user, endpoint=None: (
            "5" if ("assert" in user or "made it work" in user) else "80")
        try:
            r = a.audit(self.DRAFT, "github", model="stub")
        finally:
            a._chat = real
        fix = {e["line"]: [f["rule"] for f in e["findings"]] for e in r["fix"]}
        keep = {e["line"]: [f["rule"] for f in e["findings"]] for e in r["keep"]}
        self.assertEqual(fix, {1: ["x-not-y"], 5: ["em-dash"]})
        self.assertEqual(keep, {3: ["x-not-y"], 5: ["is-what-cleft"]})
        spec = a.render_spec(r)
        self.assertIn("stub scored the contrast 80/100", spec)
        self.assertIn("## Leave as written", spec)


if __name__ == "__main__":
    unittest.main()
