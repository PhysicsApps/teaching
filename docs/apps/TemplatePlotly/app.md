---
authors:
  - ptuemmler
categories:
  - Templates
tags:
  - Plotly
  - Introduction
date: 2025-07-01
hide:
  - toc
---

# Plotly Penguins app
Quick example for a simple plotly app. Plotly is an interactive graphics plotting library.
<!-- more -->

{{embed_app("100%", "500px")}}

To make an interactive plot with Plotly in Shiny for Python, we will need to use the shinywidgets library to connect Shiny with `#!python ipywidgets`.

To make a Plotly figure, we need to do the following steps:

1. Import the `#!python output_widget()` and `#!python render_widget()` functions from the `#!python shinywidgets` library, `#!python from shinywidgets import output_widget, render_widget`

2. Call `#!python output_widget()` to the UI of your app to create a div in which to display the figure. Where you call this function will determine where the figure will appear within the layout of the app. The id parameter you provide will be used to link to other parts of the Shiny app.

3. Define a function within the `#!python server()` function that creates the figure.

    - The name of the function should be the same value you passed into the id parameter in your `#!python output_widget()` function call in the UI.
    - If your function calls reactive values, Shiny will update your figure whenever those values change, in a reactive fashion.

4. Decorate your plotting function with a `#!python @render_widget()` decorator.
    - If your plotting function is not the same as the id you used in the `#!python ui.output_widget()`, you can add an additional `#!python @output(id=...)` decorator.
    - If you use the `#!python @output()` decorator, make sure it is **above** the `#!python @render_widget()` decorator.

Visit shiny.posit.co/py/docs/ipywidgets.html to learn more about using ipywidgets with Shiny.
[See here for more details.](https://shiny.posit.co/py/components/outputs/plot-plotly/#details)