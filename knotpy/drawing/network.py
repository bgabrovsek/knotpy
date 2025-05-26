import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import cmath
from itertools import combinations

_EPSILON = 1e-8

BOND_FORCE_CONSTANT=10
ANGLE_FORCE_CONSTANT=0.5
STIFFNESS_FORCE_CONSTANT=0.5
REPULSIVE_CONSTANT=0.1
REPULSIVE_CUTOFF_DISTANCE = 2.0
FORCE_DAMPING=0.98

_ANGLE_FORCE_TO_MIDPOINT = True
_SIN_ANGLE_FORCE = False

def _angle(z1, z2, z3):
    v1 = z1 - z2
    v2 = z3 - z2
    angle = cmath.phase(v2 / v1)  # returns angle in (-π, π]
    return angle % (2 * math.pi)  # wrap to [0, 2π)

def _rotate(z, center, angle):
    """Rotate complex point z around center by angle (radians)."""
    return center + (z - center) * cmath.exp(1j * angle)

class Network:
    def __init__(self, ideal_bond_length):
        self.names = {}
        self.positions = []
        self.connections = []  # indices of points
        self.angled_triplets = {}  # triplets of points that should share a certain angle (keys are triplets, values are angles)
        self.stiff_triplets = []
        self.forces = []
        self.ideal_bond_length = ideal_bond_length

    def add_point(self, point, name):
        if name not in self.names:
            self.names[name] = len(self.positions)  # add index to names
            self.positions.append(point)
            self.forces.append(complex(0, 0))

    def add_angled_triplet(self, triplet, angle):
        indices = tuple(self.names[_] for _ in triplet)
        self.angled_triplets[indices] = angle

    def index(self, point):
        if point in self.positions:
            return self.positions.index(point)
        pwr = self.points_within_radius(point, _EPSILON)
        if len(pwr) == 1:
            return pwr[0]
        raise IndexError(f"Point {point} not found in network")

    def closest_endpoint_to_vertex(self, vertex, endpoint):
        """Return the name of the first point next to name_src that points towards name_dst."""
        vertex_point = self.positions[self.names[vertex]]
        closest_arc_name = None
        distance = float('inf')
        for name in self.names:
            if not isinstance(name, tuple):
                continue
            arc = tuple(name[0])
            if endpoint == arc[0] and vertex == arc[1].node or endpoint == arc[1] and vertex == arc[0].node:
                point = self.positions[self.names[name]]
                dist = abs(point - vertex_point)
                if dist < distance:
                    closest_arc_name = name
                    distance = dist
        return closest_arc_name

    def points_within_radius(self, point, radius):
        return [i for i, p in enumerate(self.positions) if abs(p - point) <= radius]

    def sanity_check(self):
        for i in range(len(self.positions)):
            for j in range(i + 1, len(self.positions)):
                if abs(self.positions[i] - self.positions[j]) < _EPSILON:
                    raise "Connection points are the same"

    def add_connection(self, connection: tuple):
        # sort connection
        a_point, a_name = connection[0]
        b_point, b_name = connection[1]

        #print("connection: ", connection)

        self.add_point(a_point, a_name)
        self.add_point(b_point, b_name)

        a_index = self.names[a_name]
        b_index = self.names[b_name]
        if a_index == b_index:
            raise ValueError("Connection points are the same")

        index_connection = (min(a_index, b_index), max(a_index, b_index))
        if index_connection not in self.connections:
            self.connections.append(index_connection)

    def add_stiff_triplet(self, triplet):
        indices = tuple(self.names[_] for _ in triplet)
        self.stiff_triplets.append(indices)

    def average_connection_length(self):
        """Compute the average distance between connected beads."""
        if not self.connections:
            return 0.0
        return sum(self.distances()) / len(self.connections)

    def distances(self):
        """Compute the average distance between connected beads."""

        return [abs(self.positions[i] - self.positions[j]) for i, j in self.connections]

    def scale(self, factor):
        """Scale all bead positions by a given factor."""
        self.positions = [p * factor for p in self.positions]


    def _repulsive_force(self, i, j):
        """Compute the repulsive force on bead k due to the distance between beads i and j."""
        dist = abs(self.positions[i] - self.positions[j])
        if 0.0 < dist < REPULSIVE_CUTOFF_DISTANCE:
            force_mag = REPULSIVE_CONSTANT / (dist ** 2)
            force_vec = (self.positions[i] - self.positions[j]) / dist * force_mag
            self.forces[i] += force_vec
            self.forces[j] -= force_vec

    def _bond_force(self, i, j):
        vec = self.positions[i] - self.positions[j]
        dist = abs(vec)
        force_mag = - (dist - self.ideal_bond_length) * BOND_FORCE_CONSTANT

        self.forces[i] += 0.5 * force_mag * vec / dist
        self.forces[j] += -0.5 * force_mag * vec / dist

    def _angle_force(self, i1, i2, i3, ideal_angle):
        """Compute the force on bead k due to the angle between beads i and j."""
        z1 = self.positions[i1]
        z2 = self.positions[i2]
        z3 = self.positions[i3]

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
            force1 = ANGLE_FORCE_CONSTANT * math.sin(angle_diff) * perp1
            force3 = ANGLE_FORCE_CONSTANT * math.sin(angle_diff) * perp2
        else:
            force1 = ANGLE_FORCE_CONSTANT * angle_diff * perp1
            force3 = ANGLE_FORCE_CONSTANT * angle_diff * perp2

        # ideal_z1 = _rotate(z1, z2, 0.5 * angle_diff)
        # ideal_z3 = _rotate(z3, z2, -0.5 * angle_diff)
        #
        # force_mag_1 = (z1 - ideal_z1) * ANGLE_FORCE_CONSTANT
        # force_mag_3 = (z2 - ideal_z3) * ANGLE_FORCE_CONSTANT

        if _ANGLE_FORCE_TO_MIDPOINT:
            # self.forces[i1] += force_mag_1 * 2/3
            # self.forces[i3] += force_mag_3 * 2/3
            # self.forces[i2] += - (force_mag_1 + force_mag_3) * 1/3

            self.forces[i1] += force1
            self.forces[i3] += force3
            self.forces[i2] -= (force1 + force3)
        else:
            # self.forces[i1] += force_mag_1
            # self.forces[i3] += force_mag_3

            self.forces[i1] += force1
            self.forces[i3] += force3
            #self.forces[i2] -= (force1 + force3)

    def _stiff_force(self, i1, i2, i3):

        """Compute the force on bead k due to the angle between beads i and j."""
        z1 = self.positions[i1]
        z2 = self.positions[i2]
        z3 = self.positions[i3]

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
            force1 = STIFFNESS_FORCE_CONSTANT * math.sin(angle_diff) * perp1
            force3 = STIFFNESS_FORCE_CONSTANT * math.sin(angle_diff) * perp2
        else:
            force1 = STIFFNESS_FORCE_CONSTANT * angle_diff * perp1
            force3 = STIFFNESS_FORCE_CONSTANT * angle_diff * perp2


        if _ANGLE_FORCE_TO_MIDPOINT:
            self.forces[i1] += force1
            self.forces[i3] += force3
            self.forces[i2] -= (force1 + force3)
        else:
            self.forces[i1] += force1
            self.forces[i3] += force3

    def compute_forces(self):
        """Compute the forces on each bead based on the force function."""

        # init
        self.forces = [complex(0, 0) for _ in self.positions]

        # bond forces (distance between beads)
        for i, j in self.connections:
            self._bond_force(i, j)

        # angle forces (angles between beads connected to a vertex)
        for triplet, ideal_angle in self.angled_triplets.items():
            self._angle_force(*triplet, ideal_angle)
        # for triplet, ideal_angle in self.triplets.items():
        #     print(triplet, ideal_angle)


        for triplet in self.stiff_triplets:
            self._stiff_force(*triplet)

        for i, j in combinations(range(len(self.positions)), 2):
            # TODO: this can be precomputed
            if any(i in triplet and j in triplet for triplet in self.stiff_triplets):
                continue
            if any(i in triplet and j in triplet for triplet in self.angled_triplets):
                continue
            if any(i in c and j in c for c in self.connections):
                continue
            self._repulsive_force(i, j)




    def step(self, dt):
        self.compute_forces()
        velocities = [f for f in self.forces]
        velocities = [v * FORCE_DAMPING for v in velocities]
        self.positions = [p + v * dt for p, v in zip(self.positions, velocities)]


    def __repr__(self):
        def _r(z):
            return f"{z.real:.2f} {'+' if z.imag >= 0 else '-'} {abs(z.imag):.2f}j"
        def _d(p):
            d = dict(enumerate(p))
            return ", ".join(f"{k}: {_r(v)}" for k, v in d.items())
        return f"BeadNetwork {_d(self.positions)}\n            {self.connections})"


# def plot_bead_network(network):
#     """Plot the bead positions and draw semi-transparent lines for connections."""
#     fig, ax = plt.subplots()
#
#     # Plot bead positions
#     x = [p.real for p in network.positions]
#     y = [p.imag for p in network.positions]
#     ax.scatter(x, y, color='blue', s=30)
#
#     # Draw lines for connections
#     for i, j in network.connections:
#         p1 = network.positions[i]
#         p2 = network.positions[j]
#         ax.plot([p1.real, p2.real], [p1.imag, p2.imag], color='red', alpha=0.3)
#
#     ax.set_aspect('equal')
#     plt.grid(True)
#     plt.title("Bead Network")
#     plt.show()


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

def plot_static_frame(network, show_indices=False):
    """Plot a single static frame of the bead network using plot_bead_frame()."""
    fig, ax = plt.subplots()
    plot_bead_frame(ax, network, show_indices=show_indices)
    plt.show()

def animate_simulation(network, steps=100, dt=0.1):
    fig, ax = plt.subplots()

    def update(frame):
        network.step(dt)
        network.step(dt)
        network.step(dt)
        network.step(dt)
        network.step(dt)
        plot_bead_frame(ax, network)

    ani = animation.FuncAnimation(fig, update, frames=steps, interval=50)
    plt.show()


if __name__ == "__main__":
    pass