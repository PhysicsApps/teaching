import numpy as np
import plotly.graph_objects as go
from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("sigma", "Sigma (s)", min=0, max=20, value=10, step=0.1),
        ui.input_slider("beta", "Beta (b)", min=0, max=5, value=8/3, step=0.01),
        ui.input_slider("rho", "Rho (r)", min=0, max=50, value=28, step=0.5),
        ui.input_slider("n", "Number of points", min=10, max=500, value=100, step=10),
        ui.input_slider("dt", "Time step (dt)", min=0.001, max=0.05, value=0.015, step=0.001),
    ),
    ui.output_ui("plot", height="100%")
)



def server(input: Inputs, output: Outputs, session: Session):

    @render.ui
    def plot():
        s = input.sigma()
        b = input.beta()
        r = input.rho()
        dt = input.dt()

        n = input.n()

        fig = go.Figure(
        )

        plot_html = fig.to_html(
            auto_play=False,
            include_plotlyjs=True,
            full_html=False,
            div_id="animated_plot"
        )

        loop_script = f"""
        <script>
        (function () {{
          // ----- DESTROY PREVIOUS INSTANCE -----
          if (window.lorenzAnimation) {{
            cancelAnimationFrame(window.lorenzAnimation.frameId);
            Plotly.purge('animated_plot');
            window.lorenzAnimation = null;
          }}

          // ----- CREATE NEW INSTANCE -----
          var controller = {{
            frameId: null
          }};
          window.lorenzAnimation = controller;

          var n = {n};
          var x = [], y = [], z = [];
          var dt = {dt};

          var s = {s};
          var b = {b};
          var r = {r};

          for (var i = 0; i < n; i++) {{
            x[i] = Math.random() * 2 - 1;
            y[i] = Math.random() * 2 - 1;
            z[i] = 30 + Math.random() * 10;
          }}

         Plotly.react('animated_plot', [{{
            x: x,
            y: z,
            mode: 'markers',
          }}], {{
            xaxis: {{
              range: [-40, 40],
            }},
            yaxis: {{
              range: [0, 60],
            }}
          }});


          function compute () {{
            for (var i = 0; i < n; i++) {{
              var dx = s * (y[i] - x[i]);
              var dy = x[i] * (r - z[i]) - y[i];
              var dz = x[i] * y[i] - b * z[i];

              x[i] += dx * dt;
              y[i] += dy * dt;
              z[i] += dz * dt;
            }}
          }}

          function update () {{
            compute();

            Plotly.animate('animated_plot', {{
              data: [{{ x: x, y: z }}]
            }}, {{
              transition: {{ duration: 0 }},
              frame: {{ duration: 0, redraw: false }}
            }});

            controller.frameId = requestAnimationFrame(update);
          }}

          controller.frameId = requestAnimationFrame(update);
        }})();
        </script>
        """

        return ui.HTML(plot_html + loop_script)


app = App(app_ui, server)