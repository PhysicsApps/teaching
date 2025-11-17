import numpy as np
import plotly.graph_objects as go
import re
from shiny import App, Inputs, Outputs, Session, render, ui, reactive

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text(
            "function_x",
            "F_x",
            value="e^(-y^2)  *  e^(-z^2)",
            placeholder="Enter function like: sin(x) * cos(y).",
            update_on='blur',
        ),
        ui.input_text(
            "function_y",
            "F_y",
            value="0",
            placeholder="Enter function like: sin(x) * cos(y).",
            update_on='blur',
        ),
        ui.input_text(
            "function_z",
            "F_z",
            value="0",
            placeholder="Enter function like: sin(x) * cos(y).",
            update_on='blur',
        ),
        ui.input_checkbox('show_curl', 'Show Curl', value=True),
        ui.input_dark_mode(id='dark_mode'),
    ),
    ui.output_ui("plot")
)


def server(input: Inputs, output: Outputs, session: Session):
    num_pix = 16
    limit = np.pi
    x_axis = np.linspace(-limit, limit, num_pix)
    y_axis = np.linspace(-limit, limit, num_pix)
    z_axis = np.linspace(-limit, limit, num_pix)
    x, y, z = np.meshgrid(x_axis, y_axis, z_axis)
    # z = np.zeros_like(x)

    @reactive.calc
    def clean_function():
        """Clean and validate the input function"""
        func_strings = []
        # Replace common mathematical functions with numpy equivalents
        replacements = {
            r'\b(sin)\b': 'np.sin',
            r'\b(cos)\b': 'np.cos',
            r'\b(tan)\b': 'np.tan',
            r'\b(exp)\b': 'np.exp',
            r'\b(log)\b': 'np.log',
            r'\b(sqrt)\b': 'np.sqrt',
            r'\b(abs)\b': 'np.abs',
            r'\^': '**',  # escaped caret for literal match
        }

        for func_str in [input.function_x().strip(),
                         input.function_y().strip(),
                         input.function_z().strip()]:

           # Apply all replacements
            for pattern, replacement in replacements.items():
                func_str = re.sub(pattern, replacement, func_str)

            func_strings.append(func_str)
        return func_strings

    @reactive.calc
    def evaluate_function():
        """Evaluate the function at given x values"""
        func_strings = clean_function()

        results = []
        ones = np.ones_like(x) # force correct output dimension
        for func_str in func_strings:
            try:
                # Create a safe namespace for evaluation
                namespace = {'x': x, 'y': y, 'z': z, 'np': np, 'pi': np.pi, 'e': np.e}
                f = eval(func_str, {"__builtins__": {}}, namespace)
                results.append(ones * f)
            except Exception as e:
                # Return a default function if evaluation fails
                ui.notification_show(f"Error evaluating function: {func_str}.", duration=10,
                                     type="error")
                results.append(ones * 0)
        return results

    @render.ui
    def plot():
        # Set template based on dark mode
        if input.dark_mode() == "dark":
            template = "plotly_dark"
        else:
            template = "plotly_white"

        fx, fy, fz = evaluate_function()

        # Create 3D surface plot
        fig = go.Figure()

        if input.show_curl():
            curl_x, curl_y, curl_z = get_curl(x, y, z, fx, fy, fz)
            fig.add_trace(
                go.Cone(
                    x=x.flatten(),
                    y=y.flatten(),
                    z=z.flatten(),
                    u=curl_x.flatten(),
                    v=curl_y.flatten(),
                    w=curl_z.flatten(),
                    sizemode="raw",
                    anchor="tail",
                    hoverinfo='skip',
                )
            )
        else:
            fig.add_trace(
                go.Cone(
                    x=x.flatten(),
                    y=y.flatten(),
                    z=z.flatten(),
                    u=fx.flatten(),
                    v=fy.flatten(),
                    w=fz.flatten(),
                    sizemode="raw",
                    anchor="tail",
                    hoverinfo='skip',
                )
            )

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

def get_curl(x,y,z,u,v,w):
    dx = x[0,:,0]
    dy = y[:,0,0]
    dz = z[0,0,:]

    dummy, dFx_dy, dFx_dz = np.gradient (u, dx, dy, dz, axis=[1,0,2])
    dFy_dx, dummy, dFy_dz = np.gradient (v, dx, dy, dz, axis=[1,0,2])
    dFz_dx, dFz_dy, dummy = np.gradient (w, dx, dy, dz, axis=[1,0,2])

    rot_x = dFz_dy - dFy_dz
    rot_y = dFx_dz - dFz_dx
    rot_z = dFy_dx - dFx_dy

    return rot_x, rot_y, rot_z

app = App(app_ui, server)
