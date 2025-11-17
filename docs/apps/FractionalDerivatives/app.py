import numpy as np
import matplotlib.pyplot as plt
import re
from shiny import App, Inputs, Outputs, Session, render, ui, reactive

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text(
            "function",
            "Function f(x)",
            value="e**(-x**2)",
            placeholder="Enter function like: sin(x), cos(x), exp(x), x**2, etc.",
            update_on='blur',
        ),
        ui.input_slider(
            "order",
            "Derivative order",
            min=0,
            max=4,
            value=1,
            step=0.1,
            animate=True
        ),
        ui.input_dark_mode(id='dark_mode'),
        open='always'
    ),
    ui.output_plot("plot", width="100%", height="800px"),
)


def server(input: Inputs, output: Outputs, session: Session):
    xrange = 10  # Fixed x-range for plotting
    factor = 10  # Oversampling factor for better accuracy
    npix_real = int(2**14) + 1

    @reactive.calc
    def clean_function():
        """Clean and validate the input function"""
        func_str = input.function().strip()

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

        # Apply all replacements
        for pattern, replacement in replacements.items():
            func_str = re.sub(pattern, replacement, func_str)

        return func_str

    @reactive.calc
    def evaluate_function():
        """Evaluate the function at given x values"""
        func_str = clean_function()

        x = np.linspace(-xrange*factor, xrange*factor, npix_real)
        try:
            # Create a safe namespace for evaluation
            namespace = {'x': x, 'np': np, 'pi': np.pi, 'e': np.e}
            y = eval(func_str, {"__builtins__": {}}, namespace)
            return x, y, func_str
        except Exception as e:
            # Return a default function if evaluation fails
            ui.notification_show(f"Error evaluating function: {func_str}. Using default e**(-x**2).", duration=10, type="error")
            return x, np.exp(-x**2), "e**(-x**2)"


    @render.plot()
    def plot():
        if input.dark_mode() == "dark":
            style_label = 'dark_background'
        else:
            style_label = 'seaborn-v0_8'

        with plt.style.context(style_label):
            x, y_true, func_str = evaluate_function()
            order = input.order()

            fig, ax = plt.subplots(2,1, sharex=True)

            # Plot original function
            ax[0].plot(x, y_true, linewidth=2, label=r'$f(x)$')

            # Compute non-integer derivative using Fourier transform method
            Y = np.fft.fft(y_true)
            k = np.fft.fftfreq(len(x), d=(x[1]-x[0])) * 2 * np.pi  # Angular frequency

            Y_deriv = Y * ((1j * k) ** order)
            y_deriv = np.real(np.fft.ifft(Y_deriv))

            # Plot derivative
            ax[1].plot([0], [0])  # Dummy plot to ensure proper scaling
            ax[1].plot(x, y_deriv,  linewidth=2, label=r'$f^{(' + f'{order}' + ')}(x)$')

            ax[0].set_ylabel(r'$f(x)$')
            ax[1].set_ylabel(r'$\frac{d}{dx}^{' + f'{order}' + '}f(x)$')

            ax[1].set_xlabel('x')
            # Set reasonable y-limits based on the data

            y_min = np.min(y_true[np.abs(x)<=xrange])
            y_max = np.max(y_true[np.abs(x)<=xrange])
            y_range = y_max - y_min
            ax[0].set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)

            y_min = np.min(y_deriv[np.abs(x)<=xrange])
            y_max = np.max(y_deriv[np.abs(x)<=xrange])
            y_range = y_max - y_min
            ax[1].set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)

            ax[0].set_xlim(-xrange, xrange)
            ax[1].set_xlim(-xrange, xrange)
        return fig


app = App(app_ui, server)

