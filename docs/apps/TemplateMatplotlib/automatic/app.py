import matplotlib.pyplot as plt
from palmerpenguins import load_penguins
from shiny.express import input, render, ui

ui.input_slider("n", "Number of bins", 1, 100, 20)
ui.input_dark_mode(id="dark_mode")

@render.plot(alt="A histogram")
def plot():
    if input.dark_mode() == "dark":
        style_label = 'dark_background'
    else:
        style_label = 'seaborn-v0_8'

    df = load_penguins()
    mass = df["body_mass_g"]
    with plt.style.context(style_label):
        fig, ax = plt.subplots()
        ax.hist(mass, input.n(), density=True)
        ax.set_title("Palmer Penguin Masses")
        ax.set_xlabel("Mass (g)")
        ax.set_ylabel("Density")

    return fig