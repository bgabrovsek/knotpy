import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


import queue
q1 = queue.Queue()

q1.put(10)
q1.put(99)
print(q1.get())
G = nx.Graph()
G.add_node('a', name='A')
G.add_node('b', name='B')
G.add_node('c', name='C')
G.add_edge('a','b',weight=3)
G.add_edge('a','c',weight=5)


print(G)
print(G.degree("a"))
print("name", G.name)
mdG = nx.MultiDiGraph()
mdG.add_nodes_from([0,1,2])
mdG.add_edges_from([(0,1), [0,1], (0,2), (1,0), ])


mG = nx.MultiGraph()
mG.add_nodes_from([0,1,2])
mG.add_edges_from([(0,1), (0,1), (0,2), (1,0), ])




diG = nx.DiGraph()
diG.add_nodes_from([0,1,2])
diG.add_edges_from([(0,1), (0,1), (0,2), (1,0), ])


exit()
"""



G = G
nx.draw_networkx(G, pos = pos, labels = labels, arrows = True,
 node_shape = "s", node_color = "white")
plt.title("Organogram of a company.")
plt.savefig("Output/plain organogram using networkx.jpeg",
 dpi = 300)
plt.show()

exit()
G = nx.Graph()
G.add_edge(1, 2, name = "lala", author="kuku")
G.add_edge(1, 3)
G.add_edge(1, 5)
G.add_edge(2, 3)
G.add_edge(3, 4)
G.add_edge(4, 5)

G.add_node(8,name=999)
G.add_node("X")
G.add_node("X")

print(G.nodes)
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

"""