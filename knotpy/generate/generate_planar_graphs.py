"""
Generate planar graphs tables up to n nodes.
"""
from itertools import chain
import knotpy as kp
from knotpy.utils import iterable_depth, combinations_with_limited_repetitions
from knotpy.generators import parallel_edge, empty_graph, vertex_graph
from knotpy.notation import to_em_notation
from copy import deepcopy
import os
from pathlib import Path
from knotpy.readwrite.cleanopen import prepend_to_extension




def _nodes_to_graphs(graphs, maximal_degree=None):
    """ add planar node to planar graphs in all possible ways, the result will be data union of all planar graphs with
    an added vertex
    :param graph:
    :param maximal_degree:
    :return:
    """
    _debug = False

    new_graphs = set()

    for g in graphs:
        if _debug: print("--- (new graph) ---")

        if _debug: print(g)
        for region in g.regions():  # choose the area to put the new vertex in
            # an area is data list of endpoints, an endpoint is data pair of (vertex, position of arc)
            avail_num_endpoints = [maximal_degree - g.degree(ep[0]) for ep in region]  # how many edges can we still attach?
            for endpoints in chain(
                    *(combinations_with_limited_repetitions(region, n, avail_num_endpoints)
                      for n in range(1, maximal_degree + 1))
            ):
                if _debug: print("--- (new point) --")
                if _debug: print("  To graph", to_em_notation(g))
                if _debug: print("  Adding endpoints", endpoints)
                if _debug: print("  To region", region)

                new_g = deepcopy(g)

                if _debug: print("  Starting graph", new_g)

                new_g.add_node_in_region(node_for_adding=new_g.number_of_nodes,
                                         region=region,
                                         connect_at_endpoints=endpoints)
                if _debug: print("  After adding node (EM)", to_em_notation(new_g))
                if _debug: print("  After adding node (ADJ)", new_g._adj)
                new_g.canonical()
                if _debug: print("  Canonical", new_g)
                new_graphs.add(new_g)

                num_reg = len(new_g.regions())
                """if new_g.number_of_nodes - new_g.number_of_arcs + num_reg != 2:
                    print("Error")
                    exit()
                else:
                    print(new_g, "ok")
                """
    return new_graphs



def generate_planar_graphs(maximal_number_of_nodes,
                           degree_sequences=None,
                           maximal_degree=None,
                           output_filename=None,
                           allow_parallel_arcs=False,
                           output_ignore_degree_sequences_filename=None,
                           start_with_planar_graphs=None,
                           notation="em",
                           run_in_parallel=True):
    """Generates planar grap
    :param maximal_number_of_nodes: maximal number of nodes that we wish to generate graph.
    :param degree_sequences: list of degree sequences of graphs. Can also be data dictionary, where keys are degrees and
    values are number of points with that degree.
    :param maximal_degree: maximal degree of the nodes (e.g. 4 for knots), if not given, max of degree sequence is used.
    :param output_filename:
    :param allow_parallel_arcs:
    :param output_ignore_degree_sequences_filename: if this parameter is provided, all graphs will be saved during the
     process of generation (not only the ones that have data matching degree sequence)
    :param start_with_planar_graphs: the algorithm will start generating graphs using this list of planar.
    This can be used to continue computations from one step where all graphs up to some degree have already
    been generated.
    :param notation:
    :param run_in_parallel:
    :return:
    """


    _debug = True
    deg_seqs = degree_sequences

    if maximal_number_of_nodes < 2:
        raise ValueError("Graph generation should have at least 2 nodes.")

    # force deg_seq, so it is data list of (degree-sorted) lists
    if deg_seqs is not None:
        if len(deg_seqs) == 0:
            raise ValueError("Cannot generate diagrams with empty degree information. Use None if you do not wish to \
                             specify the degree sequence.")
        if iterable_depth(deg_seqs) == 0:
            raise ValueError("The degree_sequence parameter should be (at least) data list or dictionary.")
        if iterable_depth(deg_seqs) == 1:
            deg_seqs = [deg_seqs]

        # if deg_seq is given as data dict, convert to sorted list
        deg_seqs = [sorted(deg for deg in sorted(seq) for _ in range(seq[deg]))
                    if isinstance(seq, dict)
                    else sorted(seq)
                    for seq in deg_seqs]
        #deg_seqs = [sorted([deg for deg in deg_seqs for _ in range(deg_seqs[deg])]) if isinstance(seq, dict) else sorted(seq)
        #           for seq in deg_seqs]

        print(deg_seqs)

    # force maximal_degree to have data value
        if maximal_degree is None:
            maximal_degree = max(max(seq) for seq in deg_seqs)

    if maximal_degree is None:
        raise ValueError("A maximal degree or degree sequence must be given.")

    # construct the starting graphs (provided or with two vertices)
    graphs = []
    if start_with_planar_graphs is None or len(start_with_planar_graphs) == 0:
        graphs = {parallel_edge(mult) for mult in range(1, maximal_degree + 1)}

    start_number_of_nodes = next(iter(graphs)).number_of_nodes
    if not all(g.number_of_nodes == start_number_of_nodes for g in graphs):
        raise ValueError("All starting planar graphs must have the same number of nodes.")


    # two vertices
    #kp.savetxt(sort_graphs(graphs), output_ignore_degree_sequences_filename, "em", decorator=2)

    # main loop, generate the graphs

    for number_of_nodes in range(start_number_of_nodes + 1, maximal_number_of_nodes + 1):

        print("Number of nodes:", number_of_nodes, end="... ", flush=True)
        graphs = _nodes_to_graphs(graphs, maximal_degree)

        if output_ignore_degree_sequences_filename is not None:
            kp.savetxt(
                sort_graphs(graphs),
                prepend_to_extension(output_ignore_degree_sequences_filename, number_of_nodes),
                "em"
            )

        if output_filename is not None:
            matching_graphs = [g for g in graphs if g.degree_sequence() in deg_seqs]
            if not allow_parallel_arcs:
                matching_graphs = [g for g in matching_graphs if not g.has_parallel_arcs()]
            #for g in graphs:
            #    print(g.degree_sequence(), g.degree_sequence() in deg_seqs)

            kp.savetxt(sort_graphs(matching_graphs),
                       prepend_to_extension(output_filename, number_of_nodes),
                       notation)


        #print(output_filename)
        #print(output_ignore_degree_sequences_filename)

    return graphs


    #add_node_in_region(self, region, node_for_adding, connect_at_endpoints=tuple(), **attr):

def sort_graphs(graphs):
    """Sort graphs in order, in turn by: number of arcs, degree sequence, graphs.
    :param graphs: iterable of graphs
    :return: list of sorted graphs
    """
    return sorted(graphs, key=lambda g: (g.number_of_nodes, g.number_of_arcs, g.degree_sequence(), g))


if __name__ == '__main__':

    data_dir = Path("/Users/bostjan/Dropbox/Code/knotpy/data")

    N = 6
    # degree sequences should graphs have that are worth exporting?
    degree_seqs = [
        {3: b, 4: n - b}
        for n in range(1, N+1) for b in range(0, n+1, 2)
    ]
    print(degree_seqs)



    # degree sequences_for

    graphs = generate_planar_graphs(
        maximal_number_of_nodes=N,
        degree_sequences=degree_seqs,
        maximal_degree=4,
        allow_parallel_arcs=False,
        output_filename=data_dir / "graphs.txt",
        output_ignore_degree_sequences_filename=data_dir / "all_graphs.txt",
        start_with_planar_graphs=None,
        notation="pc",
        run_in_parallel=True
    )

