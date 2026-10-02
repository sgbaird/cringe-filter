Rewrites the README by running cringe-filter on it in the tutorial context, following SKILL.md (lint, read the prompt, rewrite, score once).

- README before: 26 findings (1 error), 2146 words, score +4.51 (reads like Claude). After: 3 info findings, 1457 words, score -77.67 (reads human).
- New docs/methods.md holds the measurement details moved out of the README.
- lint: suppression comments inside code blocks no longer apply. The README's own disable-file example had switched the linter off for the whole file. A new test keeps the README free of errors and warnings under its own linter.

Addresses #10. Package suggestions from the process are in the issue comment.
