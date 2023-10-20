import knotpy as kp

a = 'V[12,14,5];V[14,13,2];X[11,10,13,12];X[7,11,5,6];X[10,7,6,2]'
b = 'V[5,14,12];V[14,13,2];X[11,10,13,12];X[7,11,5,6];X[10,7,6,2]'

print(a)
print(b)

a = kp.from_pd_notation(a)
b = kp.from_pd_notation(b)

print(a)
print(b)

reg_a = list(kp.regions(a))
reg_b = list(kp.regions(b))

print(reg_a)
print(reg_b)

def unique(s):
    return len(set(s)) == len(s)

for reg in (reg_a, reg_b):
    print(all( unique([ep.node for ep in r]) for r in reg ))
    
print(kp.check_region_sanity(a))
print(kp.check_region_sanity(b))