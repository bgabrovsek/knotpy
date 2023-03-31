from graph import *
from timer import dot_counter
from drawknot import *

output_graph_filename = "data/graphs-[1]-verts.txt" # saves bonded graphs candidates
output_graph_filename_all= "data/graphs-[1]-verts-all.txt" # all graphs, even non-bonded ones

input_graph_filename = "data/graphs-5-verts.txt"
output_knot_filename = "data/knots-5-verts.txt"

PDF_fixed = "pdf/fixed-5-verts.pdf"

#output_graph_filename = "data/00-graphs-10-verts.txt"
#output_graph_filename_all = "data/00-graphs-all-10-verts.txt"

#input_graph_filename = "data/00-graphs-7-verts.txt"
#output_knot_filename = "data/00-knots-7-verts.txt"

#input_knot_filename = "data/00-knots-7-verts.txt"
#output_pdf_filename = "pdf/01-knots-7-verts-1000.pdf"


def generate_graphs(N):
    """
    Generates all graphs up to N vertices, saves to output_graph_filename
    :param N: number of vertices
    """
    out = arg_replace(output_graph_filename, N)
    out_all = arg_replace(output_graph_filename_all, N)
    safe_delete(out, out_all)
    GRAPHS = generate_planar_graphs(N,  out, out_all, run_in_parallel=False)
    #print(GRAPHS)


def generate_theta_curves_from_graphs():
    """
    Loads knot from file and generates all possible theta-curves and handcuff links
    """

    # load graphs
    GRAPHS = load_graphs(input_graph_filename)
    GRAPHS.sort(key=lambda K: K.name)
    print("Loaded graphs:", len(GRAPHS))

    # make graphs spatial
    SPATIAL = make_graphs_spatial(GRAPHS)
    print("Spatial graphs:", len(SPATIAL))


    normalize_bucket_names(SPATIAL)

    FIXED = BucketSet()
    for K in SPATIAL:

        K.fix_orientation()
        FIXED += K
    print("Fixed knots:", len(FIXED))

    FIXED = FIXED.sorted()

    CANONICAL = [l.canonical() for l in FIXED]
    print("Canonical:",len(CANONICAL))

   # UNORIENTED = [l.canonical_unoriented() for l in CANONICAL]
   # print("Unoriented canonical:",len(UNORIENTED))

    UNORIENTED=  CANONICAL

    # use bucket sets!!!!!!!!!!!!!!!!!!!!!!! multiples

    GOOD_UNORIENTED = [l for l in UNORIENTED if not l.bridgeQ() and not l.bridge_crossingQ()]
    #GOOD_UNORIENTED = UNORIENTED.filter(lambda l: (not l.bridgeQ() and not l.bridge_crossingQ()))
    print("Good unoriented canonical:",len(GOOD_UNORIENTED))

    print("Sorting knots")
    KNOTS = sorted(GOOD_UNORIENTED)
    print("Good unoriented canonical sorted:",len(GOOD_UNORIENTED))

    PDF_export_knots(KNOTS, PDF_fixed)


def generate_knots_from_graphs():
    """
    Loads knots from file and generates all possible knots.
    """

    # load graphs
    GRAPHS = load_graphs(input_graph_filename)
    print("Loaded graphs:", len(GRAPHS))

    # make graphs spatial
    SPATIAL = make_graphs_spatial(GRAPHS)
    print("Spatial graphs:", len(SPATIAL))




    BONDED = make_bonded_knots(SPATIAL)
    print("Bonded knots:", len(BONDED))

    FIXED = BucketSet()
    for K in BONDED:
        K.fix_orientation()
        FIXED += K
    print("Fixed knots:",len(FIXED))

    CANONICAL = FIXED.map(lambda l: l.canonical())
    print("Canonical:",len(CANONICAL))

    UNORIENTED = CANONICAL.map(lambda l: l.canonical_unoriented())
    print("Unoriented canonical:",len(UNORIENTED))

    GOOD_UNORIENTED = UNORIENTED.filter(lambda l: (not l.bridgeQ() and not l.bridge_crossingQ()))
    print("Good unoriented canonical:",len(GOOD_UNORIENTED))

    print("Sorting knots")
    KNOTS = GOOD_UNORIENTED.sorted()
    print("Good unoriented canonical sorted:",len(GOOD_UNORIENTED))

    export_knots(KNOTS, PDF_fixed, enum=True)
    #export_knots(KNOTS, "All knots", output_knot_filename)

def draw_all_knots():

    KNOTS = load_knots(input_knot_filename)[:1000]
    for name, K in enumerate(KNOTS):
        K.name = str(name)
    PDF_export_knots(KNOTS, output_pdf_filename)


if __name__ == "__main__":

    #generate_graphs(5)
    generate_theta_curves_from_graphs()
#    generate_knots_from_graphs()
#    draw_all_knots()