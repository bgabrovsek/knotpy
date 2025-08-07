from sympy.combinatorics.fp_groups import FpGroup
from sympy.combinatorics.free_groups import free_group, FreeGroupElement
from sympy import Integer, symbols, simplify, expand, fraction, gcd, Poly, Matrix
from itertools import combinations
from functools import reduce

from knotpy.classes.endpoint import IngoingEndpoint
from knotpy.classes.planardiagram import OrientedPlanarDiagram
from knotpy.algorithms.topology import overstrands as get_overstrands

"""
Relations
Positive crossing: xi * xj * x(i+1)**-1 * xj**-1 = 1
Negative crossing: xi * xj**-1 * x(i+1)**-1 * xj = 1
Vertex: x1**s1 * x2**s1 * ..., where s1 == 1 if the arc is directed into the vertex, -1 if out of the vertex

"""


def fundamental_group(k: OrientedPlanarDiagram, return_dict=False):
    """Return a presentation of the fundamental group of the complement of k in S^3."""
    if not k.is_oriented():
        raise TypeError("Cannot compute the fundamental group of an unoriented planar diagram")
    overstrands = sorted(get_overstrands(k))
    F, *generators = free_group(" ".join(f"x{i}" for i in range(len(overstrands))))  # generators are 'x1', 'x2', ...
    overstrand_generator = {ep: generator for strand, generator in zip(overstrands, generators) for ep in strand}

    relators = []
    for c in k.crossings:
        ep0, ep1, ep2, ep3 = k.endpoints[c]
        # TODO: the relation can be simplified
        if k.sign(c) > 0:
            if isinstance(ep0, IngoingEndpoint):
                relators.append(overstrand_generator[ep0] * overstrand_generator[ep1] * (overstrand_generator[ep2] ** -1) * (overstrand_generator[ep3]**-1))
            else:
                relators.append(overstrand_generator[ep2] * overstrand_generator[ep1] * (overstrand_generator[ep0] ** -1) * (overstrand_generator[ep3]**-1))
        else:
            if isinstance(ep0, IngoingEndpoint):
                relators.append(overstrand_generator[ep0] * (overstrand_generator[ep1]**-1) * (overstrand_generator[ep2] ** -1) * overstrand_generator[ep3])
            else:
                relators.append(overstrand_generator[ep2] * (overstrand_generator[ep1]**-1) * (overstrand_generator[ep0] ** -1) * overstrand_generator[ep3])

    for v in k.vertices:
        eps = k.endpoints[v]
        relator = overstrand_generator[eps[0]] ** (-1 if isinstance(eps[0], IngoingEndpoint) else 1)
        for ep in eps[1:]:
            relator *= overstrand_generator[ep] ** (-1 if isinstance(ep, IngoingEndpoint) else 1)
        relators.append(relator)

    if return_dict:
        return FpGroup(F, relators), overstrand_generator
    else:
        return FpGroup(F, relators)


def fox_derivative(relator: FreeGroupElement, variable, abelize=True):
    """
    ∂x_j/∂x_i = 1 if i == j else 0
    ∂e/∂x_i = 0
    ∂(uv)/∂x_i = ∂u/∂x_i + u * ∂v/∂x_i
    ∂(u**-1)/∂x_i = - u**-1 *  ∂u/∂x_i

    Exanmple:
    d(x * y * x * y**-1 * x**-1 * y**-1)/dx = 1 + xy - xyxy^-1 x^-1
    Args:
        relator:
        variable:

    Returns:

    """

    if not abelize:
        raise NotImplementedError("Non-abelized fox derivative not implemented.")

    if isinstance(variable, FreeGroupElement):
        variable = variable.array_form[0][0]

    derivative = Integer(0)
    multiplier = Integer(1)
    for var, exp in relator.array_form:
        if var == variable:
            if exp not in [-1, 1]:
                raise ValueError("Exponent expected to be +1 or -1")
            derivative += multiplier if exp == 1 else - multiplier * (var ** -1)
        multiplier *= var ** exp
    return derivative


def alexander_fox_matrix(G: FpGroup):
    """Compute the Fox Jacobian of the finitely presented group G."""
    return [[fox_derivative(relator, generator) for generator in G.generators] for relator in G.relators]







if __name__ == '__main__':
    pass