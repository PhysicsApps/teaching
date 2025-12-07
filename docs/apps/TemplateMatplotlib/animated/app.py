from shiny import App, render, ui, reactive
import matplotlib.pyplot as plt
import numpy as np
import time

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Animation Controls"),
        ui.input_action_button("play_pause", "Play/Pause", class_="btn-primary"),
        ui.input_slider("speed", "Speed (FPS)", min=1, max=20, value=10),
        ui.input_action_button("reset", "Reset"),
        ui.hr(),
        ui.input_slider("amplitude", "Amplitude", min=0.5, max=2.0, value=1.0, step=0.1),
        ui.input_slider("frequency", "Frequency", min=0.5, max=3.0, value=1.0, step=0.1),
        ui.input_dark_mode(id="dark_mode"),
    ),
    ui.output_plot("plot"),
)


def server(input, output, session):
    # Reactive values for the animation state
    frame = reactive.value(0)
    is_playing = reactive.value(True)
    figure_invalidator = reactive.value(0)
    last_update = reactive.value(time.time())

    x = np.linspace(0, 4 * np.pi, 100)

    @reactive.calc
    def figure_data():
        figure_invalidator()  # Depend on invalidator to force recalculation when reset

        handles = {}

        # Create figure with appropriate style
        if input.dark_mode() == "dark":
            style_label = 'dark_background'
        else:
            style_label = 'seaborn-v0_8'

        with plt.style.context(style_label):
            fig, ax = plt.subplots()

            ax.set_xlim(0, 4 * np.pi)
            ax.set_ylim(-2.5, 2.5)
            ax.set_xlabel("x")
            ax.set_ylabel(f"f(x)")

            # Initialize all required plot elements and store them in handles
            handles['line'] = ax.plot(0, 0, linewidth=2)[0]
        return fig, ax, handles

    # Handle play/pause button
    @reactive.effect
    @reactive.event(input.play_pause)
    def _():
        is_playing.set(not is_playing())
        last_update.set(time.time())  # Reset timer when toggling play state

    # Handle reset button
    @reactive.effect
    @reactive.event(input.reset)
    def _():
        frame.set(0)
        last_update.set(time.time())  # Reset timer
        # Increment the figure_invalidator to force figure_data to recalculation
        figure_invalidator.set(figure_invalidator() + 1)

    # Simple periodic timer with a max frame rate of 20 FPS
    @reactive.calc
    def timer():
        reactive.invalidate_later(0.05)  # Update every 50ms
        return time.time()

    # Update frame based on elapsed time and FPS setting
    @reactive.effect
    def _():
        current_time = timer()  # React to timer

        if is_playing():
            elapsed = current_time - last_update()
            fps = input.speed()
            frame_duration = 1.0 / fps

            # Only update frame if enough time has passed
            if elapsed >= frame_duration:
                frame.set(frame() + 1)
                last_update.set(current_time)

    @render.plot
    def plot():
        phase = frame() * np.pi / 180  # Convert to radians
        amplitude = input.amplitude()
        frequency = input.frequency()

        # Get the pre-initialized figure and handles - we avoid re-creating them each time
        fig, ax, handles = figure_data()

        y = amplitude * np.sin(frequency * x + phase)
        handles['line'].set_data(x, y) # Update line data inside the existing plot
        return fig


app = App(app_ui, server)
