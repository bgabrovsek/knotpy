"""Read and write PlanarGraph as an adjacency dictionary.
Format:
...
"""

__all__ = [
    "savetxt"
]

import networkx as nx
from knotpy.readwrite import clean_open_file, clean_close_file
from knotpy.convert import to_em_notation, guess_notation_str, to_pd_notation

_notation_converters = {
    "em": to_em_notation,
    "pd": to_pd_notation
}


def savetxt(g, path, notation="em", condensed=True, encoding="utf-8", decorator=None):
    """Writes either a graph or a list/set of graph to path in EM notation.
    :param g:
    :param path:
    :param notation:
    :param condensed: without spaces if True
    :param encoding:
    :param decorator:
    :return:
    """
    _debug = True
    notation = guess_notation_str(notation)

    f, actual_path = clean_open_file(path, mode="wb", decorator=decorator)

    try:

        graphs = g if (isinstance(g, list) or isinstance(g, set)) else [g]

        for counter, g in enumerate(graphs):  # using g is not nice
            conv_obj = _notation_converters[notation](g)

            line = str(conv_obj) + ("\n" if counter < len(graphs)-1 else "")
            if condensed:
                line = line.replace(" ", "")

            f.write(line.encode(encoding))

    except Exception as e:
        raise Exception(e)

    finally:
        clean_close_file(f)

    if _debug: print(f"wrote to {actual_path}.")

