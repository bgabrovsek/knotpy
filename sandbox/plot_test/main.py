# examples of ugly plots

import knotpy as kp

# some knots in condensed EM notation
#EM notation: each crossing has half-arcs 0,1,2,3 from it (counterclockwise).
# "h3c0g3b2" means that:
# - arc 0 of crossing "a" is connected to arc 3 of crossing "h",
# - arc 1 of crossing "a" is connected to arc 0 of crossing "c",
# - arc 2 of crossing "a" is connected to arc 3 of crossing "g"
# - arc 3 of crossing "a" is connected to arc 2 of crossing "b"
# see emcode.png for very similar notation
knot1_cem = [
    "h3c0g3b2,g1h0a3g2,a1h2l1i0,l3i2j1j0,j3j2k1k0,k3k2i1l0,i3b0b3a2,b1l2c1a0,c3f2d1g0,d3d2e1e0,e3e2f1f0,f3c2h1d0",
    "g1g0f3f2,f1f0e3e2,e1h0h3g2,h1i0i3h2,i1c0b3b2,b1b0a3a2,a1a0c3i2,c1d0d3c2,d1e0g3d2",
    "h1c2g1d0,g3f2f1g0,f3g2a1h0,a3f0i1e2,i3h2d3i0,d1b2b1c0,b3a2c1b0,c3a0e1i2,e3d2h3e0",
    "c3d0b3e2,d3h0j3a2,f3d2d1a0,a1c2c1b0,k3g0a3j2,g3g2h1c0,e1k2f1f0,b1f2i1i0,h3h2k1j0,i3k0e3b2,j1i2g1e0",
    "b1k0c3d2,k1a0j3k2,j1e0i3a2,e1j0a3i2,c1d0g3f2,h1i0e3h2,i1h0h3e2,g1f0f3g2,f1g0d3c2,d1c0k3b2,a1b0b3j2",
    "b1k0c3d2,k1a0i3k2,j1e0g3a2,e1j0a3g2,c1d0f3f2,g1g0e3e2,f1f0d3c2,i1i0j3j2,h1h0k3b2,d1c0h3h2,a1b0b3i2",
    "g3c0f3b2,f1g0a3f2,a1i0k1h2,k3j2j1k0,j3i2h3j0,h1b0b3a2,b1l2l1a0,l3f0c3e2,c1l0e1k2,e3d2d1e0,d3c2i3d0,i1g2g1h0",
    "g1c0h1b2,h3g2a3h0,a1i0l3h2,l1j0j3i2,j1k0k3j2,k1l0i3k2,i1a0b1l2,b3a2c3b0,c1g0d3f2,d1e0e3d2,e1f0f3e2,f1d0g3c2",
    "i3c0g3b2,g1h0a3g2,a1i2l1j0,l3k2k1l0,k3j2j1k0,j3i0h3h2,h1b0b3a2,b1g0f3f2,f1l2c1a0,c3e2e1f0,e3d2d1e0,d3c2i1d0",
    "i1d0d3c2,d1e0g1d2,g3f2a3g0,a1b0b3a2,b1i0j3h2,j1l0c1k2,c3b2k3c0,k1k0e3j2,e1a0l3l2,l1f0h3e2,h1h0f3g2,f1j0i3i2",
    "i1d0g1c2,g3e2j3f0,j1l0a3k2,a1h0h3g2,h1i0b1h2,b3j2k1k0,k3a2d3b0,d1e0e3d2,e1a0l3l2,l1c0f1b2,f3f2c3g0,c1j0i3i2",
    "e3b0b3m2,a1c0c3a2,b1d0f3b2,c1e2e1f0,h1d2d1a0,d3g0i1c2,f1h0h3l2,g1e0m1g2,m3f2l1j0,i3k2k1m0,l3j2j1l0,k3i2g3k0,j3h2a3i0",
    "b1b0c1c0,a1a0d3e0,a3a2e3f0,g3h0h3b2,b3h2i0c2,c3j3k1k0,k3k2l0d0,d1l3e1d2,e2m0j1j0,i3i2n1f1,f3f2g1g0,g2n0m1h1,i1l2n3n2,l1j2m3m2",
    "b3c0c3b0,a3d0e3a0,a1f0g1a2,b1g0f1h0,i1i0j1b2,c1d2g3g2,d1c2f3f2,d3j0k1k0,e1e0k3j2,h1e2i3k2,h3h2j3i2",]

# some knots in condensed PD notation
knot2_pd = ["abcd baef dcgh eijk flmg ihnj kopl mqrn orqp",
            "abcd baef dcgh ijke flmn nopg hqji lkqr omrp",
            "abcd defa bghc eijf gklh ilmn jopk nmqr orqp",
            "abcd defa bghc eijk gfkl ihmn ojpq lors srtm ntqp",
            "abcd defa bghc eijk flmg ihnj kopl mqrs srtn otqp",
            "abcd baef dcgh feij hgkl imno jpqk lrsm ontu puvq rwxs txwv",
            "abcd defa bghc eijk gflm ihnj kopq mlqr rstn otsp",
            "abcd baef dcgh iejk film mnog hpkj qrsl ntuo puvq rvts",
            "abcd defa bghc eijf gklm hmno onpi qjrs kqtl uvwp srxy tzAu vAzB xwBy",
            "abcd defa bghc ijke flmg hnoi jpqr sktu lsuv nmpo rqvt",
            "abcd defa bghc eijk gflm ihno kjpq qrsl mton tuvp rvus",
            "abcd baef dcgh ijke flmn nopg hqji rkst lruv omvu qpts"
            ]

# theta curves with two 3-valent vertices in PD notation
theta1_pd = ["V[0,1,2],V[3,1,4],X[5,6,7,8],X[2,9,8,10],X[6,11,12,13],X[13,12,4,14],X[14,0,10,7],X[9,3,11,5]",
             "V[0,1,2],V[3,4,5],X[6,2,7,4],X[8,9,10,11],X[3,12,8,6],X[9,13,14,10],X[13,12,15,14],X[15,16,17,18],X[18,17,0,11],X[1,16,5,7]",
             "V[7,8,20],V[9,20,8],X[12,5,11,10],X[10,14,13,12],X[16,15,18,17],X[19,16,0,13],X[15,19,14,11],X[7,18,5,6],X[6,0,17,9]",
             "V[12,9,27],V[27,9,8],X[25,6,16,26],X[31,35,34,28],X[26,34,35,25],X[28,19,18,31],X[8,17,6,18],X[17,12,19,16]"]

# knotted graphs, with four 3-valent vertices on the outer region in condensed PD notation
graph1_pd = ["abc cde elm amz bfgd hklg jhfi rpnj istr vuot szuv pokn",
             "agb bvc ade dcu fihg ekjf izmh klzj ontm lspr rpno suvt"]

# convert to PlanarDiagram instances
knots1 = [kp.from_condensed_em_notation(s) for s in knot1_cem]
knots2 = [kp.from_condensed_pd_notation(s) for s in knot2_pd]
thetas = [kp.from_pd_notation(s) for s in theta1_pd]
graphs = [kp.from_condensed_pd_notation(s) for s in graph1_pd]

# plot
kp.export_pdf(knots1, "plot/knots_example_1.pdf", draw_circles=True)
kp.export_pdf(knots2, "plot/knots_example_2.pdf", draw_circles=True)
kp.export_pdf(thetas, "plot/thetas_example_1.pdf", draw_circles=True)

# CONTROLLING THE OUTER REGION

for g in graphs:
    # set the endpoint of a face to "outer -> true" if all the nodes on the face are vertices (and not crossings)
    for f in g.faces:
        if all(type(g.nodes[endpoint.node]) is kp.Vertex for endpoint in f):
            for endpoint in f:
                endpoint.attr["outer"] = True

kp.export_pdf(graphs, "plot/graph_example_1.pdf", draw_circles=True)
