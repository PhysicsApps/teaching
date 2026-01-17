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
{{embed_code("static")}}
## Animations using plotly (python)
Plotly makes it easy to create animated plots with minimal setup. The following example demonstrates how to create an animated plot using Plotly within a Shiny app.
{{embed_app("100%", "550px", "animated")}}
{{embed_code("animated")}}
Note that this approach requires animations that loop smoothly. The entire frame stack must be preloaded when the plot is first rendered, which may lead to longer initial load times for complex animations. Additionally, this precludes a true "live" animation that updates based on real-time or on-the-fly generated data.
## Animations using plotly (injecting JavaScript)
For more advanced use cases, you can inject custom JavaScript code to control the animation behavior in Plotly directly. This allows for greater flexibility and smoother animations. The following example (from [plotly.js](https://plotly.com/javascript/animations/#animating-many-frames-quickly)) demonstrates how to create an animated plot using Plotly with custom JavaScript within a Shiny app, allowing for on-the-fly generation of new frames.
{{embed_app("100%", "550px", "animated_js")}}
{{embed_code("animated_js")}}
Y