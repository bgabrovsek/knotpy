import knotpy as kp
from knotpy.algorithms.topology import edges
import knotpy.algorithms.topology
from knotpy import export_pdf

pd_in = "V[1,2,3],V[8,11,9],V[10,12,11],V[12,13,14],X[8,2,13,10],X[4,5,6,1],X[5,4,3,7],X[14,6,7,9]"
k = kp.from_pd_notation(pd_in)

print(knotpy.algorithms.topology.edges.edges(k))
print(list(kp.algorithms.components_link.link_components_endpoints(k)))
print(kp.number_of_link_components(k))

c = kp.canonical(k)
p = kp.to_pd_notation(c)
q = kp.from_pd_notation(p)
Q = kp.canonical(q)

export_pdf([k,c,q,Q],"aa.pdf")
exit()

pd_in = "V[1,2,3],V[8,11,9],V[10,12,11],V[12,13,14],X[8,2,13,10],X[4,5,6,1],X[5,4,3,7],X[14,6,7,9]"
k = kp.from_pd_notation(pd_in)
k = kp.canonical(k)
pd_out = kp.to_pd_notation(k)
print("pd original:\n", pd_in, "\npd after canonical():\n", pd_out)

k_original = kp.from_pd_notation("V[1,2,3],V[8,11,9],V[10,12,11],V[12,13,14],X[8,2,13,10],X[4,5,6,1],X[5,4,3,7],X[14,6,7,9]")
k_canonical = kp.canonical(k_original)

pd_out_again = kp.from_pd_notation(pd_out)
pd_out_again = kp.canonical(pd_out_again)
print(pd_out_again== k)

export_pdf([k, pd_out_again,k, pd_out_again,k, pd_out_again,k, pd_out_again,k, pd_out_again,k, pd_out_again], "xxx.pdf")

number_of_loops = sum(edge[0].node == edge[-1].node for edge in knotpy.algorithms.topology.edges.edges(k))
if number_of_loops % 2 == 1:
    print("diagram not ok.")

print(knotpy.algorithms.topology.edges.edges(k))


exit()
plantri_code = "5 bccd,adee,aaed,aceb,bbdc"
k = kp.from_plantri_notation(plantri_code)

print(k)
exit()

k_pl = kp.to_plantri_notation(k)
k_pd = kp.to_pd_notation(k)
print("Original:", plantri_code)
print("EM", k)
print("Plantri:",k_pl)
print("PD:", k_pd)

c = kp.canonical(k)
c_pl = kp.to_plantri_notation(c)
c_pd = kp.to_pd_notation(c)

print()

print("Canonical EM:", c)
print("Canonical plantri:", c_pl)
print("Canonical PD:", c_pd)

k_ = kp.from_pd_notation(c_pd)
print("Back to PD", k_)

k_ = kp.from_plantri_notation(c_pl)
print("Back to plantri:", c_pl)


exit()


k = kp.canonical(k)
canonical_code = kp.to_plantri_notation(k)
pd_code_graph = kp.to_pd_notation(k)
print("ORIGINAL:", plantri_code, "\nCANONICAL:", canonical_code, "\nPD:",pd_code_graph)

k = kp.from_plantri_notation(canonical_code)