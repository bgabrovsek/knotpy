__all__ = ["path_from_endpoint", "bfs_shortest_path"]

__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from collections import deque

from knotpy.classes.node import Crossing
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram


# TODO: write tests



def path_from_endpoint(k: PlanarDiagram, endpoint: Endpoint) -> list:
    """
    Return the path (sequence of endpoints) starting from the given endpoint in a planar diagram.

    The path continues until it reaches a vertex node or forms a closed component. It follows connections
    through twin endpoints, treating crossings appropriately. If the diagram is oriented, the path should follow
    the orientation (this is currently not implemented).

    Args:
        k (PlanarDiagram): The planar diagram in which the path is traced.
        endpoint (Endpoint): The starting endpoint of the path.

    Returns:
        list: A list of endpoints that form the continuous path until it reaches a vertex-like node or loops back.

    Raises:
        TypeError: If the input endpoint is not an instance of Endpoint.
    """

    # TODO: in oriented diagrams

    # if not k.is_oriented():
    #     raise NotImplementedError("Path from endpoint is not implemented for unoriented diagrams")

    if not isinstance(endpoint, Endpoint):
        raise TypeError(f"Endpoint {endpoint} should be of type Endpoint")

    path = []
    ep = endpoint

    while True:
        path.append(ep)
        path.append(twin_ep := k.twin(ep))  # jump to twin
        if isinstance(k.nodes[twin_ep.node], Crossing):
            ep = k.endpoint_from_pair((twin_ep.node, (twin_ep.position + 2) % 4))
        else:
            break

        if ep is endpoint:
            break

    return path


def bfs_shortest_path(graph: PlanarDiagram, start, goal):
    """
    Find the shortest path in a graph using the Breadth-First Search (BFS) algorithm.

    This function explores paths in a graph layer by layer starting from the `start` node to
    find the shortest possible path to the `goal` node. The function returns the shortest
    path if one exists. If no path exists between `start` and `goal`, the function returns None.

    Args:
        graph (PlanarDiagram): The graph structure to search, where nodes and connections are
            defined as per the PlanarDiagram class or equivalent structure.
        start: The starting node for the search.
        goal: The target node to find the shortest path to.

    Returns:
        list: A list representing the nodes in the shortest path from `start` to `goal`,
            including both endpoints. If no path exists, returns None.
    """
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


