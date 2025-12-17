import numpy as np
import plotly.graph_objects as go
from shiny import App, Inputs, Outputs, Session, render, ui


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider('amplitude', 'Amplitude', min=0.1, max=2, value=1, step=0.1),
        ui.input_dark_mode(id="dark_mode")
    ),
    ui.output_ui("plot", height='100%')
)

def server(input: Inputs, output: Outputs, session: Session):
    x = np.linspace(0, 2 * np.pi, 100)

    @render.ui
    def plot():
        # Set template based on dark mode
        template = "plotly_dark" if input.dark_mode() == "dark" else "plotly_white"

        amp = input.amplitude()

        fig = go.Figure(
            data=[go.Scatter(x=x, y=amp * np.sin(x))],
            frames=[
                go.Frame(data=[go.Scatter(y=amp * np.sin(x + i / 10))])
                for i in range(60)
            ]
        )

        fig.update_layout(
            template=template,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False
        )

        # Generate Plotly HTML without full document wrapper
        plot_html = fig.to_html(
            include_plotlyjs="cdn",
            full_html=False,
            div_id="animated_plot"
        )

        # JavaScript to force infinite looping
        loop_script = """
        <script>
        (function () {
            const gd = document.getElementById("animated_plot");

            function loop() {
                Plotly.animate(gd, null, {
                    frame: { duration: 50, redraw: true },
                    transition: { duration: 0 }
                }).then(loop);
            }

            // Wait until Plotly is fully initialized
            if (gd && gd.data) {
                loop();
            } else {
                gd.on('plotly_afterplot', loop);
            }
        })();
        </script>
        """

        return ui.HTML(plot_html + loop_script)

app = App(app_ui, server)