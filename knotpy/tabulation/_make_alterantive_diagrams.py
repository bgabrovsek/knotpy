from knotpy.reidemeister.space import smart_reidemeister_space
from knotpy.tabulation.knot_table import knot_table, select_knots
from knotpy.utils.multiprogressbar import Bar
from knotpy.readwrite.save import init_collection, append_to_collection

if __name__ == "__main__":

    # make alternative knot diagrams
    knots = select_knots(min_crossings=0, max_crossings=13)

    init_collection("precomputed/knot_diagram_alternatives.txt", multiple_diagrams_per_line=True)

    for k in Bar(knots.values()):
        srs = smart_reidemeister_space(k, 4)
        append_to_collection("precomputed/knot_diagram_alternatives.txt", srs)

