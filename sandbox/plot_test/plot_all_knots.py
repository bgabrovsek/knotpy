import sys

sys.path.append('/home/bostjan/Dropbox/Code/knotpy/')


import knotpy as kp

all_knots = list(kp.knot_table.values())


kp.export_pdf(all_knots, "plot/knot_table.pdf", with_title=True, draw_circles=True)