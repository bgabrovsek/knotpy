"""
Dynamic bead–spring network for layout relaxation and visualization.

This module implements a simple 2D dynamic system over complex coordinates:
nodes (beads) connected by springs (bonds), with optional angular constraints,
chain stiffness, and short-range repulsion. It can be used to iteratively
relax a layout and (optionally) visualize the evolution.

Design notes
------------
- Geometry is represented with complex numbers for concise vector math.
- To keep `import knotpy` fast, `matplotlib` is imported locally inside
  functions that actually plot or animate.
"""

import math
import cmath
import statistics
from itertools import combinations, chain

__all__ = [
    "Network",
    "plot_bead_frame",
    "plot_force_history",
    "plot_static_frame",
    "animate_simulation",
    "simulation",
]

__version__ = "0.2"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

_EPSILON = 1e-8

DEFAULT_BOND_FORCE_CONSTANT = 0.2
DEFAULT_ANGLE_FORCE_CONSTANT = 0.2
DEFAULT_STIFFNESS_FORCE_CONSTANT = 0.1
DEFAULT_REPULSIVE_CONSTANT = 0.1
DEFAULT_REPULSIVE_CUTOFF_DISTANCE = 2.0
DEFAULT_FORCE_DAMPING = 0.95

# Angle force options (kept as module switches for compatibility)
_ANGLE_FORCE_TO_MIDPOINT = True
_SIN_ANGLE_FORCE = False


def _angle(z1, z2, z3):
    """Compute the oriented angle ∠(z1, z2, z3) in radians, wrapped to [0, 2π).

    Args:
        z1: First point (complex).
        z2: Vertex point (complex).
        z3: Third point (complex).

    Returns:
        float: Angle at z2 from segment z2→z1 to z2→z3, in [0, 2π).
    """
    v1 = z1 - z2
    v2 = z3 - z2
    ang = cmath.phase(v2 / v1)  # (-π, π]
    return ang % (2 * math.pi)


def _rotate(z, center, angle):
    """Rotate complex point `z` around `center` by `angle` (radians)."""
    return center + (z - center) * cmath.exp(1j * angle)


class Network:
    """Dynamic bead–spring network in 2D (complex plane).

    The network stores:
      - `positions`: bead positions (complex).
      - `connections`: pairs of indices (bonds).
      - `angled_triplets`: dict mapping (i, j, k) → ideal angle at j.
      - `stiff_triplets`: list of (i, j, k) for chain stiffness.
      - `forces`: current force on each bead (complex).
      - `names`: mapping from external names (e.g., knotpy nodes/endpoints) to indices.

    Forces:
      - Bond stretching to an ideal length.
      - Angular force toward an ideal angle.
      - Stiffness (prefers straight lines, i.e., ideal π).
      - Short-range repulsion with a cutoff.
      - Global damping.

    Args:
        ideal_bond_length (float): Equilibrium length of a bond (spring).
        force_constants (dict | None): Optional override:
            {
              "bond": float,
              "angle": float,
              "stiffness": float,
              "repulsion": float,
              "repulsion_cutoff": float,
              "damping": float,
            }
    """

    def __init__(self, ideal_bond_length, force_constants=None):
        self.names = {}  # external name -> index
        self.positions = []  # list[complex]
        self.connections = []  # list[tuple[int,int]]
        self.angled_triplets = {}  # dict[(i,j,k)] = ideal_angle
        self.stiff_triplets = []  # list[(i,j,k)]
        self.forces = []  # list[complex]
        self.ideal_bond_length = ideal_bond_length
        self.stability_history = []  # tracking mean net force over time
        self.frame = 0

        # force coefficients
        fc = force_constants or {}
        self.k_bond_force = fc.get("bond", DEFAULT_BOND_FORCE_CONSTANT)
        self.k_angle_force = fc.get("angle", DEFAULT_ANGLE_FORCE_CONSTANT)
        self.k_stiffness_force = fc.get("stiffness", DEFAULT_STIFFNESS_FORCE_CONSTANT)
        self.k_repulsion_force = fc.get("repulsion", DEFAULT_REPULSIVE_CONSTANT)
        self.repulsion_cutoff_distance = fc.get("repulsion_cutoff", DEFAULT_REPULSIVE_CUTOFF_DISTANCE)
        self.force_damping = fc.get("damping", DEFAULT_FORCE_DAMPING)

        # indices each bead should consider for repulsion (precomputed)
        self.repulsed_to = None

    # ---- Construction helpers -------------------------------------------------

    def compute_repulsive_ignore(self):
        """Precompute which bead pairs should be repelled.

        Repulsion skips immediate neighbors along bonds, stiff triplets,
        and angled triplets to avoid fighting primary constraints.
        """
        not_repulsed_to = [set() for _ in self.positions]
        for i in range(len(self.positions)):
            for t in chain(self.stiff_triplets, self.angled_triplets, self.connections):
                if i in t:
                    not_repulsed_to[i].update(t)
        self.repulsed_to = [set(range(len(self.positions))) - not_repulsed_to[i] for i in range(len(self.positions))]

    def add_point(self, point, name):
        """Add a bead if `name` is new; otherwise reuse the index.

        Args:
            point (complex): Position of the bead.
            name (Any): External identifier to map to this bead.
        """
        if name not in self.names:
            self.names[name] = len(self.positions)
            self.positions.append(point)
            self.forces.append(0j)

    def add_angled_triplet(self, triplet, angle):
        """Register an angular constraint.

        Args:
            triplet (tuple): Indices or external names (i, j, k) with angle at j.
            angle (float): Ideal angle in radians.
        """
        indices = tuple(self.names[_] for _ in triplet)
        self.angled_triplets[indices] = angle

    def add_connections_from(self, connections):
        """Add multiple connections.

        Args:
            connections (Iterable[tuple[(complex, name), (complex, name)]]):
                Each connection includes (point, name) pairs for its endpoints.
        """
        for c in connections:
            self.add_connection(c)

    def add_connection(self, connection: tuple):
        """Add a single bond.

        Args:
            connection: ((point_a, name_a), (point_b, name_b)).
        """
        a_point, a_name = connection[0]
        b_point, b_name = connection[1]
        self.add_point(a_point, a_name)
        self.add_point(b_point, b_name)

        a_index = self.names[a_name]
        b_index = self.names[b_name]
        if a_index == b_index:
            raise ValueError("Connection points are the same")

        idx_pair = (min(a_index, b_index), max(a_index, b_index))
        if idx_pair not in self.connections:
            self.connections.append(idx_pair)

    def add_stiff_triplets_from(self, triplets):
        """Add multiple stiffness triplets (i, j, k)."""
        for triplet in triplets:
            self.add_stiff_triplet(triplet)

    def add_stiff_triplet(self, triplet):
        """Add a single stiffness triplet (i, j, k)."""
        indices = tuple(self.names[_] for _ in triplet)
        self.stiff_triplets.append(indices)

    # ---- Measurements / transforms -------------------------------------------

    def average_connection_length(self):
        """Average bond length across all connections."""
        return statistics.mean(self.distances()) if self.connections else 0.0

    def distances(self):
        """List of bond lengths across all connections."""
        return [abs(self.positions[i] - self.positions[j]) for i, j in self.connections]

    def scale(self, factor):
        """Uniformly scale all bead positions by `factor`."""
        self.positions = [p * factor for p in self.positions]

    # ---- Force models ---------------------------------------------------------

    def _repulsive_force(self, i, j):
        """Apply short-range repulsion between beads i and j."""
        dist = abs(self.positions[i] - self.positions[j])
        if 0.0 < dist < self.repulsion_cutoff_distance:
            force_mag = self.k_repulsion_force / (dist**2)
            force_vec = (self.positions[i] - self.positions[j]) / dist * force_mag
            self.forces[i] += force_vec
            self.forces[j] -= force_vec

    def _bond_force(self, i, j):
        """Apply spring force between connected beads i and j."""
        vec = self.positions[i] - self.positions[j]
        dist = abs(vec) or 1e-12
        force_mag = -(dist - self.ideal_bond_length) * self.k_bond_force
        self.forces[i] += 0.5 * force_mag * vec / dist
        self.forces[j] += -0.5 * force_mag * vec / dist

    def _angle_force(self, i1, i2, i3, ideal_angle):
        """Apply angular force toward `ideal_angle` at middle bead i2."""
        z1, z2, z3 = self.positions[i1], self.positions[i2], self.positions[i3]
        angle = _angle(z1, z2, z3)
        angle_diff = angle - ideal_angle
        v1 = z1 - z2
        v2 = z3 - z2

        perp1 = complex(-v1.imag, v1.real)
        perp2 = complex(v2.imag, -v2.real)
        if abs(perp1) != 0:
            perp1 /= abs(perp1)
        if abs(perp2) != 0:
            perp2 /= abs(perp2)

        if _SIN_ANGLE_FORCE:
            force1 = self.k_angle_force * math.sin(angle_diff) * perp1
            force3 = self.k_angle_force * math.sin(angle_diff) * perp2
        else:
            force1 = self.k_angle_force * angle_diff * perp1
            force3 = self.k_angle_force * angle_diff * perp2

        self.forces[i1] += force1
        self.forces[i3] += force3
        if _ANGLE_FORCE_TO_MIDPOINT:
            self.forces[i2] -= (force1 + force3)

    def _stiff_force(self, i1, i2, i3):
        """Apply stiffness (prefers π angle at middle bead i2)."""
        z1, z2, z3 = self.positions[i1], self.positions[i2], self.positions[i3]
        angle = _angle(z1, z2, z3)
        angle_diff = angle - math.pi
        v1 = z1 - z2
        v2 = z3 - z2

        perp1 = complex(-v1.imag, v1.real)
        perp2 = complex(v2.imag, -v2.real)
        if abs(perp1) != 0:
            perp1 /= abs(perp1)
        if abs(perp2) != 0:
            perp2 /= abs(perp2)

        if _SIN_ANGLE_FORCE:
            force1 = self.k_stiffness_force * math.sin(angle_diff) * perp1
            force3 = self.k_stiffness_force * math.sin(angle_diff) * perp2
        else:
            force1 = self.k_stiffness_force * angle_diff * perp1
            force3 = self.k_stiffness_force * angle_diff * perp2

        self.forces[i1] += force1
        self.forces[i3] += force3
        if _ANGLE_FORCE_TO_MIDPOINT:
            self.forces[i2] -= (force1 + force3)

    # ---- Dynamics -------------------------------------------------------------

    def compute_forces(self):
        """Compute all forces for the current configuration."""
        if self.repulsed_to is None:
            self.compute_repulsive_ignore()

        self.forces = [0j for _ in self.positions]

        # bonds
        for i, j in self.connections:
            self._bond_force(i, j)

        # angle constraints
        for triplet, ideal_angle in self.angled_triplets.items():
            self._angle_force(*triplet, ideal_angle)

        # stiffness
        for triplet in self.stiff_triplets:
            self._stiff_force(*triplet)

        # short-range repulsion (skips neighbors)
        for i in range(len(self.positions)):
            for j in self.repulsed_to[i]:
                self._repulsive_force(i, j)

    def net_force_magnitude(self):
        """Mean magnitude of forces across beads (a stability indicator)."""
        return statistics.mean(abs(f) for f in self.forces) if self.forces else 0.0

    def step(self, dt):
        """Advance the simulation by a single time step.

        Args:
            dt (float): Time step multiplier applied to the velocity (force proxy).
        """
        self.compute_forces()
        velocities = [f * self.force_damping for f in self.forces]
        self.positions = [p + v * dt for p, v in zip(self.positions, velocities)]
        self.stability_history.append(self.net_force_magnitude())
        self.frame += 1

    def __repr__(self):
        def _r(z):
            return f"{z.real:.2f} {'+' if z.imag >= 0 else '-'} {abs(z.imag):.2f}j"

        d = {i: _r(p) for i, p in enumerate(self.positions)}
        return f"BeadNetwork {', '.join(f'{k}: {v}' for k, v in d.items())}\n            {self.connections})"


# ---- Plotting / animation (local imports for fast module load) ---------------

def plot_bead_frame(ax, network, show_indices=False):
    """Plot a single frame of the bead network onto the provided Axes.

    Args:
        ax (matplotlib.axes.Axes): Target axes.
        network (Network): Network to draw.
        show_indices (bool): If True, annotate bead indices and names.
    """
    x = [p.real for p in network.positions]
    y = [p.imag for p in network.positions]
    ax.clear()
    ax.scatter(x, y, color="blue", s=30)

    for i, j in network.connections:
        p1, p2 = network.positions[i], network.positions[j]
        ax.plot([p1.real, p2.real], [p1.imag, p2.imag], color="red", alpha=0.3)

    for i, j, k in network.angled_triplets:
        p1, p2, p3 = network.positions[i], network.positions[j], network.positions[k]
        ax.plot([p1.real, p2.real, p3.real], [p1.imag, p2.imag, p3.imag], color="green", alpha=0.3)

    if show_indices:
        for i, p in enumerate(network.positions):
            ax.text(p.real, p.imag, str(i), fontsize=8, ha="right", va="bottom", color="black")
        for name in network.names:
            if not isinstance(name, tuple):
                i = network.names[name]
                p = network.positions[i]
                ax.text(p.real, p.imag, str(name), fontsize=10, ha="left", va="top", color="black")

    ax.set_aspect("equal")
    ax.set_title("Bead Network Simulation")
    ax.grid(True)


def plot_force_history(ax, network):
    """Plot the history of the mean net force magnitude over time.

    Args:
        ax (matplotlib.axes.Axes): Target axes.
        network (Network): Source of `stability_history`.
    """
    y = network.stability_history
    x = list(range(len(y)))
    ax.clear()
    ax.plot(x, y, color="purple")
    ax.set_ylim(0, 3)
    ax.set_ylabel("Net Force")
    ax.set_xlabel("Step")
    ax.set_title("Net Force Over Time")
    ax.grid(True)


def plot_static_frame(network, show_indices=False):
    """Plot a single static frame of the bead network.

    Args:
        network (Network): The network to draw.
        show_indices (bool): If True, annotate bead indices and names.
    """
    import matplotlib.pyplot as plt  # local import

    fig, ax = plt.subplots()
    plot_bead_frame(ax, network, show_indices=show_indices)
    plt.show()


def animate_simulation(network, dt=0.1, show=True):
    """Animate the network dynamics with a two-panel view (geometry + force).

    Args:
        network (Network): The network to simulate.
        dt (float): Time step used in `Network.step`.
        show (bool): If True, call `plt.show()` at the end.
    """
    import matplotlib.pyplot as plt  # local import
    import matplotlib.animation as animation  # local import

    steps = 100
    fig, (ax_network, ax_force) = plt.subplots(
        2, 1, figsize=(6, 8), gridspec_kw={"height_ratios": [3, 1]}
    )
    plt.tight_layout()

    def update(_frame):
        network.step(dt)
        plot_bead_frame(ax_network, network)
        plot_force_history(ax_force, network)

    animation.FuncAnimation(fig, update, frames=steps, interval=50)
    if show:
        plt.show()


def simulation(network, dt=0.1, force_constants=None, show=False):
    """Run a fixed number of steps and return the stability series.

    This helper runs the dynamics for 100 steps and returns the list of mean
    net force magnitudes at each step. It does **not** plot.

    Args:
        network (Network): The network to simulate.
        dt (float): Time step used in `Network.step`.
        force_constants: Unused (reserved for future).
        show (bool): Unused (reserved for future).

    Returns:
        list[float]: Mean net force magnitude per step.
    """
    stability = []
    for _ in range(100):
        network.step(dt)
        stability.append(network.net_force_magnitude())
    return stability