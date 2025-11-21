import matplotlib.pyplot as plt
import matplotlib
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
            "Frequency",
            min=-2,
            max=2,
            value=0.5,
            step=0.025,
            animate=True
        ),
        ui.input_slider(
            "event_y",
            "Amplitude",
            min=-0.9,
            max=0.9,
            value=0.5,
            step=0.025,
            animate=True
        ),

        ui.input_checkbox(
            'include_negative_frequencies',
            'Add negative Fourier component',
            value=True,
        ),
        ui.input_checkbox(
            'flip_negative_frequencies',
            'Flip negative Fourier component',
            value=True,
        ),
        ui.input_checkbox(
            'set_imaginary',
            'Make Fourier component imaginary',
            value=True,
        ),
        ui.input_checkbox(
            'show_contributions',
            'Show individual contributions',
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

    x_axis = np.linspace(-20, 20, 1024)
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
            blue = 'lightsteelblue'
            red = 'lightcoral'
        else:
            style_label = 'seaborn-v0_8'
            blue = 'navy'
            red = 'firebrick'

        with plt.style.context(style_label):
            sigma = input.sigma()

            fig, axs = plt.subplots()
            axs.set_xlim(freq_axis_lims)
            axs.set_ylim(-1, 1)

            eventx, eventy = input.event_x(), input.event_y()
            imag = 1j if input.set_imaginary() else 1
            sign = -1 if input.flip_negative_frequencies() else 1
            fourier_signal = imag * get_gaussian(freq_axis, eventx, sigma, eventy)
            if input.include_negative_frequencies():
                fourier_signal = fourier_signal + sign * imag * get_gaussian(freq_axis, -eventx, sigma, eventy)

            if sigma == 0:
                axs.plot(freq_axis, np.zeros_like(freq_axis), color=red, label=f'Real Part')
                axs.plot(freq_axis, np.zeros_like(freq_axis), color=blue, ls='--', label=f'Imaginary Part')
                color, ls = (red, '-') if imag == 1 else (blue, '--')
                if eventx == 0 and input.include_negative_frequencies() and sign == 1:
                    axs.plot([eventx, eventx], [0, 2 * eventy], color=color, ls=ls)
                else:
                    axs.plot([eventx, eventx], [0,  eventy], color=color, ls=ls)
                    if input.include_negative_frequencies():
                        axs.plot([-eventx, -eventx], [0, sign * eventy], color=color, ls=ls)
            else:
                axs.plot(freq_axis, np.real(fourier_signal), color=red, label=f'Real Part')
                axs.plot(freq_axis, np.imag(fourier_signal), color=blue, ls='--', label=f'Imaginary Part')

            # axs.scatter([eventx], [eventy], color='black')
            axs.legend()

            axs.set_title("Fourier Transform")

            axs.set_xlabel("Frequency (Hz)")
            axs.set_ylabel("Amplitude")
        return fig

    @render.plot()
    def real_plot():
        if input.dark_mode() == "dark":
            style_label = 'dark_background'
            blue = 'lightsteelblue'
            red = 'lightcoral'
        else:
            style_label = 'seaborn-v0_8'
            blue = 'navy'
            red = 'firebrick'

        with plt.style.context(style_label):
            sigma = input.sigma()


            fig, axs = plt.subplots()
            axs.set_xlim(x_axis_lims)

            eventx, eventy = input.event_x(), input.event_y()
            imag = 1j if input.set_imaginary() else 1
            sign = -1 if input.flip_negative_frequencies() else 1
            fourier_signal = imag * get_gaussian(freq_axis, eventx, sigma, eventy)
            if input.include_negative_frequencies():
                fourier_signal = fourier_signal + sign * imag * get_gaussian(freq_axis, -eventx, sigma, eventy)

            real_signal = np.fft.ifftshift(np.fft.ifft(np.fft.ifftshift(fourier_signal))) * len(x_axis)

            if input.show_contributions():
                for freq, amplitude in zip(freq_axis, fourier_signal):
                    if np.abs(amplitude) < 1e-3:
                        continue
                    contribution = amplitude * np.exp(2j * np.pi * freq * x_axis)
                    axs.plot(x_axis, np.real(contribution), color=red, alpha=0.1)
                    axs.plot(x_axis, np.imag(contribution), color=blue, alpha=0.1)

            # real signal
            axs.plot(x_axis, np.real(real_signal), color=red, label=f'Real Part')
            axs.plot(x_axis, np.imag(real_signal), color=blue, ls='--', label=f'Imaginary Part')

            axs.legend()

            limit = np.max([np.max(np.abs(np.real(real_signal))) * 1.1, np.abs(np.max(np.imag(real_signal))) * 1.1, 1])

            axs.set_ylim(-limit, limit)
            axs.set_title("Real Space Signal")
            axs.set_xlabel("Time [s]")
            axs.set_ylabel("Amplitude")
        return fig

def get_gaussian(x, x0, sigma, amp):
    if sigma == 0:
        signal = np.zeros_like(x)
        closest_idx = (np.abs(x - x0)).argmin()
        signal[closest_idx] = amp
    else:
        signal = amp * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

    return signal

app = App(app_ui, server, debug=True)
