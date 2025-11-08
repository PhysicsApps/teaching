import plotly.graph_objects as go
from shiny import reactive
from shiny.express import input, ui
from shinywidgets import render_plotly
import numpy as np
from scipy.special import lpmv, factorial
from plotly.subplots import make_subplots

N = 128

@reactive.calc
def compute_harmonics():
    # Generate grid
    t = np.linspace(np.pi, 0, N)  # theta: 180° to 0°
    p = np.linspace(-np.pi, np.pi, N)  # phi: -180° to 180°

    T, P = np.meshgrid(t, p, indexing='ij')

    l = input.l_val()
    m = input.m_val()

    # Calculate Legendre polynomial
    if l == 0:
        Plm = np.ones_like(T)
    else:
        # Using scipy's lpmv function (note: it takes |m|)
        Plm = lpmv(m, l, np.cos(T))

    # Calculate theta component
    prefactor = (-1) ** ((m + abs(m)) / 2) * np.sqrt(
        (2 * l + 1) * factorial(l - abs(m)) / (4 * np.pi * factorial(l + abs(m))))
    theta_component = prefactor * Plm / ((-1) ** m)

    # Calculate phi component
    phi_component = np.exp(1j * m * P)

    return {
        't': t,
        'p': p,
        'theta_values': theta_component,
        'phi_values': phi_component
    }

ui.page_opts(fillable=True)

with ui.layout_sidebar(width="300px", gap="1rem"):
    with ui.sidebar():
        ui.h4("Values")
        ui.input_slider("l_val", "l value", 0, 5, 0)
        ui.input_slider("m_val", "m value", 0, 5, 0)
        ui.input_switch("representation", "Alternative representation", False)

    with ui.card(full_screen=True):
        ui.card_header("Amplitude and Phase")

        @render_plotly
        @reactive.event(input.representation, input.l_val, input.m_val)
        def theta_and_phi_plot():
            harmonics = compute_harmonics()
            theta_vals = harmonics['theta_values']
            phi_vals = np.angle(harmonics['phi_values'])

            phi = np.linspace(0, 2 * np.pi, N)
            theta = np.linspace(0, np.pi, N)
            PHI, THETA = np.meshgrid(phi, theta)

            # Convert to Cartesian coordinates
            X = np.sin(THETA) * np.cos(PHI)
            Y = np.sin(THETA) * np.sin(PHI)
            Z = np.cos(THETA)

            if input.representation():
                fig = alternative_plot(PHI, THETA, theta_vals, phi_vals)
            else:
                fig = create_plot(X, Y, Z, theta_vals, phi_vals)

            return fig


def create_plot(X, Y, Z, theta_vals, phi_vals):
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'surface'}, {'type': 'surface'}]],
    )

    fig.add_trace(
        go.Surface(
            x=X, y=Y, z=Z,
            surfacecolor=theta_vals,
            colorscale='RdBu',
            colorbar=dict(
                title="Amplitude",
                orientation="h",  # Make colorbar horizontal
                y=0.0,  # Place colorbar at the top
                yanchor="bottom",  # Anchor at bottom of colorbar
                x=0,  # Center colorbar horizontally
                xanchor="left",  # Anchor at center of colorbar
                len=0.3,  # Make colorbar 60% of the plot width
            ),
            cmin=-np.max(np.abs(theta_vals)),
            cmax=np.max(np.abs(theta_vals))
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Surface(
            x=X, y=Y, z=Z,
            surfacecolor=phi_vals,
            colorscale='icefire',
            colorbar=dict(
                title="Phase",
                orientation="h",  # Make colorbar horizontal
                y=0.0,  # Place colorbar at the top
                yanchor="bottom",  # Anchor at bottom of colorbar
                x=1,  # Center colorbar horizontally
                xanchor="right",  # Anchor at center of colorbar
                len=0.3,  # Make colorbar 60% of the plot width
            ),
            cmin=-np.pi,
            cmax=np.pi
        ),
        row=1, col=2
    )

    fig.update_layout(
        autosize=True,  # Enable autosize for responsiveness
        margin=dict(l=0, r=0, b=0, t=0),  # Reduce margins
        scene1=dict(
            aspectmode='cube',
            camera=dict(eye=dict(x=2.3, y=2.3, z=2.3))
        ),
        scene2=dict(
            aspectmode='cube',
            camera=dict(eye=dict(x=2.3, y=2.3, z=2.3))
        ),
        height=None,  # Auto height
        width=None,  # Auto width
    )

    return fig

def alternative_plot(PHI, THETA, theta_vals, phi_vals):
    rho = abs(theta_vals)
    X = rho * np.sin(THETA) * np.cos(PHI)
    Y = rho * np.sin(THETA) * np.sin(PHI)
    Z = rho * np.cos(THETA)
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{'type': 'surface'}]],
    )

    fig.add_trace(
        go.Surface(
            x=X, y=Y, z=Z,
            surfacecolor=phi_vals,
            colorscale='icefire',
            colorbar=dict(
                title="Phase",
                orientation="h",  # Make colorbar horizontal
                y=0.0,  # Place colorbar at the top
                yanchor="bottom",  # Anchor at bottom of colorbar
                x=1,  # Center colorbar horizontally
                xanchor="right",  # Anchor at center of colorbar
                len=0.3,  # Make colorbar 60% of the plot width
            ),
            cmin=-np.pi,
            cmax=np.pi
        )
    )

    return fig

# Update the m_value slider range based on the selected l_value
@reactive.effect
@reactive.event(input.l_val)
def update_m_range():
    l_val = input.l_val()
    m_val = min(input.m_val(), l_val)
    ui.update_slider("m_val", max=l_val, value=m_val)