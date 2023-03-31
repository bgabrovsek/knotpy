from knotted import *
from drawknot import *

K = Knotted([Crossing([0,1,2,3], -1), Crossing([4,5,6,1], -1), Crossing([2,6,7,8], -1), Crossing([3,9,10,11], 1), Crossing([14,4,12,13], 1), Crossing([15,7,5,14], -1), Crossing([8,15,16,9], 1), Crossing([16,13,17,10], 1), Crossing([12,0,11,17], 1)], name='1284cb')



#    Knotted([Crossing([0,1,2,3], -1), Crossing([4,5,6,1], -1), Crossing([6,7,8,2], 1), Crossing([3,8,9,10], -1), Crossing([12,4,0,11], 1), Crossing([13,14,5,12], -1), Crossing([9,7,14,15], -1), Crossing([15,13,11,10], 1)], name='13219cb')
KNOTS = [K]
PDF_export_knots(KNOTS, "pdf/111.pdf")
exit()

KNOTS = load_knots("data/00-knots-7-reduced-01.txt")
PDF_export_knots(KNOTS, "pdf/01-knots-7-verts-reduced1.pdf")