Tutorial
========

Step-by-step tutorial introducing KnotPy, from installation to
constructing knots, links, and computing invariants.

Basic operations
----------------

Create the (unoriented) trefoil knot and compute the Jones polynomial.

.. code:: ipython2

    import knotpy as kp
    from knotpy import from_pd_notation, from_knotpy_notation
    
    K = kp.knot("3_1")
    kp.jones(K)




.. math::

    \displaystyle - t^{4} + t^{3} + t



.. code:: ipython2

    kp.is_knot(K)




.. parsed-literal::

    True



.. code:: ipython2

    A = kp.knot("3_1")
    B = kp.knot("4_1")
    AB = kp.connected_sum(A, B)
    kp.is_connected_sum(AB)




.. parsed-literal::

    True



.. code:: ipython2

    A_, B_ = kp.connected_sum_decomposition(AB)
    kp.identify(A_), kp.identify(B_)




.. parsed-literal::

    ('3_1', '4_1')



.. code:: ipython2

    D = kp.disjoint_union(A, B)
    kp.is_disjoint_union(D)




.. parsed-literal::

    True



.. code:: ipython2

    A_, B_ = kp.disjoint_union_decomposition(D)
    kp.identify(A_), kp.identify(B_)




.. parsed-literal::

    ('3_1', '4_1')



.. code:: ipython2

    K = kp.knot("trefoil")
    K.name




.. parsed-literal::

    '3_1'



.. code:: ipython2

    K = kp.knot("miller institute knot")
    K.name




.. parsed-literal::

    '6_2'



.. code:: ipython2

    K = kp.knot("unknot")
    K.name




.. parsed-literal::

    '0_1'



.. code:: ipython2

    K = kp.knot("+3_1")
    K.is_oriented()




.. parsed-literal::

    True



.. code:: ipython2

    K_ = kp.knot("-3_1")
    kp.identify(kp.knot("-3_1"))




.. parsed-literal::

    '+3_1'



.. code:: ipython2

    K = kp.knot("3_1")
    print("Knot:", K.name)
    print("Jones polynomial:", kp.jones(K))
    print("Alexander polynomial:", kp.alexander(K))
    print("Bracket polynomial:", kp.bracket(K, normalize=True))
    print("HOMFLYPT polynomial:", kp.homflypt(K))
    print("HOMFLYPT polynomial (az):", kp.homflypt(K, variables="az"))
    print("HOMFLYPT polynomial (lm):", kp.homflypt(K, variables="lm"))
    print("HOMFLYPT polynomial (xyz):", kp.homflypt(K, variables="xyz"))
    print("Kauffman 2-variable polynomial:", kp.kauffman(K))



.. parsed-literal::

    Knot: 3_1
    Jones polynomial: -t**4 + t**3 + t
    Alexander polynomial: t**2 - t + 1
    Bracket polynomial: A**(-4) + A**(-12) - 1/A**16
    HOMFLYPT polynomial: -v**4 + v**2*z**2 + 2*v**2
    HOMFLYPT polynomial (az): z**2/a**2 + 2/a**2 - 1/a**4
    HOMFLYPT polynomial (lm): m**2/l**2 - 2/l**2 - 1/l**4
    HOMFLYPT polynomial (xyz): -2*y/x - y**2/x**2 + z**2/x**2
    Kauffman 2-variable polynomial: a**5*z + a**4*z**2 - a**4 + a**3*z + a**2*z**2 - 2*a**2


.. code:: ipython2

    K = kp.knot("+3_1")
    G = kp.fundamental_group(K)
    G.generators, G.relators




.. parsed-literal::

    ((x0, x1, x2), [x0*x1*x2**-1*x1**-1, x2*x0*x1**-1*x0**-1, x1*x2*x0**-1*x2**-1])



.. code:: ipython2

    K = kp.from_pd_notation("[[1,5,2,4],[3,1,4,6],[5,3,6,2]]")
    kp.identify(K)




.. parsed-literal::

    '3_1'



.. code:: ipython2

    K = kp.from_pd_notation("PD[X[1,9,2,8], X[3,10,4,11], X[5,3,6,2],X[7,1,8,12], X[9,4,10,5], X[11,7,12,6]]")
    kp.identify(K)




.. parsed-literal::

    '6_2'



.. code:: ipython2

    kp.to_pd_notation(kp.knot("3_1"))




.. parsed-literal::

    'X[0,1,2,3],X[3,4,5,0],X[1,5,4,2]'



.. code:: ipython2

    # EM, CONDENSED EM,... PLANTRI

.. code:: ipython2

    K = kp.knot("3_1")
    kp.identify(kp.orient(K))




.. parsed-literal::

    '+3_1'



.. code:: ipython2

    [kp.identify(K) for K in kp.orientations(kp.knot("9_32"))]




.. parsed-literal::

    ['+9_32', '-9_32']



.. code:: ipython2

    K = kp.knot("3_1")
    kp.identify(kp.mirror(K))




.. parsed-literal::

    '3_1*'



.. code:: ipython2

    K = kp.knot("+9_32")
    kp.identify(kp.reverse(K))




.. parsed-literal::

    '-9_32'



.. code:: ipython2

    K = kp.knot("+9_32")
    K = kp.mirror(kp.reverse(K))
    kp.identify(K)


