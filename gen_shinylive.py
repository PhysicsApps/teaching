#!/usr/bin/env python
from pathlib import Path
from shinylive import _export
import os
from pymdownx.slugs import slugify


target_url = 'https://physicsapps.github.io/teaching/' #use this for QR-code generation via e.g. https://pypi.org/project/qrcode/


for file_path in sorted(Path("docs").glob("**/app.md")):
    file_path = file_path.relative_to("docs") # e.g. "docs/blog/PlotlyPenguins/app.md"
    parts = Path(file_path).parts

    # find title in app.md
    title = None
    with open(Path("docs", *parts[:-1], "app.md"), "r") as f:
        for line in f:
            if line.startswith("# "):
                title = line[2:].strip()
                break

    # Check if a title is defined in app.md
    if title is None:
        raise ValueError(f"No title found in {file_path}. Please ensure the app.md file contains a title starting with '# '.")

    base_apppath = Path("docs", *parts[:-1])  # e.g. "docs/blog/PlotlyPenguins"
    base_shinypath = Path('apps', slugify(case='lower')(title, sep='-'))
    # Look for all app.py files here and in subdirectories e.g. "docs/apps/FastFourierTransforms/1d/app.py"
    for app_path in Path("docs", *parts[:-1]).glob("**/app.py"):
        subdirpath = app_path.relative_to(Path("docs", *parts[:-1])) # 1d/app.py
        subdirparts = subdirpath.parts
        if len(subdirparts) == 1:
            target_apppath = base_apppath
            target_shinypath = base_shinypath
        else:
            target_apppath = Path(base_apppath, subdirparts[0])
            target_shinypath = Path(str(base_shinypath) +  '_' + str(subdirparts[0]))

        os.makedirs(Path("./site", target_shinypath), exist_ok=True)
        _export.export(target_apppath, Path("./site"), subdir=target_shinypath, verbose=True, full_shinylive=True)
