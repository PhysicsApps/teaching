import numpy as np
from shiny import reactive
from shiny.express import input, render, ui
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

ui.page_opts(fillable=True, title="Scattering Pattern Simulator")

with ui.layout_columns(col_widths=(4, 8)):
    with ui.card(full_screen=True, height="100%"):
        ui.card_header("Parameters")

        ui.input_slider("radius", "Radius [nm]", min=1, max=100, value=20, step=1)
        ui.input_slider("wavelength", "Wavelength [nm]", min=1, max=10, value=1, step=0.1)
        ui.input_numeric("z_det", "Detector distance [m]", value=0.1, min=0.01, max=10, step=0.01)
        ui.input_numeric("delta", "Refractive index (δ)", value=1e-5, min=1e-7, max=1e-3, step=1e-6)
        ui.input_numeric("beta", "Absorption (β)", value=0, min=0, max=1e-4, step=1e-6)

        with ui.accordion(id="advanced_options", open=False):
            with ui.accordion_panel("Advanced Options"):
                ui.input_numeric("msft_npix_real", "Real space grid size", value=32, min=16, max=128, step=8)
                ui.input_numeric("msft_npix_fourier", "Fourier space grid size", value=128, min=64, max=512, step=64)

    with ui.card(full_screen=True, height="100%"):
        ui.card_header("Scattering Pattern")


        @render.plot()
        def scattering_plot():
            # Get parameters from inputs
            radius = input.radius()
            wavelength = input.wavelength()
            delta = input.delta()
            beta = input.beta()
            z_det = input.z_det()
            msft_npix_real = int(input.msft_npix_real())
            msft_npix_fourier = int(input.msft_npix_fourier())

            # Calculate derived parameters
            box_delta = 2 * radius / (msft_npix_real - 1)
            k_0 = 2 * np.pi / wavelength  # [1/nm]

            # Create real space grid
            msft_real_axis = np.linspace(-1, 1, msft_npix_real) * radius
            X, Y, Z = np.meshgrid(msft_real_axis, msft_real_axis, msft_real_axis)
            msft_density = (delta - 1j * beta) * (X ** 2 + Y ** 2 + Z ** 2 < radius ** 2)

            # Create Fourier space grid
            Q_perp_cut = np.fft.fftshift(np.fft.fftfreq(msft_npix_fourier, d=box_delta / (2 * np.pi)))
            Q_X, Q_Y = np.meshgrid(Q_perp_cut, Q_perp_cut, indexing='ij')
            Q_Z = k_0 - np.sqrt(k_0 ** 2 - Q_X ** 2 - Q_Y ** 2 + 0j)

            # Polarization map
            PolMap = 1 - (Q_Y / k_0) ** 2
            PolMap[Q_X ** 2 + Q_Y ** 2 > k_0 ** 2] = np.nan

            # Calculate scattered field
            msft_image = np.fft.fftshift(np.fft.fft2(np.sum(msft_density, axis=0),
                                                     s=(msft_npix_fourier, msft_npix_fourier))) * box_delta ** 2 * 1 / (
                                     2 * np.pi)

            # Cull evanescent waves
            msft_image[Q_X ** 2 + Q_Y ** 2 > k_0 ** 2] = np.nan
            msft_image *= k_0 / z_det
            msft_image = PolMap * np.abs(msft_image ** 2)

            # Create plot
            fig, ax = plt.subplots(figsize=(10, 8))

            # Use log scale for better visualization
            norm = LogNorm(vmin=np.nanmin(msft_image[msft_image > 0]),
                           vmax=np.nanmax(msft_image))

            im = ax.imshow(msft_image.T, origin='lower', cmap='viridis',
                           extent=[Q_perp_cut[0], Q_perp_cut[-1], Q_perp_cut[0], Q_perp_cut[-1]],
                           norm=norm)

            # Add colorbar and labels
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Intensity (log scale)')

            ax.set_xlabel('Q_x [1/nm]')
            ax.set_ylabel('Q_y [1/nm]')
            ax.set_title(f'Scattering Pattern for {radius}nm Sphere, λ={wavelength}nm')

            # Draw a circle at k_0 to show the boundary of propagating waves
            circle = plt.Circle((0, 0), k_0, fill=False, color='red', linestyle='--')
            ax.add_artist(circle)

            # Draw circles with labels for corresponding scattering angles
            for angle in [15, 30, 60]:
                radius_angle = k_0 * np.sin(np.radians(angle))
                circle_angle = plt.Circle((0, 0), radius_angle, fill=False, color='blue', linestyle='--')
                ax.add_artist(circle_angle)

                # Only draw text if its radius is within the plot limits
                if radius_angle < np.max(Q_perp_cut):
                    ax.text(radius_angle + 0.02, 0.02, f'{angle}°', color='blue')

            ax.set_aspect('equal')
            if np.max(Q_perp_cut) > k_0:
                ax.set_xlim(-k_0, k_0)
                ax.set_ylim(-k_0, k_0)
            plt.tight_layout()
            return fig

with ui.card():
    ui.card_header("About This App")
    ui.markdown("""
    This app simulates the far-field scattering pattern from a spherical object.

    **Parameters:**
    - **Radius**: Size of the spherical object in nanometers
    - **Wavelength**: Incident light wavelength in nanometers
    - **Detector distance**: Distance from the object to the detector in meters
    - **Refractive index (δ)**: Real part of the refractive index contrast (n = 1 - δ + iβ)
    - **Absorption (β)**: Imaginary part of the refractive index (absorption)

    The red dashed circle indicates the boundary between propagating and evanescent waves.
    """)
