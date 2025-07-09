import matplotlib.pyplot as plt
from palmerpenguins import load_penguins
from shiny.express import input, render, ui

plt.style.use('seaborn-v0_8')
ui.input_slider("n", "Number of bins", 1, 100, 20)

@render.plot(alt="A histogram")
def plot():
    df = load_penguins()
    mass = df["body_mass_g"]

    fig, ax = plt.subplots()
    ax.hist(mass, input.n(), density=True)
    ax.set_title("Palmer Penguin Masses")
    ax.set_xlabel("Mass (g)")
    ax.set_ylabel("Density")

    return fig