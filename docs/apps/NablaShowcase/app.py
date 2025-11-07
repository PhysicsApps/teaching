import numpy as np
import plotly.graph_objects as go
import re
from shiny import App, Inputs, Outputs, Session, render, ui, reactive

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text(
            "function",
            "Function f(x)",
            value="e**(-x**2 - y**2) * sin(x)",
            placeholder="Enter function like: sin(x) * cos(y)."
        ),
        ui.input_checkbox('show_gradient', 'Show Gradient', value=True),
        ui.input_checkbox('align_gradient', 'Align Gradient', value=True),
        ui.input_dark_mode(id='dark_mode'),
        open='always'
    ),
    ui.card(ui.output_ui("plot"), full_screen=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    num_pix = 100
    limit = 5
    x_axis = np.linspace(-limit, limit, num_pix)
    y_axis = np.linspace(-limit, limit, num_pix)
    x, y = np.meshgrid(x_axis, y_axis)

    @reactive.calc
    def clean_function():
        """Clean and validate the input function"""
        func_str = input.function().strip()

        # Replace common mathematical functions with numpy equivalents
        replacements = {
            'sin': 'np.sin',
            'cos': 'np.cos',
            'tan': 'np.tan',
            'exp': 'np.exp',
            'log': 'np.log',
            'sqrt': 'np.sqrt',
            'abs': 'np.abs',
        }

        # Apply replacements only to function names (not as part of other words)
        for old, new in replacements.items():
            func_str = re.sub(r'\b' + old + r'\b', new, func_str)

        # Replace 'x' with the actual variable name for evaluation
        return func_str

    @reactive.calc
    def evaluate_function():
        """Evaluate the function at given x values"""
        func_str = clean_function()
        try:
            # Create a safe namespace for evaluation
            namespace = {'x': x, 'y': y, 'np': np, 'pi': np.pi, 'e': np.e}
            f = eval(func_str, {"__builtins__": {}}, namespace)
            return f, func_str
        except Exception as e:
            # Return a default function if evaluation fails
            ui.notification_show(f"Error evaluating function: {func_str}. Using default e**(-x**2).", duration=10,
                                 type="error")
            return np.e**(-x**2 - y**2) * np.sin(x), "e**(-x**2 - y**2) * sin(x)"

    @render.ui
    def plot():
        f, func_str = evaluate_function()

        gradient = np.gradient(f)


        # Set template based on dark mode
        if input.dark_mode() == "dark":
            template = "plotly_dark"
        else:
            template = "plotly_white"


        skip = (slice(None, None, 1), slice(None, None, 1))  # Skip some points for clarity
        # Create 3D surface plot
        fig = go.Figure(data=[
            go.Cone(
                x=x[skip].flatten(),
                y=y[skip].flatten(),
                z=f[skip].flatten() if input.align_gradient() else np.zeros_like(f[skip].flatten()),
                u=gradient[1][skip].flatten(),
                v=gradient[0][skip].flatten(),
                w=np.sqrt(gradient[0][skip].flatten() ** 2 + gradient[1][skip].flatten() ** 2) if input.align_gradient() else np.zeros_like(gradient[0][skip].flatten()),
                sizemode="absolute",
                sizeref=0.2,
                anchor="tip",
                # colorscale='portland',
                # showscale=True,
            )
            if input.show_gradient() else
            go.Surface(
                x=x,
                y=y,
                z=f,
                colorscale='turbo',
                colorbar_title_text='f(x,y)',
                showscale=True,
            ),
        ])

        fig.update_layout(
            template=template,
            scene=dict(
                xaxis_title='X-axis',
                yaxis_title='Y-axis',
                zaxis_title='f(x,y)',
            ),
            height=700,
            margin=dict(l=0, r=0, t=0, b=0),
        )

        return ui.HTML(fig.to_html())


app = App(app_ui, server)
