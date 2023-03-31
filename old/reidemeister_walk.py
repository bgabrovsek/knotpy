from knotted import *
from crossing import *
from reidemeister_moves import *
from HOMFLYPT import *

DEBUG_FIND_REIDEMEISTER = False

# FIND POSITIONS WHERE REIDEMEISTER MOVES CAN BE PERFORMED
# TODO: exclude loops

def find_areas(K, n, alternating=None):
    n_areas = [a for a in K.areas() if len(a) == n]
    if alternating is None: return n_areas
    if alternating: return [a for a in n_areas if all(K.alternatingQ(arc) for arc, dir in a)]
    if not alternating: return [a for a in n_areas if not all(K.alternatingQ(arc) for arc, dir in a)]
    raise ValueError("Error.")


# FIND REIDMEISTER MOVES

def find_R1_unkinks(K): # returns unkink arcs
    return [a[0][0] for a in K.areas() if len(a) == 1 and XQ(K.D(a[0][0])[0][0])]

def find_R1_kinks(K): # return all arcs
    return list(K.arcs())

def find_R2_unpokes(K): # return unpoke arcs
    return [a for a in K.areas() if len(a) == 2 and K.middleQ(a[0][0]) and K.non_alternatingQ(a[0][0])]

def find_R2_pokes(K): # returns poke pairs of arcs
    return [pair for a in K.areas() if len(a) > 1 for pair in combinations(a,2)]

def find_R3_moves(K): # returns R3 areas)

    return [a for a in K.areas() if len(a) == 3
            and all(K.middleQ(arc) for arc, side in a)
            and sum(K.alternatingQ(arc) for arc, side in a) == 1
            and all(not K.loopQ(arc) for arc, side in a)]

def find_R4_unpokes(K): # return unpoke areas
    #print("Find R4 unpokes.", K)
    return [a for a in K.CCW_areas() if len(a) == 3 and
            len([node for node in area_nodes(K, a) if VQ(node)]) == 1 and  # only one vertex
            len([arc for arc, side in a if K.non_alternatingQ(arc)]) == 1]  # only one non-alternating arc

def find_R4_pokes(K):  # return poke arcs
    return [arc for arc in K.arcs() if (VQ(K.D(arc)[0][0]) ^ VQ(K.D(arc)[1][0]))]

def find_R5_twists(K):
    return [arc for arc in K.arcs() if VQ(K.D(arc)[0][0]) or VQ(K.D(arc)[1][0])]

def find_R5_untwists(K):
    return [a for a in K.areas() if len(a) == 2 and len([node for node in area_nodes(K, a) if VQ(node)])==1]

# BOND-SPECIFIC VARIATIONS
def find_R4_bond_pokes(K):
    return [arc for arc in find_R4_pokes(K) if K.color(arc) != 0]

def print_reidemeister_moves(K):
    print("  R1 kinks:", find_R1_kinks(K))
    print("  R1 unkinks:", find_R1_unkinks(K))
    print("  R2 pokes:", find_R2_pokes(K))
    print("  R2 unpokes:", find_R2_unpokes(K))
    print("  R3 moves:", find_R3_moves(K))
    print("  R4 pokes:", find_R4_pokes(K))
    print("  R4 bond pokes:", find_R4_bond_pokes(K))
    print("  R4 unpokes:", find_R4_unpokes(K))
    print("  R5 twists:", find_R5_twists(K))
    print("  R5 untwists:", find_R5_untwists(K))

# RANDOM REIDEMEISTER MOVES

def choose_reidemeister_move(K, find_function, perform_function):
    choices = find_function(K)
    ret = False
    if choices:
        if DEBUG_FIND_REIDEMEISTER: print("CHOICES", choices)
        param = choice(choices)
        ret = "param " + str(param)

        perform_function(K, param)

        if not check_knotted(K):
            print("KNOT NOT OK:", K)
            exit(0)
    return ret

def random_R1_unkink(K): return choose_reidemeister_move(K, find_R1_unkinks, R1_unkink)
def random_R1_kink(K): return choose_reidemeister_move(K, find_R1_kinks, R1_kink)
def random_R2_unpoke(K): return choose_reidemeister_move(K, find_R2_unpokes, R2_unpoke)
def random_R2_poke(K): return choose_reidemeister_move(K, find_R2_pokes, R2_poke)
def random_R3_move(K): return choose_reidemeister_move(K, find_R3_moves, R3_move)
def random_R4_poke(K): return choose_reidemeister_move(K, find_R4_pokes, R4_poke)
def random_R4_bond_poke(K): return choose_reidemeister_move(K, find_R4_bond_pokes, R4_poke)
def random_R4_unpoke(K): return choose_reidemeister_move(K, find_R4_unpokes, R4_unpoke)
def random_R5_twist(K): return choose_reidemeister_move(K, find_R5_twists, R5_twist)
def random_R5_untwist(K): return choose_reidemeister_move(K, find_R5_untwists, R5_untwist)

# RANDOM WALK

def random_walk(K, n, invariant):
    knot = K.copy()
    invariant_value_K = invariant(K)
    for count in range(n):
        random_moves = [("R1 unkink", random_R1_unkink), ("R1 kink", random_R1_kink), ("R2 unpoke", random_R2_unpoke),
                        ("R2 poke", random_R2_poke), ("R3 move", random_R3_move), ("R4 poke", random_R4_poke),
                        ("R4 band poke", random_R4_bond_poke), ("R4 unpoke", random_R4_unpoke),
                        ("R5 twist", random_R5_twist), ("R5 untwist", random_R5_untwist)]
        shuffle(random_moves)

        for move_name, move in random_moves:
            if move(knot):
                break
        print(knot)
        invariant_value = invariant(knot)
        if invariant_value != invariant_value_K:
            print("[ERROR ]Invariants not equal after performing",move_name)
            print(invariant_value_K)
            print(invariant_value)


def random_Reidemesiter_move_check(K, invariant):
    random_moves = [("R1 unkink",random_R1_unkink),
             ("R1 kink",random_R1_kink),
             ("R2 unpoke",random_R2_unpoke),
            ("R2 poke",random_R2_poke),
            ("R3 move",random_R3_move),
            ("R4 poke",random_R4_poke),
            ("R4 bond",random_R4_bond_poke),
            ("R4 unpoke",random_R4_unpoke),
            ("R5 twist",random_R5_twist),
            ("R5 untwist",random_R5_untwist)]
    shuffle(random_moves)

    invariant_value = invariant(K)
    knot = K.copy()
    for move_name, move in random_moves:
        ret_value = move(knot)
        if ret_value:
            break
    invariant_value_after = invariant(knot)
    if invariant_value != invariant_value_after:
        print()
        print(move_name, "(" + ret_value + ")")
        print(K)
        print(knot)
        print(str(invariant_value).replace("Θ","T").replace("**","^"))
        print(str(invariant_value_after).replace("Θ","T").replace("**","^"))


# BOND ISOLATAION

def isolate_bonds(K):
    """ Isolated the bonds, so that they do not contain any crossings."""
    new_knot = K.copy()
    while random_R4_bond_poke(new_knot): pass
    return new_knot



# SIMPLIFICATION

def decreasing_simplify(K, make_canonical = True, rigid = False):
    name = K.name
    #print("START", K)
    while True:
        #print("(decrease step)",len(K.components()),K)
        changed = False
        while random_R1_unkink(K):
            #print("(R1)", len(K.components()), K)
            changed = True
        while random_R2_unpoke(K):
            #print("(R2)", len(K.components()), K)
            changed = True

        if not rigid:
            while random_R5_untwist(K):
                changed = True

        while random_R4_unpoke(K):
            changed = True

        if not changed: break

    if make_canonical:
        K.self_canonical_unoriented()
    K.name = name
    #print("END", K)


def simplify_and_split(knot, depth = 0):

    #if depth == 0: print("SS", knot, "c",len(knot.components()))
    decreasing_simplify(knot, make_canonical=False)
    #if depth == 0: print("ss", knot,"c" ,len(knot.components()))


    disjoint_components = knot.disjoin()

    #if depth == 0: print("D", disjoint_components)

    #print(")"," "*depth, knot,"-->",disjoint_components, len(disjoint_components))

    if len(disjoint_components) == 1:
        return disjoint_components
    else:
        return [K for C in disjoint_components for K in simplify_and_split(C, depth+1)]

