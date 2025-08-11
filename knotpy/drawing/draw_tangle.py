"""
Drawing utilities for algebraic tangles.

This module provides a lightweight way to render “algebraic” tangles built
from the formal sum/product of elementary pieces (-1, 0, 1). It converts
symbolic tangle expressions into geometric zig-zag polylines and offers two
renderers:

- `draw(expr)`: quick polyline rendering
- `draw_smooth(expr)`: smooth rendering using B-splines

Notes:
- Heavy dependencies (matplotlib, numpy, scipy) are imported locally inside
  the functions that require them to keep `import knotpy` fast.
"""

from itertools import combinations
from math import atan2, degrees

__all__ = [
    "TangleExpr",
    "TangleSum",
    "TangleProduct",
    "integral",
    "angle_between_points",
    "ZigZag",
    "connect",
    "crossings",
    "to_zigzag",
    "add_corners_and_smoothen",
    "draw",
    "are_continuation",
    "draw_smooth",
]

__version__ = "0.2"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

# Rendering/config constants
ETS = 1  # elementary tangle size
GAP = 0.475
LINE_WIDTH = 4.0
ENDPOINT_SIZE = 60
SUBTANGLE_DISTANCE = 0.75  # distance between subtangles when adding/multiplying

ANGLE_LIMIT = 10  # if three points differ by this angle, remove the middle point
LENGTH_MIN = 3 * 1.4142

FIT_INTO_SQUARE = True
SHOW_GRID = False
SHOW_AXIS = False

STRAND_COLOR = "black"
EP_COLOR = "gray"

COL = ["#185674", "#3F6D44", "#A04D5A", "#593C60", "#61615B", "#6B504F"]


class TangleExpr:
    """General expression for a tangle; a binary tree of sums/products.

    The expression nodes hold two terms. Leaf values are integers in {-1, 0, 1}.

    Args:
        term1: Left term.
        term2: Right term.
    """

    def __init__(self, term1, term2):
        self.terms = (term1, term2)

    def __add__(self, other):
        return TangleSum(self, other)

    def __mul__(self, other):
        return TangleProduct(self, other)

    def __iter__(self):
        return iter(self.terms)


class TangleSum(TangleExpr):
    """Formal sum of tangles."""

    def __repr__(self):
        return f"({self.terms[0]} + {self.terms[1]})"


class TangleProduct(TangleExpr):
    """Formal product of tangles."""

    def __repr__(self):
        return f"({self.terms[0]} * {self.terms[1]})"


def integral(n: int):
    """Build an integral tangle as a nested sum of ±1 and 0.

    For |n| ≤ 1 returns the integer directly. Otherwise returns
    TangleSum(±1, integral(n∓1)) recursively.

    Args:
        n: Integer tangle value.

    Return:
        int | TangleExpr: The expression representing the integral tangle.
    """
    if -1 <= n <= 1:
        return n
    if n > 1:
        return TangleSum(1, integral(n - 1))
    # n < -1
    return TangleSum(-1, integral(n + 1))


def angle_between_points(z1: complex, z2: complex, z3: complex) -> float:
    """Return signed angle (degrees) at z2 determined by points z1–z2–z3.

    Positive means left turn, negative right turn; 0 means collinear.

    Args:
        z1: First point.
        z2: Vertex point.
        z3: Third point.

    Return:
        float: Angle in degrees in range (-180, 180].
    """
    v1 = z2 - z1
    v2 = z3 - z2
    dot = (v1.real * v2.real) + (v1.imag * v2.imag)
    cross = (v1.real * v2.imag) - (v1.imag * v2.real)
    return degrees(atan2(cross, dot))


class ZigZag:
    """A zig-zag polyline representation of a tangle.

    The geometry is a list of polyline segments, each a list of complex points.
    We also store a “compass” rectangle (NW, SW, SE, NE) that indicates the
    bounding endpoints for the left/right/top/bottom boundary of the tangle.
    """

    def __init__(self):
        self.lines: list[list[complex]] = []
        self.set_compass(0j, 0j, 0j, 0j)

    # Bounding box corners computed from the compass
    @property
    def N(self) -> complex:  # north y-position as complex (0 + yi)
        return 1j * max(self.NE.imag, self.NW.imag)

    @property
    def S(self) -> complex:  # south y-position
        return 1j * min(self.SW.imag, self.SE.imag)

    @property
    def W(self) -> float:  # west x-position
        return min(self.NW.real, self.SW.real)

    @property
    def E(self) -> float:  # east x-position
        return max(self.NE.real, self.SE.real)

    @property
    def height(self) -> float:
        return (self.N - self.S).imag

    @property
    def width(self) -> float:
        return (self.E - self.W).real

    def bounding_box(self, compass: str) -> complex | float:
        """Return tight bounding coordinate for a given compass letter."""
        if compass == "N":
            return 1j * max(z.imag for line in self.lines for z in line)
        if compass == "S":
            return 1j * min(z.imag for line in self.lines for z in line)
        if compass == "W":
            return min(z.real for line in self.lines for z in line)
        if compass == "E":
            return max(z.real for line in self.lines for z in line)
        raise ValueError(f"Unknown direction {compass}")

    def __bool__(self):
        return bool(self.lines)

    def add_line(self, line: list[complex]):
        """Append a non-degenerate polyline to the zig-zag."""
        if len(line) > 1 and not all(z == line[0] for z in line):
            self.lines.append(line if isinstance(line, list) else list(line))
            self.join()

    def set_compass(self, NW: complex, SW: complex, SE: complex, NE: complex):
        """Set the compass rectangle of the zig-zag."""
        self.NW, self.SW, self.SE, self.NE = NW, SW, SE, NE

    def __add__(self, other: "ZigZag") -> "ZigZag":
        """Concatenate two zig-zags (and re-join any meeting endpoints)."""
        z = ZigZag()
        z.lines = self.lines + other.lines
        z.join()
        z.NW, z.SW, z.SE, z.NE = self.NW, self.SW, other.SE, other.NE
        return z

    def mirror(self):
        """Mirror through the y-axis."""
        self.lines = [[complex(-z.real, z.imag) for z in line] for line in self.lines]
        self.set_compass(
            NW=complex(-self.NE.real, self.NE.imag),
            SW=complex(-self.SE.real, self.SE.imag),
            SE=complex(-self.SW.real, self.SW.imag),
            NE=complex(-self.NW.real, self.NW.imag),
        )

    def rotate(self):
        """Rotate once CCW (multiply coordinates by 1j)."""
        self.lines = [[z * 1j for z in line] for line in self.lines]
        self.set_compass(NW=self.NE * 1j, SW=self.NW * 1j, SE=self.SW * 1j, NE=self.SE * 1j)

    def reflect(self):
        """Reflect (mirror then rotate)."""
        self.mirror()
        self.rotate()

    def move(self, dz: complex):
        """Translate the entire zig-zag by complex offset `dz`."""
        self.lines = [[z + dz for z in line] for line in self.lines]
        self.set_compass(self.NW + dz, self.SW + dz, self.SE + dz, self.NE + dz)

    def join(self):
        """Join polyline segments that share endpoints into longer polylines."""
        changes = True
        while changes:
            changes = False
            length = len(self.lines)
            for i, j in combinations(range(length), 2):
                if self.lines[i][-1] == self.lines[j][0]:
                    self.lines[i] = self.lines[i] + self.lines[j][1:]
                    del self.lines[j]
                elif self.lines[i][0] == self.lines[j][-1]:
                    self.lines[i] = self.lines[j] + self.lines[i][1:]
                    del self.lines[j]
                elif self.lines[i][0] == self.lines[j][0]:
                    self.lines[i] = list(reversed(self.lines[i][1:])) + self.lines[j]
                    del self.lines[j]
                elif self.lines[i][-1] == self.lines[j][-1]:
                    self.lines[i] = self.lines[i] + list(reversed(self.lines[j][:-1]))
                    del self.lines[j]

                if len(self.lines) != length:
                    changes = True
                    break

    def smoothen(self):
        """Placeholder for point simplification (kept for compatibility)."""
        return

    def split(self):
        """Split long nearly straight segments (used for smoothing heuristics)."""
        new_lines = []
        for line in self.lines:
            new_line = [line[0]]
            for i in range(len(line) - 2):
                z0, z1, z2 = line[i : i + 3]
                if not (-ANGLE_LIMIT <= angle_between_points(z0, z1, z2) <= ANGLE_LIMIT) and abs(
                    z1 - z0
                ) < LENGTH_MIN and abs(z2 - z1) < LENGTH_MIN:
                    new_line.append(z1)
            new_line.append(line[-1])
            new_lines.append(new_line)
        self.lines = new_lines

    def __iter__(self):
        return iter(self.lines)

    def __repr__(self):
        return f"Zig-zag {self.NW}, {self.SW}, {self.SE}, {self.NE}"


def connect(z: complex, w: complex, pos: str) -> list[complex]:
    """Return a short polyline connecting z (left) to w (right) by H/V/diag segments.

    Heuristic that prefers diagonal+horizontal or diagonal+vertical depending on
    geometry and whether we connect along the “north” or “south” side.

    Args:
        z: Left endpoint (complex).
        w: Right endpoint (complex).
        pos: "N" or "S" — the side we are connecting across.

    Return:
        list[complex]: 2 or 3 points forming the connection polyline.
    """
    if z == w:
        return []

    def sign(i):
        return 1 if i > 0 else (-1 if i < 0 else 0)

    d = w - z
    dx, dy = d.real, d.imag

    # Straight lines if axis-aligned or 45°
    if z.real == w.real or z.imag == w.imag or abs(dx) == abs(dy):
        return [z, w]

    result = []
    # diagonal + horizontal
    if abs(dx) > abs(dy):
        if (pos == "N" and dy > 0) or (pos == "S" and dy < 0):
            result = [z, z + abs(dy) + 1j * dy, w]
        else:
            result = [z, w - abs(dy) - 1j * dy, w]

    # diagonal + vertical
    if abs(dx) < abs(dy):
        if (pos == "N" and dy < 0) or (pos == "S" and dy > 0):
            result = [z, z + dx + 1j * sign(dy) * dx, w]
        else:
            result = [z, w - dx - 1j * sign(dy) * dx, w]

    if abs(result[1] - result[0]) < 1 or abs(result[2] - result[1]) < 1:
        return [result[0], result[2]]
    return result


def crossings(expr) -> int:
    """Return the number of crossings contributed by an expression.

    Args:
        expr: int or TangleExpr.

    Return:
        int: Sum of absolute values at integer leaves.
    """
    if isinstance(expr, int):
        return abs(expr)
    return sum(crossings(t) for t in expr)


def to_zigzag(expr) -> ZigZag:
    """Convert an algebraic tangle expression to a geometric zig-zag.

    Supports leaf tangles −1, 0, 1 and compositions via TangleSum/TangleProduct.

    Args:
        expr: int in {-1, 0, 1} or a TangleExpr.

    Return:
        ZigZag: Polyline representation with compass endpoints.
    """
    if isinstance(expr, int):
        zz = ZigZag()
        if expr in (1, -1):
            zz.add_line([1j, 0.5 + 0.5j + (-0.5 + 0.5j) * GAP])
            zz.add_line([1, 0.5 + 0.5j - (-0.5 + 0.5j) * GAP])
            zz.add_line([0j, 1 + 1j])
            zz.set_compass(NW=1j, SW=0j, SE=1 + 0j, NE=1 + 1j)
            if expr == -1:
                zz.mirror()
        elif expr == 0:
            zz.add_line([1j, 0.5 + 0.5j, 1 + 1j])
            zz.add_line([0j, 0.5 + 0.5j, 1 + 0j])
            zz.set_compass(NW=1j, SW=0j, SE=1 + 0j, NE=1 + 1j)
        else:
            raise NotImplementedError("Can only layout integral tangles −1, 0, or 1")
        return zz

    if isinstance(expr, TangleExpr) and isinstance(expr.terms[1], int) and expr.terms[1] == 0:
        # Addition or multiplication by 0 (right term 0): draw only the left term
        zz = to_zigzag(expr.terms[0])
        if isinstance(expr, TangleProduct):
            zz.reflect()
        return zz

    if isinstance(expr, TangleExpr):
        L, R = expr.terms
        zl = to_zigzag(L)
        zr = to_zigzag(R)

        if isinstance(expr, TangleProduct):
            zl.reflect()

        # center the two subtangles vertically
        zr.move(0.5 * (zl.N + zl.S - zr.N - zr.S))
        # move right tangle to the right
        if zl.height == 1 and zr.height == 1:
            zr.move(zl.bounding_box("E") - zr.bounding_box("W"))
        else:
            zr.move(zl.bounding_box("E") - zr.bounding_box("W") + SUBTANGLE_DISTANCE)

        zz = zl + zr
        # connecting arcs (north and south)
        zz.add_line(connect(zl.NE, zr.NW, "N"))
        zz.add_line(connect(zl.SE, zr.SW, "S"))
        return zz

    raise TypeError(f"Cannot convert to zig-zag: unsupported type {type(expr)}")


def add_corners_and_smoothen(zz: ZigZag):
    """Add bounding-box corners so the zig-zag starts/ends on the rectangle.

    If `FIT_INTO_SQUARE` is True, the compass rectangle is padded to become a square.

    Args:
        zz: A ZigZag to modify in place.
    """
    additional_corner_length = 0.5

    N = zz.bounding_box("N") + additional_corner_length * 1j
    S = zz.bounding_box("S") - additional_corner_length * 1j
    W = zz.bounding_box("W") - additional_corner_length
    E = zz.bounding_box("E") + additional_corner_length

    if FIT_INTO_SQUARE:
        w, h = E.real - W.real, N.imag - S.imag
        if h < w:
            N += (w - h) * 0.5j
            S -= (w - h) * 0.5j
        elif h > w:
            W -= (h - w) * 0.5
            E += (h - w) * 0.5

    if zz.NW != N + W:
        zz.add_line(connect(N + W, zz.NW, "S"))
    if zz.SW != S + W:
        zz.add_line(connect(S + W, zz.SW, "N"))
    if zz.SE != S + E:
        zz.add_line(connect(zz.SE, S + E, "S"))
    if zz.NE != N + E:
        zz.add_line(connect(zz.NE, N + E, "N"))

    zz.set_compass(NW=N + W, SW=S + W, SE=S + E, NE=N + E)
    zz.smoothen()


def draw(expr, translate: complex = 0j):
    """Quick polyline drawing of an algebraic tangle.

    Heavy imports are local to keep module import time low.

    Args:
        expr: Tangle expression (int | TangleExpr).
        translate: Complex offset applied to all points before plotting.
    """
    import matplotlib.pyplot as plt  # local import

    z = to_zigzag(expr)
    add_corners_and_smoothen(z)

    for line in z.lines:
        x_values = [pt.real + translate.real for pt in line]
        y_values = [pt.imag + translate.imag for pt in line]
        plt.plot(x_values, y_values, lw=LINE_WIDTH, color=STRAND_COLOR)

    plt.grid(SHOW_GRID)
    plt.axis("on" if SHOW_AXIS else "off")
    plt.gca().set_aspect("equal", adjustable="box")


def are_continuation(a: list[complex], b: list[complex], radius: float) -> bool:
    """Heuristic test if polyline `b` is a continuation of polyline `a`.

    Args:
        a: First polyline points.
        b: Second polyline points.
        radius: Unused but kept for compatibility.

    Return:
        bool: True if endpoints are close in one of four adjacency checks.
    """
    d = 0.9
    x, y, z = a[1], a[0], b[0]
    if abs(z - y) < d:
        return True
    x, y, z = a[-2], a[-1], b[0]
    if abs(z - y) < d:
        return True
    x, y, z = a[1], a[0], b[-1]
    if abs(z - y) < d:
        return True
    x, y, z = a[-2], a[-1], b[-1]
    if abs(z - y) < d:
        return True
    return False


def draw_smooth(expr):
    """Smooth B-spline rendering of an algebraic tangle.

    Uses SciPy BSplines and NumPy for sampling. Imports are done locally to
    keep the library import fast when drawing is not used.

    Args:
        expr: Tangle expression (int | TangleExpr).
    """
    import matplotlib.pyplot as plt  # local import
    import numpy as np  # local import
    from scipy.interpolate import BSpline  # local import

    degree = 2  # spline degree (2 or 3 recommended)
    N = 10  # interpolation density factor

    z = to_zigzag(expr)
    add_corners_and_smoothen(z)

    already: list[tuple[list[complex], int]] = []
    current_color = -1

    for line in z.lines:
        k = 1 if len(line) == 2 else (2 if len(line) == 3 else degree)
        control_points = np.array(line)
        length = np.sum(np.abs(np.diff(control_points)))

        x = np.real(control_points)
        y = np.imag(control_points)

        n = len(control_points)
        t = np.concatenate(([0] * k, np.linspace(0, 1, n - k + 1), [1] * k))
        t_fine = np.linspace(0, 1, max(int(length * N), 2))

        spline_x = BSpline(t, x, k)(t_fine)
        spline_y = BSpline(t, y, k)(t_fine)

        radius = 1.5
        found_color = False
        for other, color in already:
            if are_continuation(line, other, radius):
                current_color = color
                found_color = True
                break
        if not found_color:
            current_color += 1
            already.append((line, current_color))

        plt.plot(spline_x, spline_y, linewidth=LINE_WIDTH, color=STRAND_COLOR)

    if ENDPOINT_SIZE > 0:
        endpoints = np.array([z.NW, z.SW, z.SE, z.NE])
        x = np.real(endpoints)
        y = np.imag(endpoints)
        plt.scatter(x, y, color=EP_COLOR, marker="o", s=ENDPOINT_SIZE, zorder=10)

    plt.grid(SHOW_GRID)
    plt.axis("on" if SHOW_AXIS else "off")
    plt.gca().set_aspect("equal", adjustable="box")


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Example:
    # tangle = (integral(-3) * 0) + (integral(5) * 0) + integral(6)
    # or a very simple product
    tangle = TangleProduct(0, 0)

    draw_smooth(-1)
    plt.savefig("tangle.svg", format="svg", bbox_inches="tight", pad_inches=0)
    plt.show()