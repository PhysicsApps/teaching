import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
from shiny import App, render, ui, reactive

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons("dimensions",
                               "Dimensions", choices=["1D", "2D"], selected="2D", inline=True),
        ui.input_slider(
            "n_steps",
            "Number of steps",
            min=1,
            max=200,
            value=100,
            step=1,
        ),
        ui.input_slider(
            "n_trials",
            "Number of trials",
            min=1,
            max=200,
            value=100,
            step=1,
        ),
        ui.input_slider(
            "alpha",
            "Line Opacity",
            min=0.01,
            max=1.0,
            value=0.2,
            step=0.01,
        ),
        ui.input_checkbox(
            'show_mean_distance',
            'Show Mean Distance',
            value=True,
        ),
        ui.input_checkbox(
            "show_colors",
            "Color each trial differently",
            value=False,
        ),
        ui.input_dark_mode(id='dark_mode'),
        open='always',
    ),
    ui.layout_columns(
        ui.output_plot(
            "plot",
            width="100%", height="700px"
        ),
    ),
)

def server(input, output, session):
    @reactive.calc
    def get_sim():
        n_steps = input.n_steps()
        n_trials = input.n_trials()

        if input.dimensions() == "1D":
            results = np.zeros((n_steps + 1, n_trials))
            for trial in range(n_trials):
                steps = np.random.choice([-1, 1], size=n_steps)
                results[1:, trial] = np.cumsum(steps)
        else:  # 2D
            results = np.zeros((n_steps + 1, 2, n_trials))
            for trial in range(n_trials):
                direction = np.random.choice([0, 1, 2, 3], size=n_steps)
                lr_steps = np.where(direction == 0, 1, np.where(direction == 1, -1, 0))
                ud_steps = np.where(direction == 2, 1, np.where(direction == 3, -1, 0))
                results[1:, 0, trial] = np.cumsum(lr_steps)
                results[1:, 1, trial] = np.cumsum(ud_steps)

        return results

    @render.plot()
    def plot():
        if input.dark_mode() == "dark":
            style_label = 'dark_background'
            blue = 'lightsteelblue'
            red = 'lightcoral'
        else:
            style_label = 'seaborn-v0_8'
            blue = 'navy'
            red = 'firebrick'

        with plt.style.context(style_label):
            fig, ax = plt.subplots()

            results = get_sim()
            n_trials = results.shape[-1]

            if input.dimensions() == "1D":
                for trial in range(n_trials):
                    if input.show_colors():
                        ax.plot(results[:, trial], alpha=input.alpha(), color=plt.cm.viridis(trial / n_trials))
                    else:
                        ax.plot(results[:, trial], color=blue, alpha=input.alpha())

                if input.show_mean_distance():
                    mean_distance = np.mean(results**2, axis=1)
                    ax.plot(np.sqrt(mean_distance), color=red, linewidth=2, label='Mean Distance')
                ax.legend()

                max_dist = np.abs(results).max()
                ax.set_ylim(-max_dist * 1.1, max_dist * 1.1)
                ax.set_xlabel('Steps')
                ax.set_ylabel('Position')
            else: # 2D
                for trial in range(n_trials):
                    if input.show_colors():
                        ax.plot(results[:, 0, trial], results[:, 1, trial], alpha=input.alpha(), color=plt.cm.viridis(trial / n_trials))
                    else:
                        ax.plot(results[:, 0, trial], results[:, 1, trial], alpha=input.alpha(), color=blue)
                if input.show_mean_distance():
                    mean_distance = np.mean(results[:, 0, :]**2 + results[:, 1, :]**2, axis=1)
                    ax.add_patch(Circle((0, 0), np.sqrt(mean_distance[-1]), color=red, fill=False, linewidth=2, label='Mean Distance'))
                    ax.legend()
                max_dist = np.abs(results).max()
                ax.set_xlim(-max_dist * 1.1, max_dist * 1.1)
                ax.set_ylim(-max_dist * 1.1, max_dist * 1.1)
                ax.set_xlabel('Position X')
                ax.set_ylabel('Position Y')
                ax.set_aspect('equal')
        return fig

app = App(app_ui, server, debug=True)
