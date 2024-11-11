"""
Simulation lower energy state, better looking knot
"""
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import pprint as pp

from knotpy.notation.native import from_knotpy_notation, from_pd_notation
from knotpy.notation.pd import to_pd_notation
from knotpy.drawing.draw_matplotlib import draw, draw_from_layout
from knotpy.utils.geometry import Circle

import knotpy as kp
from knotpy.drawing.layout import circlepack_layout

#__all__ = ['draw', 'export_pdf', "circlepack_layout", "draw_from_layout", "add_support_arcs", "plt", "export_png"]
__version__ = 'god knows'


"""
Simple Trefoil:
PD notation: X[4,2,5,1],X[2,6,3,5],X[6,4,1,3]

from_pd_notation -> PlanarDiagram object:
PlanarDiagram with 3 nodes, 6 arcs, and adjacencies a → X(c1 b0 b3 c2), b → X(a1 c0 c3 a2), c → X(b1 a0 a3 b2) with framing 0

circlepack_layout:
{frozenset({b0, a1}): <knotpy.utils.geometry.Circle object at 0x000002B19BBB5CD0>,
 frozenset({c1, a0}): <knotpy.utils.geometry.Circle object at 0x000002B19B40BCB0>,
 frozenset({c0, b1}): <knotpy.utils.geometry.Circle object at 0x000002B19CC01AC0>,
 frozenset({a2, b3}): <knotpy.utils.geometry.Circle object at 0x000002B19CC560F0>,
 frozenset({a3, c2}): <knotpy.utils.geometry.Circle object at 0x000002B19CC56120>,
 frozenset({c3, b2}): <knotpy.utils.geometry.Circle object at 0x000002B19CC56150>,
 'a': <knotpy.utils.geometry.Circle object at 0x000002B19B3587D0>,
 'b': <knotpy.utils.geometry.Circle object at 0x000002B19AC882F0>,
 'c': <knotpy.utils.geometry.Circle object at 0x000002B19B3585F0>,
 (b0, a2): <knotpy.utils.geometry.Circle object at 0x000002B19CC2D340>,
 (b2, c0): <knotpy.utils.geometry.Circle object at 0x000002B19CC561B0>,
 (c2, a0): <knotpy.utils.geometry.Circle object at 0x000002B19CC56180>,
 (c3, a3, b3): <knotpy.utils.geometry.Circle object at 0x000002B19CC2D520>}

Simulation here:


draw_from_layout(circlepack_layout):
image
"""

# Simulation functions ________________________________________________________

def extract_circle_positions(circle_dict):
    """Extract circle centers from the dictionary of circles."""
    positions = {}
    for key, circle in circle_dict.items():
        positions[key] = circle.center  # Each circle has a .center attribute
    return positions

def extract_main_points_and_connections(ret):
    return {k: v for k, v in ret.items() if isinstance(k, (str, frozenset))}


class SimCircle(Circle):
    def __init__(self, center, radius):
        super().__init__(center, radius)
        self.force = 0+0j      # Initialize force as a complex number
        self.velocity = 0+0j   # Initialize velocity as a complex number
        self.mass = 1.0        # Assume unit mass for simplicity
        self.positions_ot = []
        self.radius_ot = []

def prep_sim(ret): 
    circlepack_layout_sim = {}
    for key, circle in ret.items():
        #print(f"Key: {key}, Center: {circle.center}, Radius: {circle.radius}")
        c = circle.center
        r = circle.radius
        sim_circle = SimCircle(c, r)
        circlepack_layout_sim[key] = sim_circle
    
    return circlepack_layout_sim


# Function to compute repulsive forces
def compute_repulsive_forces(circles, koeff):
    for _, ci in circles.items():
        ci.force = 0+0j  # Reset force
        for _, cj in circles.items():
            if ci != cj:
                delta = ci.center - cj.center
                distance = abs(delta) + 1e-6  # Avoid division by zero
                force_magnitude = koeff**2 / distance
                force_direction = delta / distance
                ci.force += force_magnitude * force_direction


def limit_displacement(delta, temperature):
    delta_magnitude = abs(delta)
    if delta_magnitude > temperature:
        return delta / delta_magnitude * temperature
    else:
        return delta


def make_step(circles, koeff, dt, iteration, temperature):

    compute_repulsive_forces(circles, koeff)

    # Update positions
    for key, circle in circles.items():
        displacement = circle.force * dt
        displacement = limit_displacement(displacement, temperature)
        circle.center += displacement

        # Store positions for plotting every 10 iterations
        if iteration % 10 == 0:
            circle.positions_ot.append(circle.center)
            circle.radius_ot.append(circle.radius)

    # Cool down the system
    temperature *= 0.95  # Decrease temperature over time

def run_sim(ret):
    """
    Run the simulation given a dictionary of circlepack layout ret.

    Parameters
    ----------
    ret : dict
        A dictionary of circlepack layout, where the keys are the node labels and
        the values are the Circle objects.

    Returns
    -------
    circles : dict
        A dictionary of Circle objects, where the keys are the node labels and
        the values are the Circle objects.

    Notes
    -----
    The simulation parameters are set as follows:
        - n: the number of circles
        - area: assumed unit area for simplicity
        - koeff: the repulsion constant, set to sqrt(area/n)
        - dt: the time step, set to 0.1
        - max_iterations: the maximum number of iterations, set to 50
        - temperature: the initial temperature to limit displacement, set to 0.1
    """
    circles = prep_sim(ret)

    # Simulation parameters
    n = len(circles)  # Number of circles
    area = 1.0        # Assume unit area for simplicity
    koeff = np.sqrt(area / n)
    dt = 0.1          # Time step
    max_iterations = 50
    temperature = 0.1  # Initial temperature to limit displacement

    # Simulation loop
    for iteration in range(max_iterations):
        make_step(circles, koeff, dt, iteration, temperature) 
        
    return circles

# Visualization function
def plot_circles(circles_data, iteration):
    
    fig, ax = plt.subplots(figsize=(6,6))

    for key, circle_obj in circles_data.items():
        center = circle_obj.center
        radius = circle_obj.radius
        circle = plt.Circle((center.real, center.imag), radius, fill=False, edgecolor='blue')
        ax.add_artist(circle)
        # Plot the center
        ax.plot(center.real, center.imag, 'ro', markersize=2)
        ax.text(center.real, center.imag, key, fontsize=8)
    
    ax.set_aspect('equal', 'box')
    ax.set_title(f'Iteration {iteration}')

    # Adjust plot limits
    all_centers = np.array([circle.center for _, circle in circles_data.items()])
    min_x, max_x = np.min(all_centers.real), np.max(all_centers.real)
    min_y, max_y = np.min(all_centers.imag), np.max(all_centers.imag)
    padding = 1.0
    plt.xlim(min_x - padding, max_x + padding)
    plt.ylim(min_y - padding, max_y + padding)
    plt.grid(True)

    plt.show()

# End of SIM functions ________________________________________________________

# Using matplotlib.path and matplotlib.patches ______________________________________________
def extract_points(points_dict, keys):
    """Extracts x and y coordinates from the points dictionary based on the provided keys."""
    points = [points_dict[key] for key in keys]
    x = [p.real for p in points]
    y = [p.imag for p in points]
    return x, y

import matplotlib.patches as patches
from matplotlib.path import Path

def bezier_curve_matplotlib(points_dict, keys):
    """Generates a Bézier curve using matplotlib's Path."""
    points = [points_dict[key] for key in keys]
    verts = [(p.real, p.imag) for p in points]
    if len(verts) == 4:
        codes = [Path.MOVETO,
                 Path.CURVE4,
                 Path.CURVE4,
                 Path.CURVE4]
    elif len(verts) == 3:
        codes = [Path.MOVETO,
                 Path.CURVE3,
                 Path.CURVE3]
    else:
        raise ValueError("Matplotlib's Path supports quadratic (3 points) and cubic (4 points) Bézier curves.")
    path = Path(verts, codes)
    return path

def plot_bezier_curve_matplotlib(path, x_points, y_points, title="Bézier Curve"):
    """Plots the Bézier curve using matplotlib's PathPatch."""
    fig, ax = plt.subplots()
    patch = patches.PathPatch(path, facecolor='none', lw=2, edgecolor='blue')
    ax.add_patch(patch)
    ax.plot(x_points, y_points, 'ro--', label='Control Points')
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    ax.axis('equal')
    plt.show()

from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import pprint

pp = pprint.PrettyPrinter(indent=4)

def build_graph(ret):
    graph = defaultdict(list)
    circles = {}
    identifiers = set()

    for key, circle in ret.items():
        if isinstance(key, frozenset):
            id_from, id_to = key
            node_from = str(id_from)[0]
            node_to = str(id_to)[0]
            # Store both directions in the graph
            graph[node_from].append((node_to, key))  # Edge from node_from to node_to
            graph[node_to].append((node_from, key))  # Edge from node_to to node_from
            # Map the connection to its circle
            circles[key] = circle
            identifiers.update([id_from, id_to])
        elif isinstance(key, str):
            # Key is a node
            node = str(key)
            circles[node] = circle
            identifiers.add(node)

    print(f"\nGraph")
    pp.pprint(graph)

    return graph, circles, identifiers

def extract_unique_connections(graph):
    """
    Extracts unique connections from a graph represented as an adjacency list.
    
    Parameters:
        graph (dict): Adjacency list, where each key is a node and its value is a list of tuples, each containing the neighbor node and a set of control points.
    
    Returns:
        list: List of unique connections, where each connection is a list of three elements: the node the connection starts at, the set of control points, and the node the connection ends at.
    """
    unique_connections = set()
    connections_list = []

    for node_from, edges in graph.items():
        for node_to, control_points in edges:
            # Create a sorted tuple to avoid duplicates
            connection = tuple(sorted([node_from, node_to]) + [control_points])
            if connection not in unique_connections:
                unique_connections.add(connection)
                connections_list.append([node_from, control_points, node_to])
    return connections_list

def get_positions(circles, elements):
    """Retrieve positions from circles dictionary for the given elements."""
    positions = []
    for elem in elements:
        positions.append(circles[elem])
    return positions

def bezier_curve_matplotlib_multiple(connections, circles):
    """Plots multiple Bezier curves on the same plot."""
    fig, ax = plt.subplots(figsize=(6, 6))
    
    for connection in connections:
        start_node, control_points_set, end_node = connection
        # Get positions
        start_pos = circles[start_node]
        end_pos = circles[end_node]
        control_points = list(control_points_set)
        # Sort control points if necessary
        control_points.sort()  # Implement a better sorting if needed
        #control_positions = [circles[cp] for cp in control_points]
        control_positions = circles[control_points_set]     # lets hope
        
        # Build vertices and codes for the Bezier curve
        verts = [(start_pos.real, start_pos.imag)]
        codes = [Path.MOVETO]
        """
        if len(control_positions) == 1:
            # Quadratic Bezier Curve
            verts.extend([(control_positions[0].real, control_positions[0].imag),
                          (end_pos.real, end_pos.imag)])
            codes.extend([Path.CURVE3, Path.CURVE3])
        elif len(control_positions) == 2:
            # Cubic Bezier Curve
            verts.extend([(control_positions[0].real, control_positions[0].imag),
                          (control_positions[1].real, control_positions[1].imag),
                          (end_pos.real, end_pos.imag)])
            codes.extend([Path.CURVE4, Path.CURVE4, Path.CURVE4])
        else:
            # Handle higher-order Bezier curves if necessary
            print(f"Unsupported number of control points: {len(control_positions)}")
            continue  # Skip this curve
        """
        # Quadratic Bezier Curve
        verts.extend([(control_positions.real, control_positions.imag),
                        (end_pos.real, end_pos.imag)])
        codes.extend([Path.CURVE3, Path.CURVE3])

        
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor='none', lw=2, edgecolor='blue')
        ax.add_patch(patch)
        # Plot control points and lines
        all_points = [start_pos] + [control_positions] + [end_pos]
        x_points = [p.real for p in all_points]
        y_points = [p.imag for p in all_points]
        #ax.plot(x_points, y_points, 'ro--', markersize=4)

    ax.set_title("Bezier Curves for Graph Connections")
    ax.grid(True)
    ax.axis('equal')
    plt.show()

# End of Bezier functions _____________________________________________________

# Start of Sequencing Spline __________________________________________________

def traverse_knot(graph, start_node):
    visited_edges = set()
    sequence = []

    def dfs(node):
        sequence.append(node)
        for neighbor, conn_key in graph[node]:
            edge = frozenset({node, neighbor, conn_key})
            if edge not in visited_edges:
                visited_edges.add(edge)
                sequence.append(conn_key)  # Add the connection
                dfs(neighbor)
                # Optional: sequence.append(node)  # If you want to record returning to the node

    dfs(start_node)
    print(sequence)
    return sequence



def build_circles_data(sequence, circles):
    circles_data = []
    for key in sequence:
        circle = circles.get(key)
        if circle:
            center = circle.center
            radius = circle.radius
            circles_data.append((center, radius))
        else:
            print(f"Warning: Circle not found for key {key}")
    return circles_data

def plot_spline(circles_data):
    from scipy.interpolate import make_interp_spline
    import numpy as np
    import matplotlib.pyplot as plt

    # Extract centers from circles_data
    centers = [center for center, _ in circles_data]
    x_points = np.array([center.real for center in centers])
    y_points = np.array([center.imag for center in centers])

    # Compute cumulative distance
    distances = np.sqrt(np.diff(x_points)**2 + np.diff(y_points)**2)
    cumulative_distances = np.insert(np.cumsum(distances), 0, 0)

    # Use cumulative distances as the parameter t
    t = cumulative_distances

    # Generate new t values for smooth interpolation
    t_new = np.linspace(t[0], t[-1], 300)

    # Determine the spline degree
    num_points = len(centers)
    if num_points < 2:
        print("Need at least two points to plot a spline.")
        return
    elif num_points < 4:
        k = num_points - 1
    else:
        k = 3  # Cubic spline

    # Create splines for x and y coordinates
    x_spline = make_interp_spline(t, x_points, k=k)
    y_spline = make_interp_spline(t, y_points, k=k)

    # Evaluate the splines to get smooth x and y values
    x_smooth = x_spline(t_new)
    y_smooth = y_spline(t_new)

    # Plotting
    fig, ax = plt.subplots()

    # Plot the spline
    ax.plot(x_smooth, y_smooth, 'r-', linewidth=2, label='Spline')

    # Plot the circles and their centers
    for center, radius in circles_data:
        circle = plt.Circle((center.real, center.imag), radius, fill=False, edgecolor='blue')
        ax.add_artist(circle)
        # Plot the center
        ax.plot(center.real, center.imag, 'ro', markersize=5)

    ax.set_aspect('equal', 'box')
    # Adjust plot limits
    all_centers = np.array(centers)
    min_x, max_x = np.min(all_centers.real), np.max(all_centers.real)
    min_y, max_y = np.min(all_centers.imag), np.max(all_centers.imag)
    padding = 1.0
    plt.xlim(min_x - padding, max_x + padding)
    plt.ylim(min_y - padding, max_y + padding)
    plt.grid(True)
    plt.title('Spline Through Knot Diagram Points')
    plt.legend()
    plt.show()

# End of Sequencing Spline ____________________________________________________

"""
Splines would work wonderfully, especially the Hobby algorithm that I discovered
 later on, if only I could get a proper sequence of points in order
There are multiple ways to continue down the knot and I need to know how to 
 traverse it correctly, this information is baked into the PlanarDiagram 
 from what I've noticed, but I lack the understanding of PlanarDiagram 
 encoding to understand how to extract it
Without proper sequencing the splines or the Bezier plots do not work well
Also problems with sequencing through the knot arise when the node has 3 connections

I will be attempting a different approach to the simulation making it possible
 to utilise pre-existing plotting functions, namely --> draw_from_layout()

The main constriction is the requirement for tangential circles, which creates
 issues with any kind of disturbance of the tight CirclePacking algorithm
 as the proper connections get lost.
I have also attempted to adjust radiuses after the simulation for a sequence of
 just a few points, but the draw_from_layout() function demands entire dictionary
 of all points to be plotted

My next idea is making the simple sim but adding a few more points, namely
 for each connection two circles are touching, I would place a point at the 
 intersection of these two circles as additional points,
 run through the dispersion simulation making the points separate
Then we look at the points where the intersections of circles used to be,
 we calculate where the circles center should be by calculating the difference
 from ep0, ep1, ep2, ... to the circle center, and adjust position of center
 until distance to all points on edge is equal making that the new radius
Repeat this for each node and arc circle center and wed get a new radiuses and
 proper positions of circles that should still be touching the right circles
 (yes edge cases will be problematic, this is not finding a minimum in energy
 this is cutting off a simulation at just the right time so as not to lose.)
"""

if __name__ == "__main__":
    # Trefoil:
    #s = "X[4,2,5,1],X[2,6,3,5],X[6,4,1,3]"
    # Large:
    s = "X[1,9,2,8],X[3,10,4,11],X[5,3,6,2],X[7,1,8,12],X[9,4,10,5],X[11,7,12,6]"
    s = "V[0,1,2], V[0,2,1]"
    s = "V[1,2,0], V[1,3,4], X[5,6,3,0], X[7,5,2,8], X[6,7,8,4]"
    # Problematic:
    #s = "X[0,1,2,3],X[4,5,6,7],X[1,8,9,10],X[11,12,13,9],X[14,15,7,16],X[17,18,19,13],X[10,20,17,12],X[20,19,15,14],V[3,21,22],V[5,23,24],V[6,24,16],V[4,18,23],V[0,22,8],V[2,11,21]"
    k2 = from_pd_notation(s)
    print(k2)

    ret = circlepack_layout(k2)

    print("\n")

    filtered_ret = extract_main_points_and_connections(ret)
    filtered_ret = ret
    #ret1 = run_sim(filtered_ret)
    ret1 = {key: ret[key].center for key in ret}
    pp.pprint(ret1)

    # Build graph
    graph, circles, identifiers = build_graph(ret1)

    # Extract unique connections
    connections = extract_unique_connections(graph)

    # Plot Bezier curves
    draw_from_layout(k2, ret, with_labels=True, with_title=True)
    bezier_curve_matplotlib_multiple(connections, circles)

    plot_circles(prep_sim(filtered_ret), 0)
    print("\nSimulation")
    ret1 = run_sim(filtered_ret)
    plot_circles(prep_sim(ret1), 50)
    ret2 = {key: ret1[key].center for key in ret1}
    pp.pprint(ret2)

    # Build graph
    graph, circles, identifiers = build_graph(ret2)

    # Extract unique connections
    connections = extract_unique_connections(graph)

    # Plot Bezier curves
    bezier_curve_matplotlib_multiple(connections, circles)

    # Plot Spline curves
    # Determine the sequence (adjust 'start_node' and traversal as needed)
    start_node = 'a'  # Adjust as appropriate
    sequence = traverse_knot(graph, start_node)

    # Build the ordered circles_data
    circles_data = build_circles_data(sequence, ret1)

    # Plot the spline
    plot_spline(circles_data)

