import knotpy as kp

bonded_graphs = []

for N in range(4, 11):
    graphs = kp.load_headerless_collection(f"data/plantri/plantri_c3_d3_n{N}.txt", "plantri", )

    for g in graphs:
        deg_seq = kp.degree_sequence(g)
        count_threes = deg_seq.count(3)
        if all(d in [3,4] for d in deg_seq) and count_threes % 2 == 0:
            # graph good
            bonded_graphs.append(g)
        else:
            pass

    print("----\n", N, "crossings", len(graphs), "->", len(bonded_graphs))

kp.save_collection("data/graphs10.txt",bonded_graphs,"CEM")