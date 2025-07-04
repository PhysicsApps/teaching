from shiny.express import input, ui, render
from shiny import reactive
import numpy as np
import matplotlib.pyplot as plt
import math
import re

with ui.sidebar():
    ui.input_text(
        "function",
        "Function f(x)",
        value="cos(x)",
        placeholder="Enter function like: sin(x), cos(x), exp(x), x**2, etc."
    )
    ui.input_slider(
        "order",
        "Taylor Expansion Order",
        min=0,
        max=10,
        value=2,
        step=1,
        animate=True
    )
    ui.input_slider(
        "center",
        "Expansion Center",
        min=-4,
        max=4,
        value=0,
        step=0.1
    )
    ui.input_slider(
        "x_range",
        "X-axis Range",
        min=1,
        max=10,
        value=2 * np.pi,
        step=0.1
    )
    ui.input_checkbox(
        'show_contrib',
        'Show Contributions',
        value=False,
    )

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
        'abs': 'np.abs'
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
    x_range = input.x_range()
    x = np.linspace(-x_range, x_range, 1024 + 1)

    try:
        # Create a safe namespace for evaluation
        namespace = {'x': x, 'np': np, 'pi': np.pi, 'e': np.e}
        y = eval(func_str, {"__builtins__": {}}, namespace)
        return x, y, func_str
    except Exception as e:
        # Return a default function if evaluation fails
        return x, np.cos(x), "cos(x)"


@reactive.calc
def calculate_derivatives():
    """Calculate numerical derivatives using numpy gradients"""
    x, y, func_str = evaluate_function()
    a = input.center()

    # Find the index closest to the expansion center
    center_idx = np.argmin(np.abs(x - a))

    # Calculate derivatives using numpy gradient
    derivatives = [y]  # 0th derivative is the function itself
    current_derivative = y

    # Calculate up to the required order
    for i in range(input.order()):
        # Calculate numerical derivative
        current_derivative = np.gradient(current_derivative, x)
        derivatives.append(current_derivative)

    # Extract derivative values at the expansion center
    derivative_values = []
    for deriv in derivatives:
        derivative_values.append(deriv[center_idx])

    return derivative_values


@render.plot
def taylor_plot():
    x, y_true, func_str = evaluate_function()
    a = input.center()
    order = input.order()
    derivative_values = calculate_derivatives()

    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot original function
    ax.plot(x, y_true, 'b-', linewidth=2, label=f'f(x) = {func_str}', alpha=0.8)

    # Calculate Taylor expansion
    y_taylor_terms = []
    for n in range(order + 1):
        # Add nth term of Taylor series
        y_taylor_terms.append(derivative_values[n] * ((x - a) ** n) / math.factorial(n))
        if input.show_contrib():
            ax.plot(x, y_taylor_terms[n], 'k--', linewidth=1, alpha=0.5)

    y_taylor = np.sum(y_taylor_terms, axis=0)

    # Plot Taylor approximation
    ax.plot(x, y_taylor, 'r--', linewidth=2,
            label=f'Taylor approximation (order {order})', alpha=0.8)

    # Mark the expansion center
    ax.axvline(x=a, color='green', linestyle=':', alpha=0.7,
               label=f'Expansion center (x={a:.2f})')

    # Mark the point on the original function at expansion center
    center_idx = np.argmin(np.abs(x - a))
    ax.plot(a, y_true[center_idx], 'go', markersize=8, alpha=0.7)

    # Formatting
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    # ax.set_title(f'Taylor Expansion of {func_str} around x = {a:.2f}')
    ax.grid(True, alpha=0.3)
    # ax.legend()

    # Set reasonable y-limits based on the data
    y_min = np.min(y_true)
    y_max = np.max(y_true)
    y_range = y_max - y_min
    ax.set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)

    return fig
