from sympy.combinatorics.fp_groups import FpGroup
from sympy.combinatorics.free_groups import free_group, FreeGroupElement
from sympy import Integer, Expr
from itertools import combinations

from knotpy.classes.endpoint import IngoingEndpoint
from knotpy.classes.planardiagram import OrientedPlanarDiagram, PlanarDiagram
from knotpy.algorithms.topology import overstrands as get_overstrands

"""
Relations
Positive crossing: xi * xj * x(i+1)**-1 * xj**-1 = 1
Negative crossing: xi * xj**-1 * x(i+1)**-1 * xj = 1
Vertex: x1**s1 * x2**s1 * ..., where s1 == 1 if the arc is directed into the vertex, -1 if out of the vertex


"""

def alexander_fox_matrix(G: FpGroup):
    """Compute the Fox Jacobian of the finitely presented group G."""
    return [[fox_derivative(relator, generator) for generator in G.generators] for relator in G.relators]


def minor(matrix, row_indices, col_indices):
    """Extract submatrix given selected rows and columns."""
    return [[matrix[i][j] for j in col_indices] for i in row_indices]

def determinant(matrix):
    """Compute determinant of a square matrix recursively (Laplace expansion)."""
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        # Base case for 2x2 matrix
        return matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]
    # Recursive case
    det = 0
    for j in range(n):
        sub = [row[:j] + row[j+1:] for row in matrix[1:]]  # Minor matrix
        det += ((-1)**j) * matrix[0][j] * determinant(sub)
    return det

def minors(matrix):
    n = len(matrix)        # number of rows
    m = len(matrix[0])     # number of columns
    if m < n - 1:
        raise ValueError("Cannot compute matrix minors (too few rows)")

    result = []

    row_combos = list(combinations(range(n), n - 1))
    col_combos = list(combinations(range(m), n - 1))

    for rows in row_combos:
        for cols in col_combos:
            submatrix = minor(matrix, rows, cols)
            det = determinant(submatrix)
            result.append((rows, cols, det))

    return result

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

def fundamental_group(k: OrientedPlanarDiagram):
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

    return FpGroup(F, relators)


def multivariable_alexander_polynomial(k: PlanarDiagram | OrientedPlanarDiagram):
    """Return the multivariate Alexander polynomial of a knot or link.
    In the case of a link, the multivariable Alexander polynomial is a Laurent polynomial in n-variables, where
    n is the number of link components. In the case of a knot, the polynomial is divided by (t-1) so it matches the
    skein-relation definition.

    """
    pass


if __name__ == '__main__':
    #
    # # test fox
    # f, x, y = free_group("x y")
    # print(type(x))
    # print(type(x * y * y))
    # x_ = x.array_form[0][0]
    # print(type(x_))
    # xx = FreeGroupElement([(x_,1)])
    # print(type(xx))
    # print(x)
    # print(xx)
    # print(x == xx)
    # exit()
    #
    #
    # f, x, y, z = free_group("x y z")
    # print(f)
    # print(fox_derivative(z * y * x**-1 * y **-1, x))  # z * y * (-x**-1)
    # print(fox_derivative(z * y * x**-1 * y **-1, y))
    # print(fox_derivative(z * y * x**-1 * y **-1, z))
    # exit()
    # #r = 1 + x*y - x*y*x * y**-1 +x**-1
    # # 1 + xy - xyxy^-1 x^-1
    # """
    # 1 + x ( y * (  1 + x * ( y^-1 * (-x^-1 + x^-1 ( 0 ) ) ) )  )
    # 1 + x ( y * (  1 + x * ( -y^-1  )  )
    #
    # """
    # print(d)
    # exit()
    # # assert f == r

    import knotpy as kp
    k = kp.knot("3_1")
    k = kp.orient(k)
    G = fundamental_group(k)
    A = alexander_fox_matrix(G)
    print(A)
