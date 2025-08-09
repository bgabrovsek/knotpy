# knotpy/invariants/fundamental_group.py
"""
Fundamental group presentation and Fox calculus utilities.
"""

__all__ = ["fundamental_group", "fox_derivative", "alexander_fox_matrix"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

import sympy as sp
from sympy.combinatorics.fp_groups import FpGroup
from sympy.combinatorics.free_groups import free_group, FreeGroupElement

from knotpy.classes.endpoint import IngoingEndpoint
from knotpy.classes.planardiagram import OrientedPlanarDiagram
from knotpy.algorithms.topology import overstrands as get_overstrands


def fundamental_group(
    k: OrientedPlanarDiagram,
    return_dict: bool = False,
) -> FpGroup | tuple[FpGroup, dict]:
    """Return a presentation of the fundamental group of the complement of ``k`` in S³.

    **Relations:**
        - Positive crossing:
          ``x_i * x_j * x_{i+1}⁻¹ * x_j⁻¹ = 1``
        - Negative crossing:
          ``x_i * x_j⁻¹ * x_{i+1}⁻¹ * x_j = 1``
        - Vertex:
          ``x₁^{s₁} * x₂^{s₂} * ...`` where ``sᵢ = 1`` if the arc is directed
          **into** the vertex, and ``-1`` if **out** of the vertex.

    Args:
        k: Oriented planar diagram.
        return_dict: If True, also return a dict mapping each overstrand endpoint to its generator.

    Returns:
        - ``FpGroup`` if ``return_dict`` is False.
        - Tuple ``(FpGroup, overstrand_generator_dict)`` if True.

    Raises:
        TypeError: If ``k`` is not oriented.
    """
    if not k.is_oriented():
        raise TypeError("Cannot compute the fundamental group of an unoriented planar diagram.")

    overstrands = sorted(get_overstrands(k))
    F, *generators = free_group(" ".join(f"x{i}" for i in range(len(overstrands))))
    overstrand_generator = {
        ep: generator
        for strand, generator in zip(overstrands, generators)
        for ep in strand
    }

    relators = []
    for c in k.crossings:
        ep0, ep1, ep2, ep3 = k.endpoints[c]
        if k.sign(c) > 0:
            if isinstance(ep0, IngoingEndpoint):
                relators.append(
                    overstrand_generator[ep0]
                    * overstrand_generator[ep1]
                    * (overstrand_generator[ep2] ** -1)
                    * (overstrand_generator[ep3] ** -1)
                )
            else:
                relators.append(
                    overstrand_generator[ep2]
                    * overstrand_generator[ep1]
                    * (overstrand_generator[ep0] ** -1)
                    * (overstrand_generator[ep3] ** -1)
                )
        else:
            if isinstance(ep0, IngoingEndpoint):
                relators.append(
                    overstrand_generator[ep0]
                    * (overstrand_generator[ep1] ** -1)
                    * (overstrand_generator[ep2] ** -1)
                    * overstrand_generator[ep3]
                )
            else:
                relators.append(
                    overstrand_generator[ep2]
                    * (overstrand_generator[ep1] ** -1)
                    * (overstrand_generator[ep0] ** -1)
                    * overstrand_generator[ep3]
                )

    for v in k.vertices:
        eps = k.endpoints[v]
        relator = overstrand_generator[eps[0]] ** (
            -1 if isinstance(eps[0], IngoingEndpoint) else 1
        )
        for ep in eps[1:]:
            relator *= overstrand_generator[ep] ** (
                -1 if isinstance(ep, IngoingEndpoint) else 1
            )
        relators.append(relator)

    G = FpGroup(F, relators)
    return (G, overstrand_generator) if return_dict else G


def fox_derivative(
    relator: FreeGroupElement,
    variable,
    abelize: bool = True,
):
    """Compute the Fox derivative of ``relator`` with respect to ``variable``.

    Rules:
        ∂x_j/∂x_i = 1 if i == j else 0  
        ∂e/∂x_i = 0  
        ∂(uv)/∂x_i = ∂u/∂x_i + u * ∂v/∂x_i  
        ∂(u⁻¹)/∂x_i = -u⁻¹ * ∂u/∂x_i  

    Example:
        ``d(x*y*x*y⁻¹*x⁻¹*y⁻¹)/dx = 1 + xy - xyxy⁻¹x⁻¹``

    Args:
        relator: Free group element (relator).
        variable: Generator or its index in ``relator``.
        abelize: If True, return the abelianized derivative.

    Returns:
        Fox derivative (SymPy expression).

    Raises:
        NotImplementedError: If ``abelize`` is False.
        ValueError: If a variable exponent is not ±1.
    """
    if not abelize:
        raise NotImplementedError("Non-abelized Fox derivative not implemented.")

    if isinstance(variable, FreeGroupElement):
        variable = variable.array_form[0][0]

    derivative = sp.Integer(0)
    multiplier = sp.Integer(1)
    for var, exp in relator.array_form:
        if var == variable:
            if exp not in (-1, 1):
                raise ValueError("Exponent expected to be +1 or -1.")
            derivative += multiplier if exp == 1 else -multiplier * (var ** -1)
        multiplier *= var ** exp
    return derivative


def alexander_fox_matrix(G: FpGroup) -> sp.Matrix:
    """Compute the Fox Jacobian matrix for a finitely presented group.

    Args:
        G: Finitely presented group.

    Returns:
        List of lists of Fox derivatives (as SymPy expressions).
    """
    rows = [
        [fox_derivative(relator, generator) for generator in G.generators]
        for relator in G.relators
    ]
    return sp.Matrix(rows)


if __name__ == "__main__":
    pass
