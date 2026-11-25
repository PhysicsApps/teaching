import json

import numpy as np
import plotly.graph_objects as go
from shiny import App, Inputs, Outputs, Session, render, ui


TRAIL_CYCLES = 12
FRAMES_PER_CYCLE = 16
STEPS_PER_FRAME = 8
TRAP_STRENGTH = 0.18
INITIAL_STATE = (0.55, 0.25, 0.03, 0.0)

SURFACE_SCRIPT = """
        const context = plot.getContext('2d');
        let azimuth = Math.PI / 4;
        let elevation = 0.52;

        function drawSurface(voltage) {
            const cosAzimuth = Math.cos(azimuth);
            const sinAzimuth = Math.sin(azimuth);
            const cosElevation = Math.cos(elevation);
            const sinElevation = Math.sin(elevation);
            const center = plot.width / 2;
            const scale = plot.width / 4;
            function project(x, z, height) {
                const depth = x * sinAzimuth + z * cosAzimuth;
                return [
                    center + scale * (x * cosAzimuth - z * sinAzimuth),
                    center + scale * (depth * sinElevation - height * cosElevation),
                    depth * cosElevation + height * sinElevation,
                ];
            }

            context.clearRect(0, 0, plot.width, plot.height);
            context.font = '18px sans-serif';
            context.fillStyle = '#28374a';
            context.fillText('Instantaneous quadrupole potential', 20, 30);

            const resolution = 24;
            const vertices = Array.from({length: resolution + 1}, (_, row) =>
                Array.from({length: resolution + 1}, (_, column) => {
                    const x = 2 * column / resolution - 1;
                    const z = 2 * row / resolution - 1;
                    const height = potentialAt(x, z, voltage);
                    return [...project(x, z, height), height];
                })
            );
            const tiles = [];
            for (let row = 0; row < resolution; row++) {
                for (let column = 0; column < resolution; column++) {
                    const corners = [
                        vertices[row][column], vertices[row][column + 1],
                        vertices[row + 1][column + 1], vertices[row + 1][column],
                    ];
                    const depth = corners.reduce((sum, point) => sum + point[2], 0);
                    const height = corners.reduce((sum, point) => sum + point[3], 0) / 4;
                    tiles.push({corners, depth, height});
                }
            }
            tiles.sort((a, b) => a.depth - b.depth);
            for (const {corners, height} of tiles) {
                context.beginPath();
                context.moveTo(...corners[0].slice(0, 2));
                for (const [x, y] of corners.slice(1)) context.lineTo(x, y);
                context.closePath();
                const hue = height < 0 ? 213 : 7;
                context.fillStyle = `hsl(${hue}, 65%, ${94 - 51 * Math.abs(height)}%)`;
                context.fill();
                context.strokeStyle = 'rgba(40, 55, 74, 0.21)';
                context.lineWidth = 0.65;
                context.stroke();
            }

            const labels = [
                [1.15, 0, 0, 'x'], [0, 1.15, 0, 'z'], [0, 0, 1.15, 'Potential'],
            ];
            context.fillStyle = '#28374a';
            for (const [x, z, height, label] of labels) {
                const [left, top] = project(x, z, height);
                context.fillText(label, left, top);
            }

            context.beginPath();
            let drawing = false;
            for (const [x, z] of trail) {
                if (!onSurface(x, z)) {
                    drawing = false;
                    continue;
                }
                const [left, top] = project(x, z, potentialAt(x, z, voltage));
                if (drawing) context.lineTo(left, top);
                else context.moveTo(left, top);
                drawing = true;
            }
            context.strokeStyle = '#28374a';
            context.lineWidth = 2;
            context.stroke();

            const [x, z] = state;
            if (onSurface(x, z)) {
                const [left, top] = project(x, z, potentialAt(x, z, voltage));
                context.beginPath();
                context.arc(left, top, 6, 0, 2 * Math.PI);
                context.fillStyle = '#ffcc4d';
                context.fill();
                context.stroke();
            }
        }

        function potentialAt(x, z, voltage) {
            return voltage * (x * x - 2 * z * z) / 2;
        }

        function onSurface(x, z) {
            return Math.abs(x) <= 1 && Math.abs(z) <= 1;
        }

        function rotate(horizontal, vertical) {
            azimuth += horizontal;
            elevation = Math.max(0.1, Math.min(1.45, elevation + vertical));
            showFrame();
        }

        plot.addEventListener('pointerdown', event => plot.setPointerCapture(event.pointerId));
        plot.addEventListener('pointermove', event => {
            if (plot.hasPointerCapture(event.pointerId)) {
                rotate(event.movementX * 0.01, event.movementY * 0.01);
            }
        });
        plot.addEventListener('keydown', event => {
            const direction = {
                ArrowLeft: [-0.1, 0], ArrowRight: [0.1, 0],
                ArrowUp: [0, -0.1], ArrowDown: [0, 0.1],
            }[event.key];
            if (direction) {
                event.preventDefault();
                rotate(...direction);
            }
        });
        showFrame();
"""


def build_plot(initial_state):
    extent = 1.0
    x, z, _, _ = initial_state
    grid = np.linspace(-extent, extent, 41)
    saddle = (grid[None, :] ** 2 - 2 * grid[:, None] ** 2) / 2
    potential_limit = np.max(np.abs(saddle))

    figure = go.Figure(data=[
        go.Heatmap(
            x=grid, y=grid, z=saddle,
            zmin=-potential_limit, zmax=potential_limit,
            colorscale="RdBu_r", zsmooth="best",
            colorbar=dict(title="Potential", thickness=14),
            hovertemplate="x: %{x:.3f}<br>z: %{y:.3f}<br>Φ / V₀: %{z:.3f}<extra></extra>",
        ),
        go.Scatter(
            x=[x], y=[z], mode="lines",
            line=dict(color="#28374a", width=1.5), hoverinfo="skip",
        ),
        go.Scatter(
            x=[x], y=[z], mode="markers",
            marker=dict(color="#ffcc4d", size=13, line=dict(color="#28374a", width=2)),
            hovertemplate="Charge<br>x: %{x:.3f}<br>z: %{y:.3f}<extra></extra>",
        ),
    ])
    figure.update_layout(
        template="plotly_white",
        title="Instantaneous quadrupole potential",
        showlegend=False,
        margin=dict(l=50, r=20, t=52, b=55),
        xaxis=dict(title="x", range=[-extent, extent], constrain="domain"),
        yaxis=dict(title="z", range=[-extent, extent], scaleanchor="x", constrain="domain"),
    )
    return figure, saddle


def plot_html(initial_state, frequency, static_potential, view_3d=False):
    saddle = []
    if not view_3d:
        figure, grid = build_plot(initial_state)
        saddle = grid.tolist()
    if static_potential:
        frequency = 1
    x, z, vx, vz = initial_state
    # Convert the initial velocities from RF phase to simulation time.
    solver_state = (x, z, vx * frequency, vz * frequency)
    animation_script = f"""
        const plot = document.getElementById('{{plot_id}}');
        const button = document.getElementById('paul-trap-playback');
        const time = document.getElementById('paul-trap-time');
        const saddle = {json.dumps(saddle)};
        const initialState = {json.dumps(solver_state)};
        const strength = {TRAP_STRENGTH};
        const staticPotential = {json.dumps(static_potential)};
        const view3d = {json.dumps(view_3d)};
        const stepsPerFrame = {STEPS_PER_FRAME};
        const framesPerCycle = {FRAMES_PER_CYCLE} / {frequency};
        const trailLength = Math.ceil({TRAIL_CYCLES} * framesPerCycle) + 1;
        const phasePerFrame = 2 * Math.PI / framesPerCycle;
        const step = 2 * Math.PI / ({FRAMES_PER_CYCLE} * stepsPerFrame);
        const phasePerStep = phasePerFrame / stepsPerFrame;
        let state = initialState;
        const trail = [initialState];
        const frameInterval = 65;
        let frameId = null;
        let lastFrameTime = 0;
        let index = 0;

        function amplitude(phase) {{
            return staticPotential ? 1 : Math.cos(phase);
        }}

        function derivative(phase, state) {{
            const [x, z, vx, vz] = state;
            const field = strength * amplitude(phase);
            return [vx, vz, -field * x, 2 * field * z];
        }}

        function offset(state, slope, increment) {{
            return state.map((value, i) => value + increment * slope[i]);
        }}

        function integrateFrame(startPhase, state) {{
            for (let substep = 0; substep < stepsPerFrame; substep++) {{
                const phase = startPhase + substep * phasePerStep;
                const k1 = derivative(phase, state);
                const k2 = derivative(phase + phasePerStep / 2, offset(state, k1, step / 2));
                const k3 = derivative(phase + phasePerStep / 2, offset(state, k2, step / 2));
                const k4 = derivative(phase + phasePerStep, offset(state, k3, step));
                state = state.map((value, i) =>
                    value + step * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) / 6
                );
            }}
            return state;
        }}

        function showFrame() {{
            const [x, z] = state;
            const voltage = amplitude((index % framesPerCycle) * phasePerFrame);
            if (view3d) {{
                drawSurface(voltage);
            }} else {{
                const potential = saddle.map(row => row.map(value => value * voltage));
                Plotly.update(plot, {{
                    z: [potential, undefined, undefined],
                    x: [undefined, trail.map(point => point[0]), [x]],
                    y: [undefined, trail.map(point => point[1]), [z]],
                }}, {{}}, [0, 1, 2]);
            }}
            time.textContent = (index / framesPerCycle).toFixed(4);
        }}

        function animate(now) {{
            if (!plot.isConnected) return;
            if (now - lastFrameTime >= frameInterval) {{
                state = integrateFrame((index % framesPerCycle) * phasePerFrame, state);
                index++;
                trail.push(state);
                if (trail.length > trailLength) trail.shift();
                showFrame();
                lastFrameTime = now;
            }}
            frameId = requestAnimationFrame(animate);
        }}

        function pause() {{
            if (frameId !== null) cancelAnimationFrame(frameId);
            frameId = null;
            button.textContent = 'Start simulation';
        }}

        button.addEventListener('click', () => {{
            if (frameId !== null) {{
                pause();
                return;
            }}
            lastFrameTime = performance.now();
            frameId = requestAnimationFrame(animate);
            button.textContent = 'Pause simulation';
        }});

        button.disabled = false;
    """
    if view_3d:
        canvas = ui.tags.canvas(
            id="paul-trap-surface", width=720, height=720, tabindex=0,
            aria_label="3D potential surface. Drag or use the arrow keys to rotate.",
        )
        script = animation_script.replace("{plot_id}", "paul-trap-surface")
        return f"{canvas}<script>(() => {{ {script}{SURFACE_SCRIPT} }})();</script>"
    return figure.to_html(
        full_html=False, include_plotlyjs=True, post_script=animation_script,
        default_height="100%", config={"responsive": True},
    )


app_ui = ui.page_fluid(
    ui.tags.style("""
        .paul-trap-demo {
            display: grid;
            grid-template-rows: auto minmax(0, 1fr);
            height: calc(100vh - 1rem);
            min-height: 420px;
        }
        .paul-trap-controls {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-top: 0.5rem;
        }
        .paul-trap-plot > div { height: 100%; }
        .paul-trap-plot > canvas {
            display: block;
            width: 100%;
            height: 100%;
            object-fit: contain;
            touch-action: none;
            cursor: grab;
        }
    """),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_slider("initial_x", "Initial x", -1, 1, INITIAL_STATE[0], step=0.001),
            ui.input_slider("initial_z", "Initial z", -1, 1, INITIAL_STATE[1], step=0.001),
            ui.input_checkbox("static_potential", "Static potential", value=False),
            ui.input_checkbox("view_3d", "3D potential surface", value=False),
            ui.panel_conditional(
                "!input.static_potential",
                ui.input_slider("frequency", "Frequency)", 0.5, 2, 1, step=0.01),
            ),
        ),
        ui.output_ui("simulation"),
    ),
    title="Paul Trap",
)

def server(input: Inputs, output: Outputs, session: Session):
    @render.ui
    def simulation():
        initial_state = (input.initial_x(), input.initial_z(), *INITIAL_STATE[2:])
        static_potential = input.static_potential()
        time_label = "Time"
        return ui.div(
            ui.div(
                ui.tags.button(
                    "Start simulation", id="paul-trap-playback", type="button",
                    class_="btn btn-primary", disabled=True,
                ),
                ui.span(time_label, ui.span("0.0000", id="paul-trap-time")),
                class_="paul-trap-controls",
            ),
            ui.div(
                ui.HTML(plot_html(initial_state, input.frequency(), static_potential, input.view_3d())),
                class_="paul-trap-plot",
            ),
            class_="paul-trap-demo",
        )


app = App(app_ui, server)
