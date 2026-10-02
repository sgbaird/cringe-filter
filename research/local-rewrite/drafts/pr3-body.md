Removes the references to Sterling ("his median", "reads like Sterling", "Real passages Sterling wrote", "the way Sterling Baird would write it") and describes each context by the task it is tuned for.

- **Wording:** "the human median/rate", "reads human", "Examples of human writing", context labels like "GitHub reply in your own repos"; corrections credited to "a reviewer"
- **Unchanged:** quoted exemplar passages (byte-identical), English word lists and regexes that contain "he"/"his" as data, author metadata in `pyproject.toml`/`LICENSE`, and the internal `sterling` key in `profile.json` (the build pipeline writes it)
- 48 tests pass; docs build clean with `sphinx -W`

Heads-up: the private build pipeline still generates the old wording, so the next profile rebuild needs the same changes upstream or it will reintroduce them.
