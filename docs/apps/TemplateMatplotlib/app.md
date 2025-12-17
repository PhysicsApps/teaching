---
authors:
  - ptuemmler
categories:
  - Templates
tags:
  - Templates
date: 
    created: 2025-07-02
    updated: 2025-12-07
hide:
  - toc
---

# Matplotlib Template
Quick example for a simple matplotlib app. Matplotlib is a popular Python library that can be used to create plots.
<!-- more -->
This is a simple example to showcase different matplotlib apps using Shiny for Python.
## Simplest matplotlib plot
{{embed_app("100%", "500px", "static")}}
## Animations using matplotlib
While it is in principle possible to create animations using Matplotlib in Shiny for Python, it requires some additional setup compared to static plots. The following example demonstrates how to create an animated plot using Matplotlib within a Shiny app.
{{embed_app("100%", "500px", "animated")}}
This approach might lead to flickering in certain browsers, as the entire plot is re-rendered for each frame of the animation. For smoother animations, consider using libraries specifically designed for interactive visualizations, such as Plotly or Bokeh, which integrate more seamlessly with web applications.