

from pathlib import Path
from sympy import *

def PDB_files(path):
     for pth in Path(path).glob('**/*.ent'):
          yield str(pth)


#for s in PDB_files('/home/bostjan/PDB/pdb_div'):
#     print(s)