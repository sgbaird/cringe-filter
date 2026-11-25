I rebuilt the figure and pushed it. I removed the Sterling references so the context is defined by its task instead of by the author.

I kept the quoted exemplar passages, the English word lists, the regexes, and the internal `sterling` key in `profile.json`.

- Wording: "the human median/rate", "reads human", "Examples of human writing", context labels like "GitHub reply in your own repos"
- Unchanged: quoted exemplar passages, English word lists and regexes that contain "he"/"his" as data, author metadata in `pyproject.toml`/`LICENSE`, and the internal `sterling` key in `profile.json`
- 48 tests pass; docs build clean with `sphinx -W`

The private build pipeline still generates the old wording, so the next profile rebuild needs the same changes upstream or it will reintroduce them.
