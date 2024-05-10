import knotpy as kp
from random import uniform

def crand():
    return uniform(-1, 1) + 1J * uniform(-1, 1)

def mobius(layout):
    result = dict()
    q = 0.3
    p1 = 0
    p2 = 1
    p1_ = 0
    p2_= 1
    abcd = (uniform(p1, p2) + 1J * uniform(p1, p2),
            uniform(-q, q) + 1J * uniform(-q, q),
            uniform(p1_, p2_) + 1J * uniform(p1_, p2_),
            uniform(-q, q) + 1J * uniform(-q, q))
    #print(a,b,c,d)
    #print("determinant", abcd[0]*abcd[3]-abcd[1]*abcd[2])
    def f(circle, a, b,c,d):
        z1 = circle.center + circle.radius
        z2 = circle.center - circle.radius
        z3 = circle.center + 1J * circle.radius
        z4 = circle.center - 1J * circle.radius
        w1 = (a*z1 + b) / (c*z1 + d)
        w2 = (a*z2 + b) / (c*z2 + d)
        w3 = (a*z3 + b) / (c*z3 + d)
        w4 = (a*z4 + b) / (c*z4 + d)

        #print(a,b,c,d,w1,w2,w3,w4)

        c1 = kp.circle_through_points(w1, w2, w3)
        c2 = kp.circle_through_points(w1, w2, w4)
        c3 = kp.circle_through_points(w1, w3, w4)
        c4 = kp.circle_through_points(w2, w3, w4)
        # print(c1)
        # print(c2)
        # print(c3)
        # print(c4)

        if c1 is None or c2 is None or c3 is None or c4 is None:
            return None


        return kp. Circle(
            (c1.center + c2.center + c3.center + c4.center) / 4,
            (c1.radius + c2.radius + c3.radius + c4.radius) / 4,

        )

        #return kp.Circle((w1+w2+w3+w4)/4, 0.5*abs(w2-w1))

    for key, val in layout.items():
        #print(*abcd)
        new_val = f(val, *abcd)
        result[key] = new_val
        #print(val, "->", result[key])

    return result


pds = {
    "0_1": "[[5,2,4,1],[3,1,4,6],[5,3,6,2]]",
    "3_1": "[[1,5,2,4],[3,1,4,6],[5,3,6,2]]",
    "4_1":	"[[4,2,5,1],[8,6,1,5],[6,3,7,4],[2,7,3,8]]",
    "5_1":	"[[2,8,3,7],[4,10,5,9],[6,2,7,1],[8,4,9,3],[10,6,1,5]]",
    "5_2":	"[[1,5,2,4],[3,9,4,8],[5,1,6,10],[7,3,8,2],[9,7,10,6]]",
    "6_1":	"[[1,7,2,6],[3,10,4,11],[5,3,6,2],[7,1,8,12],[9,4,10,5],[11,9,12,8]]",
    "6_2":	"[[1,8,2,9],[3,11,4,10],[5,1,6,12],[7,2,8,3],[9,7,10,6],[11,5,12,4]]",
    "6_3":	"[[4,2,5,1],[8,4,9,3],[12,9,1,10],[10,5,11,6],[6,11,7,12],[2,8,3,7]]"}

name = "5_2"
pd = pds[name]

k = kp.from_pd_notation(pd)
print(k)


layout = kp.circlepack_layout(k)

count = 20
counter = 0
while counter < count:

    new_layout = mobius(layout)
    max_radius = max(m.radius for m in new_layout.values())
    min_radius = min(m.radius for m in new_layout.values())

    if min_radius < 0.05:
        continue
    if max_radius > 5:
        continue

    try:
        kp.draw_from_layout(k, new_layout, draw_circles=False,
                            save_to_file="pics/{}_{:03d}.png".format(name,counter),
                            bounding_box=True)
        print("saved to", "pics/01_{:03d}.png".format(counter), "MINMAX", round(min_radius,3), round(max_radius,3))
        counter += 1
    except:
        pass
