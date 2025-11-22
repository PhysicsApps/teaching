import numpy as np
import plotly.graph_objects as go
import re
from shiny import App, Inputs, Outputs, Session, render, ui, reactive

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("q", "Mass Ratio (q)", min=0.0, max=1.0, value=0.05, step=0.01),
        # ui.input_slider("x", "x", min=0.0, max=2.0, value=1.0, step=0.01),
        ui.input_dark_mode(id='dark_mode'),
    ),
    ui.output_ui("plot")
)

def server(input: Inputs, output: Outputs, session: Session):
    @render.ui
    def plot():
        # Set template based on dark mode
        if input.dark_mode() == "dark":
            template = "plotly_dark"
        else:
            template = "plotly_white"

        fig = go.Figure()
        # Add isosurface representing the potential field
        x, y = np.meshgrid(np.linspace(-2, 2, 256),
                           np.linspace(-2, 2, 256))
        z = np.zeros_like(x)

        q = input.q()
        # x_pos = input.x()
        values = (x - q/(1+q))**2 + y**2 + 2/((1+q)*np.sqrt(x**2 + y**2 + z**2)) + 2*q/((1+q)*np.sqrt((x-1)**2 + y**2 + z**2))


        values -= np.min(values)
        min_value = 1.5
        values[values > min_value] = np.nan  # Mask values above a certain threshold

        fig.add_trace(go.Surface(
            contours = {
                "z": {"show": True, "start": -min_value, "end": 0.01, "size": 0.05}
            },
            x=x,
            y=y,
            z=-values,  # Offset for better visibility
            colorscale='turbo',
            colorbar_title_text='f(x,y)',
            showscale=True,
            hoverinfo='skip'
        ))

        # Set layout
        fig.update_layout(
            template=template,
            scene=dict(
                xaxis_title='X-axis',
                yaxis_title='Y-axis',
                zaxis_title='Z-axis',
                xaxis_showspikes=False,
                yaxis_showspikes=False,
                zaxis_showspikes=False,
            ),
            height=700,
            margin=dict(l=0, r=0, t=0, b=0),
        )

        return ui.HTML(fig.to_html())

app = App(app_ui, server)
