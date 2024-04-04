s = "('BondedKnot', {'name': 't0_1#(+3_1#+3_1)(1).0'}, [('Crossing', 'c', (('Endpoint', 'e', 1, {}), ('Endpoint', 'f', 0, {}), ('Endpoint', 'bond', 1, {}), ('Endpoint', 'e', 2, {})), {}), ('Crossing', 'd', (('Endpoint', 'h', 1, {}), ('Endpoint', 'bond', 3, {}), ('Endpoint', 'g', 3, {}), ('Endpoint', 'h', 2, {})), {}), ('Crossing', 'e', (('Endpoint', 'f', 1, {}), ('Endpoint', 'c', 0, {}), ('Endpoint', 'c', 3, {}), ('Endpoint', 'f', 2, {})), {}), ('Crossing', 'f', (('Endpoint', 'c', 1, {}), ('Endpoint', 'e', 0, {}), ('Endpoint', 'e', 3, {}), ('Endpoint', 'bond', 2, {})), {}), ('Crossing', 'g', (('Endpoint', 'bond', 0, {}), ('Endpoint', 'h', 0, {}), ('Endpoint', 'h', 3, {}), ('Endpoint', 'd', 2, {})), {}), ('Crossing', 'h', (('Endpoint', 'g', 1, {}), ('Endpoint', 'd', 0, {}), ('Endpoint', 'd', 3, {}), ('Endpoint', 'g', 2, {})), {}), ('Bond', 'bond', (('Endpoint', 'g', 0, {}), ('Endpoint', 'c', 2, {}), ('Endpoint', 'f', 3, {}), ('Endpoint', 'd', 1, {})), {})])"
from knotpy.notation.native import from_knotpy_notation
from knotpy.algorithms.structure import cut_edges, cut_vertices
k = from_knotpy_notation(s)
print(k)

print(cut_edges(k))
print(cut_vertices(k))

print()