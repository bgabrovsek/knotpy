"""Read and write PlanarGraph as an adjacency dictionary.
Format:
...
"""

from datetime import datetime

from pathlib import Path
from glob import glob


#from knotpy.readwrite.cleanopen import clean_open_file, clean_close_file
#from knotpy import to_notation_dispatcher, from_notation_dispatcher

__all__ = ["save_txt"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'





def _save_txt_knot_format(k, path, notation="knot", ccw=True, attributes=True, delimiter=' ', comments='#',
                          encoding="utf-8"):
    """
    :param k: planardiagram object
    :param path:
    :param notation:
    :param ccw:
    :param attributes:
    :param delimiter:
    :param comments:
    :param encoding:
    :return:
    """
    with open(path, 'wt') as file:

        # time stamp
        file.write(f"{comments} {datetime.now().astimezone()} ({datetime.now().astimezone().tzinfo})")

        


def save_txt(k, path, notation="knot", ccw=True, attributes=True, delimiter=' ', comments='#', encoding="utf-8"):
    """
    :param k: planardiagram object
    :param path:
    :param notation:
    :param ccw:
    :param attributes:
    :param delimiter:
    :param comments:
    :param encoding:
    :return:
    """

    with open(path, "wt") as file:
        file.write()


#
#
# def savetxt_multiple_obsolete(graph, path, notation="em", ccw=True, separator=",", prepended_node_count=False, encoding="utf-8",
#                               comment=None, mode="wb"):
#     """
#     :param graph: one or more graphs as iterable
#     :param path:
#     :param notation:
#     :param ccw:
#     :param separator:
#     :param prepended_node_count:
#     :param encoding:
#     :param comment: will be prepended as first line, should contain, e.g. a "#"
#     :return:
#     """
#
#     _debug = False
#
#     graphs = graph if type(graph).__name__ in ("list", "set", "tuple", "dict") else [graph]
#     f = clean_open_file(path, mode=mode)
#
#     to_dispatched = to_notation_dispatcher(notation)
#     dispatcher_args = dict()
#     if not ccw and ccw is not None: dispatcher_args["ccw"] = False
#     if separator is not None: dispatcher_args["separator"] = separator
#     if prepended_node_count: dispatcher_args["prepended_node_count"] = True
#
#     if comment is not None:
#         f.write((str(comment) + "\n").encode(encoding))
#
#     for g in graphs:
#         line = to_dispatched(g, **dispatcher_args) + "\n"
#         f.write(line.encode(encoding))
#
#     clean_close_file(f)
#
#     if _debug: print(f"Wrote {len(graphs)} lines to {path}.")


def loadtxt_multiple(path, notation="em", ccw=True, comment="#", separator=",", prepended_node_count=False, max_rows=None,
                     encoding="utf-8"):
    """
    :param path: can also be a Unix style pathname pattern expansion, e.g. "knots-*.txt"
    :param notation:
    :param ccw:
    :param comment:
    :param separator:
    :param prepended_node_count:
    :param max_rows:
    :param encoding:
    :return:
    """

    _debug = False

    graphs = []

    filenames = sorted(glob(str(path))) #if "*" in str(path) or "?" in str(path) else [str(path)]


    for filename in filenames:

        f = clean_open_file(filename, mode="rb")

        count = 0
        for line in f:
            line = line.decode(encoding).strip()
            if _debug: print(line)

            if max_rows is not None and len(graphs) >= max_rows:
                break

            if line.find(comment) > -1:
                line = line[:line.find(comment)].strip()
            if len(line) == 0:
                continue

            from_dispatched = from_notation_dispatcher(notation)
            dispatcher_args = dict()
            if ccw is False: dispatcher_args["ccw"] = ccw
            if separator is not None: dispatcher_args["separator"] = separator
            if prepended_node_count: dispatcher_args["prepended_node_count"] = True

            graph = from_dispatched(line, **dispatcher_args)
            graphs.append(graph)
            count += 1

            if _debug:
                print(graphs[-1])

        clean_close_file(f)
        if _debug: print(f"Read {len(graphs)} lines from {path}.")
        #print(f"Read {count} lines from {filename}.")

    return graphs #if len(graphs) != 1 else graphs[0]



def loadtxt_iterator(path, notation="em", ccw=True, comment="#", separator=",", prepended_node_count=False, max_rows=None,
            encoding="utf-8"):
    """
    :param path: can also be a Unix style pathname pattern expansion, e.g. "knots-*.txt"
    :param notation:
    :param ccw:
    :param comment:
    :param separator:
    :param prepended_node_count:
    :param max_rows:
    :param encoding:
    :return:
    """

    _debug = False

    for filename in sorted(glob(str(path))):

        f = clean_open_file(filename, mode="rb")

        count = 0
        for line in f:
            line = line.decode(encoding).strip()
            if _debug: print(line)

            if max_rows is not None and len(graphs) >= max_rows:
                break

            if line.find(comment) > -1:
                line = line[:line.find(comment)].strip()
            if len(line) == 0:
                continue

            from_dispatched = from_notation_dispatcher(notation)
            dispatcher_args = dict()
            if ccw is False: dispatcher_args["ccw"] = ccw
            if separator is not None: dispatcher_args["separator"] = separator
            if prepended_node_count: dispatcher_args["prepended_node_count"] = True

            graph = from_dispatched(line, **dispatcher_args)

            yield graph
            count += 1

            if _debug:
                print(graphs[-1])

        clean_close_file(f)
        if _debug: print(f"Read {len(graphs)} lines from {path}.")
        print(f"Read {count} lines from {filename}.")

    return# graphs if len(graphs) != 1 else graphs[0]

def _test_text_write():
    from knotpy.classes.spatialgraph import SpatialGraph
    k = SpatialGraph(name="x1", color="red")
    k.add_crossings_from("ab", color="blue")
    k.add_vertices_from("uv")
    k.set_arc([("a",0),("b",0)], color="Orange")
    k.set_arc([("a",1),("b",2)], color="Orange")
    k.set_arc([("a",2),("b",1)], color="Orange")
    k.set_arc([("a", 3), ("v", 0)], color="Orange")
    k.set_arc([("b", 3), ("u", 0)], color="Orange")
    print(k)
    save_txt(k,"../data/test.knot")

if __name__ == '__main__':
    _test_text_write()

    #data_dir = Path("/sandbox/data")
    #graphs = loadtxt_multiple(data_dir / "plantri-7.txt", notation="pl", prepended_node_count=True, ccw=False)
    #savetxt_multiple_obsolete(graphs, data_dir / "test_plantri-7.txt", notation="pl", prepended_node_count=True, ccw=False)
