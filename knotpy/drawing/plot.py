

def plot_circlepack(k):

    external_radius_node = 1.0  # radius of external circles corresponding to crossings
    external_radius_arc = 0.6  # radius of external circles corresponding to arcs
    external = dict()  # radii of external circles, keys are circles, values are redii
    internal = dict()  # neighbourhood circles of internal circles {circle key: list of ordered surrounding circles}



    regions = [tuple(a) for a in K.CCW_areas()] # turn areas into tuples (as they will be circle keys)

    # choose the external area as the longest one
    max_area_size = max(len(a) for a in areas)
    max_areas = [a for a in areas if len(a) == max_area_size]
    external_area = min(max_areas) # out of longest area, chose the alphabetically smallest one


    # EXTERNAL CIRCLES

    for arc, ccw_b in external_area[::-1]:
        cr, pos = K.D(arc)[not ccw_b] # TODO: is CCW direction OK? It probably does not matter.
        external[arc] = external_radius_arc
        external[cr.tuple()] = external_radius_crs

    for a in areas: internal[a] = [] # add areas to interior circles
    for a in K.arcs(): internal[a] = []        # add arcs to interior circles
    for node in K.nodes: internal[node.tuple()] = [] # add arcs to interior circles

    # add internal area circles connections
    for a in areas:
        # append all arcs and crossings to it
        for arc, ccw_b in a:
            ccw_cr, ccw_pos = K.D(arc)[ccw_b] # TODO: is CCW direction OK? It probably does not matter.
            internal[a].append(arc)
            internal[a].append(ccw_cr.tuple())

    # add internal arc circles
    for arc in K.arcs():
        if arc in external: continue
        true_area, false_area = None, None
        (cr0, pos0), (cr1, pos1) = K.D(arc)
        for a in areas:
            if (arc, True) in a: true_area = a
            if (arc, False) in a: false_area = a
        internal[arc] += [cr1.tuple(), true_area, cr0.tuple(), false_area]

    # add internal crossings
    for node in K.nodes:
        for pos in node:
            arc = node[pos]
            arc_dir = (arc,True) if node.outQ(pos) else (arc,False)
            area = [a for a in areas if arc_dir in a][0] # get the area
            internal[node.tuple()].append(arc)
            internal[node.tuple()].append(area)



    # remove external keys from internal, since they should be disjoint
    del internal[external_area]
    for key in external:
        if key in internal: del internal[key]

    # reverse everything, since we are having the wrong orientation the whole time
    for key in internal:
        internal[key].reverse()

    #print(K.export())
    #print(K)
    #print("EX", external)
    #print("IN", internal)

    #print(K.bridgeQ(), K.bridge_crossingQ())

    #print(K.areas())
    # pack the circles"

    #print("ex",K)
    ret = CirclePack(internal, external)

    plot_circles(K, ret)




