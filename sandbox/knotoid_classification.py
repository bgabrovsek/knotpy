
from knotpy import from_pd_notation, from_plantri_notation


code = ["XABC", "YADE", "CBED", "X", "Y"]
k = from_plantri_notation("5 "+ "XABC,YADE,CBED,X,Y")
print(k)