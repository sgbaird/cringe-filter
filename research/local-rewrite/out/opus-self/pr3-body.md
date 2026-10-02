This removes the references to Sterling ("his median", "reads like Sterling", "Real passages Sterling wrote", "the way Sterling Baird would write it") and describes each context by the task it's tuned for.

The new wording is "the human median/rate", "reads human" and "Examples of human writing", with context labels like "GitHub reply in your own repos". Corrections are credited to "a reviewer".

I left a few things alone: the quoted exemplar passages (byte-identical), the English word lists and regexes that contain "he"/"his" as data, the author metadata in `pyproject.toml`/`LICENSE`, and the internal `sterling` key in `profile.json`, since the build pipeline writes it.

48 tests pass and the docs build clean with `sphinx -W`.

The private build pipeline still generates the old wording, so we need the same changes upstream before the next profile rebuild, or it will bring them back.
