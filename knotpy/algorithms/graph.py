from knotpy.classes.planardiagram import PlanarDiagram
from collections import deque


def bfs_shortest_path(graph: PlanarDiagram, start, goal):
    # Queue for exploring nodes and tracking paths
    queue = deque([[start]])
    visited = set()

    while queue:
        # Get the current path and node
        path = queue.popleft()
        node = path[-1]

        # Check if the goal is reached
        if node == goal:
            return path  # This is the shortest path

        # If the node hasn't been visited yet, explore its neighbors
        if node not in visited:
            visited.add(node)
            for neighbor in graph.nodes[node]:
                new_path = list(path)
                new_path.append(neighbor.node)
                queue.append(new_path)

    return None  # Return None if no path exists between start and goal