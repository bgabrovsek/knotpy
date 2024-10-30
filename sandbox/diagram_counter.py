import knotpy as kp
import sympy

k = kp.from_name("8_2")

j = kp.jones_polynomial(k)




diagram_with_same_jones = []# [ name for name in kp.knot_table if     kp.knot_table.invariants[name]["Jones"] == j ]


# knots up to 9 crossings

knots_max = kp.select_knots(max_crossings=11)
unique_jones = set( (kp.knot_table.invariants[name]["HOMFLYPT"],
                     kp.knot_table.invariants[name]["Kauffman"]) for name in knots_max)


real_jones = kp.knot_table.invariants["3_1"]["Jones"]

print(len(diagram_with_same_jones))
print(diagram_with_same_jones)

print("Knots up to 10 crossings:", len(knots_max), "number of unique jones", len(unique_jones))