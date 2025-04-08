
import pytextssss

import knotpy as kp

class textssssTangles:

    def textssss_tangle_insert(self):

        print("\ntextssss tangle insert")
        t = kp.integer_tangle(2)
        g = kp.from_plantri_notation("cbdd,acd,adb,abca")
        k = kp.insert_tangle(g, "b", t, create_using=kp.SpatialGraph)

        print("\n",g,"\nTangle",t,"\nResult\n",k)

        #print("disjoint components", kp.disjoint_components(k))
        #print("link components", kp.link_components_endpoints(k))
        assert len(k) == len(g) + len(t) - 4 - 1
        return

        t = kp.horizontal_tangle()
        g = kp.from_plantri_notation("cbdd,acd,adb,abca")
        k = kp.insert_tangle(g, "b", t, create_using=kp.SpatialGraph)
        #print("disjoint components", kp.disjoint_components(k))
        #print("link components", kp.link_components_endpoints(k))
        print("\n",g,"\nTangle",t,"\nResult\n",k)

        assert len(k) == len(g) + len(t) - 4 - 1


        t = kp.vertical_tangle()
        g = kp.from_plantri_notation("cbdd,acd,adb,abca")
        k = kp.insert_tangle(g, "b", t, create_using=kp.SpatialGraph)
        print("\n",g,"\nTangle",t,"\nResult\n",k)

        #print("disjoint components", kp.disjoint_components(k))
        #print("link components", kp.link_components_endpoints(k))
        assert len(k) == len(g) + len(t) - 4 - 1

    def textssss_tangle_insert_from(self):
        for t, s in zip([kp.horizontal_tangle(), kp.vertical_tangle(), kp.integer_tangle(1)],
                        ["Horizontal", "Vertical", "Integer"]):
            print("\n###", s, "###")

            # g = kp.from_plantri_notation("cbbc,aca,aab")
            g = kp.PlanarGraph()
            g.add_node("a", degree=4, create_using=kp.Vertex)
            g.add_node("b", degree=2, create_using=kp.Vertex)
            g.set_arc((("a", 0), ("a", 1)))
            g.set_arc((("a", 2), ("b", 1)))
            g.set_arc((("a", 3), ("b", 0)))

            print(g)
            print(t)
            k = kp.insert_tangles_from(g, {"a": t}, create_using=kp.SpatialGraph)
            print("Result")
            print(k)

    def textssss_two_tangle_insert(self):

        tangles = [kp.horizontal_tangle(), kp.vertical_tangle(), kp.integer_tangle(1)]
        strs = ["Horizontal", "Vertical", "Integer"]
        ts = list(zip(tangles, strs))

        for (t0, s0), (t1, s1) in product(ts, ts):
            print("\n###", s0, s1, "###")

            g = kp.from_plantri_notation("bccb,daad,ada,bbc")
            print(g)
            print(t0)
            print(t1)
            k = kp.insert_tangles_from(g, {"a": t0, "b": t1}, create_using=kp.SpatialGraph)
            print("Result")
            print(k)

        pass
