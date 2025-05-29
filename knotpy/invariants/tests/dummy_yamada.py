def __yamada_rec(k: PlanarDiagram):
    # basic recursive yamada for testing purposes

    # we have a crossing
    if k.crossings:
        crossing = next(iter(k.crossings))
        return (_A * __yamada_rec(smoothen_crossing(k, crossing_for_smoothing=crossing, method="A")) +
                (_A ** -1) * __yamada_rec(smoothen_crossing(k, crossing_for_smoothing=crossing, method="B")) +
                __yamada_rec(crossing_to_vertex(k, crossing=crossing)))

    # we have a bridge
    if bridges(k):
        return Integer(0)

    # we have a loop
    if L := loops(k):
        return -(_A + Integer(1) + _A**-1) *  __yamada_rec(remove_arc(k, arc_for_removing=L[0], inplace=False))

    # we have a isolated vertex
    if vs := [v for v in k.vertices if k.degree(v) == 0]:
        return Integer(-1) * __yamada_rec(k.copy().remove_node(vs[0], remove_incident_endpoints=False))

    # we have a normal edge
    if (arc := next(iter(k.arcs), None)) is not None:
        return __yamada_rec(remove_arc(k, arc_for_removing=arc, inplace=False)) + __yamada_rec(contract_arc(k, arc_for_contracting=arc, inplace=False))

    # empty graph
    if len(k) == 0:
        return Integer(1)

def _yamada_rec(k: PlanarDiagram, normalize=True):
    polynomial = expand(__yamada_rec(k.copy()))

    if normalize:
        lowest_exponent = min(term.as_coeff_exponent(_A)[1] for term in polynomial.as_ordered_terms())
        polynomial = expand(polynomial * (-_A) ** (-lowest_exponent))
    return polynomial
