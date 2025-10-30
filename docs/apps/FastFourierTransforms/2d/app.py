import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from shiny import App, render, ui, reactive

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider(
            "sigma",
            "Width of Gaussian (σ)",
            min=0,
            max=0.5,
            value=0,
            step=0.025,
            animate=True
        ),
        ui.input_slider(
            "event_x",
            "Frequency in x",
            min=-2,
            max=2,
            value=0.5,
            step=0.025,
            animate=True
        ),
        ui.input_slider(
            "event_y",
            "Frequency in y",
            min=-2,
            max=2,
            value=0.5,
            step=0.025,
            animate=True
        ),
        ui.input_checkbox(
            'include_negative_frequencies',
            'Add imaginary Fourier component',
            value=True,
        ),
        ui.input_checkbox(
            'flip_imaginary',
            'Flip imaginary Fourier component',
            value=True,
        ),
        ui.input_dark_mode(id='dark_mode'),
        open='always',
    ),
    ui.layout_columns(
        ui.output_plot(
            "fourier_plot",
            click=True,
            width="100%", height="700px"
        ),
        ui.output_plot(
            "real_plot",
            width="100%", height="700px"
        ),
    ),
)

def server(input, output, session):
    click_data = reactive.value(None)
    blue = 'navy'
    red = 'firebrick'

    x_axis = np.linspace(-20, 20, 1024)
    y_axis = np.linspace(-20, 20, 1024)
    freq_axis = np.fft.fftfreq(len(x_axis), d=(x_axis[1] - x_axis[0]))
    freq_axis = np.fft.fftshift(freq_axis)

    x_axis_lims = (-5, 5)
    freq_axis_lims = (-2, 2)

    # Update click data when plot is clicked
    @reactive.effect
    def _():
        if input.fourier_plot_click() is not None:
            click_data.set(input.fourier_plot_click())
            ui.update_slider('event_x', value=input.fourier_plot_click()['x'])
            ui.update_slider('event_y', value=input.fourier_plot_click()['y'])
            # One could actually calculate everything here and then only use the resulting data in the plots



    @render.plot()
    def fourier_plot():
        if input.dark_mode() == "dark":
            style_label = 'dark_background'
        else:
            style_label = 'seaborn-v0_8'

        with plt.style.context(style_label):
            sigma = input.sigma()
            fig, axs = plt.subplots()
            axs.set_xlim(freq_axis_lims)
            axs.set_ylim(freq_axis_lims)

            eventx, eventy = input.event_x(), input.event_y()
            fourier_signal = get_gaussian2d(freq_axis, freq_axis, eventx, eventy, sigma, 1)

            sign = -1 if input.flip_imaginary() else 1
            if input.include_negative_frequencies():
                # add negative frequencies for real signal
                fourier_signal = fourier_signal + sign * 1j * get_gaussian2d(freq_axis, freq_axis, -eventx, -eventy, sigma, 1)

            if sigma == 0:
                img = axs.imshow(np.zeros((len(freq_axis), len(freq_axis))), interpolation='none',
                                 cmap='RdBu_r', extent=(freq_axis[0], freq_axis[-1], freq_axis[0], freq_axis[-1]), origin='lower', vmin=-1, vmax=1)
                axs.plot([eventx], [eventy], marker='o', color='red', label='Real Part')
                if input.include_negative_frequencies():
                    axs.plot([sign * eventx], [sign * eventy], marker='x', color='blue', label='Imaginary Part')
                axs.legend()
            else:
                img = axs.imshow(np.sqrt(np.abs(fourier_signal)) * np.sign(np.real(fourier_signal ** 2)), interpolation='none', cmap='RdBu_r', vmin=-1, vmax=1,
                           extent=(freq_axis[0], freq_axis[-1], freq_axis[0], freq_axis[-1]), origin='lower')
            cbar = fig.colorbar(img, ax=axs)
            cbar.ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{-float(x):.1f}i" if x < 0 else f"{float(x):.1f}"))


            axs.set_title("Fourier Transform")

            axs.set_xlabel("Frequency in x (Hz)")
            axs.set_ylabel("Frequency in y (Hz)")
        return fig

    @render.plot()
    def real_plot():
        if input.dark_mode() == "dark":
            style_label = 'dark_background'
        else:
            style_label = 'seaborn-v0_8'
        with plt.style.context(style_label):
            sigma = input.sigma()

            fig, axs = plt.subplots()
            axs.set_xlim(x_axis_lims)
            axs.set_ylim(x_axis_lims)

            eventx, eventy = input.event_x(), input.event_y()
            fourier_signal = get_gaussian2d(freq_axis, freq_axis, eventx, eventy, sigma, 1)

            sign = -1 if input.flip_imaginary() else 1
            if input.include_negative_frequencies():
                # add negative frequencies for real signal
                fourier_signal = fourier_signal + sign * 1j * get_gaussian2d(freq_axis, freq_axis, -eventx, -eventy, sigma, 1)

            real_signal = np.fft.ifftshift(np.fft.ifft2(np.fft.fftshift(fourier_signal))) * len(x_axis) * len(y_axis)

            # real signal
            img = axs.imshow(np.abs(real_signal), interpolation='none', cmap='turbo',
                       extent=(x_axis[0], x_axis[-1], x_axis[0], x_axis[-1]), origin='lower')
            cbar = fig.colorbar(img, ax=axs)

            axs.set_title("Real Space Signal")
            axs.set_xlabel("Time in x [s]")
            axs.set_ylabel("Time in y [s]")
        return fig

def get_gaussian2d(x, y, x0, y0, sigma, amp):
    if sigma == 0:
        signal = np.zeros((len(x), len(y)))
        closest_idx_x = (np.abs(y - y0)).argmin()
        closest_idx_y = (np.abs(x - x0)).argmin()
        signal[closest_idx_x, closest_idx_y] = amp
    else:
        X, Y = np.meshgrid(x, y, indexing='xy')
        signal = amp * np.exp(-((X - x0) ** 2 + (Y - y0) ** 2) / (2 * sigma ** 2))

    return signal

app = App(app_ui, server, debug=True)
