I rewrote the README by running cringe-filter on it in the tutorial context, the way SKILL.md says to (lint, read the prompt, rewrite, score once).

Before, the README had 26 findings (1 error), 2146 words and a score of +4.51, which reads like Claude. Now it has 3 info findings, 1457 words and a score of -77.67, which reads human.

The measurement details moved out of the README into a new docs/methods.md.

I also fixed lint so suppression comments inside code blocks no longer apply. The README's own disable-file example had switched the linter off for the whole file. A new test keeps the README free of errors and warnings under its own linter.

Addresses #10. My package suggestions from the process are in the issue comment.
