from knotpy.drawing.draw_tangle import TangleProduct, integral, draw_smooth, draw, crossings
import matplotlib.pyplot as plt
from time import time
import re
from matplotlib.backends.backend_pdf import PdfPages
from math import floor
def nested_to_product(t):
    """ convert a nested tuple, e.g. 1,(2,3) to nested product of tangles Product(1, Product(2,3))."""

    if isinstance(t, int):
        return integral(t)

    if isinstance(t, tuple):
        if len(t) == 1:
            return nested_to_product(t[0])
        # start with first 2 elements
        result = TangleProduct(nested_to_product(t[0]), nested_to_product(t[1]))
        for elem in t[2:]:
            result = TangleProduct(result, nested_to_product(elem))
        return result

    raise ValueError("Input must be a nested tuple of integers.")

# Function to generate and save a PDF with plots
def generate_plots_to_pdf(tangles, pdf_filename):
    """
    Generates a PDF with each element of `tangles` plotted on a separate page.

    Parameters:
    - tangles (list of str): The list of strings to plot.
    - pdf_filename (str): The name of the PDF file to save.
    """
    with PdfPages(pdf_filename) as pdf:
        for t in tangles:
            print("drawing", t)
            plt.figure()
            draw_smooth(t)  # Call the draw function for the tangle
            #plt.title(f"Tangle: {str(t)}")  # Add a title for clarity
            pdf.savefig(bbox_inches='tight')  # Save the current figure to the PDF
            plt.close()

# Function to generate a LaTeX file with a 5x7 table of the PDF images
import math

import math


def smaller(a, b, first=True):
    """ reutrn true if tangle a < b"""
    #print("ab",a,b)
    if a == b:
        #print("eq")
        return None

    def smt(a,b):
        if isinstance(a, int) and not isinstance(b, int): return True
        if not isinstance(a, int) and isinstance(b, int): return False
        if isinstance(a, int) and isinstance(b, int):
            if a == b: return None
            if a > 0 and b < 0: return True
            return abs(a) > abs(b)
    def depth(t):
        return 0 if not isinstance(t, tuple) else (1 + max((depth(item) for item in t), default=0))

    def flatten(t):
        def flatten_(t):
            if isinstance(t, int):
                yield t
            else:
                for item in t:
                    if isinstance(item, tuple):
                        yield from flatten(item)  # Recursively yield items from nested tuples
                    else:
                        yield item  # Yield non-tuple items as is
        return tuple(flatten_(t))

    def count_int(t):
        return len([x for x in flatten(t) if x])
    def C(t):
        return sum(abs(x) for x in flatten(t))



    if first and C(a) != C(b):
        # print(flatten(a), flatten(b))
        # print(C(a), C(b))
        return C(a) < C(b)

    if first and count_int(a) != count_int(b):
        return count_int(a) < count_int(b)

    if smt(a, b) is not None:
        return smt(a, b)

    """
     2 1 (3 0) -1 < 2 -1 (3 0) -1
     
     """

    #print(a, b)

    if depth(a) != depth(b):
        return depth(a) < depth(b)

    # if len(a) != len(b):
    #     return len(a) < len(b)

    for aa, bb in zip(a,b):
        #print("recors")
        s = smaller(aa, bb, first=False)
        if s is not None:
            return s
    return None

def custom_sort(items):
    for i in range(1, len(items)):
        key_item = items[i]
        j = i - 1
        # Compare using the `smaller` function
        while j >= 0 and smaller(key_item, items[j]):
            items[j + 1] = items[j]
            j -= 1
        # Place the key_item at the correct position
        items[j + 1] = key_item
    return items


def generate_latex_table(fn, fig_name, data, cols=5, rows=6):
    """data should be list of tuple (tangle, symetry)"""
    from math import floor
    print(f"Generating latex table {fn}")
    stretch = 1.2
    w = round(1/cols * 0.95 / stretch, 2)
    width = f"{w}\\textwidth"  # Adjust image width to fit N columns

    print("Elements:", len(data))


    # fix data
    data += [("","")]*(rows - len(data) % rows)

    # Generate the full LaTeX document
    latex_code = "\\documentclass[sn-mathphys-num]{sn-jnl}\n"
    latex_code += "\\usepackage{amsfonts}\n"
    latex_code += "\\usepackage{graphicx}\n\n"
    latex_code += f"\\renewcommand{{\\arraystretch}}{{{stretch}}}\n"
    latex_code += f"\\newcommand{{\\tangle}}[1]{{\\includegraphics[width={width}, page=#1]{{{fig_name}}}}}\n"
    latex_code += f"\\newcommand{{\\n}}[1]{{#1}}  % tangle name, e.g. 3, (2,0)\n"
    latex_code += f"\\newcommand{{\\s}}[1]{{\\ensuremath{{#1}}}}  % tangle symmetry, e.g. x\n"
    latex_code += f"\\newcommand{{\\raisename}}{{-0.5em}}\n"
    latex_code += f"\\newcommand{{\\raisesym}}{{-0.5em}}\n"
    latex_code += f"\\newcommand{{\\raisenext}}{{0.5em}}\n\n"


    latex_code += "\\begin{document}\n\n"

    print("Elements:", len(data))

    # split the data
    page = 1
    for i in range(0, len(data), cols*rows):


        page_rows = min(len(data) - i, cols*rows) // cols

        page_data = data[i: i + page_rows * rows]

        print("elts", i, i + page_rows * rows)
        print("  rows", page_rows)

        table_code = f"\n% Tangles starting from {i}"
        table_code += "\n\\begin{tabular}{" + "c" * rows + "}\n"
        for j in range(i, i + page_rows * cols, cols):
            table_code += "   "
            table_code += " & ".join(
                f"\\tangle{{{k+1}}}" if data[k][0] else "" for k in range(j, j+cols)
            ) + "\\\\[\\raisename]\n"
            table_code += "   "
            table_code += " & ".join(
                f"\\n{{{data[k][0]}}}" for k in range(j, j+cols)
            ) + "\\\\[\\raisesym]\n"
            table_code += "   "
            table_code += " & ".join(
                f"\\s{{{data[k][1][1:-1]}}}" for k in range(j, j + cols)
            ) + "\\\\[\\raisenext]\n"
        table_code += "\\end{tabular}\n\n\\newpage\n"
        latex_code +=  table_code

    latex_code += "\\end{document}"

    # Save to file
    with open(fn, "w", encoding="utf-8") as f:
        f.write(latex_code)

    print(f"LaTeX document generated as {fn}.")

if __name__ == "__main__":

    # load tangles and output representative
    #
    # tangles = []
    # names = []
    # sym = []
    lines = []
    tangles = []

    what = "simple"

    PLOT = True
    print("Reading lines")
    with open("paper_data/diagrams_" + what + ".txt") as f:
        lines = f.readlines()
        lines = [line.strip().split(";") for line in lines]

    index = 0
    for name, sym in lines:
        t = eval("(" + name + ",)")
        t = nested_to_product(t)
        tangles.append(t)

    if PLOT:
        generate_plots_to_pdf(tangles, "" + what + "b.pdf")

    generate_latex_table("tangles_extra.tex", "" + what + ".pdf", lines, 5,6)



# ! [('4,1,(5,-1)', '-5,(5,0)', "('e','x','μz','μy')"), ('4,1,(5,-1),0', '-5,(5,0),0', "('ηx','μηy','μηz','η')"), ('5,(4,1,-1),0', '5,(-5,0),0', "('μηx','ηy','ηz','μη')"), ('5,(4,1,-1)', '5,(-5,0)', "('y','z','μ','μx')")]