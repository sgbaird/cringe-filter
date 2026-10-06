"""Sphinx configuration. The CLI reference is regenerated from each
subcommand's --help on every build, so it cannot drift from the code."""
import contextlib
import io
import os

from cringe_filter import __version__
from cringe_filter.cli import main

project = "cringe-filter"
author = "Sterling Baird"
copyright = "2026, Sterling Baird"
release = __version__

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
myst_heading_anchors = 3
exclude_patterns = ["_build"]
html_theme = "furo"
html_title = f"cringe-filter {release}"
autodoc_member_order = "bysource"

COMMANDS = ["lint", "score", "prompt", "rewrite", "audit",
            "instructions", "contexts", "profile", "mcp"]


def _help(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.suppress(SystemExit):
        main(argv)
    return out.getvalue().rstrip()


def _write_cli_reference():
    parts = ["# CLI reference", "",
             "Generated from `cringe-filter <command> --help` at build time.", "",
             "```text", _help(["--help"]), "```", ""]
    for cmd in COMMANDS:
        parts += [f"## `{cmd}`", "", "```text", _help([cmd, "--help"]), "```", ""]
    path = os.path.join(os.path.dirname(__file__), "cli.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


_write_cli_reference()
