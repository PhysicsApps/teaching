import numpy as np
import plotly.graph_objects as go
from shiny import App, ui
from shinywidgets import output_widget, render_widget


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons(
          'polarization',
            "Polarization",
            {"lin_pol": "linear", "circ_pol": "circular"},
            inline=True,
        ),

        ui.layout_columns(
            ui.card(
                ui.card_header("Field E1 (x)"),
                ui.input_slider('E1_amp', "Amplitude", 0, 1, 0.5),
                ui.input_slider('phase1', "Phase", 0.0, 2.0, 0),
                ui.input_slider('w1', "Frequency", 1.0, 5.0, 10),
                ui.input_switch('show_E1', "Show Field", True),
            ),
            ui.card(
                ui.card_header("Field E2 (y)"),
                ui.input_slider('E2_amp', "Amplitude", 0.0, 1.0, 0),
                ui.input_slider('phase2', "Phase", 0.0, 2.0, 0),
                ui.input_slider('w2', "Frequency", 1.0, 5.0, 10),
                ui.input_switch('show_E2', "Show Field", True),
            ),
            col_widths=6,
        ),
        ui.card(
            ui.layout_columns(
                ui.input_switch('set_dphi', "Set phase difference", False),
                ui.input_slider('dphi', "", 0.0, 2.0, 0, step=0.25),
            ),
        ),
        ui.layout_columns(
            ui.input_switch('same_freq', "Same frequency", True),
            ui.input_numeric('time_max', "upper time limit", 1, min=1, max=100),
        ),

        ui.input_dark_mode(id='dark_mode'),
        open='always',
        width = "35%"
    ),
    ui.card(
        output_widget(
            "plot_fields",
            width="600px", height="600px"
        ),
        ui.layout_columns(
            ui.input_switch('show_total', "Show total field", False),
            ui.input_switch('show_v_proj', "Show vertical projection", False),
            ui.input_switch('show_h_proj', "Show horizontal projection", False),
        )
    ),
)

def server(input, output, session):

    grey_bg = 'rgb(28, 30, 32)'

    def calculate_fields():
        step = 0.01
        t = np.arange(0, input.time_max()+step, step=step)

        w2 = input.w2()
        if input.same_freq():
            w2 = input.w1()
            ui.update_slider('w2', value=w2)

        phase2 = input.phase2()
        if input.set_dphi():
            help_phase = input.phase1() + input.dphi()
            phase2 = help_phase%2
            ui.update_slider('phase2', value=phase2)

        if input.polarization() == "lin_pol":
            e1_val = input.E1_amp() * np.cos(input.w1() * np.pi * t - input.phase1() * np.pi)
            e2_val = input.E2_amp() * np.cos(w2 * np.pi * t - phase2 * np.pi)
            ex1 = e1_val
            ey1 = np.zeros_like(ex1)
            ex2 = np.zeros_like(ex1)
            ey2 = e2_val
        else:
            e1_val = input.E1_amp() * np.cos(input.w1() * np.pi * t - input.phase1() * np.pi) + input.E2_amp() * np.cos(w2 * np.pi * t - phase2 * np.pi)
            e2_val = input.E1_amp() * np.sin(input.w1() * np.pi * t - input.phase1() * np.pi) - input.E2_amp() * np.sin(w2 * np.pi * t - phase2 * np.pi)
            ex2 = input.E2_amp() * np.cos(w2 * np.pi * t - phase2 * np.pi)
            ey2 = -input.E2_amp() * np.sin(w2 * np.pi * t - phase2 * np.pi)
            ex1 = input.E1_amp() * np.cos(input.w1() * np.pi * t - input.phase1() * np.pi)
            ey1 = input.E1_amp() * np.sin(input.w1() * np.pi * t - input.phase1() * np.pi)

        return t, e1_val, e2_val, ex1, ey1, ex2, ey2

    @render_widget
    def plot_fields():
        if input.dark_mode() == "dark":
            template = 'plotly_dark'
            bg_color = grey_bg
            c_tot = 'white'
            c1 = 'rgb(245, 34, 104)'
            c2 = 'rgb(58, 233, 233)'
            c_proj = 'rgb(170, 170, 170)'
        else:
            template = 'plotly_white'
            bg_color = 'white'
            c_tot = 'black'
            c1 = 'rgb(157, 13, 21)'
            c2 = 'rgb(13, 76, 149)'
            c_proj = 'rgb(89, 89, 89)'

        fig = go.Figure()

        t, E1, E2, ex1, ey1, ex2, ey2 = calculate_fields()

        if input.show_v_proj():
            fig.add_trace(go.Scatter3d(
                x=E1, y=E2, z=np.zeros_like(t),
                mode='lines',
                line=dict(color=c_proj,width=4),
                opacity=0.7,
            ))
        if input.show_h_proj():
            fig.add_trace(go.Scatter3d(
                x=E1, y=np.ones_like(E2)*1.5, z=t,
                mode='lines',
                line=dict(color=c_proj,width=4),
                opacity=0.7,
            ))
            fig.add_trace(go.Scatter3d(
                x=np.ones_like(E1)*1.5, y=E2, z=t,
                mode='lines',
                line=dict(color=c_proj, width=4),
                opacity=0.7,
            ))
        if input.show_E1():
            fig.add_trace(go.Scatter3d(
                x=ex1, y=ey1, z=t,
                mode='lines',
                line=dict(color=c1,width=4),
            ))
        if input.show_E2():
            fig.add_trace(go.Scatter3d(
                x=ex2, y=ey2, z=t,
                mode='lines',
                line=dict(color=c2,width=4),
            ))
        if input.show_total():
            fig.add_trace(go.Scatter3d(
                x=E1, y=E2, z=t,
                mode='lines',
                line=dict(color=c_tot,width=4),
            ))


        fig.update_layout(
            template=template,
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            scene=dict(
                xaxis_title="Ex",
                yaxis_title="Ey",
                zaxis_title="time",
                xaxis=dict(range=[-1.5, 1.5]),
                yaxis=dict(range=[-1.5, 1.5]),
                zaxis=dict(range=[0, input.time_max()]),
                camera=dict(
                    eye=dict(x=-1.6, y=-1.6, z=0.5),
                    center=dict(x=0, y=0, z=0.0),
                    #up=dict(x=0, y=0, z=1),
                ),
                aspectmode="cube",
            ),
            width=600,
            height=600,
            margin={"r": 0, "t": 0, "l": 0, "b": 60},
            showlegend=False,
        )
        return fig


app = App(app_ui, server, debug=True)