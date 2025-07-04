---
authors:
  - ptuemmler
categories:
  - Templates
tags:
  - Matplotlib
  - Introduction
date: 2025-07-02
hide:
  - toc
---

# Matplotlib Penguins app
Quick example for a simple matplotlib app. Matplotlib is a popular Python library that can be used to create plots.
<!-- more -->

{{embed_app("100%", "500px")}}

Follow three steps to display a Matplotlib figure in your app:

1. Add `#!python ui.output_plot()` to the UI of your app to create a div in which to display the figure. Where you call this function will determine where the figure will appear within the layout of the app. The id parameter you provide will be used to link to other parts of the Shiny app.

2. Define a function within the `#!python server()` function that creates the figure.

    - The name of the function should be the same value you passed into the id parameter in your ui.output_plot() function call in the UI.

    - If your function calls reactive values, Shiny will update your figure whenever those values change, in a reactive fashion.

    - If you use matplotlib.pyplot to plot, your function does not need to return a value. Otherwise, your function should return one of the following objects:
      - A `#!python matplotlib.figure.Figure` instance
      - A `#!python matplotlib.artist.Artist` instance
      - A `#!python list`/`#!python tuple` of `#!python Figure`/`#!python Artist` instances
      - An `#!python object` with a ‘figure’ attribute pointing to a `#!python matplotlib.figure.Figure` instance
      - A `#!python PIL.Image.Image` instance
3. Decorate your plotting function with a `#!python @render.plot()` decorator.

   - If your plotting function is not the same as the id you used in the `#!python ui.output_plot()`, you can add an additional `#!python @output(id=...)` decorator.
   - If you use the `#!python @output()` decorator, make sure it is above the `#!python @render.plot()` decorator.

[See here for more details.](https://shiny.posit.co/py/components/outputs/plot-matplotlib/#details)