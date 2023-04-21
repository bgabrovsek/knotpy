from graph import *
from knotted import *
from reidemeister_moves import *
from reidemeister_walk import *
from invariant_bucket import *

def primeQ(K):
    # CHECK IF KNOT HAS BONDS
    if not K.bondedQ():
        print("has no bonds.", end=" ")

    # CHECK IF CONNECTED SUM
    if K.connected_sumQ():
        print("is data connected sum.", end= " ")
        return False

    # CHECK IF SPLIT
    if len(simplify_and_split(K.copy())) > 1:
        print("is split.", end= " ")
        return False

    if len(K) == 0:
        print("is unknot/unlink", end=" ")
        return False

    if len(K.filter_nodes(XQ)) == 0:
        print("does not have crossings", end= " ")
        return False

    if K.bridgeQ():
        print("has data bridge arc", end = " ")
        return False

    if K.bridge_crossingQ():
        print("has data bridge crossing", end = " ")
        return False

    return True

def reduce_table_simple_1(input_filename, output_filename):
    # perform decreasing Reidemeister moves
    KNOTS = load_knots(input_filename)
    TABLE = BucketSet()

    for K in KNOTS:
        print()
        print("Knot", K.name, end=" ")
        if not primeQ(K): continue

        # CHECK IF CAN BE SIMPLIFIED
        K_copy = K.copy()

        decreasing_simplify(K_copy)

        K_copy.self_canonical_unoriented()

        if not primeQ(K_copy): continue

        table_len = len(TABLE)
        TABLE += K_copy
        if table_len == len(TABLE): print("already tabulated.", end= " ")

    for K in TABLE:
        print(K.name)

    print("Reduced table from", len(KNOTS), "knots to", len(TABLE), "knots.")
    TABLE = TABLE.sorted()
    export_knots(TABLE, output_filename)

def reduce_table_only_bonded_2(input_filename, output_filename):
    KNOTS = load_knots(input_filename)
    TABLE = BucketSet()
    for K in KNOTS:
        if not K.bondedQ(): continue
        TABLE += K
    print("Reduced table from", len(KNOTS), "knots to", len(TABLE), "knots.")
    TABLE = TABLE.sorted()
    export_knots(TABLE, output_filename)

def reduce_table_only_bonded_knots_3(input_filename, output_filename):
    KNOTS = load_knots(input_filename)
    TABLE = BucketSet()
    for K in KNOTS:
        knot_mirror = K.copy()
        knot_mirror.mirror()
        knot_mirror = knot_mirror.canonical_unoriented()

        knot = K if K < knot_mirror else knot_mirror
        closed_components, open_components = knot.split_components()
        if len(closed_components) > 1:
            continue
        TABLE += knot
    print("Reduced table from", len(KNOTS), "knots to", len(TABLE), "knots.")
    TABLE = TABLE.sorted()
    export_knots(TABLE, output_filename)


def split_to_buckets(input_filename):
    KNOTS = load_knots(input_filename)

    SPLIT_LIST = []
    for K in KNOTS:

        K0, K1 = K.copy(), K.copy()
        K1.mirror()

        if K1 < K0:
            K0, K1 = K1, K0

        inv0 = HSM(K0)
        inv1 = HSM(K1)

        unique = True

        for i0, i1, L0, L1 in SPLIT_LIST:
            if (i0 == inv0) and (i1 == inv1):
                unique = False
                print("Same.")
            elif (i0 == inv1) and (i1 == inv0):
                unique = False
                print("Opposite.")
            elif i0 == inv0:
                print("ERROR\n",L0, "\n", K0)
            elif i1 == inv1:
                print("ERROR\n",L1, "\n", K1)
            elif i0 == inv1:
                print("ERROR\n",L0, "\n", K1)
            elif i1 == inv0:
                print("ERROR\n",L1, "\n", K0)

            else:
                pass
                #print("*")

        if unique:
            SPLIT_LIST.append((inv0, inv1, K0, K1))







def classify(input_filename):
    KNOTS = load_knots(input_filename)
    BUCKET = InvariantBucket(lambda K: HSM(K, refined=True))
    DRAW_TABLE = []
    print("Putting into buckets.")
    for i, K in enumerate(KNOTS):
        #print(K)
        print("\r" + str(i), "/", len(KNOTS), end="")
        BUCKET.add(K)

    print(len(BUCKET.keys()),"keys", len(KNOTS), "knots")
    for index, H in enumerate(BUCKET.keys()):
        for knt in BUCKET[H]:
            knt.name = str(index)
            DRAW_TABLE.append(knt)
        print("Key", i, ":", str(H)[:10] + "...", "Values:", len(BUCKET[H]))
    PDF_export_knots(DRAW_TABLE, "pdf/00-classify-02.pdf")

    return BUCKET




if  __name__ == "__main__":

    #classify("data/00-knotknot-7-reduced-03.txt")
    split_to_buckets("data/00-knotknot-7-reduced-03.txt")



    #exit()

    # reduce_table_simple_1("data/00-knots-7-verts.txt", "data/00-knots-7-reduced-01.txt")
    # reduce_table_only_bonded_2("data/00-knots-7-reduced-01.txt", "data/00-knots-7-reduced-02.txt")
    # reduce_table_only_bonded_knots_3("data/00-knots-7-reduced-02.txt", "data/00-knotknot-7-reduced-03.txt")
