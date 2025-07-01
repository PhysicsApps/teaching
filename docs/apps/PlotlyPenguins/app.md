---
authors:
  - ptuemmler
categories:
  - Search
  - Performance
date: 2025-07-01
---

# Plotly Penguins app
Quick example for a simple plotly app.
<!-- more -->
<div>
    <iframe src={{app_html()}} width="100%" height="600px"></iframe>
</div>

Plotly is an interactive graphics plotting library.

To make an interactive plot with Plotly in Shiny for Python, we will need to use the shinywidgets library to connect Shiny with ipywidgets.

To make a Plotly figure, we need to do the following steps:

Import the output_widget() and render_widget() functions from the shinywidgets library, from shinywidgets import output_widget, render_widget

Call output_widget() to the UI of your app to create a div in which to display the figure. Where you call this function will determine where the figure will appear within the layout of the app. The id parameter you provide will be used to link to other parts of the Shiny app.

Define a function within the server() function that creates the figure.

The name of the function should be the same value you passed into the id parameter in your output_widget() function call in the UI.

If your function calls reactive values, Shiny will update your figure whenever those values change, in a reactive fashion.

Decorate your plotting function with a @render_widget() decorator.
    If your plotting function is not the same as the id you used in the ui.output_widget(), you can add an additional @output(id=...) decorator.
    If you use the @output() decorator, make sure it is above the @render_widget() decorator.

Visit shiny.posit.co/py/docs/ipywidgets.html to learn more about using ipywidgets with Shiny.
