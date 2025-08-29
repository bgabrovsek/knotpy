Notation (knot, links, and knotted graphs encoding via EM and PD codes)
===========================================

Description of two key diagram encodings that KnotPy supports natively for knots, links, and spatial graphs:
- **EM code** (Ewing–Millett code) [1]
- **PD code** (Planar Diagram code) [2]

Both encodings are supported by KnotPy, though the internal representation is structured most closely to EM codes.---


Definitions and Examples
------------------------

###  EM Code

The **Ewing–Millett (EM) code** denotes how arcs connect at each crossing using adjacency lists:

- Represented as a dictionary where each node’s value is a list of tuples in CCW order: `(adjacent_node, position)`.
- Condensed string format example:
  A graph `C / A—B—D` yields:


References
----------

.. [1] B. Ewing and K. C. Millett. `*A load balanced algorithm for the calculation of the polynomial knot and link invariants* <https://www.worldscientific.com/doi/10.1142/9789814503457_0017>`_ (1991). In: The Mathematical Heritage of C. F. Gauss.

.. [2] M. Mastin. `*Links and Planar Diagram Codes* <https://www.worldscientific.com/doi/abs/10.1142/S0218216515500169>`_ (2015). J. Knot Theory Ramifications.