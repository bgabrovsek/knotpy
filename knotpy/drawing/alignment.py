from sklearn.decomposition import PCA
import math
from statistics import mean

from knotpy.utils.geometry import Circle, bounding_box, translate

def _principal_component_analysis(complex_points: list, angle=0.0):
    """
    https: // en.wikipedia.org / wiki / Principal_component_analysis

    :param complex_points: list of complex points
    : angle in radians
    :return:
    """
    # Convert complex numbers to a 2D array
    points_2d = [[z.real, z.imag] for z in complex_points]

    # Fit PCA model to the data
    pca = PCA(n_components=2)
    pca.fit(points_2d)

    # Extract the principal components and explained variance
    conjugated_principal_components = [complex(c[0], -c[1]) for c in pca.components_]
    conjugated_principal_components = [c / abs(c) for c in conjugated_principal_components]  # they should already be normalized
    # the 0th principal component should be the biggest

    conj_princ_comp = conjugated_principal_components[0] * complex(math.cos(angle), math.sin(angle))  # align along x and then rotate

    return [z * conj_princ_comp for z in complex_points]


def canonically_rotate_circles(circles:dict, degree=0):
    """Given a dictionary where values are circles, canonically rotate the system of circles so that they are aligned
    along an axis with 'degree' degrees. If degree = 0, the circles will be vertically aligned."""
    """
    :param circles: dictionary where values are circles
    :param PCA_degrees: https://en.wikipedia.org/wiki/Principal_component_analysis
    :return:
    """
    if any(not isinstance(value, Circle) for value in circles.values()):
        raise ValueError("Can only align along axis if all values are circles.")

    centers = [circle.center for circle in circles.values()]
    radii = [circle.radius for circle in circles.values()]
    mass_center = sum(c * r for c, r in zip(centers, radii)) / sum(radii)

    centers = [c - mass_center for c in centers]  # centering around (0, 0)
    centers = _principal_component_analysis(centers, math.radians(degree))  # align along the x axis

    # move so that more circles are to the right (diagram is more complex to the right)
    if sum(centers).real < 0:
        centers = [-z  for z in centers]

    # rotate centers
    return {key: Circle(center, radius) for key, center, radius in zip(circles, centers, radii)}


def align_layouts(layout_circles_pairs):

    mean_radius = mean(
        mean(circle.radius for circle in circles.values() if isinstance(circle, Circle))
        for layout, circles in layout_circles_pairs
    )

    bounding_boxes = [bounding_box(layout.values()) for layout, circles in layout_circles_pairs]

    gap = mean_radius * 2
    start_x = bounding_boxes[0][1].real + gap # start x position of the 0th component
    for (layout, circles), bb in zip(layout_circles_pairs[1:], bounding_boxes[1:]):
        # translate layout
        for key, val in layout.items():
            layout[key] = translate(val, start_x - bb[0].real)
        for key, val in circles.items():
            circles[key] = translate(val, start_x - bb[0].real)
        start_x += (bb[1].real-bb[0].real) + gap

