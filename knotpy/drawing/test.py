import matplotlib.pyplot as plt
from matplotlib.patches import Circle


def plot_circles(coordinates, radii):
    fig, ax = plt.subplots()

    for coord, radius in zip(coordinates, radii):
        circle = Circle(coord, radius, fill=False)
        ax.add_patch(circle)

    ax.set_aspect('equal', adjustable='box')
    ax.autoscale()
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Plot of Circles')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    # Example usage:
    coordinates = [(1, 1), (3, 2), (-2, -2)]
    radii = [1, 1.5, 2]

    plot_circles(coordinates, radii)