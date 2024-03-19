from pathlib import Path

from knotpy.notation.native import from_knotpy_notation

data_folder = Path("data")
txt_input_file = data_folder / 'bonded-simple.txt'

# load the simple bonded knots
with open(txt_input_file, 'r', newline='') as file:
    lines = file.readlines()
simple = [from_knotpy_notation(s) for s in lines]
print(f"Loaded {len(simple)} simple bonded knots.")

