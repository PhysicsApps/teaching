import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from palmerpenguins import load_penguins
from shiny import App, render, ui, reactive

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.output_plot(
            "charge_density_plot",
            #click=True,
            width="100%", height="700px"
        ),
        ui.input_checkbox(
            'monopole',
            'Monopole',
            value=False,
        ),
        ui.input_checkbox(
            'dipole',
            'Dipole',
            value=False,
        ),
        ui.input_checkbox(
            'quadrupole',
            'Quadrupole',
            value=False,
        ),
        ui.input_dark_mode(id='dark_mode'),
        open='always',
    ),
    ui.layout_column_wrap(
        ui.output_plot(
            "monopole_plot",
            width="100%", height="700px"
        ),
        ui.output_plot(
            "dipole_plot",
            width="100%", height="700px"
        ),
    ),
    ui.layout_column_wrap(
        ui.output_plot(
            "quadrupole_plot",
            width="100%", height="700px"
        ),
        ui.output_plot(
            "sum_plot",
            width="100%", height="700px"
        ),
    ),
)

def server(input, output, session):
    # some overall definitions and stuff
    click_data = reactive.value(None)
    blue = 'navy'
    red = 'firebrick'

    x_axis = np.linspace(-20, 20, 1024)
    x_axis_lims = (-5, 5)

    # Update click data when plot is clicked
    # @reactive.effect
    # def _():
        # if input.fourier_plot_click() is not None:
            # click_data.set(input.fourier_plot_click())
            # ui.update_slider('event_x', value=input.fourier_plot_click()['x'])
            # ui.update_slider('event_y', value=input.fourier_plot_click()['y'])
            # One could actually calculate everything here and then only use the resulting data in the plots



    @render.plot()
    def charge_density_plot():
        if input.dark_mode() == "dark":
            style_label = 'dark_background'
            blue = 'lightsteelblue'
            red = 'lightcoral'
        else:
            style_label = 'seaborn-v0_8'
            blue = 'navy'
            red = 'firebrick'

        with plt.style.context(style_label):
            if input.monopole:
                pointlike_r = [0, 0, 0]
                pointlike_charge = [red]
            if input.dipole:
                pointlike_r = [[-1, 0, 0],[1, 0, 0]]
                pointlike_charge = [red, blue]
            if input.quadrupole:
                pointlike_r = [[0, 1, 0],[0, -1, 0],[-1, 0, 0],[1, 0, 0]]
                pointlike_charge = [red, red, blue, blue]

            fig, axs = plt.subplots()
            axs.set_xlim(-1.5, 1.5)
            axs.set_ylim(-1.5, 1.5)
            axs.set_zlim(-1.5, 1.5)

            hs = axs.scatter(pointlike_r, color=pointlike_charge, x='X', y='Y', z='Z')

            axs.set_title("Charge density")

        return fig

    @render.plot()
    def monopole_plot():
        df = load_penguins()
        mass = df["body_mass_g"]

        fig, ax = plt.subplots()
        ax.hist(mass, input.n(), density=True)
        ax.set_title("Palmer Penguin Masses")
        ax.set_xlabel("Mass (g)")
        ax.set_ylabel("Density")

    @render.plot()
    def dipole_plot():
        df = load_penguins()
        mass = df["body_mass_g"]

        fig, ax = plt.subplots()
        ax.hist(mass, input.n(), density=True)
        ax.set_title("Palmer Penguin Masses")
        ax.set_xlabel("Mass (g)")
        ax.set_ylabel("Density")

    @render.plot()
    def quadrupole_plot():
        df = load_penguins()
        mass = df["body_mass_g"]

        fig, ax = plt.subplots()
        ax.hist(mass, input.n(), density=True)
        ax.set_title("Palmer Penguin Masses")
        ax.set_xlabel("Mass (g)")
        ax.set_ylabel("Density")

    @render.plot()
    def sum_plot():
        df = load_penguins()
        mass = df["body_mass_g"]

        fig, ax = plt.subplots()
        ax.hist(mass, input.n(), density=True)
        ax.set_title("Palmer Penguin Masses")
        ax.set_xlabel("Mass (g)")
        ax.set_ylabel("Density")

app = App(app_ui, server, debug=True)
