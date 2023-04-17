import matplotlib.pyplot as plt
import networkx as nx


G = nx.Graph()
G.add_node("a",weight=77)
G.add_node("b",weight=88)
G.add_edge("a", "b", weight=1)
G.add_edge("b", "c", weight=2)
G.add_edge("a", "c", weight=3)
G.add_edge("c", "d", weight=4)

print(G.__str__())
print(G.__repr__())
print("ok.")


G2 = nx.MultiDiGraph()

G2.add_node(1)
G2.add_nodes_from([2, 3])
#H2 = nx.path_graph(3)

key = G2.add_edge(1, 2, weight=4.7 )
key = G2.add_edge(1, 3, weight=4.7 )

#G2.node[1]['room'] = 714
#del G2.node[1]['room'] # remove attribute

print(key)
print("-")
exit()


G = nx.Graph()

G.add_edge("a", "b", weight=0.6)
G.add_edge("a", "c", weight=0.2)
G.add_edge("c", "d", weight=0.1)
G.add_edge("c", "e", weight=0.7)
G.add_edge("c", "f", weight=0.9)
G.add_edge("a", "d", weight=0.3)

elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0.5]
esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 0.5]

pos = nx.spring_layout(G, seed=7)  # positions for all nodes - seed for reproducibility

# nodes
nx.draw_networkx_nodes(G, pos, node_size=700)

# edges
nx.draw_networkx_edges(G, pos, edgelist=elarge, width=6)
nx.draw_networkx_edges(
    G, pos, edgelist=esmall, width=6, alpha=0.5, edge_color="b", style="dashed"
)

# node labels
nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")
# edge weight labels
edge_labels = nx.get_edge_attributes(G, "weight")
nx.draw_networkx_edge_labels(G, pos, edge_labels)

ax = plt.gca()
ax.margins(0.08)
plt.axis("off")
plt.tight_layout()
plt.show()