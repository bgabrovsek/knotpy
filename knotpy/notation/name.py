# """Conway names (3_1, 4_1, ...).
#
# For knots with 10 or fewer crossings we use the classical names (polished by Perko). For knots with 11 crossings, the
# naming convention is that of Dowker-Thistlethwaite.
# """
#
# #from knotpy.tabulation.knot_table import knot_table
#
#
#
#
# _knot_aliases = {
#     "unknot": "0_1", "o": "0_1", "trivial knot": "0_1", "trefoil": "3_1", "figure eight": "4_1", "figure 8": "4_1",
#     "cinquefoil": "5_1", "pentafoil": "5_1", "3-twist": "5_2", "stevedore": "6_1", "miller institute": "6_2",
#     "septafoil": "7_1", "nonafoil": "9_1"
# }
#
# #
# # database_root_folder = Path("./database")
# # path_PD_up_to_10_crossings = database_root_folder / "PD_knots_up_to_10_crossings.csv"
#
# # _knots_up_to_10_crossings = None  # contains dictionaty, e.g. {"3_1":  {'PD': '[[1;5;2;4];[3;1;4;6];[5;3;6;2]]', 'symmetry': 'reversible'}, ...}
#
# # def _name_unoriented_knot(k: PlanarDiagram):
# #     global _knots_up_to_10_crossings
# #     global path_PD_up_to_10_crossings
# #
# #     if _knots_up_to_10_crossings is None:
# #         pass
# #
# #     k = simplify_crossing_reducing(k)
# #     print(k)
#
# # def name(k: PlanarDiagram):
# #     return None
#
#
# def from_name(name):
#
#     global _knot_aliases
#
#     name = _knot_aliases.get(name.lower(), name)
#
#     if name in knot_table:
#         return knot_table[name]
#
#     raise ValueError(f"Knot {name} not found.")
#
# if __name__ == "__main__":
#     print(from_name("o"))
#
#     """
#     predicted file sizes:
#
#     16 knots: n = 1,701,934
#
#     PD:
#     [(10,0,11,31),(0,14,1,13),(14,2,15,1),(23,3,24,2), ....
#     20 bitov * 16 = 320 bytes per knot = 68 MB
#
#     DT:
#     [4, 8, 10, 14, 2, 16, 20, 6, 22, 12, 24, 18] -> [2,4,5,7,1,8,10,3,11,6,12,9] -> 0,...
#     DT: 12 * 5 = 60 bitov 0 =  102 MB
#
#
#     """