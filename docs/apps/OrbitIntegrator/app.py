import numpy as np
import plotly.graph_objects as go
from shiny import App, Inputs, Outputs, Session, render, ui, reactive
from copy import deepcopy


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select('ref_frame', 'Reference Frame', choices=['Heliocentric', 'Geocentric'], selected='Geocentric'),
        ui.input_selectize('bodies', 'Bodies to Simulate', {'Sun': 'Sun', 'Moon': 'Moon'},
                           selected=['Sun', 'Earth', 'Moon'], multiple=True),
        ui.input_slider('time_step', 'Time Step (hours)', min=1, max=24, value=5, step=0.01),
        ui.input_slider('total_time', 'Total Simulation Time (days)', min=0, max=365, value=5, step=0.005),
        ui.input_slider('max_frames', 'Maximum Animation Frames', min=100, max=10000, value=1000, step=100),
        ui.input_dark_mode(id='dark_mode'),
    ),
    ui.output_ui("plot", height='100%')
)

class Body:
    def __init__(self, mass: float, position, velocity, name: str=None):
        self.name = name
        self.mass = mass
        self.pos = position
        self.velo = velocity

    def return_vec(self):
        return np.concatenate((self.pos, self.velo))


class Simulation:
    def __init__(self, bodies: list[Body]):
        self.calc_diff_eqs: callable = None
        self.diff_eq_kwargs: dict = {}

        self.times = None
        self.history = None
        self.bodies = bodies
        self.N_bodies = len(self.bodies)

        self.quant_vec = np.concatenate(np.array([i.return_vec() for i in self.bodies]))
        self.mass_vec = np.array([i.mass for i in self.bodies])
        self.name_vec = [i.name for i in self.bodies]

    def set_diff_eq(self, calc_diff_eqs: callable, **kwargs):
        """
        Method which assigns an external solver function as the diff-eq solver for RK4.
        For N-body or gravitational setups, this is the function which calculates accelerations.
        ---------------------------------
        Params:
            calc_diff_eqs: A function which returns a [y] vector for RK4
            **kwargs: Any additional inputs/hyperparameters the external function requires
        """
        self.diff_eq_kwargs = kwargs
        self.calc_diff_eqs = calc_diff_eqs

    def rk4(self, t:float, dt:float):
        """
        RK4 integrator. Calculates the K values and returns a new y vector
        --------------------------------
        Params:
            t: a time.
            dt: timestep.
        """
        k1 = dt * self.calc_diff_eqs(t,self.quant_vec,self.mass_vec,**self.diff_eq_kwargs)
        k2 = dt * self.calc_diff_eqs(t + 0.5*dt,self.quant_vec+0.5*k1,self.mass_vec,**self.diff_eq_kwargs)
        k3 = dt * self.calc_diff_eqs(t + 0.5*dt,self.quant_vec+0.5*k2,self.mass_vec,**self.diff_eq_kwargs)
        k4 = dt * self.calc_diff_eqs(t + dt,self.quant_vec + k2,self.mass_vec,**self.diff_eq_kwargs)

        y_new = self.quant_vec + ((k1 + 2*k2 + 2*k3 + k4) / 6.0)

        return y_new


    def run(self, T, dt, t0=0):
        """
        Method which runs the simulation on a given set of bodies.
        ---------------------
        Params:
            T: total time (in simulation units) to run the simulation.
            dt: timestep (in simulation units) to advance the simulation.
            t0 (optional): set a non-zero start time to the simulation.

        Returns:
            None, but leaves an attribute history accessed via
            'simulation.history' which contains all y vectors for the simulation.
            These are of shape (Nstep,Nbodies * 6), so the x and y positions of particle 1 are
            simulation.history[:,0], simulation.history[:,1], while the same for particle 2 are
            simulation.history[:,6], simulation.history[:,7]. Velocities are also extractable.
        """

        if self.calc_diff_eqs is None:
            raise AttributeError('You must set a differential equation to solve first.')

        self.history = [self.quant_vec]
        nsteps = int((T - t0) / dt)
        for step in range(nsteps):
            y_new = self.rk4(step, dt)
            self.history.append(y_new)
            self.quant_vec = y_new
        self.history = np.array(self.history)
        self.times = np.arange(nsteps) * dt

    def translate_history_to_dict(self):
        """
        Method which translates the history array into a dictionary of arrays for easier access.
        ----------------------
        Params:
            None
        Returns:
            A dictionary where each key is the name of a body, and each value is another dictionary
            with keys 'pos' and 'velo' containing the position and velocity arrays over time.
        """

        if self.history is None:
            raise AttributeError('You must run the simulation first.')
        history_dict = {}
        for i, name in enumerate(self.name_vec):
            history_dict[name] = {'pos': self.history[:, i*6:i*6+3],
                                  'velo': self.history[:, i*6+3:i*6+6]}
        return history_dict


grav_constant = 6.67430e-11  # m^3 kg^-1 s^-2
def nbody_gravity(t, y, masses, progress_callback=None):
    """
    y: 1D array with length 6*N in the layout [x,y,z,vx,vy,vz,  x,y,z,vx,vy,vz, ...]
    masses: array-like of length N
    """

    y = np.asarray(y)
    masses = np.asarray(masses)
    N = len(masses)
    assert y.size == 6 * N, "y must have length 6*N"

    # reshape into (N,6): columns 0:3 => pos, 3:6 => vel
    state = y.reshape(N, 6)
    pos = state[:, 0:3]   # (N,3)
    vel = state[:, 3:6]   # (N,3)

    # pairwise displacement: r_ij = pos[i] - pos[j]
    rij = pos[:, None, :] - pos[None, :, :]   # (N, N, 3)

    # distances
    dist2 = np.sum(rij * rij, axis=2)        # (N, N)

    # compute |r|^3 with safety for self-terms
    dist3 = dist2 * np.sqrt(dist2)           # (N, N)

    # avoid division by zero on diagonal by setting diagonal to inf so contribution is 0
    np.fill_diagonal(dist3, np.inf)

    # acceleration: -G * sum_j m_j * r_ij / |r_ij|^3
    # einsum sums over j: result shape (N,3)
    acc = -grav_constant * np.einsum('ijk,ij->ik', rij, 1.0 / dist3   * masses[None, :])

    # assemble derivative in same interleaved format
    dydt = np.empty_like(state)
    dydt[:, 0:3] = vel
    dydt[:, 3:6] = acc

    if progress_callback is not None:
        progress_callback(t)

    return dydt.reshape(-1)

def server(input: Inputs, output: Outputs, session: Session):
    Sun = Body(mass=1.989e30, # kg
               position=np.array([0, 0, 0]), # m
               velocity=np.array([0, 0, 0]), # m/s
               name='Sun')

    Earth = Body(mass=5.972e24,  # kg
                 position=np.array([1.496e11, 0., 0.]),  # m
                 velocity=np.array([0, 29780, 0]),  # m/s
                 name='Earth')

    Moon = Body(mass=7.347e22,  # kg
                position=np.array([1.496e11 + 3.844e8, 0., 0.]),  # m
                velocity=np.array([0, 29780 + 1022, 0]),  # m/s
                name='Moon')

    bodies = [Sun, Earth, Moon]

    @reactive.calc
    def sim():
        with ui.Progress(min=0, max=input.total_time() * 86400) as p:
            p.set(message='Solving...')
            selected_bodies = input.bodies()
            simulation = Simulation([Earth, *[body for body in [Sun, Earth, Moon] if body.name in selected_bodies]])
            simulation.set_diff_eq(nbody_gravity)
            simulation.run(T=input.total_time() * 86400, dt=input.time_step() * 3600)
        ui.notification_show("Simulation complete!", type="message")
        return simulation.translate_history_to_dict()

    @render.ui
    def plot():
        # Set template based on dark mode
        if input.dark_mode() == "dark":
            template = "plotly_dark"
        else:
            template = "plotly_white"


        result = deepcopy(sim())
        if input.ref_frame() == 'Geocentric':
            earth_pos = result['Earth']['pos']
            for body_name, data in result.items():
                data['pos'] = data['pos'] - earth_pos

        fig = go.Figure()

        # Initialize empty scatter for animation
        for body_name, data in result.items():
            fig.add_trace(go.Scatter3d(
                x=[], y=[], z=[],
                mode="markers", marker=dict(size=10), name=body_name
            )) # current position


        # Create frames for animation
        frames = []
        N_steps = result[body_name]['pos'].shape[0]
        N_bodies = len(result.keys())

        if N_steps > input.max_frames():
            indices = np.linspace(0, N_steps, input.max_frames(), endpoint=False).astype(int)
        else:
            indices = list(range(N_steps))

        with ui.Progress(min=0, max=len(indices)) as p:
            p.set(message='Creating frames...')
            for k in indices:
                frame_data = []
                for body_name, data in result.items():
                    frame_data.append(go.Scatter3d(
                        x=[data['pos'][k,0]],
                        y=[data['pos'][k,1]],
                        z=[data['pos'][k,2]]
                    ))
                frames.append(go.Frame(data=frame_data, traces=list(range(N_bodies)), name=f'frame{k}'))
                p.set(k)

            fig.update(frames=frames)

        for body_name, data in result.items():
            fig.add_trace(go.Scatter3d(
                        x=data['pos'][:,0],
                        y=data['pos'][:,1],
                        z=data['pos'][:,2],
                mode="lines", line=dict(color="grey", width=2), showlegend=False,
            )) # full trajectory

        def frame_args(duration):
            return {
                    "frame": {"duration": duration},
                    "mode": "immediate",
                    "fromcurrent": True,
                    "transition": {"duration": duration, "easing": "linear"},
                    }


        sliders = [
            {"pad": {"b": 10, "t": 60},
             "len": 0.9,
             "x": 0.1,
             "y": 0,

             "steps": [
                         {"args": [[f.name], frame_args(0)],
                          "label": str(k),
                          "method": "animate",
                          } for k, f in enumerate(fig.frames)
                      ]
             }
                ]

        fig.update_layout(
            updatemenus = [{"buttons":[
                            {
                                "args": [None, frame_args(50)],
                                "label": "Play",
                                "method": "animate",
                            },
                            {
                                "args": [[None], frame_args(0)],
                                "label": "Pause",
                                "method": "animate",
                          }],

                        "direction": "left",
                        "pad": {"r": 10, "t": 70},
                        "type": "buttons",
                        "x": 0.1,
                        "y": 0,
                    }
                 ],
                 sliders=sliders
            )

        # Collect max x and y values for setting axis limits
        max_range = 0
        for body_name, data in result.items():
            pos = data['pos']
            max_range = max(max_range,
                            np.max(np.abs(pos[:,0])),
                            np.max(np.abs(pos[:,1])),
                            np.max(np.abs(pos[:,2])))
        axis_limit = max_range * 1.2

        fig.update_layout(
            scene=dict(
                xaxis_title='X Position (m)',
                yaxis_title='Y Position (m)',
                zaxis_title='Z Position (m)',
                xaxis_showspikes=False,
                yaxis_showspikes=False,
                zaxis_showspikes=False,
                xaxis=dict(range=[-axis_limit, axis_limit]),
                yaxis=dict(range=[-axis_limit, axis_limit]),
            ),
            height=700,
            template=template,
            sliders = sliders
        )
        return ui.HTML(fig.to_html())

app = App(app_ui, server)
