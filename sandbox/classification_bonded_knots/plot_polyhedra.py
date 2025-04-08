import knotpy as kp



graphs = kp.load_collection("data/graphs10.txt")
# convert to graphs
for g in graphs:
    g.convert_nodes(g.crossings, kp.Vertex)

graphs_with_bonds = {i: [] for i in range(6)}
count_graphs = [[0 for b in range(6)] for c in range(11)]

for g in graphs:
    deg_seq = kp.degree_sequence(g)
    bonds = deg_seq.count(3)//2
    crossings = deg_seq.count(4)
    count_graphs[crossings][bonds] += 1
    graphs_with_bonds[bonds].append(g)
    for node in g.vertices:
        if len(g.nodes[node]) == 3:
            g.nodes[node].attr = {"color":"red"}
        else:
            g.nodes[node].attr = {"color":"blue"}


for crossings in range(11):
    print(str(count_graphs[crossings]))

for bonds in range(6):
    if graphs_with_bonds[bonds]:
        kp.export_pdf(graphs_with_bonds[bonds], f"plots/polyhedra-{bonds}-bonds.pdf")