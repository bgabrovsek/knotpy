from multiprocessing import cpu_count, Pool
from math import ceil
from planar_graph import *
from reidemeister_moves import *
from timer import *
import gc
gc.collect()

#output_graph_filename = "data/" + platform.system().lower() + "-results.txt"
#input_graph_filename = "data/linux-results.txt"
#output_knot_filename = "data/" + platform.system().lower() + "-knots.txt"

CPU_COUNT = cpu_count() #(3*cpu_count())//4  # detect system properties
POOL_SIZE = CPU_COUNT


def add_planar_vertex_graphs(GRAPHS, print_progress = False):
    """
    Adds planar vertex to all graphs in all possible ways
    :param GRAPHS: list of graphs
    :return: list (BucketSet) of graphs
    """

    NEW_GRAPHS = BucketSet()
    count, prev_perc = 0, None
    for g in GRAPHS:

        if print_progress:
            percent = int(1000*count / len(GRAPHS))/10
            if prev_perc != percent:

                print("\r"+str(percent)+"%", end="", flush=True)
                prev_perc = percent

            count += 1
        #print("Graph", g)
        for area in g.CCW_areas():  # choose the area to put the new vertex in
            #print("  Area", area)
            #good_dots = [(area_index, 1 if len(g[index]) == 3 else 2)  for area_index, (index, pos) in enumerate(area) if len(g[index]) < 4]
            good_dots = [(area_index, 4 - len(g[index])) for area_index, (index, pos) in enumerate(area) if len(g[index]) < 4]
            #print(" Good", good_dots)

            for dot_list in chain( # list of all possible combinations of crossings to insert the new arc connected to new vertex
                    double_combinations_with_repetition(good_dots, 1),
                    double_combinations_with_repetition(good_dots, 2),
                    double_combinations_with_repetition(good_dots, 3),
                    double_combinations_with_repetition(good_dots, 4)):

                #print("  DotL", dot_list)
                new_g = deepcopy(g)
                new_arc = max(g.arcs()) + 1
                new_vertex_deg = sum(m for x, m in dot_list)
                new_vertex = CircularList(new_arc + i for i in range(new_vertex_deg))
                #print("    New vertex", new_vertex)

                for dli, (iindex, m) in enumerate(dot_list):
                    # insert arc at (c,p) with multiplicity m (which can be 1 or 2)
                    index, pos = area[iindex]
                    #print("      Adding", new_arc, "at pos", pos, "to", new_g)
                    # of there are any arcs to the same crossing before, but on the opposite side, increase index position
                    inc_pos = 0
                    for (iindex_aux, m_aux) in dot_list[:dli]:
                        index_aux, pos_aux = area[iindex_aux]
                        if (index_aux == index) and (pos_aux < pos): inc_pos += 1

                    # insert m arcs into node
                    for i in range(m):
                        new_g[index].insert(pos+1+inc_pos, new_arc+i)
                    new_arc += m

                if max(new_g.degree()) > 4: continue # only consider graphs with <= 4 vertices
                new_g.nodes.append(new_vertex)
                #print("    Canonical", new_g.canonical())
                #if all(len(node) == 4 for node in new_g.nodes):
                #        print("      Result", new_g)
                new_g_canonical = new_g.canonical()


                NEW_GRAPHS += new_g_canonical  # add new knot to list

    if print_progress:
        print("\r", end="")
    return NEW_GRAPHS


def generate_planar_graphs(N, filename = None, filename_all = None,  run_in_parallel = True):
    """
    Generate all loopless connected planar graphs planar graphs up to 4 edges per vertex
    :param N: number of vertices
    :param filename: save graphs, if not given, returns the graphs
    :param run_in_parallel:
    :return:
    """

    global CPU_COUNT, POOL_SIZE
    TASKS_PER_PROCESS = 510




    ALL_GRAPHS = BucketSet() # store here all graphs with number of vertices 2,...,N

    if N < 2: raise ValueError("Number of vertices should be two or higher")
    print("Generating planar graphs "+("in non-parallel","in parallel")[run_in_parallel]+ " up to",N,"vertices, using", CPU_COUNT, "CPUs with pool size of " + str(POOL_SIZE)+".")

    # generate graphs with two vertices
    GRAPHS = BucketSet([
        PlanarGraph(((0,),(0,)), name=-2),
        PlanarGraph(((0,1),(1,0)), name=-1),
        PlanarGraph(((0,1,2),(2,1,0)), name=0),
        PlanarGraph(((0,1,2,3),(3,2,1,0)),name=1)])

    graph_name = 2  # giving graphs names

    ALL_GRAPHS +=  GRAPHS.filter(lambda l: l.bondedQ())  # filter only to bonded graphs

    if filename_all:
        export_graphs(GRAPHS, "All graphs with 2 vertices", filename_all)
    if filename:
        export_graphs(GRAPHS.filter(lambda l: l.bondedQ()), "Graphs with 2 vertices", filename)

    for n in range(3, N+1):

        NEW_GRAPHS = BucketSet()

        if run_in_parallel:
            # PARALLEL, split to chunks, since we do not want the pool size to be too large
            count = 0
            count_all = int(ceil(len(GRAPHS)/(POOL_SIZE*TASKS_PER_PROCESS)))

            for GRAPH_CHUNK in GRAPHS.chunks(POOL_SIZE*TASKS_PER_PROCESS):
                print("Chunk",count,"of",count_all)
                count += 1
                pool = Pool(CPU_COUNT)
                GRAPH_LIST = pool.map(add_planar_vertex_graphs, n_chunks(GRAPH_CHUNK, CPU_COUNT))
                NEW_GRAPHS += GRAPH_LIST
                pool.close()
                pool = None # remove pool
                gc.collect()

        else:
            # NON-PARALLEL
            NEW_GRAPHS += add_planar_vertex_graphs(GRAPHS, print_progress=True) #union of sets


        NEW_BONDED = NEW_GRAPHS.filter(lambda l: l.bondedQ()) # filter only to bonded graphs

        normalize_bucket_names(NEW_BONDED, graph_name)
        graph_name += len(NEW_BONDED)

        if filename_all:
            export_graphs(NEW_GRAPHS, "All graphs with "+str(n)+ " vertices", filename_all)
        if filename:
            export_graphs(NEW_BONDED, "Graphs with "+str(n)+ " vertices", filename)

        GRAPHS = NEW_GRAPHS
        ALL_GRAPHS += NEW_BONDED

    return ALL_GRAPHS


def export_graphs(GRAPHS, title, filename):
    print("[EXPORT]", title, "to file", filename, "(count = " + str(len(GRAPHS)) + ")")
    file = open(filename, 'data')
    if title:
        file.write("*** " + title+ " ***" + " (count = " + str(len(GRAPHS)) + ")\n")
    for g in GRAPHS:
        file.write(str(g) + "\n")
    file.close()


def load_graphs(filename, max_loaded_graphs = None):
    """ loads graphs from file given"""
    graphs = []
    #ticker = dot_counter___()
    count = 0
    with open(filename) as f:
        for line in f:
            if "PlanarGraph" in line:
                g = eval(line);
                graphs.append(g)
                #ticker.tick()
                count += 1
                if max_loaded_graphs is not None and count >= max_loaded_graphs:
                    break
    #ticker.end()
    #print("Loaded", len(graphs),"graphs.");
    return graphs


def make_graphs_spatial(GRAPHS):
    """
    Generates spatial graphs by placing under/over crossings to graphs
    :param GRAPHS: list of graphs
    :return: list of spatial graphs (knotted graphs)
    """

    SPATIAL = BucketSet()
    ticker = dot_counter(100)

    print(GRAPHS[:4])
    print()

    for g in GRAPHS: # loop through graphs
        ticker.tick()
        # convert graph g to knot
        four_valent_node_index = [i for i, v in enumerate(g.nodes) if len(v) == 4]  # list of 4-valent crossing indices
        for under_b_list in product((False, True), repeat=len(four_valent_node_index)):
            K = g.to_knot(under_b_list)
            SPATIAL += K
    ticker.end()
    return SPATIAL


def make_bonded_knots(SPATIAL):
    """ convert data list of spatial_graphs to bonded knots, by selecting each possible path as data bond (i.e. color it)"""
    BONDED = BucketSet() # store final knots
    ticker = dot_counter(1000, 100, print_stats=True, unit="")

    for K in SPATIAL:
        ticker.tick()
        diagrams = [K] # begin with only the knot in the list

        while diagrams:
            d = diagrams.pop() # get data diagram from the list
            trivalent_nodes = [node for node in d.filter_nodes(TRIVALENTQ) if not node.color]
            if not trivalent_nodes: # if no trivalent bonds, it's done!
                d.fix_orientation()
                BONDED += d
                continue

            start_node = trivalent_nodes.pop() # select data trivalent node
            for start_pos in (0,1,2): # select start position
                dgrm = d.copy()
                node = dgrm.nodes[d.nodes.index(start_node)]
                node.color = ((1,0,0),(0,1,0),(0,0,1))[start_pos] # set bond color

                # walk along the arc, until we hit another 3-valent vertex, then color it
                pos = start_pos
                while True:
                    node, pos = dgrm.d(node, pos) # get other endpoint
                    if TETRAVALENTQ(node):
                        pos = node.move_forward(pos)

                    if TRIVALENTQ(node):
                        if not node.color:  # node not already colored
                            node.color = ((1,0,0),(0,1,0),(0,0,1))[pos]
                            diagrams.append(dgrm)
                        break
    ticker.end()
    return BONDED

def unoriented_canonical(KNOTS):
    RESULT = BucketSet()
    for k in KNOTS:
        RESULT += k.canonical()
    return RESULT



if  __name__ == "__main__":

    pass
    """
    [EXPORT] All graphs #2 (count = 4)
    [EXPORT] Graphs #2 (count = 2)
    Chunk 0 of 1
    [EXPORT] All graphs #3 (count = 9)
    [EXPORT] Graphs #3 (count = 2)
    Chunk 0 of 1
    [EXPORT] All graphs #4 (count = 48)
    [EXPORT] Graphs #4 (count = 2)
    Chunk 0 of 1
    [EXPORT] All graphs #5 (count = 285)
    [EXPORT] Graphs #5 (count = 9)
    Chunk 0 of 1
    [EXPORT] All graphs #6 (count = 2366)
    [EXPORT] Graphs #6 (count = 31)
    
    
    Deleting file.
    Generating planar graphs in parallel up to 12 vertices, using 12 CPUs with pool size of 12.
    [EXPORT] All graphs #2 (count = 4)
    [EXPORT] Graphs #2 (count = 2)
    Chunk 0 of 1
    [EXPORT] All graphs #3 (count = 9)
    [EXPORT] Graphs #3 (count = 2)
    Chunk 0 of 1
    [EXPORT] All graphs #4 (count = 48)
    [EXPORT] Graphs #4 (count = 2)
    Chunk 0 of 1
    [EXPORT] All graphs #5 (count = 285)
    [EXPORT] Graphs #5 (count = 9)
    Chunk 0 of 1
    [EXPORT] All graphs #6 (count = 2366)
    [EXPORT] Graphs #6 (count = 31)
    
    """

"""
    GENERATE_GRAPHS = False
    LOAD_GRAPHS = False
    MAKE_KNOTS = False
    EXPORT_KNOTS = False
    LOAD_KNOTS = True
    PLOT_KNOTS = False
    COMPUTE_HOMFLYPT = True
    COMPARE_SKEIN = False

    if GENERATE_GRAPHS:
        # Generate planar graphs
        safe_delete(output_graph_filename)
        safe_delete(output_graph_filename.replace(".","-all."))
        GRAPHS = generate_planar_graphs(6, output_graph_filename, run_in_parallel=True)

        #GRAPHS = GRAPHS_ALL.filter(lambda l: l.bondedQ())

    if LOAD_GRAPHS:
        GRAPHS = load_graphs(input_graph_filename)

    if MAKE_KNOTS:

        SPATIAL = make_graphs_spatial(GRAPHS)
        print("Spatial graphs:",len(SPATIAL))

        BONDED = make_bonded_knots(SPATIAL)
        print("Bonded knots:",len(BONDED))

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

        for name, K in enumerate(KNOTS):
            K.name = str(name)


    if EXPORT_KNOTS:
        export_knots(KNOTS, output_knot_filename)

    if LOAD_KNOTS:
        KNOTS = load_knots(output_knot_filename)

    if COMPUTE_HOMFLYPT:

        counta = 0
        countb = 0
        for i in range(4):
            for K in KNOTS:
                if K.bondedQ():
                    #continue
                    pass

                print("---")

                #print("[KNOT]",K)

                #poly_K = HOMFLYPT_polynomial(K)
                #print("------knot------")
                poly_K = HSM(K)

                print(str(poly_K).replace("**","^"))

                PP = HSM(K, refined=True)
                PP = sy_simplify(PP)
                print(str(PP).replace("**", "^"))

                if len(str(poly_K).replace("**","^")) < len(str(PP).replace("**", "^")):
                    counta += 1
                else:
                    countb += 1

                print("   ", counta, ":", countb)



                #print("------copy------")

                L = K.copy()
                L.name += "_C"

                random_reidemeister_walk(L, 10)
                #print("[REID]", L)

                #poly_L = HOMFLYPT_polynomial(L)
                poly_L = HSM(L)
                #print(poly_L)
                #print("-----------------")
                if not equal(poly_K, poly_L):
                    print("[KNOT]", K)
                    print("[COPY]", L)
                    print(" ", poly_K)
                    print(" ", poly_L)
                    print("   ", sy_simplify(poly_K-poly_L))
                    raise ValueError("HOMFLYPT invariant different for same knots.")
                    #print("  NOT EQUAL", L)

    if COMPARE_SKEIN:
        for K in KNOTS:
            if K.bondedQ(): pass
            print("TEST",K,end="    ... ",flush=True)
            test_HOMFLYPT_skein_relation(K)
            print("OK")

    if PLOT_KNOTS:
        PDF_export_knots(KNOTS, "slike/knots.pdf")

        #print("Canonical:\n" + "\n".join([str(g) for g in C_B_KNOTS]) + "\n")

        #export_knots(CU_B_KNOTS, output_knot_filename, enum=True)
        #PDF_export_knots(CU_B_KNOTS, "cbknots_unor.pdf")

    exit()
"""

# DOES NOT WORK:
"""
[KNOT] Knotted([Crossing([0,1,2,3], -1), Crossing([4,5,1,0], -1), Crossing([3,2,5,6], -1), Vertex([4,7,8],[0,0,1],[1,0,0]), Vertex([6,9,10],[1,1,0],[1,0,0]), Crossing([7,10,9,8], -1)], name='1156')
[REID] Knotted([Crossing([0,1,2,3], -1), Crossing([4,5,1,0], -1), Crossing([24,2,5,6], -1), Vertex([4,7,20],[0,0,1],[1,0,0]), Vertex([6,9,10],[1,1,0],[1,0,0]), Crossing([18,10,9,8], -1), Crossing([26,21,17,20], -1), Crossing([17,19,18,8], 1), Crossing([22,19,21,22], -1), Crossing([7,3,25,23], -1), Crossing([25,24,26,23], 1)], name='1156_C')
[KNOT] Knotted([Crossing([0,1,2,3], -1), Crossing([4,5,1,0], -1), Crossing([3,2,5,6], -1), Vertex([4,7,8],[0,0,1],[1,0,0]), Vertex([6,9,10],[1,1,0],[1,0,0]), Crossing([7,10,9,8], -1)], name='1156')
[COPY] Knotted([Crossing([0,1,2,3], -1), Crossing([4,5,1,0], -1), Crossing([24,2,5,6], -1), Vertex([4,7,20],[0,0,1],[1,0,0]), Vertex([6,9,10],[1,1,0],[1,0,0]), Crossing([18,10,9,8], -1), Crossing([26,21,17,20], -1), Crossing([17,19,18,8], 1), Crossing([22,19,21,22], -1), Crossing([7,3,25,23], -1), Crossing([25,24,26,23], 1)], name='1156_C')
  -l**7*m + l**5*m - l**5/m + l**3*m**5 - 6*l**3*m**3 + 10*l**3*m - 5*l**3/m + l*m**5 - 7*l*m**3 + 14*l*m - 8*l/m - m**3/l + 4*m/l - 4/(l*m)
  -l**7*m + l**5*m - l**5/m + l**3*m**5 - 6*l**3*m**3 + 9*l**3*m - 5*l**3/m - l**2*m**2 + l*m**5 - 7*l*m**3 + 12*l*m - 8*l/m - m**2 - m**3/l + 3*m/l - 4/(l*m)
    m*(l*(l**3 + l**2*m + 2*l + m) + 1)/l


"""