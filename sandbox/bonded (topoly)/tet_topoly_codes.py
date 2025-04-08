from topoly_codes import PD
import knotpy as kp
from itertools import chain, combinations
from copy import deepcopy

links = [
    'X[0,1,2,3];X[1,4,5,2];X[4,0,3,5]',
    'V[0,6];X[0,1,2,3];X[1,4,5,2];X[4,6,3,5]',
    'V[0,8];X[0,1,2,3];X[1,4,5,2];X[4,6,3,5];X[6,8,7,7]',
    'V[0,6];X[0,1,2,3];X[8,4,5,2];X[1,7,7,8];X[4,6,3,5]',
    'X[1,7,7,8];X[0,1,2,3];X[8,4,5,2];X[4,0,3,5]',
    'X[6,1,7,2];X[12,8,9,7];X[4,12,1,11];X[10,5,11,6];X[8,4,5,3];X[2,9,3,10]',
    'V[1,13];V[14,5];V[15,9];X[6,1,7,2];X[12,8,15,7];X[4,12,13,11];X[10,5,11,6];X[8,4,14,3];X[2,9,3,10]',
    'X[6,1,7,2];X[12,8,9,7];X[4,12,1,11];X[10,5,11,6];X[8,4,5,3];X[2,9,3,10];X[14,14,13,13]',
    'V[0,1,2];V[0,3,4];X[1,4,6,5];X[5,6,7,2];X[11,10,9,8];X[8,7,12,11];X[9,10,14,13];X[14,12,16,15];X[15,16,3,13]',
    'V[0,1,2];V[3,4,5];X[9,8,7,6];X[6,2,10,9];X[12,11,4,13];X[3,7,8,13];X[11,14,0,5];X[10,1,14,12]',
    'V[0,0,1];V[2,3,4];X[3,2,6,5];X[6,1,4,5]',
    'V[0,0,1];V[2,2,4];X[3,3,6,5];X[6,1,4,5]',
    'V[0,2,1];V[4,7,8];V[6,11,7];V[9,11,10];X[3,0,1,2];X[4,5,6,3];X[8,9,10,5]',
    'V[0,3,4];V[1,5,2];V[4,6,7];V[5,7,6];X[3,0,1,2]',
    'V[0,3,4];V[1,5,2];V[4,6,7];V[5,7,6];X[3,0,1,2];X[8,9,10,11];X[9,12,13,10];X[12,8,11,13]'
]
# TODO add tests for tangles
tangles = []

for n in links:
    #print(n)

    k = kp.from_pd_notation(n)

    if kp.check_faces_sanity(k) and  kp.sanity_check(k):
        continue


    for f in faces:

   #
   # # loop through all subsets of degree 3 nodes of length > 0
   #  nodes3 = [node for node in k.nodes if k.degree(node) == 3]
   #  has_sane_candidate = False
   #  L = None
   #
   #  for nodes in chain(*(combinations(nodes3, i) for i in range(1, len(nodes3) + 1))):
   #      L = deepcopy(k)
   #      for node in nodes:
   #          kp.permute_node(L, node, list(range(len(L.nodes[node]) - 1, -1, -1)))
   #      if kp.sanity_check(k):
   #          pass
   #
   #      if kp.check_faces_sanity(k):
   #          has_sane_candidate = True
   #          print("good:",k)
   #          break
   #
   #  if has_sane_candidate:
   #      print( + " converted to \"" + str(L) + "\"")
   #
   #  else:
   #      print("Unable to convert" +  "(\"" + kp.to_pd_notation(L) + "\")")
   #
   #  print()
