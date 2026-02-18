import numpy as np
import faicons as fa
from pyodide.http import pyfetch

from typing import Callable
from shiny.express import input, render, ui
from shiny import reactive
from shinywidgets import render_widget
from plotly import graph_objects as go
from utils import turbo_white_colorscale, stl_to_numpy, apply_rotation, _get_density
from pathlib import Path

ui.page_opts(fillable=True)
axis_length = 1.3

ICONS = {
    "gear": fa.icon_svg("gear")
}

with ui.sidebar(title="Settings"):
    with ui.accordion(id="numerical_settings", open=True):
        with ui.accordion_panel("Experiment"):
            ui.input_slider("diameter", "Diameter [nm]", min=1, max=200, value=150, step=1)
            ui.input_slider("wavelength", "Wavelength [nm]", min=1, max=15, value=13.5, step=0.1)
            ui.input_numeric("delta", "Refractive index (δ)", value=0.11, min=1e-7, max=1e-3, step=1e-6)
            ui.input_numeric("beta", "Absorption (β)", value=0.09, min=0, max=1e-4, step=1e-6)
        with ui.accordion_panel("Numerics"):
            ui.input_select("method", "Simulation method",
                            {
                                "Propagation": {"pMSFT" : "pMSFT",
                                                "Hare": "Hare",
                                                },
                                "Multi-Slice": {"MSFT": "MSFT",
                                                "Born": "Born",
                                                },
                                "Projection": {"SAXS": "SAXS",
                                               },
                            })
            ui.input_numeric("msft_npix_real", "Real space grid size", value=32, min=16, max=128, step=8)
            ui.input_numeric("msft_npix_fourier", "Fourier space grid size", value=128, min=64, max=512, step=64)
    ui.input_dark_mode(id="dark_mode")

with ui.layout_column_wrap(width="600px"):
    with ui.card(full_screen=True):
        with ui.layout_sidebar():
            with ui.sidebar(open='always'):
                ui.input_slider("rot_x", "α", min=-180, max=180, value=0, step=1)
                ui.input_slider("rot_y", "β", min=-180, max=180, value=0, step=1)
                ui.input_slider("rot_z", "γ", min=-180, max=180, value=0, step=1)
                with ui.accordion(id="sample_settings", open=True):
                    with ui.accordion_panel("Sample type"):
                        ui.input_select("sample_type", "Source", {"STL": "STL", "Ellipsoid": "Ellipsoid", "Code": "Code"})
                        with ui.panel_conditional("input.sample_type == 'STL'"):
                            ui.input_file("stl_file", "Upload STL file", multiple=False, accept=".stl", placeholder="truncated_octahedron.stl")
                        with ui.panel_conditional("input.sample_type == 'Ellipsoid'"):
                            ui.input_numeric("a", "Semi-axis fraction a", value=1, min=1, max=10, step=0.1)
                            ui.input_numeric("b", "Semi-axis fraction b", value=1, min=1, max=10, step=0.1)
                            ui.input_numeric("c", "Semi-axis fraction c", value=1, min=1, max=10, step=0.1)
                        with ui.panel_conditional("input.sample_type == 'Code'"):
                            ui.input_action_button("execute", "Execute Code", class_="btn-primary")
                    with ui.accordion_panel("Visualization"):
                        ui.input_numeric("volumetric_npix", "Volumetric grid size", value=32, min=16, max=256, step=16)

            @render_widget
            def density_plot():
                fig = go.Figure(data=[
                    go.Isosurface(
                        x=[], y=[], z=[],
                        value=[],
                        isomin=0.4, isomax=0.6,
                        surface_count=1,
                        colorscale= 'Blues_r',
                        showscale=False,
                    ),
                    go.Scatter3d(
                        x=[0, axis_length], y=[0, 0], z=[0, 0],
                        mode='lines+text',
                        line=dict(width=4, color='red'),
                        text=['', 'X'],
                        textposition='middle right',
                        textfont=dict(size=14, color='red'),
                        name='X-axis',
                        showlegend=False,
                        visible=True,
                    ),
                    go.Scatter3d(
                        x=[0, 0], y=[0, axis_length], z=[0, 0],
                        mode='lines+text',
                        line=dict(width=4, color='green'),
                        text=['', 'Y'],
                        textposition='middle right',
                        textfont=dict(size=14, color='green'),
                        name='Y-axis',
                        showlegend=False,
                        visible=True,
                    ),
                    go.Scatter3d(
                        x=[0, 0], y=[0, 0], z=[0, axis_length],
                        mode='lines+text',
                        line=dict(width=4, color='blue'),
                        text=['', 'Z (laser)'],
                        textposition='middle right',
                        textfont=dict(size=14, color='blue'),
                        name='Z-axis',
                        showlegend=False,
                        visible=True,
                    ),
                    go.Scatter3d(
                        x=[0, axis_length], y=[0, 0], z=[0, 0],
                        mode='lines',
                        line=dict(width=4, color='red', dash='dot'),
                        name='rot-X-axis',
                        showlegend=False,
                    ),
                    go.Scatter3d(
                        x=[0, 0], y=[0, axis_length], z=[0, 0],
                        mode='lines',
                        line=dict(width=4, color='green', dash='dot'),
                        name='rot-Y-axis',
                        showlegend=False,
                    ),
                    go.Scatter3d(
                        x=[0, 0], y=[0, 0], z=[0, axis_length],
                        mode='lines',
                        line=dict(width=4, color='blue', dash='dot'),
                        name='rot-Z-axis',
                        showlegend=False,
                    ),
                ])
                fig.update_layout(
                    scene=dict(
                        aspectmode='cube',
                        xaxis = dict(visible=False, range=[-axis_length, axis_length]),
                        yaxis = dict(visible=False, range=[-axis_length, axis_length]),
                        zaxis = dict(visible=False, range=[-axis_length, axis_length]),
                    ),
                    margin=dict(l=1, r=1, t=1, b=1)
                )
                fig.update_traces(
                    hoverinfo='skip'  # Disable hover info for better performance
                )
                return fig

            with ui.panel_conditional("input.sample_type == 'Code'"):
                with ui.panel_absolute(
                        width="350px",
                        right="50px",
                        top="50px",
                        draggable=True,
                ):
                    ui.h5("Python Code Editor")
                    @render.code
                    def text():
                        return "import numpy as np\ngrid = np.linspace(-1, 1, N)\nX, Y, Z = np.meshgrid(grid, grid, grid)"
                    ui.div(
                        ui.input_text_area(
                            "python_code",
                            "",
                            value="result = X ** 2 + Y ** 2 + Z ** 2 < 1",
                            rows=15,
                            cols=60,
                            resize='both',
                            update_on="blur",
                        ),
                    style = "font-family: 'Courier New', Monaco, monospace;")

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Scattering Image"
            with ui.popover(title="Settings"):
                ICONS["gear"]
                ui.input_numeric("dynamic_range", "Dynamic range", value=3.5, min=1, max=10, step=0.5)
                ui.input_radio_buttons("pol_dir", "Polarization direction", {"Vertical": "vertical", "Horizontal": "horizontal"}, inline=True)


        @render_widget
        def scattering_plot():
            fig = go.Figure(go.Heatmap(colorscale=turbo_white_colorscale))

            color = 'white' if input.dark_mode() == "dark" else 'black'
            for angle in [15, 30, 60, 90]:
                radius_angle = np.sin(np.radians(angle))
                fig.add_shape(type="circle", xref="x", yref="y",
                              x0=-radius_angle, y0=-radius_angle, x1=radius_angle, y1=radius_angle,
                              line=dict(color=color, width=1), fillcolor="rgba(0,0,0,0)",
                              layer="above")
                fig.add_annotation(
                    x=radius_angle, y=0,
                    text=f"{angle}°",
                    showarrow=False,
                    font=dict(color=color),
                    xshift = 15,
                )
            fig.update_traces(
                hoverinfo='skip'
            )
            fig.update_layout(
                margin=dict(l=1, r=1, t=1, b=1)
            )
            fig.update_xaxes(scaleanchor="y", scaleratio=1, title_text="kx/k0", range=[-1, 1])
            fig.update_yaxes(scaleanchor="x", scaleratio=1, title_text="ky/k0", range=[-1, 1])
            return fig

@reactive.effect
async def _():
    response = await pyfetch("/apps/coherent-diffractive-imaging/truncated_octahedron.stl")
    data = await response.bytes()

    with open("truncated_octahedron.stl", "wb") as f:
        f.write(data)

@reactive.calc
@reactive.event(input.execute)
def execute_code():
    def density_func(X, Y, Z) -> np.ndarray:
        code = input.python_code()
        local_vars = {'np': np, 'X': X, 'Y': Y, 'Z': Z}
        try:
            exec(code, {}, local_vars)
            return local_vars['result']  # Assuming the code returns a variable named 'grid'
        except Exception as e:
            ui.notification_show(f"Error in code execution: {e}", type="error")
            return X ** 2 + Y ** 2 + Z ** 2 < 1
    return density_func

@reactive.calc
def get_density_func() -> Callable:
    if input.sample_type() == "Ellipsoid":
        def density_func(X, Y, Z) -> np.ndarray:
            A, B, C = input.a(), input.b(), input.c()
            return (X * A) ** 2 + (Y * B) ** 2 + (Z * C) ** 2 < 1
    elif input.sample_type() == "STL":
        if input.stl_file() is None:
            stl_datapath = Path("truncated_octahedron.stl")
        else:
            stl_datapath = Path(input.stl_file()[0]['datapath'])
        rot_x, rot_y, rot_z = input.rot_x(), input.rot_y(), input.rot_z()
        def density_func(X, Y, Z) -> np.ndarray:
            resolution = X.shape[0]
            density_array = stl_to_numpy(stl_datapath, resolution, np.radians(rot_x), np.radians(rot_y), np.radians(rot_z))
            print(f"Loaded STL file: {stl_datapath}, resolution: {resolution}")
            print(f"Density array shape: {density_array.shape}")
            return density_array

    elif input.sample_type() == "Code":
        density_func = execute_code()
    return density_func

@reactive.calc
def get_density():
    msft_npix_real = int(input.msft_npix_real())
    rot_x = input.rot_x()
    rot_y = input.rot_y()
    rot_z = input.rot_z()

    return _get_density(msft_npix_real, rot_x, rot_y, rot_z, get_density_func())

@reactive.calc
def get_density_downscaled():
    if input.volumetric_npix() == input.msft_npix_real():
        return get_density()
    else:
        return _get_density(input.volumetric_npix(), input.rot_x(), input.rot_y(), input.rot_z(), get_density_func())

@reactive.effect
@reactive.event(input.dark_mode)
def _():
    # Update the dark mode of the app
    template_name = "plotly_dark" if input.dark_mode() == "dark" else "plotly"
    bg_color = 'rgb(28, 30, 32)' if input.dark_mode() == "dark" else 'white'


    density_plot.widget.update_layout(
        template=template_name,
        paper_bgcolor=bg_color,
    )
    scattering_plot.widget.update_layout(
        template=template_name,
        paper_bgcolor=bg_color,
    )

@reactive.effect
def _():
    # If the volumetric grid size is different, downsample the density grid
    try:
        msft_density, X, Y, Z = get_density_downscaled()

        orig_axis_coordstack = np.array([[axis_length, 0, 0],  # X-axis
                                    [0, axis_length, 0],  # Y-axis
                                    [0, 0, axis_length]]) # Z-axis
        x_stack, y_stack, z_stack = apply_rotation(orig_axis_coordstack[:, 0], orig_axis_coordstack[:, 1], orig_axis_coordstack[:, 2],
                                                   -np.radians(input.rot_x()), -np.radians(input.rot_y()), -np.radians(input.rot_z()))

        density_plot.widget.update_traces(selector=dict(type="isosurface"),
            x=X.flatten(), y=Y.flatten(), z=Z.flatten(),
            value=msft_density.flatten(),
        ).update_traces(selector=dict(type="scatter3d", name="rot-X-axis"),
            x=[0, x_stack[0]], y=[0, y_stack[0]], z=[0, z_stack[0]],
        ).update_traces(selector=dict(type="scatter3d", name="rot-Y-axis"),
            x=[0, x_stack[1]], y=[0, y_stack[1]], z=[0, z_stack[1]],
        ).update_traces(selector=dict(type="scatter3d", name="rot-Z-axis"),
            x=[0, x_stack[2]], y=[0, y_stack[2]], z=[0, z_stack[2]],
        )


    except Exception as e:
        ui.notification_show(f"Error updating density plot: {e}", type="error")
        density_plot.widget.update_traces(selector=dict(type="isosurface"),
            x=[], y=[], z=[],
            value=[],
        )


@reactive.effect
async def _():
    try:
        # Get parameters from inputs
        diameter = input.diameter()
        wavelength = input.wavelength()
        delta = input.delta()
        beta = input.beta()
        msft_npix_real = input.msft_npix_real()
        msft_npix_fourier = input.msft_npix_fourier()

        # # Validate inputs
        # if msft_npix_real is None or msft_npix_fourier is None:
        #     raise ValueError("Real space and Fourier space grid sizes must be set.")

        # Calculate derived parameters
        box_delta = diameter / (msft_npix_real - 1)
        k_0 = 2 * np.pi / wavelength  # [1/nm]

        msft_density = 1 - get_density()[0] * (delta - 1j * beta)  # Complex refractive index

        # Create Fourier space grid
        K_perp_cut = np.fft.fftshift(np.fft.fftfreq(msft_npix_fourier, d=box_delta / (2 * np.pi)))
        K_X, K_Y = np.meshgrid(K_perp_cut, K_perp_cut, indexing='ij')
        K_Z = np.sqrt(k_0**2 - K_X**2 - K_Y**2 + 0j)
        K_Z_shifted = np.fft.fftshift(K_Z)

        # Polarization map
        if input.pol_dir() == 'Vertical':
            PolMap = 1 - (K_X / k_0) ** 2
        else:
            PolMap = 1 - (K_Y / k_0) ** 2
        PolMap[K_X ** 2 + K_Y ** 2 > k_0 ** 2] = np.nan

        # Calculate scattered field
        if input.method() == "SAXS":
            result = np.fft.fft2(np.sum(msft_density - 1, axis=-1), s=(msft_npix_fourier, msft_npix_fourier))
        else:
            with ui.Progress(min=1, max=msft_npix_real) as p:
                p.set(message="Calculation in progress", detail="This may take a while...")

                _fft_fourspace = np.empty((msft_npix_fourier, msft_npix_fourier), dtype='complex128')
                ref_index_response = np.ones((msft_npix_fourier, msft_npix_fourier), dtype='complex128')
                reference_input_field = np.ones((msft_npix_fourier, msft_npix_fourier), dtype='complex128')

                padding = msft_npix_fourier // 2 - msft_npix_real // 2

                if input.method() == "pMSFT" or input.method() == "Hare":
                    _fft_realspace = np.ones((msft_npix_fourier, msft_npix_fourier), dtype='complex128')
                    if input.method() == "pMSFT":
                        fourier_prop_slice = np.exp(1j * box_delta * K_Z_shifted)
                    else: # input.method() == "Hare"
                        paraxial_K_Z_shifted = np.fft.fftshift(k_0 - (K_X ** 2 + K_Y ** 2) / (2 * k_0))
                        fourier_prop_slice = np.exp(1j * box_delta * paraxial_K_Z_shifted)

                    for slice_index in np.arange(msft_npix_real):
                        p.set(slice_index, message="Computing")

                        particle_slice_ref_index = msft_density[..., slice_index]

                        ref_index_response[padding:-padding, padding:-padding] \
                            = np.exp(1j * box_delta * k_0 * (particle_slice_ref_index - 1))
                        _fft_realspace *= ref_index_response
                        _fft_fourspace = np.fft.fft2(_fft_realspace)
                        _fft_fourspace *= fourier_prop_slice
                        _fft_realspace = np.fft.ifft2(_fft_fourspace)

                    result = np.fft.fft2(_fft_realspace) - np.exp(
                        1j * msft_npix_real * box_delta * K_Z_shifted) * np.fft.fft2(reference_input_field)

                else:
                    result = np.zeros((msft_npix_fourier, msft_npix_fourier), dtype='complex128')
                    _fft_realspace = np.zeros((msft_npix_fourier, msft_npix_fourier), dtype='complex128')
                    if input.method() == "MSFT":
                        ref_index_depth = np.ones((msft_npix_real, msft_npix_real), dtype='complex128')

                        for slice_index in np.arange(msft_npix_real):
                            p.set(slice_index, message="Computing")

                            particle_slice_ref_index = msft_density[..., slice_index]

                            _fft_realspace[padding:-padding, padding:-padding] = \
                                (np.exp(1j * box_delta * k_0 * (particle_slice_ref_index - 1)) - 1) * ref_index_depth

                            np.multiply(ref_index_depth, np.exp(1j * particle_slice_ref_index * k_0 * box_delta),
                                        out=ref_index_depth)

                            np.fft.fft2(_fft_realspace, axes=(0, 1), out=_fft_fourspace)
                            result += _fft_fourspace * np.exp(1j * K_Z_shifted * box_delta * (msft_npix_real - slice_index))

                    else: # input.method() == "Born":
                        fourier_prop_slice = np.exp(1j * K_Z_shifted * box_delta)
                        for slice_index in np.arange(msft_npix_real):
                            p.set(slice_index, message="Computing")
                            particle_slice_ref_index = msft_density[..., slice_index]

                            _fft_realspace[padding:-padding, padding:-padding] = \
                                (np.exp(1j * box_delta * k_0 * (particle_slice_ref_index - 1)) - 1) * np.exp(
                                    1j * k_0 * box_delta * slice_index)

                            np.fft.fft2(_fft_realspace, axes=(0, 1), out=_fft_fourspace)

                            result += _fft_fourspace
                            result *= fourier_prop_slice



        fft_norm_correction = (box_delta**2 / (2 * np.pi))**2 # Normalization factor for the FFT2
        msft_image = np.fft.fftshift(np.real(result * np.conj(result)))
        msft_image[K_X ** 2 + K_Y ** 2 > k_0 ** 2] = np.nan
        msft_image *= PolMap
        msft_image *= fft_norm_correction * k_0 / np.real(K_Z)

        msft_image = np.log10(msft_image)
        max_val = np.nanmax(msft_image)
        min_val = max_val - input.dynamic_range()

        msft_image[np.isnan(msft_image)] = min_val  # Replace NaNs with min_val
        msft_image = np.clip(msft_image, min_val, max_val)

        scattering_plot.widget.update_traces(selector=dict(type="heatmap"),
            z=msft_image, x=K_perp_cut/k_0, y=K_perp_cut/k_0,
            zmin=min_val, zmax=max_val,
        )

    except Exception as e:
        ui.notification_show(f"Error updating scattering plot: {e}", type="error")
        scattering_plot.widget.update_traces(selector=dict(type="heatmap"),
            z=np.zeros((input.msft_npix_fourier(), input.msft_npix_fourier())),
            x=np.linspace(-1, 1, input.msft_npix_fourier()),
            y=np.linspace(-1, 1, input.msft_npix_fourier()),
            zmin=0, zmax=1,
        )

@reactive.effect
def show_notification():
    try:
        if input.volumetric_npix() > input.msft_npix_real():
            ui.notification_show(
                f"Warning: Volumetric grid size ({input.volumetric_npix()}) is larger than real space grid size ({input.msft_npix_real()}).", id="volumetric_warning",
                type="warning",
            )
        elif input.volumetric_npix() < input.msft_npix_real():
            ui.notification_show(
                f"Volumetric grid size ({input.volumetric_npix()}) is smaller than real space grid size ({input.msft_npix_real()}).", id="volumetric_warning",
                type="default",
            )
        else:
            ui.notification_remove("volumetric_warning")
    except Exception as e:
        ui.notification_show(f"Error in volumetric grid size check: {e}", type="error")
