import networkx as nx
import matplotlib.pyplot as plt

g = nx.Graph(
[(7,3),(7,6),(7,5),(7,4),(6,3),(6,5),(6,7),(5,2),(5,4),(5,7),(5,6),(4,1),(4,7),(4,5),(4,2),(3,0),(3,6),(3,7),(3,1),(2,0),(2,1),(2,4),(2,5),(1,0),(1,3),(1,4),(1,2),(0,1),(0,2),(0,3)]
)

h = nx.Graph(
[(6,2),(6,5),(6,7),(6,3),(2,0),(2,1),(2,5),(2,6),(5,2),(5,4),(5,7),(5,6),(7,3),(7,6),(7,5),(7,4),(3,0),(3,6),(3,7),(3,1),(0,1),(0,2),(0,3),(1,0),(1,3),(1,4),(1,2),(4,1),(4,7),(4,5)]

)

print(g)
print(h)
print(nx.could_be_isomorphic(g,h ))
exit()
G = nx.Graph()
G.add_edge(1, 2)
G.add_edge(1, 3)
G.add_edge(1, 5)
G.add_edge(2, 3)
G.add_edge(3, 4)
G.add_edge(4, 5)

G[1] = "erik"
G.nodes[1]["name"] = "o"

print(G)
print(G.graph)
print(G.nodes(data=True))
print(G.edges(data=True))

exit()

# explicitly set positions
pos = {1: (0, 0), 2: (-1, 0.3), 3: (2, 0.17), 4: (4, 0.255), 5: (5, 0.03)}

options = {
    "font_size": 36,
    "node_size": 3000,
    "node_color": "white",
    "edgecolors": "black",
    "linewidths": 5,
    "width": 5,
}
nx.draw_networkx(G, pos, **options)

# Set margins for the axes so that nodes aren't clipped
ax = plt.gca()
ax.margins(0.20)
plt.axis("off")
plt.show()