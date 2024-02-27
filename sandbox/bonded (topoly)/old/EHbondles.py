# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 14:24:14 2023

@author: BerdajsEv
"""

# from sympy import *

from SNracks import *
from pprint import pprint


####################################################
# By Eva Horvat
#
####################################################

#######################
# Bondle structures
#######################

#######################
### Quandles ###
#######################

def mtranspose(M):
    ### transpose matrix###
    out = []
    for i in range(1, len(M[0]) + 1):
        r = []
        for j in range(1, len(M) + 1):
            r.append(M[j - 1][i - 1])
        out = out + [r]
    return out


# M = [[1, 1, 1], [3, 2, 2], [2, 3, 3]]
# M = [[1, 3, 2], [3, 2, 1], [2, 1, 3]]
# pprint(M)
# Mt = mtranspose(M)
# pprint(Mt)


def inverseq(M):
    ### Compute the matrix for the inverse quandle operation ###
    M = mtranspose(M)
    iM = []
    for i in range(1, len(M) + 1):
        c = []
        for j in range(1, len(M) + 1):
            c.append(M[i - 1].index(j) + 1)
        iM = iM + [c]
    return mtranspose(iM)

#
# Mi = inverseq(M)
# pprint(Mi)


def trivial(n):
    ### The trivial quandle on the set {1,2,...,n} ###
    Q = []
    for i in range(1, n + 1):
        q = []
        for j in range(1, n + 1):
            q.append(i)
        Q = Q + [q]
    return (tm(Q))

#
# print(trivial(4))


def racklist(N):
    ### find all racks matching pattern ###
    L = []
    L.append(tm(N))
    out = []
    while len(L)>0:
       M = L[0]
       L[0:1] = []
       q = findzero(M)
       if q:
           for i in pavail(getcolumn(M,q[1])):
               M2 = lm(M)
               M2[q[0]-1][q[1]-1] = i
               M3 = sdfill(M2)
               if M3:
                    col = True
                    for j in range(1,len(M)+1):
                        if not reptest(getcolumn(M3,j)):
                            col = False
                    if col:  L.append(tm(M3))
       else:
           out.append(tuple(M))
    return out
def quandles(n):
    ### Find all nontrivial quandles on the set {1,2,...,n} ###
    Q = []
    for i in range(1, n + 1):
        q = []
        for j in range(1, n + 1):
            if j == i:
                q.append(j)
            else:
                q.append(0)
        Q = Q + [q]
    qua = racklist(Q)
    qua.remove(trivial(n))
    return (qua)

#
# print("qundles")
# q = quandles(3)
# pprint(q)


def redlist(L):
    ### Remove isomorphic copies from a list of quandles ###
    C = []
    for i in range(1, len(L) + 1):
        for j in range(i + 1, len(L) + 1):
            hom = homlist(L[i - 1], L[j - 1])
            for h in hom:
                if reptest(h):
                    C.append(L[j - 1])
                    break
    for l in C:
        if l in L:
            L.remove(l)
    return (L)

#
# print("reduce")
# rq = redlist(q)
# pprint(rq)


def retest(p):
    ### Test whether p has no repeated entries ###
    q = True
    L = []
    for i in range(1, len(p) + 1):
        if p[i - 1] in L:
            q = False
        else:
            L.append(p[i - 1])
    return q


def autlist(M):
    ### List of quandle automorphisms M --> M ###
    l = homlist(M, M)
    for p in l:
        if retest(p) == False:
            l.remove(p)
    return l

#
# for w in rq:
#     print(":", autlist(w))




#######################
### Bondles ###
#######################


def bondletest(M, l):
    ### Test whether a list l of automorphisms defines a bondle  ###
    ### structure on a quandle M ###
    iM = inverseq(M)
    aut = autlist(M)
    test = True
    for i in range(1, len(M) + 1):
        for j in range(1, len(M) + 1):
            if M[iM[i - 1][j - 1] - 1][aut[l[i - 1] - 1][j - 1] - 1] != i:
                test = False
                break
        if test == False:
            break
        for k in range(1, len(M) + 1):
            if aut[l[M[i - 1][j - 1] - 1] - 1][M[k - 1][j - 1] - 1] != M[aut[l[i - 1] - 1][k - 1] - 1][j - 1]:
                test = False
                break
            if M[M[k - 1][aut[l[i - 1] - 1][j - 1] - 1] - 1][aut[l[j - 1] - 1][M[i - 1][j - 1] - 1] - 1] != \
                    M[M[k - 1][i - 1] - 1][j - 1]:
                test = False
                break
            if M[iM[k - 1][j - 1] - 1][aut[l[i - 1] - 1][j - 1] - 1] != M[iM[k - 1][aut[l[j - 1] - 1][i - 1] - 1] - 1][
                i - 1]:
                test = False
                break
        if test == False:
            break
    return test


def nixt(l, d):
    ### find the next element in the lexicographic sequence of tuples ###
    if l[-1] != d:
        l = l[:-1] + [l[-1] + 1]
    else:
        l = nixt(l[:-1], d) + [1]
    if l is not None:
        return l


def bondlestr(M):
    ### Find all bondle structures on M ###
    aut = autlist(M)
    st = []
    ind = []
    m = []
    for i in range(1, len(M) + 1):
        ind.append(1)
        m.append(len(aut))
    while ind != m:
        if bondletest(M, ind):
            st = st + [ind]
        ind = nixt(ind, len(aut))
    if bondletest(M, m):
        st = st + [m]
    return (st)


def btable(M, l):
    ### Multiplication tables for three bondle operations on M ###
    aut = autlist(M)
    T = []
    if bondletest(M, l):
        R1 = []
        R2 = []
        R3 = []
        for i in range(1, len(M) + 1):
            a = []
            b = []
            c = []
            for j in range(1, len(M) + 1):
                a = a + [aut[l[i - 1] - 1][j - 1]]
                b = b + [aut[l[j - 1] - 1][M[i - 1][j - 1] - 1]]
                c = c + [aut[l[j - 1] - 1][i - 1]]
            R1 = R1 + [a]
            R2 = R2 + [b]
            R3 = R3 + [c]
        T = [R1, R2, R3]
    return T


def isobondle(M, l, N, t):
    ### Test whether the bondles (Eva) (M,l) and (N,t) are isomorphic ###
    hom = homlist(M, N)
    aM = autlist(M)
    aN = autlist(N)
    L = []
    for k in range(1, len(hom) + 1):
        h = hom[k - 1]
        if retest(h):
            v = True
            for i in range(1, len(M) + 1):
                for j in range(1, len(M) + 1):
                    if h[aM[l[i - 1] - 1][j - 1] - 1] != aN[t[h[i - 1] - 1] - 1][h[j - 1] - 1]:
                        v = False
                        break
                if v == False:
                    break
            if v:
                L.append(h)
    return (len(L) > 0)


def redbondlestr(M):
    ### Find all nonisomorphic bondle structures on a quandle M ###
    L = bondlestr(M)
    C = []
    for i in range(1, len(L) + 1):
        for j in range(i + 1, len(L) + 1):
            if isobondle(M, L[i - 1], M, L[j - 1]):
                C.append(L[j - 1])
    for l in C:
        if l in L:
            L.remove(l)
    return (L)


def bondles(n):
    ### Find nonisomorphic bondle structures on the set {1,2,...n} ###
    L = []
    qua = redlist(quandles(n))
    for q in qua:
        for b in redbondlestr(q):
            v = True
            for s in L:
                if isobondle(q, b, s[0], s[1]):
                    v = False
                    break
            if v:
                r = [q] + [b]
                L.append(r)
    return (L)
#
#
# print("bonds")
# print(1)
# b = bondles (Eva)(1)
# for x in b:
#     print(x)
#
# print(2)
# b = bondles (Eva)(2)
# for x in b:
#     print(x)
#
# print(3)
# b = bondles (Eva)(3)
# for x in b:
#     print(x)
#
# print("---")

#################################################################
###  Counting colorings of planar diagrams (knots with bonds) ###
#################################################################

def bdiagram(PD):  ### Translates a PD diagram of a theta curve ###
    ### A planar diagram PD consists of lists of length 5 in CCW orientation,
    ### corresponding to crossings, where the first entry corresponds to the
    ### crossing sign (1-positive, -1-negative) and the remaining entries
    ### correspond to the arcs, starting with the inbound lower arc),
    ### and lists of length 3 in CCW orientation, corresponding to vertices.
    ### We rearrange the vertex lists so that each one begins with the bond
    ### arc and has an additional information about parallel/antiparallel
    ### strands (the first entry is either -2 for parallel or -3 for antiparallel)
    Xi = []
    Xo = []
    X = []
    V = []
    W = []
    for P in PD:
        if len(P) == 5:
            X = X + [P]
            if P[1] not in Xi:
                Xi = Xi + [P[1]]
            if P[3] not in Xo:
                Xo = Xo + [P[3]]
            for i in range(3, 6, 2):
                if (i == 3 and P[0] == 1 and P[2] not in Xo) or (i == 5 and P[0] == -1 and P[4] not in Xo):
                    Xo = Xo + [P[i - 1]]
                elif P[i - 1] not in Xi:
                    Xi = Xi + [P[i - 1]]
        if len(P) == 3:
            if P[1] not in Xi and P[1] not in Xo:
                P1 = [P[1]] + [P[2]] + [P[0]]
                V = V + [P1]
            elif P[2] not in Xi and P[2] not in Xo:
                P2 = [P[2]] + [P[0]] + [P[1]]
                V = V + [P2]
            else:
                V = V + [P]
    for i in range(1, len(V) + 1):
        for j in range(i + 1, len(V) + 1):
            if V[i - 1][0] == V[j - 1][0]:
                if (V[i - 1][1] in Xi and V[j - 1][1] in Xi):
                    W.append([-3] + [V[i - 1][2]] + [V[i - 1][1]] + [V[j - 1][2]] + [V[j - 1][1]])
                elif (V[i - 1][1] in Xo and V[j - 1][1] in Xo):
                    W.append([-3] + V[i - 1][1:] + V[j - 1][1:])
                elif (V[i - 1][1] in Xi):
                    W.append([-2] + V[j - 1][1:] + V[i - 1][1:])
                else:
                    W.append([-2] + V[i - 1][1:] + V[j - 1][1:])
    return (X + W)


def hfindzero(f):
    ### find zero in homomorphism template ###
    j = -1
    for i in range(0, len(f)):
        if f[i] == 0:
            j = i + 1
            break
    if j < 0:
        out = False
    else:
        out = j
    return out


def pdhomlist(PD, N, l):  # list bondle homomorphisms
    ### Lists homomorphisms from knot bondle of planar diagram ###
    z = []
    for i in range(1, 2 * len(PD) + 1):
        z = z + [0]
    L = [z]
    out = []
    while len(L) != 0:
        w = L[0]
        L[0:1] = []
        if w:
            i = hfindzero(w)
            if not i:
                out.append(w)
            else:
                for j in range(1, len(N) + 1):
                    phi = list(w)
                    phi[i - 1] = j
                    v = pdhomfill(PD, N, l, phi)
                    if v: L.append(tuple(v))
    return out


def pdhomfill(PD, N, l, phi):  # N is a quandle matrix, l is a bondle structure
    ### Fills in entries in a quandle homomorphism ###
    ### A planar diagram PD consists of lists of length 5 in CCW orientation.
    ### Some correspond to crossings, where the first entry defines the
    ### crossing sign (1-positive, -1-negative) and the remaining entries
    ### correspond to the arcs (starting with the inbound lower arc).
    ### Other lists correspond to singular points (contracted bonds),
    ### whose first entry defines the orientation of the (bonded) parallel
    ### strands (-2 for parallel, -3 for antiparallel), while the remaining CCW
    ### arcs are V[-2,x,R_{1}(x,y),R_{2}(x,y),y] or V[-3,x,R_{3}(x,y),y,R_{3}(y,x)]
    aut = autlist(N)
    f = phi
    c = True
    out = True
    while c == True:
        c = False
        for X in PD:
            if X[0] in (-1, 1):  ### crossing
                if f[X[2] - 1] == 0 and f[X[4] - 1] != 0:
                    f[X[2] - 1] = f[X[4] - 1]
                    c = True
                if f[X[4] - 1] == 0 and f[X[2] - 1] != 0:
                    f[X[4] - 1] = f[X[2] - 1]
                    c = True
                if f[X[4] - 1] != f[X[2] - 1] and (f[X[2] - 1] != 0 and f[X[4] - 1] != 0):
                    out = False
                if X[0] == 1:  ### positive crossing
                    if f[X[1] - 1] != 0 and f[X[4] - 1] != 0:
                        if f[X[3] - 1] == 0:
                            f[X[3] - 1] = N[f[X[1] - 1] - 1][f[X[4] - 1] - 1]
                            c = True
                        elif f[X[3] - 1] != N[f[X[1] - 1] - 1][f[X[4] - 1] - 1]:
                            out = False
                else:  ### negative crossing
                    if f[X[3] - 1] != 0 and f[X[4] - 1] != 0:
                        if f[X[1] - 1] == 0:
                            f[X[1] - 1] = N[f[X[3] - 1] - 1][f[X[4] - 1] - 1]
                            c = True
                        elif f[X[1] - 1] != N[f[X[3] - 1] - 1][f[X[4] - 1] - 1]:
                            out = False
            else:  ### bond
                if X[0] == -2:  ### parallel strands
                    if f[X[1] - 1] != 0 and f[X[4] - 1] != 0:
                        if f[X[2] - 1] == 0:
                            f[X[2] - 1] = aut[l[f[X[1] - 1] - 1] - 1][f[X[4] - 1] - 1]
                        elif f[X[2] - 1] != aut[l[f[X[1] - 1] - 1] - 1][f[X[4] - 1] - 1]:
                            out = False
                        if f[X[3] - 1] == 0:
                            f[X[3] - 1] = aut[l[f[X[4] - 1] - 1] - 1][N[f[X[1] - 1] - 1][f[X[4] - 1] - 1] - 1]
                        elif f[X[3] - 1] != aut[l[f[X[4] - 1] - 1] - 1][N[f[X[1] - 1] - 1][f[X[4] - 1] - 1] - 1]:
                            out = False
                else:  ### antiparallel strands
                    if f[X[1] - 1] != 0 and f[X[3] - 1] != 0:
                        if f[X[2] - 1] == 0:
                            f[X[2] - 1] = aut[l[f[X[4] - 1] - 1] - 1][f[X[1] - 1] - 1]
                        elif f[X[2] - 1] != aut[l[f[X[4] - 1] - 1] - 1][f[X[1] - 1] - 1]:
                            out = False
                        if f[X[4] - 1] == 0:
                            f[X[4] - 1] = aut[l[f[X[1] - 1] - 1] - 1][f[X[4] - 1] - 1]
                        elif f[X[4] - 1] != aut[l[f[X[1] - 1] - 1] - 1][f[X[4] - 1] - 1]:
                            out = False
    if out == True:
        return f
    else:
        return out

# from topoly_pd import *

PD_codes = [
#    [[1, 1, 6, 2, 5], [1, 7, 3, 8, 2], [1, 4, 1, 5, 8], [-3, 3, 4, 6, 7]],
#    [[-2,6,7,1,0], [-1,1,7,2,8], [-1,8,2,9,3],[-1,3,9,4,10],[-1,10,4,11,5],[-1,5,11,6,0]],
 #   [[-2,1,0,6,7,], [-1,1,7,2,8], [-1,8,2,9,3],[-1,3,9,4,10],[-1,10,4,11,5],[-1,5,11,6,0]],
 #   [[-3,10,2,1,11],[-1,5,11,6,0],[-1,0,6,1,7],[-1,7,2,8,3],[-1,3,8,4,9],[-1,9,4,10,5]],
   [[-3,0,4,3,1],[-1,7,1,8,2],[-1,2,8,3,9],[-1,9,4,10,5],[-1,5,10,6,11],[-1,11,6,0,7]],
    [[-3,  3, 1,0, 4], [-1, 7, 1, 8, 2], [-1, 2, 8, 3, 9], [-1, 9, 4, 10, 5], [-1, 5, 10, 6, 11], [-1, 11, 6, 0, 7]],
    #   [[-3, 3, 1,0, 4], [-1, 7, 1, 8, 2], [-1, 2, 8, 3, 9], [-1, 9, 4, 10, 5], [-1, 5, 10, 6, 11], [-1, 11, 6, 0, 7]]

]

for b in bondles(3):
    print("Bondle", b)
    for pd in PD_codes:
        #print("  PD:", pd)
        print("   HOM:", pdhomlist(pd, *b))

#     print("BONDLE", b)
#     N = 0
#     for tip in PD_types:
#         #print("\n", tip, "\n", "-"*18)
#         for theta_name in PD_types[tip]:
#             print(theta_name, end=" ")
#             text = PD[theta_name]
#             #print(pdhomlist(PD, *b))


#
# PD1 = [[1, 1, 6, 2, 5], [1, 7, 3, 8, 2], [1, 4, 1, 5, 8], [-3, 3, 4, 6, 7]]
# PD2 = ((1, 3, 2), (3, 2, 1), (2, 1, 3))
#
#
# print(pdhomlist(PD1, ((1, 3, 2), (3, 2, 1), (2, 1, 3)), [1, 1, 1]))
# print(pdhomlist(PD2, ((1, 3, 2), (3, 2, 1), (2, 1, 3)), [1, 1, 1]))
#
# for b in bondles (Eva)(3):
#     h = pdhomlist(PD1, ((1, 3, 2), (3, 2, 1), (2, 1, 3)), b)
#     print(h)
#
#
# h = pdhomlist(PD2, ((1, 1, 1), (3, 2, 2), (2, 3, 3)), [3, 1, 2])
#
# print(h)
# #
# from pprint import pprint
#
#pprint(bondles (Eva)(3))