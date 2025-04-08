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

def generate_latex_for_pdf(tangles, pdf_filename, latex_filename):
    """
    Generates a LaTeX file that arranges the images from a PDF in a 5x7 table.
    Each image and its corresponding name are placed in the same table cell using `minipage`.
    The image width is defined as a LaTeX constant for easy modification.

    Parameters:
    - tangles (list of str): The list of strings to display below each image.
    - pdf_filename (str): The name of the PDF containing the plots.
    - latex_filename (str): The name of the LaTeX file to generate.
    """
    num_columns = 5
    width = math.floor((1.0 / num_columns) * 100) / 100  # Dynamically compute the width

    with open(latex_filename, "w") as latex_file:
        latex_file.write("\\documentclass{article}\n")
        latex_file.write("\\usepackage{graphicx}\n")
        latex_file.write("\\usepackage[margin=1in]{geometry}\n")
        latex_file.write("\\newcommand{\\mpwidth}{%.2f\\textwidth}\n" % width)  # Define the image width constant
        latex_file.write("\\newcommand{\\iwidth}{0.90\\textwidth}\n")  # Define the image width constant
        latex_file.write("\\begin{document}\n")
        latex_file.write("\\begin{center}\n")
        latex_file.write("\\setlength{\\tabcolsep}{4pt}\n")
        latex_file.write("\\renewcommand{\\arraystretch}{1.5}\n")

        for i, t in enumerate(tangles):
            if i % num_columns == 0:  # Start a new row in the table
                if i > 0:  # Close the previous row if it's not the first one
                    latex_file.write("\\end{tabular}\n\\vspace{0.5cm}\n")
                latex_file.write("\\begin{tabular}{%s}\n" % ("c" * num_columns))

            # Use minipage with the defined image width constant
            latex_file.write(
                "\\begin{minipage}[t]{\\mpwidth}\\centering"
                "\\includegraphics[page=%d,width=\\iwidth]{%s}\\\\"
                "%s\\end{minipage}" % (i + 1, pdf_filename, str(t))
            )

            if (i + 1) % num_columns == 0:  # End the current row
                latex_file.write("\n")
            else:
                latex_file.write(" & ")

        # Close the last open table
        latex_file.write("\\end{tabular}\n")
        latex_file.write("\\end{center}\n")
        latex_file.write("\\end{document}\n")


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

if __name__ == "__main__":

    # load tangles and output representative

    tangles = []
    names = []
    best_cols = [] # minimal/positive representative of a tangle
    representatives = []
    with open("data/repr-8-simple.txt", "w") as g:
        with open("data/results_8_simple.txt") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().split(" ")
                same = eval(line[-1])
                rep = [col[1] if col[1] != "-" else col[0] for col in same]
                rep = [eval("(" + x + ",)") for x in rep]
                best_rep = custom_sort(list(rep))[0]
                representatives.append(best_rep)
                index = rep.index(best_rep)
                g.write(f"{index} {str(best_rep).replace(' ','')[1:-1]}\n")

    representatives2 = [nested_to_product(r) for r in representatives]
    print("read & output.")

    # plot the diagrams

    print("to pdf...")
    generate_plots_to_pdf(representatives2, "tangles_simple.pdf")
    print("pdf.")

    # generate latex

    print("to tex...")
    generate_latex_for_pdf(representatives, "tangles_sorted.pdf", "tangle_table_sorted.tex")
    print("tex.")

    # check minimal crossings
    # for i in range(len(tangles)-1):
    #     t, t_ = tangles[i], tangles[i+1]
    #     c, c_ = crossings(t), crossings(t_)
    #     if c != c_:
    #         print(c, "->", c_)


# ! [('4,1,(5,-1)', '-5,(5,0)', "('e','x','μz','μy')"), ('4,1,(5,-1),0', '-5,(5,0),0', "('ηx','μηy','μηz','η')"), ('5,(4,1,-1),0', '5,(-5,0),0', "('μηx','ηy','ηz','μη')"), ('5,(4,1,-1)', '5,(-5,0)', "('y','z','μ','μx')")]