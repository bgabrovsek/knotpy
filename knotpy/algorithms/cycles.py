from knotpy.classes.planardiagram import PlanarDiagram

def cycles(g:PlanarDiagram, n:int):
    """ return cycles of length n"""

    if n < 1:
        raise ValueError("Length must be at least 1")

    all_cycles = set()

    def depth_first_search(path, visited):
        current = path[-1]
        start = path[0]
        if len(path) == n:
            if start in [node for node, _ in g.nodes[current]]:
                cycle = tuple(path)
                canonical = _min_lex_rotation(cycle)
                all_cycles.add(canonical)
            return

        for neighbour_node, position in g.nodes[current]:
            if neighbour_node in visited or neighbour_node in path:
                continue
            depth_first_search(path + [neighbour_node], visited | {neighbour_node})

    for v in g.nodes:
        depth_first_search(path=[v], visited={v})

    return all_cycles

def _min_lex_rotation(cycle):
    """Return canonical rotation of a cycle (min of all rotations and reversed rotations)."""
    rotations = [tuple(cycle[i:] + cycle[:i]) for i in range(len(cycle))]
    reversed_rotations = [tuple(reversed(c)) for c in rotations]
    return min(rotations + reversed_rotations)


if __name__ == "__main__":
    import knotpy as kp
    k = kp.from_knotpy_notation(
        "a=V(b0) b=X(a0 c0 c3 d3) c=X(b1 d2 e0 b2) d=X(f0 e1 c1 b3) e=X(c2 d1 g3 f1) f=X(d0 e3 g2 h0) g=X(h3 h1 f2 e2) h=X(f3 g1 i0 g0) i=V(h2)")

    print(k)
    k_ = kp.dual_planar_diagram(k)
    print(k_)

    print(    )
    print("regions")
    for r in k_.nodes:
        print("  region", r)

    for n in range(1, 5):
        print()
        print(n)
        for c in cycles(k_, n):
            print("  cycle", c)
