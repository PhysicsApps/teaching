---
authors:
  - ptuemmler
categories:
  - Templates
tags:
  - Templates
date: 
    created: 2025-07-01
    updated: 2025-12-17
hide:
  - toc
---

# Plotly Template
Plotly is a powerful graphing library that makes interactive, publication-quality graphs online. It is well-suited for both static and animated plots, making it a great choice for web applications.
<!-- more -->
## Simplest plotly plot
The following example demonstrates how to create a simple static plot using Plotly within a Shiny app
{{embed_app("100%", "550px", "static")}}
## Animations using plotly
Plotly makes it easy to create animated plots with minimal setup. The following example demonstrates how to create an animated plot using Plotly within a Shiny app.
{{embed_app("100%", "550px", "animated")}}
Note that this approach requires animations that loop smoothly. The entire frame stack must be preloaded when the plot is first rendered, which may lead to longer initial load times for complex animations. Additionally, this precludes a true "live" animation that updates based on real-time or on-the-fly generated data.