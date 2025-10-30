import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from shiny import App, render, ui, reactive

# plt.style.use('seaborn-v0_8')

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider(
            "velocity",
            "Velocity (units of c)",
            min=-0.99,
            max=0.99,
            value=0,
            step=0.01,
            animate=True
        ),
        ui.input_checkbox(
            'show_minkowski',
            'Minkowski Metric',
            value=True,
        ),
        ui.input_checkbox(
            'show_isolines',
            'Isolines',
            value=True,
        ),
        open='always'
    ),
    ui.output_plot(
        "plot",
        click=True,
        width="100%", height="700px"
    ),
    ui.output_text("event_params"),
)

def server(input, output, session):
    click_data = reactive.value(None)
    x_ct_axis = np.linspace(-5, 5, 251)
    metric_x, metric_ct = np.meshgrid(x_ct_axis, x_ct_axis)
    minkowski_metric = metric_ct**2 - metric_x**2

    blue = 'navy'
    red = 'firebrick'
    # Update click data when plot is clicked
    @reactive.effect
    def _():
        if input.plot_click() is not None:
            click_data.set(input.plot_click())

    @render.plot()
    def plot():
        v = input.velocity()

        fig, ax = plt.subplots()
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(base=1))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(base=1))
        tick_positions = ax.get_xticks()

        if input.show_minkowski():
            img = ax.imshow(np.sqrt(np.abs(minkowski_metric)) * np.sign(minkowski_metric), extent=(-5, 5, -5, 5),
                            origin='lower', cmap='RdBu', alpha=0.3)
            cbar=fig.colorbar(img, ax=ax, label=r'Eigenzeit $\sqrt{(c^2t^2 - x^2)}$', ticks=tick_positions)
            cbar.ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{-int(x)}i" if x < 0 else f"{int(x)}"))


        if input.show_isolines():
            for tick_pos in tick_positions:
                if tick_pos <= 0:
                    continue
                x0 = np.sqrt(x_ct_axis ** 2 + tick_pos ** 2)
                ax.plot(x0, x_ct_axis, color='grey', linestyle='--', alpha=0.5)
                ax.plot(-x0, x_ct_axis, color='grey', linestyle='--', alpha=0.5)
                ax.plot(x_ct_axis, x0, color='grey', linestyle='--', alpha=0.5)
                ax.plot(x_ct_axis, -x0, color='grey', linestyle='--', alpha=0.5)

        # Draw axes
        ax.axhline(0, color=blue)
        ax.axvline(0, color=blue)
        # Apply Lorentz transformation to axes
        if v != 0:
            x_axis_transformed, ct_axis_transformed = lorentz_transform(x_ct_axis, np.zeros_like(x_ct_axis), v)
            ax.plot(x_axis_transformed, ct_axis_transformed, color=red)
            ax.plot(ct_axis_transformed, x_axis_transformed, color=red)

        # Draw intersections of isolines and axes
        for tick_pos in tick_positions:
            if tick_pos == 0:
                continue
            x_axis_transformed, ct_axis_transformed = lorentz_transform(tick_pos, 0, v)
            ax.plot(x_axis_transformed, ct_axis_transformed, 'o', color=red)
            ax.plot(ct_axis_transformed, x_axis_transformed, 'o', color=red)

            ax.plot(tick_pos, 0, 'o', color=blue)
            ax.plot(0, tick_pos, 'o', color=blue)

        stored_click = click_data()
        if stored_click is not None:
            eventx, eventy = stored_click["x"], stored_click["y"]
            ax.scatter(eventx, eventy, color='green')
            # Draw lines from click to axes
            ax.plot([eventx, eventx], [0, eventy], color=blue, linestyle=':')
            ax.plot([0, eventx], [eventy, eventy], color=blue, linestyle=':')

            x_transformed, y_transformed = lorentz_transform(eventx, eventy, -v)

            # Draw lines to transformed axes
            ref_x_transformed, ref_ct_transformed = lorentz_transform(x_transformed, 0, v)
            ax.plot([ref_x_transformed, eventx], [ref_ct_transformed, eventy], color=red, linestyle=':')
            ref_x_transformed, ref_ct_transformed = lorentz_transform(0, y_transformed, v)
            ax.plot([ref_x_transformed, eventx], [ref_ct_transformed, eventy], color=red, linestyle=':')

        ax.set_xlabel("x")
        ax.set_ylabel("ct")
        ax.set_aspect('equal')
        return fig

    @render.text()
    def event_params():
        stored_click = click_data()
        if stored_click is None:
            return "Click on the plot to select an event."

        eventx, eventy = stored_click["x"], stored_click["y"]
        return (f"Event coordinates:\n"
                f"  In rest frame: x = {eventx:.2f}, ct = {eventy:.2f}\n")

def lorentz_transform(x, t, v):
    c = 1 # velocity of light v will be in units of c
    gamma = 1 / (1 - (v**2 / c**2))**0.5
    x_prime = gamma * (x + v * t)
    t_prime = gamma * (t + (v * x) / c**2)
    return x_prime, t_prime

app = App(app_ui, server, debug=True)
