import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import cmath
import statistics
from itertools import combinations, chain

_EPSILON = 1e-8

DEFAULT_BOND_FORCE_CONSTANT=0.2
DEFAULT_ANGLE_FORCE_CONSTANT=0.2
DEFAULT_STIFFNESS_FORCE_CONSTANT=0.1
DEFAULT_REPULSIVE_CONSTANT=0.1
DEFAULT_REPULSIVE_CUTOFF_DISTANCE = 2.0
DEFAULT_FORCE_DAMPING=0.95

_ANGLE_FORCE_TO_MIDPOINT = True
_SIN_ANGLE_FORCE = False

def _angle(z1, z2, z3):
    """Compute the angle between z1, z2, and z3 in radians."""
    v1 = z1 - z2
    v2 = z3 - z2
    angle = cmath.phase(v2 / v1)  # returns angle in (-π, π]
    return angle % (2 * math.pi)  # wrap to [0, 2π)

def _rotate(z, center, angle):
    """Rotate complex point z around center by angle (radians)."""
    return center + (z - center) * cmath.exp(1j * angle)

class Network:
    def __init__(self, ideal_bond_length, force_constants=None):
        self.names = {}  # keys are knotpy items (nodes, endpoints), values are point indices
        self.positions = []  # atom positions
        self.connections = []  # tuples of atom indices
        self.angled_triplets = {}  # triplets of atoms that span an angle - nodes (keys are triplets, values are angles)
        self.stiff_triplets = []  # three consecutive points on an edge
        self.forces = []  # current force of each atom
        self.ideal_bond_length = ideal_bond_length
        self.stability_history = []  # how stable the system is over time
        self.frame = 0  # current frame

        # network forces
        force_constants = force_constants or {}
        self.k_bond_force = force_constants.get("bond", DEFAULT_BOND_FORCE_CONSTANT)
        self.k_angle_force = force_constants.get("angle", DEFAULT_ANGLE_FORCE_CONSTANT)
        self.k_stiffness_force = force_constants.get("stiffness", DEFAULT_STIFFNESS_FORCE_CONSTANT)
        self.k_repulsion_force = force_constants.get("repulsion", DEFAULT_REPULSIVE_CONSTANT)
        self.repulsion_cutoff_distance = force_constants.get("repulsion_cutoff", DEFAULT_REPULSIVE_CUTOFF_DISTANCE)
        self.force_damping = force_constants.get("damping", DEFAULT_FORCE_DAMPING)

        # for repulsive force ignore neighbours
        self.repulsed_to = None

    def compute_repulsive_ignore(self):
        # for every atom compute to which atoms it is repulsed to
        not_repulsed_to = [set() for _ in self.positions]
        for i in range(len(self.positions)):
            for t in chain(self.stiff_triplets, self.angled_triplets, self.connections):
                if i in t:
                    not_repulsed_to[i].update(t)
        self.repulsed_to = [set(range(len(self.positions))) - not_repulsed_to[i] for i in range(len(self.positions))]

    def add_point(self, point, name):
        if name not in self.names:
            self.names[name] = len(self.positions)  # add index to names
            self.positions.append(point)
            self.forces.append(complex(0, 0))

    def add_angled_triplet(self, triplet, angle):
        indices = tuple(self.names[_] for _ in triplet)
        self.angled_triplets[indices] = angle

    # def index(self, point):
    #     # index of a point
    #     if point in self.positions:
    #         return self.positions.index(point)
    #     pwr = self.points_within_radius(point, _EPSILON)
    #     if len(pwr) == 1:
    #         return pwr[0]
    #     raise IndexError(f"Point {point} not found in network")

    # def points_within_radius(self, point, radius):
    #     return [i for i, p in enumerate(self.positions) if abs(p - point) <= radius]

    def add_connections_from(self, connections):
        for c in connections:
            self.add_connection(c)

    def add_connection(self, connection: tuple):
        # sort connection
        a_point, a_name = connection[0]
        b_point, b_name = connection[1]
        self.add_point(a_point, a_name)
        self.add_point(b_point, b_name)

        a_index = self.names[a_name]
        b_index = self.names[b_name]
        if a_index == b_index:
            raise ValueError("Connection points are the same")

        index_connection = (min(a_index, b_index), max(a_index, b_index))
        if index_connection not in self.connections:
            self.connections.append(index_connection)

    def add_stiff_triplets_from(self, triplets):
        for triplet in triplets:
            self.add_stiff_triplet(triplet)

    def add_stiff_triplet(self, triplet):
        indices = tuple(self.names[_] for _ in triplet)
        self.stiff_triplets.append(indices)

    def average_connection_length(self):
        """Compute the average distance between connected beads."""
        return statistics.mean(self.distances()) if self.connections else 0.0

    def distances(self):
        """Compute the average distance between connected beads."""
        return [abs(self.positions[i] - self.positions[j]) for i, j in self.connections]

    def scale(self, factor):
        """Scale all bead positions by a given factor."""
        self.positions = [p * factor for p in self.positions]

    def _repulsive_force(self, i, j):
        """Compute the repulsive force on bead k due to the distance between beads i and j."""
        dist = abs(self.positions[i] - self.positions[j])
        if 0.0 < dist < self.repulsion_cutoff_distance:
            force_mag = self.k_repulsion_force / (dist ** 2)
            force_vec = (self.positions[i] - self.positions[j]) / dist * force_mag
            self.forces[i] += force_vec
            self.forces[j] -= force_vec

    def _bond_force(self, i, j):
        vec = self.positions[i] - self.positions[j]
        dist = abs(vec)
        force_mag = - (dist - self.ideal_bond_length) * self.k_bond_force

        self.forces[i] += 0.5 * force_mag * vec / dist
        self.forces[j] += -0.5 * force_mag * vec / dist

    def _angle_force(self, i1, i2, i3, ideal_angle):
        """Compute the force on bead k due to the angle between beads i and j."""
        z1, z2, z3 = self.positions[i1], self.positions[i2], self.positions[i3]
        angle = _angle(z1, z2, z3)
        angle_diff = angle - ideal_angle
        v1 = z1 - z2
        v2 = z3 - z2
        # Direction vectors perpendicular to v1 and v2 (in-plane rotation)
        perp1 = complex(-v1.imag, v1.real)
        perp2 = complex(v2.imag, -v2.real)

        # Normalize
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
        """Compute the force on bead k due to the angle between beads i and j."""
        z1, z2, z3 = self.positions[i1], self.positions[i2], self.positions[i3]
        angle = _angle(z1, z2, z3)
        angle_diff = angle - math.pi
        v1 = z1 - z2
        v2 = z3 - z2

        # Direction vectors perpendicular to v1 and v2 (in-plane rotation)
        perp1 = complex(-v1.imag, v1.real)
        perp2 = complex(v2.imag, -v2.real)

        # Normalize
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


    def compute_forces(self):
        """Compute the forces on each bead based on the force function."""
        if self.repulsed_to is None:
            self.compute_repulsive_ignore()
        # init
        self.forces = [complex(0, 0) for _ in self.positions]

        # bond forces (distance between beads)
        for i, j in self.connections:
            self._bond_force(i, j)

        # angle forces (angles between beads connected to a vertex)
        for triplet, ideal_angle in self.angled_triplets.items():
            self._angle_force(*triplet, ideal_angle)

        # stiff force
        for triplet in self.stiff_triplets:
            self._stiff_force(*triplet)

        for i in range(len(self.positions)):
            for j in self.repulsed_to[i]:
                self._repulsive_force(i, j)
        #
        # #repulsive force
        # for i, j in combinations(range(len(self.positions)), 2):
        #     # TODO: this can be precomputed
        #     if any(i in triplet and j in triplet for triplet in self.stiff_triplets):
        #         continue
        #     if any(i in triplet and j in triplet for triplet in self.angled_triplets):
        #         continue
        #     if any(i in c and j in c for c in self.connections):
        #         continue
        #     self._repulsive_force(i, j)

    def net_force_magnitude(self):
        return statistics.mean([abs(f) for f in self.forces])


    def step(self, dt):
        # one step of the dynamic simulation
        self.compute_forces()
        velocities = [f for f in self.forces]
        velocities = [v * self.force_damping for v in velocities]
        self.positions = [p + v * dt for p, v in zip(self.positions, velocities)]
        self.stability_history.append(self.net_force_magnitude())
        self.frame += 1


    def __repr__(self):
        def _r(z):
            return f"{z.real:.2f} {'+' if z.imag >= 0 else '-'} {abs(z.imag):.2f}j"
        def _d(p):
            d = dict(enumerate(p))
            return ", ".join(f"{k}: {_r(v)}" for k, v in d.items())
        return f"BeadNetwork {_d(self.positions)}\n            {self.connections})"


def plot_bead_frame(ax, network, show_indices=False):
    ax.clear()
    x = [p.real for p in network.positions]
    y = [p.imag for p in network.positions]
    ax.scatter(x, y, color='blue', s=30)

    for i, j in network.connections:
        p1, p2 = network.positions[i], network.positions[j]
        ax.plot([p1.real, p2.real], [p1.imag, p2.imag], color='red', alpha=0.3)

    for i,j,k in network.angled_triplets:
        p1,p2,p3 = network.positions[i], network.positions[j], network.positions[k]
        ax.plot([p1.real, p2.real, p3.real], [p1.imag, p2.imag, p3.imag], color='green', alpha=0.3)

    if show_indices:
        for i, p in enumerate(network.positions):
            ax.text(p.real, p.imag, str(i), fontsize=8, ha='right', va='bottom', color='black')
        for name in network.names:
            #print(name)
            if not isinstance(name, tuple):
                i = network.names[name]
                p = network.positions[i]
                ax.text(p.real, p.imag, str(name), fontsize=10, ha='left', va='top', color='black')

    ax.set_aspect('equal')
    ax.set_title("Bead Network Simulation")
    ax.grid(True)


def plot_force_history(ax, network):
    ax.clear()
    y = network.stability_history
    x = list(range(len(y)))
    ax.plot(x, y, color='purple')
    ax.set_ylim(0, 3)
    ax.set_ylabel("Net Force")
    ax.set_xlabel("Step")
    ax.set_title("Net Force Over Time")
    ax.grid(True)

def plot_static_frame(network, show_indices=False):
    """Plot a single static frame of the bead network using plot_bead_frame()."""
    fig, ax = plt.subplots()
    plot_bead_frame(ax, network, show_indices=show_indices)
    plt.show()

def animate_simulation(network, dt=0.1, show=True):

    steps = 100

    #fig, ax = plt.subplots()
    fig, (ax_network, ax_force) = plt.subplots(2, 1, figsize=(6, 8), gridspec_kw={'height_ratios': [3, 1]})
    plt.tight_layout()



    def update(frame):
        network.step(dt)
        plot_bead_frame(ax_network, network)
        plot_force_history(ax_force, network)

    ani = animation.FuncAnimation(fig, update, frames=steps, interval=50)
    plt.show()



def simulation(network, dt=0.1, force_constants=None, show=False):

    global BOND_FORCE_CONSTANT
    global ANGLE_FORCE_CONSTANT
    global STIFFNESS_FORCE_CONSTANT
    global REPULSIVE_CONSTANT

    stability = []

    for i in range(100):
        network.step(dt)
        stability.append(network.net_force_magnitude())

    return stability


if __name__ == "__main__":
    pass