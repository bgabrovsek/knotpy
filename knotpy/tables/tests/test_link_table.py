import knotpy as kp

def test_link_table_names():

    l = kp.link("L2a1++")
    assert len(l) == 2
    assert type(l) == kp.OrientedPlanarDiagram

    l = kp.link("L2a1+-")
    assert len(l) == 2
    assert type(l) == kp.OrientedPlanarDiagram

    l = kp.link("L2a1-+")
    assert len(l) == 2
    assert type(l) == kp.OrientedPlanarDiagram

    l = kp.link("L2a1--")
    assert len(l) == 2
    assert type(l) == kp.OrientedPlanarDiagram

    l = kp.link("L2a1")
    assert len(l) == 2
    assert type(l) == kp.PlanarDiagram
    assert l.name == "L2a_1"

    a = kp.link("L5a_1")
    assert len(a) == 5
    assert type(a) == kp.PlanarDiagram

    b = kp.link("L5a1*")
    assert len(b) == 5
    assert type(b) == kp.PlanarDiagram
    assert b.name == "L5a_1*"

    assert a != b

    links = [
        kp.link("L8n_3+++"),
        kp.link("L8n_3++-"),
        kp.link("L8n_3+-+"),
        kp.link("L8n_3+--"),
        kp.link("L8n_3-++"),
        kp.link("L8n_3-+-"),
        kp.link("L8n_3--+"),
        kp.link("L8n_3---"),
        kp.link("L8n_3*+++"),
        kp.link("L8n_3*++-"),
        kp.link("L8n_3*+-+"),
        kp.link("L8n_3*+--"),
        kp.link("L8n_3*-++"),
        kp.link("L8n_3*-+-"),
        kp.link("L8n_3*--+"),
        kp.link("L8n_3*---"),
    ]

    # Make sure every pair is different
    for i, li in enumerate(links):
        for j, lj in enumerate(links):
            if i < j:
                assert li != lj, f"Links {li} and {lj} should be different"

    a = kp.link("L8n_3")
    b = kp.link("L8n_3*")
    assert a != b
    assert not a.name.endswith("+")
    assert not a.name.endswith("-")
    assert not b.name.endswith("+")
    assert not b.name.endswith("-")

def test_link_table():

    links_1 = kp.links(range(0, 8), mirror=False)
    assert all(type(_) == kp.PlanarDiagram for _ in links_1)

    links_2 = kp.links(range(0, 8), mirror=True)
    assert all(type(_) == kp.PlanarDiagram for _ in links_2)

    assert len(links_1)*1.5 < len(links_2)

    links_3 = kp.links(range(0, 8), oriented=True, mirror=False)
    assert all(type(_) == kp.OrientedPlanarDiagram for _ in links_3)

    links_4 = kp.links(range(0, 8), oriented=True, mirror=True)
    assert all(type(_) == kp.OrientedPlanarDiagram for _ in links_4)

    assert len(links_3)*1.5 < len(links_4)
    assert len(links_1)*1.5 < len(links_3)
    assert len(links_2)*1.5 < len(links_4)

def test_link_identification():
    k = kp.link("L2a1++")
    print(k)
    for x in range(10):
        print(kp.canonical(k))
        print(kp.canonical(kp.canonical(k)))
    #l = kp.canonical(k)
    # print(k, "<<<<")
    # print(kp.identify(k))


if __name__ == "__main__":
    test_link_identification()
    test_link_table_names()
    test_link_table()
