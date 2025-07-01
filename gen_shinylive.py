#!/usr/bin/env python
from pathlib import Path
from shinylive import _export
import os
from pymdownx.slugs import slugify


for filepath in sorted(Path("docs").glob("**/app.md")):
    filepath = filepath.relative_to("docs") # e.g. "docs/blog/PlotlyPenguins/app.md"
    parts = Path(filepath).parts

    # find title in app.md
    title = None
    with open(Path("docs", *parts[:-1], "app.md"), "r") as f:
        for line in f:
            if line.startswith("# "):
                title = line[2:].strip()
                break

    if title is None:
        raise ValueError(f"No title found in {filepath}. Please ensure the app.md file contains a title starting with '# '.")

    test = slugify(case='lower')(title, sep='-')
    subdirpath = Path('apps', test)
    os.makedirs(Path("./site", subdirpath), exist_ok=True)
    _export.export(Path("docs", *parts[:-1]), Path("./site"), subdir=subdirpath, verbose=True)
