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
Quick example for a simple matplotlib app. Matplotlib is a popular Python library that can be used to create plots. It is most suited for static plots, but can also be coerced to create animations.
<!-- more -->
## Simplest matplotlib plot
The following example demonstrates how to create a simple static plot using Matplotlib within a Shiny app.
{{embed_app("100%", "500px", "static")}}
This is the most straightforward way to integrate plots into your tools by leveraging matplotlib's vast capabilities for visualizations.
## Animations using matplotlib
While it is in principle possible to create animations using Matplotlib in Shiny for Python, it requires some additional setup compared to static plots. The following example demonstrates how to create an animated plot using Matplotlib within a Shiny app.
{{embed_app("100%", "500px", "animated")}}
This approach might lead to flickering in certain browsers, as the entire plot is re-rendered for each frame of the animation. For smoother animations it is recommended to instead use plotly (see [here](https://physicsapps.github.io/teaching/plotly-template.html) for the corresponding template), which integrate more seamlessly with web applications.