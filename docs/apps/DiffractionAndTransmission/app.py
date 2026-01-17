import numpy as np
import plotly.graph_objects as go
from shiny import App, ui, render
from shinywidgets import output_widget, render_widget


app_ui = ui.page_fillable(
    ui.layout_columns(
        ui.card(
            ui.card(
                ui.card_header("Medium 1"),
                ui.input_slider("n_1", "Index of refraction", 0.0, 5.0, 1.0),
            ),
            ui.card(
                ui.card_header("Reflected wave"),
                ui.output_text("reflexion"),
                ui.input_switch("show_reflected_wave", "Show reflected wave", False),
            ),
            ui.card(
                ui.card_header("Incident wave"),
                ui.input_slider("k_abs", "k-vector length", 0.0, 5.0, 1.0),
                ui.input_slider("k_angle", "k-vector angle", 0.0, 90.0, 0.0),
                ui.input_radio_buttons("polarisation", "Polarisation", {"perp": "Perpendicular", "parallel": "Parallel"}),
                ui.input_switch("show_incident_wave", "Show incident wave", True),
            ),

            ui.input_dark_mode(id='dark_mode'),
            open='always',
            width = "35%"
        ),
        ui.card(
            output_widget(
                "plot_field",
                width="600px", height="600px"
            ),
        ),
        ui.card(
            ui.card(
                ui.card_header("Medium 2"),
                ui.input_slider("n_2", "Index of refraction", 0.0, 5.0, 1.0),
                ui.input_slider("n_2_imag", "imaginary part of index of refraction", 0.0, 1.0, 0.0),
            ),
            ui.card(
                ui.card_header("Transmitted wave"),
                ui.output_text("transmission"),
                ui.input_switch("show_transmitted_wave", "Show transmitted wave", True),
            ),
            ui.input_switch("Run", "Run simulation", False),
        ),
        col_widths=(3, 6, 3),
    ),
)

def server(input, output, session):

    grey_bg = 'rgb(28, 30, 32)'
    x = np.linspace(-10, 10, 201)
    y = np.linspace(-10, 10, 201)
    x_mat, y_mat = np.meshgrid(x, y)
    roi_medium_1 = x_mat < 0
    roi_medium_2 = x_mat >= 0

    @render.text
    def transmission():
        return "Transmission"

    @render.text
    def reflexion():
        return "Reflexion"

    def calculate_fields():
        a_inc = 1

        k_inc_abs = input.k_abs()
        k_inc_angle = input.k_angle()/180 * np.pi

        k_inc = k_inc_abs * np.array([np.cos(k_inc_angle), np.sin(k_inc_angle)])

        n_1 = input.n_1()
        n_2 = input.n_2() #+ 1j*input.n_2_imag()

        k_refl = np.array([-k_inc[0], k_inc[1]])

        #ui.notification_show(np.shape(k_inc), duration=None)
        help_k = np.sqrt((n_2/n_1)**2 * (k_inc[0]**2 + k_inc[1]**2)) - k_inc[1]**2
        k_trans = np.array([help_k, k_inc[1]])

        alpha = np.atan2(k_inc[1], k_inc[0])
        beta = np.asin(np.sin(alpha)*n_1/n_2)

        if input.polarisation == "perp":
            # perpendicular polarisation
            a_trans = 2*n_1*np.cos(alpha) / (n_1*np.cos(alpha) + n_2*np.cos(beta))
            a_refl = (n_1*np.cos(alpha)-n_2*np.cos(beta)) / (n_1*np.cos(alpha) + n_2*np.cos(beta))
        else:
            # parallel polarisation
            a_trans = 2*n_1*np.cos(alpha) / (n_2*np.cos(alpha) + n_1*np.cos(beta))
            a_refl = (n_2*np.cos(alpha)-n_1*np.cos(beta)) / (n_2*np.cos(alpha) + n_1*np.cos(beta))

        e_inc = a_inc * np.exp(1j * (k_inc[0] * x_mat + k_inc[1] * y_mat))
        e_refl = a_refl * np.exp(1j * (k_refl[0] * x_mat + k_refl[1] * y_mat))
        e_trans = a_trans * np.exp(1j * (k_trans[0] * x_mat + k_trans[1] * y_mat))

        e_inc[roi_medium_2] = 0
        e_refl[roi_medium_2] = 0
        e_trans[roi_medium_1] = 0

        e_tot = np.zeros_like(e_inc, dtype=complex)

        if input.show_incident_wave():
            e_tot += e_inc

        if input.show_reflected_wave():
            e_tot += e_refl

        if input.show_transmitted_wave():
            e_tot += e_trans

        return e_tot

    @render_widget
    def plot_field():
        if input.dark_mode() == "dark":
            template = 'plotly_dark'
            bg_color = grey_bg
        else:
            template = 'plotly_white'
            bg_color = 'white'

        e_tot = calculate_fields()

        fig = go.Figure(go.Surface(
            x=x,
            y=y,
            z=np.real(e_tot),
        ))

        fig.update_layout(
            template=template,
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            scene=dict(
                xaxis_title="x",
                yaxis_title="y",
                xaxis=dict(range=[-10, 10]),
                yaxis=dict(range=[-10, 10]),
                camera=dict(
                    eye=dict(x=-1.6, y=-1.6, z=0.5),
                    center=dict(x=0, y=0, z=0.0),
                    # up=dict(x=0, y=0, z=1),
                ),
            ),

            width=600,
            height=600,
            margin={"r": 0, "t": 0, "l": 0, "b": 60},
            showlegend=False,
        )

        return fig


app = App(app_ui, server, debug=True)