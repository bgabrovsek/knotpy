import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch

if __name__ == '__main__':
    fig, ax = plt.subplots()

    # Points in data coordinates
    point1 = (1, 2)
    point2 = (5, 8)

    # ConnectionPatch connecting the two points
    connection_patch = ConnectionPatch(point1, point2, 'data', 'data')
    ax.add_patch(connection_patch)

    ax.set_xlim(0, 6)
    ax.set_ylim(0, 10)

    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('ConnectionPatch with "data" coordinates')
    plt.grid(True)
    plt.show()
