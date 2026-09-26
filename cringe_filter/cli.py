"""Command line: python -m cringe_filter <lint|score|prompt|rewrite|audit|instructions|contexts|profile>."""
import argparse
import json
import sys

from . import __version__
from .bundle import profile, reference
from .lint import format_finding, introduced, lint_text
from .prompt import build_minimal_prompt, build_prompt, render
from .registers import contexts, infer_context, resolve
from .score import format_score, score_text


def read_input(args):
    if getattr(args, "text", None):
        return args.text, "<text>"
    path = getattr(args, "file", None) or "-"
    if path == "-":
        return sys.stdin.read(), "<stdin>"
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read(), path


def pick_context(args, path=None):
    if getattr(args, "url", None):
        return infer_context(args.url)
    if not getattr(args, "context", None):
        path = path or getattr(args, "file", None)
        if path and str(path).lower().endswith((".tex", ".ltx")):
            return resolve("paper")
    return resolve(getattr(args, "context", None) or "any")


def add_structure(sp):
    sp.add_argument("--structure", action=argparse.BooleanOptionalAction, default=None,
                    help="include (or leave out) the priority on how human sentences "
                         "and paragraphs are built, where the register has rates")


def add_common(sp, single=True):
    sp.add_argument("--context", "-c", "--register", dest="context", default=None,
                    help="where the text is going: github, discussion, "
                         "third-party, email, message, linkedin, tutorial, "
                         "paper, any (aliases accepted)")
    sp.add_argument("--url", help="infer the context from a destination URL "
                                  "or path instead")
    sp.add_argument("--json", action="store_true")
    if single:
        sp.add_argument("file", nargs="?", default="-",
                        help="input file, or - for stdin")
        sp.add_argument("--text", help="the text itself, instead of a file")


def cmd_lint(args):
    used = set()
    all_findings = []
    files = args.files or ["-"]
    for path in files:
        if path == "-":
            text, name = sys.stdin.read(), "<stdin>"
        else:
            try:
                text = open(path, encoding="utf-8", errors="ignore").read()
            except (IsADirectoryError, FileNotFoundError):
                continue
            name = path
        # A .tex file with no context given is a manuscript.
        ctx = pick_context(args, path)
        used.add(ctx)
        if args.against:
            with open(args.against, encoding="utf-8", errors="ignore") as f:
                all_findings += introduced(f.read(), text, ctx, name)
        else:
            all_findings += lint_text(text, ctx, name)
    if args.quiet:
        all_findings = [f for f in all_findings if f["severity"] == "error"]
    if args.json:
        json.dump(all_findings, sys.stdout, indent=1)
        print()
    else:
        for f in all_findings:
            print(format_finding(f, color=not args.no_color))
        n_err = sum(1 for f in all_findings if f["severity"] == "error")
        ctxs = ", ".join(sorted(used)) or pick_context(args)
        print(f"\n{len(all_findings)} findings, {n_err} errors  (context: {ctxs})")
    return 1 if any(f["severity"] == "error" for f in all_findings) else 0


def cmd_score(args):
    ctx = pick_context(args)
    text, _ = read_input(args)
    r = score_text(text, ctx)
    if args.json:
        json.dump(r, sys.stdout, indent=1)
        print()
    else:
        print(format_score(r))
    return 0


def shape_opt(args):
    """--structure / --no-structure, or the prompt's own default."""
    v = getattr(args, "structure", None)
    return {} if v is None else {"structure": v}


def cmd_prompt(args):
    ctx = pick_context(args)
    # --system-only never touches stdin: in a CI shell stdin is open and
    # not a terminal, and reading it would block forever.
    if args.system_only and not args.text and args.file == "-":
        text = ""
    elif args.file == "-" and not args.text and sys.stdin.isatty():
        text = ""
    else:
        text, _ = read_input(args)
    if args.minimal:
        if not text.strip():
            raise ValueError("--minimal needs the draft: its lint findings go "
                             "into the prompt")
        system, user = build_minimal_prompt(text, ctx)
        if args.json:
            json.dump({"context": ctx, "system": system, "user": user},
                      sys.stdout, indent=1)
            print()
        else:
            print(system if args.system_only else render(system, user))
        return 0
    system, user, evidence = build_prompt(text, ctx, n_exemplars=args.exemplars,
                                          with_evidence=True, **shape_opt(args))
    if args.json:
        json.dump({"context": ctx, "system": system, "user": user,
                   "evidence": evidence}, sys.stdout, indent=1)
        print()
    elif args.system_only or not text.strip():
        print(system)
    else:
        print(render(system, user))
    if args.evidence and not args.json:
        print("\n" + evidence)
    return 0


# Where each document context's files live, for path-scoped instructions.
# A path naming a proposal or grant is a proposal before it is a .tex file
# (infer_context), but globs cannot express that order: a .tex file in a
# proposal folder matches both, and Copilot then applies both files.
APPLY_TO = {"proposal": "**/*proposal*/**,**/*grant*/**",
            "paper": "**/*.tex,**/*.bib",
            "tutorial": "**/*.md,**/*.rst,**/*.ipynb"}


def cmd_instructions(args):
    """Path-scoped instructions for GitHub Copilot, one file per context.

    Copilot's cloud agent and its code review apply a
    .github/instructions/NAME.instructions.md file to the files its applyTo
    globs match, so a repository can carry the paper filter for .tex files
    and the tutorial filter for its docs without anyone choosing a context.
    Replies are not files, so those contexts need --apply-to, or the
    prompt pasted into .github/copilot-instructions.md."""
    import os
    os.makedirs(args.dir, exist_ok=True)
    for name in args.contexts:
        ctx = resolve(name)
        glob = args.apply_to or APPLY_TO.get(ctx)
        if not glob:
            raise ValueError(
                f"{ctx} text is not a file in the repository; pass --apply-to, "
                f"or put `cringe-filter prompt -c {ctx} --system-only` in "
                ".github/copilot-instructions.md")
        system, _ = build_prompt("", ctx, n_exemplars=args.exemplars,
                                 standing=True, **shape_opt(args))
        head = f'applyTo: "{glob}"'
        if args.exclude_agent:
            head += f'\nexcludeAgent: "{args.exclude_agent}"'
        path = os.path.join(args.dir, f"cringe-filter-{ctx}.instructions.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"---\n{head}\n---\n\n{system.strip()}\n")
        print(f"wrote {path} (applyTo {glob})")
    return 0


def cmd_rewrite(args):
    from .rewrite import rewrite
    ctx = pick_context(args)
    text, _ = read_input(args)
    if args.dry_run:
        system, user = (build_minimal_prompt(text, ctx) if args.minimal
                        else build_prompt(text, ctx, **shape_opt(args)))
        print(render(system, user))
        return 0
    r = rewrite(text, ctx, model=args.model, revise=not args.no_revise,
                fallbacks=not args.no_fallback, effort=args.effort,
                minimal=args.minimal, **shape_opt(args))
    if args.json:
        json.dump(r, sys.stdout, indent=1)
        print()
    else:
        print(r["text"])
        print(f"\n[cringe-filter] {r['passes']} pass(es), model {r['model']}, "
              f"style score {r['score_before']['log_odds']:+.1f} -> "
              f"{r['score_after']['log_odds']:+.1f}, "
              f"{len(r['findings'])} findings remain", file=sys.stderr)
        for f in r["findings"]:
            print("  " + format_finding(f, color=False).split("\n")[0],
                  file=sys.stderr)
    return 0


def cmd_audit(args):
    from .audit import audit, render_spec
    text, path = read_input(args)
    ctx = pick_context(args, path)
    r = audit(text, ctx, path, model=args.model, endpoint=args.endpoint,
              threshold=args.threshold)
    if args.json:
        json.dump(r, sys.stdout, indent=1)
        print()
    else:
        print(render_spec(r), end="")
    return 0


def cmd_contexts(args):
    rows = contexts()
    if args.json:
        json.dump(rows, sys.stdout, indent=1)
        print()
        return 0
    print(f"{'context':12s}{'label':46s}{'docs':>7s}{'words':>9s}"
          f"{'median':>8s}{'budget':>8s}")
    for r in rows:
        cf = "  (carried forward)" if r["carried_forward"] else ""
        print(f"{r['context']:12s}{r['label'][:45]:46s}{r['n_docs']:7d}"
              f"{r['n_words']:9d}{str(r['median_words']):>8s}"
              f"{str(r['budget_words']):>8s}{cf}")
    print("\naliases:", "; ".join(f"{r['context']}: {', '.join(r['aliases'][1:6])}"
                                 for r in rows))
    return 0


def cmd_profile(args):
    p = profile()
    if args.json:
        json.dump(p if not args.context else
                  p["registers"][resolve(args.context)], sys.stdout, indent=1)
        print()
        return 0
    ctx = resolve(args.context or "github")
    reg = p["registers"][ctx]
    ref = reference(ctx)
    print(f"{ctx}: {reg['label']} ({reg['n_docs']:,} docs, {reg['n_words']:,} "
          f"words; built {p['built']})")
    print(f"{'marker':26s}{'human/1k':>9s}{'Claude/1k':>11s}")
    for k in sorted(reg["mechanical"]):
        print(f"{k[:-7]:26s}{reg['mechanical'][k]:9.2f}"
              f"{ref['mechanical'].get(k, 0):11.2f}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="cringe-filter",
        description="AI-cringe filter and human-voice filter, from "
                    "measured writing.")
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("lint", help="deterministic tells with their evidence")
    add_common(sp, single=False)
    sp.add_argument("files", nargs="*", help="files, or - for stdin")
    sp.add_argument("--quiet", action="store_true", help="errors only")
    sp.add_argument("--against", metavar="OLD",
                    help="report only findings that are not already in OLD, "
                         "the version before a revision")
    sp.add_argument("--no-color", action="store_true")
    sp.set_defaults(fn=cmd_lint)

    sp = sub.add_parser("score", help="Claude-versus-human log-odds, by feature")
    add_common(sp)
    sp.set_defaults(fn=cmd_score)

    sp = sub.add_parser("prompt", help="the voice filter as a prompt")
    add_common(sp)
    sp.add_argument("--exemplars", type=int, default=2)
    sp.add_argument("--system-only", action="store_true",
                    help="print the filter without the text")
    sp.add_argument("--evidence", action="store_true",
                    help="append the measured rates and intervals behind "
                         "the filter (for people, not for the model)")
    sp.add_argument("--minimal", action="store_true",
                    help="the smallest edit a reviewer would make, with the "
                         "draft's lint findings; for text headed to review")
    add_structure(sp)
    sp.set_defaults(fn=cmd_prompt)

    sp = sub.add_parser("rewrite", help="apply the filter with Claude and lint the result")
    add_common(sp)
    sp.add_argument("--model", default="claude-opus-5")
    sp.add_argument("--effort", default="medium",
                    choices=["low", "medium", "high", "xhigh", "max"])
    sp.add_argument("--no-revise", action="store_true",
                    help="skip the one revision pass against lint errors")
    sp.add_argument("--no-fallback", action="store_true",
                    help="do not request the server-side refusal fallback")
    sp.add_argument("--dry-run", action="store_true",
                    help="print the prompt instead of calling the model")
    sp.add_argument("--minimal", action="store_true",
                    help="edit as little as a reviewer would instead of "
                         "rewriting; no revision pass")
    add_structure(sp)
    sp.set_defaults(fn=cmd_rewrite)

    sp = sub.add_parser("audit", help="findings by sentence as an edit spec, with "
                                      "judgment calls put to a local model")
    add_common(sp)
    sp.add_argument("--model", default=None,
                    help="model for the judgment calls, e.g. qwen2.5:14b under "
                         "Ollama; without it they are left to the editor")
    sp.add_argument("--threshold", type=int, default=30,
                    help="score (0-100) at or above which a judged contrast "
                         "stays on the fix list")
    sp.add_argument("--endpoint", default=None,
                    help="OpenAI-compatible base URL (default "
                         "$CRINGE_FILTER_LLM_ENDPOINT or Ollama on localhost)")
    sp.set_defaults(fn=cmd_audit)

    sp = sub.add_parser("instructions",
                        help="path-scoped Copilot instruction files, one per context")
    sp.add_argument("contexts", nargs="+", help="e.g. paper proposal tutorial")
    sp.add_argument("--dir", default=".github/instructions")
    sp.add_argument("--apply-to", metavar="GLOBS",
                    help="comma-separated globs, instead of the context's default")
    sp.add_argument("--exclude-agent", choices=["code-review", "cloud-agent"],
                    help="keep one of Copilot's agents from reading the file")
    sp.add_argument("--exemplars", type=int, default=2)
    add_structure(sp)
    sp.set_defaults(fn=cmd_instructions)

    sp = sub.add_parser("contexts", help="the contexts the bundle can serve")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_contexts)

    sp = sub.add_parser("profile", help="the measured rates for a context")
    sp.add_argument("--context", "-c", default=None)
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_profile)

    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except ValueError as e:
        print(f"cringe-filter: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
