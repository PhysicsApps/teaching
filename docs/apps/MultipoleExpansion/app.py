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
            width="200px", height="200px"
        ),
        ui.input_select(
          'charge_scenario',
            "Select charge distribution",
            {"monopole": "Monopole", "dipole": "Dipole", "quadrupole": "Quadrupole"},
        ),
        # ui.output_text("value"),

        ui.input_dark_mode(id='dark_mode'),
        open='always',
    ),
    ui.layout_column_wrap(
        ui.output_plot(
            "monopole_plot",
            width="300px", height="300px"
        ),
        ui.output_plot(
            "dipole_plot",
            width="300px", height="300px"
        ),
    ),
    ui.layout_column_wrap(
        ui.output_plot(
            "quadrupole_plot",
            width="300px", height="300px"
        ),
        ui.output_plot(
            "sum_plot",
            width="300px", height="300px"
        ),
    ),
)

def server(input, output, session):
    # some overall definitions and stuff
    click_data = reactive.value(None)

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


    @render.text
    def value():
        return f"{input.charge_scenario()}"

    def set_charges():
        pointlike_r = []
        pointlike_charge = []

        blue = 'b'
        red = 'r'

        moments_Q = 0
        moments_P = np.array([[0,0,0]])
        moments_Qij = np.array([[0,0,0],[0,0,0],[0,0,0]])

        if input.charge_scenario() == "monopole":
            pointlike_r = np.array([[0, 0, 0]])
            pointlike_charge = [red]
            moments_Q = 1
        if input.charge_scenario() == "dipole":
            pointlike_r = np.array([[-1, 0, 0], [1, 0, 0]])
            pointlike_charge = [red, blue]
            moments_P = np.array([[2, 0, 0]])
        if input.charge_scenario() == "quadrupole":
            pointlike_r = np.array([[0, 1, 0], [0, -1, 0], [-1, 0, 0], [1, 0, 0]])
            pointlike_charge = [red, red, blue, blue]
            moments_Qij = np.array([[-12, 0, 0], [0, 12, 0], [0, 0, 0]])
        number_of_charges = np.shape(pointlike_r)[0]

        return pointlike_r, pointlike_charge, number_of_charges, moments_Q, moments_P, moments_Qij


    @render.plot()
    def charge_density_plot():
        if input.dark_mode() == "dark":
            style_label = 'dark_background'
        else:
            style_label = 'seaborn-v0_8'


        with plt.style.context(style_label):

            pointlike_r, pointlike_charge, number_of_charges = set_charges()

            fig, axs = plt.subplots()
            axs.set_xlim(-1.5, 1.5)
            axs.set_ylim(-1.5, 1.5)

            for idx_charge in np.arange(number_of_charges):
                #print(pointlike_charge[])
                axs.scatter(pointlike_r[idx_charge,0], pointlike_r[idx_charge,1], color=pointlike_charge[idx_charge])

            axs.set_title("Charge density")

        return fig

    @render.plot()
    def monopole_plot():

        pointlike_r, pointlike_charge, number_of_charges, moments_Q, moments_P, moments_Qij = set_charges()

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
