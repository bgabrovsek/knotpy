Notation
===========================================

Description of two key diagram encodings that KnotPy supports natively for knots, links, and spatial graphs:
- **EM code** (Ewing–Millett code) [1]
- **PD code** (Planar Diagram code) [2]

Both encodings are supported by KnotPy, though the internal representation is structured most closely to EM codes.---


Definitions and Examples
------------------------

###  EM Code

Ewing–Millett (EM) encoding — informal specification
----------------------------------------------------

1. **Crossings.** Enumerate every crossing by any hashable, totally ordered key
   (commonly letters `a, b, c, …`, but any comparable objects are fine).

2. **Half-arcs.** At each crossing `x`, index the four incident half-arcs by
   integers `0, 1, 2, 3` in counterclockwise order, with the **undercrossing**
   half-arcs assigned the **even** indices (`0` and `2`).

3. **Endpoints.** An **endpoint** is a pair `(x, i)` where `x` is a crossing and
   `i ∈ {0,1,2,3}` is a half-arc index. Thus crossing `a` is incident to
   `(a, 0), (a, 1), (a, 2), (a, 3)`.

4. **Local connection data (the EM record).** For each crossing `x`, record an
   ordered 4-tuple of endpoints giving, in order, where `(x, 0), (x, 1),
   (x, 2), (x, 3)` continue to (i.e., which endpoints they connect to along
   the same arc).

   Example mapping (your data, normalized):

   - `a → ((b, 3), (b, 2), (c, 3), (c, 2))`
   - `b → ((d, 3), (e, 0), (a, 1), (a, 0))`
   - `c → ((e, 3), (d, 0), (a, 3), (a, 2))`
   - `d → ((c, 1), (e, 2), (e, 1), (b, 0))`
   - `e → ((b, 1), (d, 2), (d, 1), (c, 0))`

5. **Arcs.** An (unoriented) **arc** is the unordered pair of endpoints that
   are connected. For the example above, the arcs are:

   `{(a, 0), (b, 3)}, {(a, 1), (b, 2)}, {(a, 2), (c, 3)}, {(a, 3), (c, 2)},`
   `{(b, 0), (d, 3)}, {(b, 1), (e, 0)}, {(c, 0), (e, 3)}, {(c, 1), (d, 0)},`
   `{(d, 1), (e, 2)}, {(d, 2), (e, 1)}`


References
----------

.. [1] B. Ewing and K. C. Millett. `*A load balanced algorithm for the calculation of the polynomial knot and link invariants* <https://www.worldscientific.com/doi/10.1142/9789814503457_0017>`_ (1991). In: The Mathematical Heritage of C. F. Gauss.

.. [2] M. Mastin. `*Links and Planar Diagram Codes* <https://www.worldscientific.com/doi/abs/10.1142/S0218216515500169>`_ (2015). J. Knot Theory Ramifications.