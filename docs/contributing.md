---
render_macros: false
---
# Contributing to TeachingTools
We welcome contributions to this project! If you have an idea for a new tool, a bug fix, or any other improvement, please follow these steps:

## Setting up a development environment
You should first fork [this](https://github.com/physicsapps/teaching) repository and then clone it to your local machine.
```bash
git clone https://github.com/physicsapps/teaching.git
cd TeachingTools
```

The easiest way to then set up a virtual environment is using the `venv` module 
```bash
python3.12 -m venv .venv
source .venv/bin/activate
# for windows this would is .venv/Scripts/activate
python -m pip install -r .
```
Your next steps should be to create a new branch for your changes.
```bash
git switch -c my-new-feature
```

## Creating a new tool
To create a new tool, you should copy one of the template tools from the `apps` directory and modify it to your needs.
Each tool should have its own directory with the following structure:
```
apps/
└── MyNewTool
    ├── app.py
    ├── app.md
    └── requirements.txt
```
If you want to use multiple apps in one tool, you can create a separate directory for every app:
```
apps/
└── MyNewTool
    ├── app1
    |   ├── app.py
    |   └── requirements.txt
    ├── app2
    |   ├── app.py
    |   └── requirements.txt
    └── app.md
```
The tools themselves are created using [Shiny for python](https://shiny.posit.co/py/), which allows you to create interactive web applications using Python.
In the case of static sites, such as this one, the tools are rendered as static HTML files using the [shinylive](https://github.com/posit-dev/py-shinylive) library.
For details on how to create a Shiny app, please refer to the [Shiny for Python documentation](https://shiny.posit.co/py/get-started/).
## Writing documentation
Each tool should have a corresponding `app.md` file in the same directory. This file should contain the documentation for the tool, including a description, usage instructions, and any other relevant information.
The documentation is written in [Markdown](https://www.markdownguide.org/), and parsed using [mkdocs](https://www.mkdocs.org/) with the [material theme](https://squidfunk.github.io/mkdocs-material/). 
Especially check out the latter for more information on how to use the available features.
You can use the following template to get started:
```markdown title="app.md"
---
authors:
  - <author>
categories:
  - Templates
tags:
  - Matplotlib
  - Introduction
date: YYYY-MM-DD
hide:
  - toc
---
# Matplotlib Template
Quick example for a simple matplotlib app. Matplotlib is a popular Python library that can be used to create plots.
<!-- more -->
This is a simple example to showcase different matplotlib apps using Shiny for Python.
## Default matplotlib theme
{{embed_app("100%", "500px", "default")}}
## Dark matplotlib theme
{{embed_app("100%", "500px", "dark")}}
## Seaborn matplotlib theme
{{embed_app("100%", "500px", "seaborn")}}
```
This documentation differs slightly from standard markdown files, as it includes a few additional necessary sections.
The front matter at the top of the file is used to specify metadata about the tool, such as the authors, categories, tags, and date.
If this is your first time contributing to this project, you should also add your name to the `.authors.yml` list.
``` yml title=".authors.yml"
authors:
  <author>:
    name: string        # Author name
    description: string # Author description
    avatar: url         # Author avatar
    slug: url           # Author profile slug
    url: url            # Author website URL
```
Set the category to one of the existing categories, or create a new one to `mkdocs.yml` if necessary.
```yml title="mkdocs.yml"
plugins:
- blog:
    categories_allowed:
      - <category>
```
The tags are used to further categorize the tool and can be anything you like.
The name of the tool is generated from the title of the `app.md` file, so make sure to use a descriptive title.
The `<!-- more -->` tag is used to separate the introduction, which is shown as an excerpt, from the rest of the documentation.
To embed the app in the documentation, you can use the `{{embed_app("width", "height")}}` macro.
The width and height can be set to any valid CSS value, such as `100%`, `500px`, or `50vw`.
If you have multiple apps in a single tool, as is the case in the example above, you can specify the app name as a third argument, e.g. `{{embed_app("100%", "500px", "app1")}}`, where the app name must match the name of the subirectory containing the `app.py` file.
## Testing your tool locally
To test your tool locally, you should build the full documentation using the following command in the root directory of your repository:
```bash
mkdocs build --clean
python -m http.server --directory ./site --bind localhost 8008 
```
This will create a `site` directory containing the static HTML files for the documentation, including your new tool.
You can then open your browser and navigate to [localhost](http://[::1]:8008/) to see the documentation and test if everything works.
If that is the case, congratulations! You have successfully created a new tool for TeachingTools and can now submit your changes.

## Submitting your changes
Once you have made your changes and tested them locally, you can commit your changes and push them to your forked repository:
```bash
git add .
git commit -m "Add MyNewTool"
git push origin my-new-feature
```
Then, create a pull request on the original repository. Make sure to provide a clear description of your changes and what they do.
