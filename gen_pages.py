#!/usr/bin/env python
from pathlib import Path
from shinylive import _export
import mkdocs_gen_files
import os

# Generate documentation pages for all Python files in the 'test' directory
nav = mkdocs_gen_files.Nav()
for filepath in sorted(Path("docs").glob("**/app.md")):
    filepath = filepath.relative_to("docs")
    # split into directories and write nav files
    parts = Path(filepath).parts
    print(parts)
    # Create a Navigation page SUMMARY.md
    nav[[part for part in parts[1:-1]]] = Path(*parts[1:])

    # While we are here, build shinylive apps
    subdirpath = Path(*parts[1:-1])
    os.makedirs(Path("docs/site", subdirpath), exist_ok=True)
    _export.export(Path("docs", *parts[:-1]), Path("docs/site"), subdir=subdirpath, verbose=True)

    # And apply the magic embed:
    # <div>
    #     <iframe src="/site/topic1_plotlydummy/index.html" width="100%" height="600px"></iframe>
    # </div>

    # shinylive_html_filepath = Path("docs/site", "_".join(parts[1:-1]), "index.html")
    # with mkdocs_gen_files.open(filepath, "w") as fwrite:
    #     pass


with mkdocs_gen_files.open("apps/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())


