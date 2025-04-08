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
            return nested_to_product(t)
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

    if a == b:
        return True

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
    def C(t):
        return sum(abs(x) for x in flatten(t))



    if first and C(a) != C(b):
        # print(flatten(a), flatten(b))
        # print(C(a), C(b))
        return C(a) < C(b)

    if smt(a, b) is not None:
        return smt(a, b)

    """
     2 1 (3 0) -1 < 2 -1 (3 0) -1
     
     """

    #print(a, b)

    if depth(a) != depth(b):
        return depth(a) < depth(b)

    if len(a) != len(b):
        return len(a) < len(b)

    for aa, bb in zip(a,b):

        s = smaller(aa, bb, first=False)
        if s is not None:
            return s
    return None

def custom_sort(items):
    for i in range(1, len(items)):
        key_item = items[i]
        j = i - 1
        # Compare using the `smaller` function
        while j >= 0 and smaller(key_item[0], items[j][0]):
            items[j + 1] = items[j]
            j -= 1
        # Place the key_item at the correct position
        items[j + 1] = key_item
    return items

def compute_tuple_properties(t):
    """
    Computes the properties of a nested tuple for sorting purposes:
    1. Minimal sum of absolute values of all integers inside all nests.
    2. Least nested depth.
    3. Shortest tuple length.
    4. Largest numbers for tie-breaking (compared lexicographically).
    5. Priority to positive numbers over negatives.

    Parameters:
    - t (tuple): A nested tuple of integers.

    Returns:
    - tuple: A tuple of sorting keys based on the defined priorities.
    """
    def flatten_and_depth(nested, current_depth=0):
        """Flatten the nested tuple and compute the depth."""
        max_depth = current_depth
        elements = []
        for item in nested:
            if isinstance(item, tuple):
                sub_elements, sub_depth = flatten_and_depth(item, current_depth + 1)
                elements.extend(sub_elements)
                max_depth = max(max_depth, sub_depth)
            else:
                elements.append(item)
        return elements, max_depth

    # Flatten the tuple and calculate its depth
    flattened, depth = flatten_and_depth(t)

    # 1. Sum of absolute values of all integers
    abs_sum = sum(abs(x) for x in flattened)

    # 2. Depth of the tuple (least depth has priority)
    # The `depth` is already computed during flattening.

    # 3. Shortest tuple length
    total_length = len(flattened)

    # 4. Largest numbers for tie-breaking (compared lexicographically)
    largest_numbers = sorted(flattened, reverse=True)

    # 5. Positive numbers priority for tie-breaking
    positives_priority = [-1 if x < 0 else 0 for x in flattened]

    return (abs_sum, depth, total_length, largest_numbers, positives_priority)
def sort_nested_tuples(nested_tuples):
    """
    Sorts a list of nested tuples based on the defined priorities.

    Parameters:
    - nested_tuples (list of tuple): The list of tuples to be sorted.

    Returns:
    - list of tuple: The sorted list of tuples.
    """
    return sorted(nested_tuples, key=lambda x: compute_tuple_properties(x[0]))

if __name__ == "__main__":

    tangles = []
    names = []
    best_cols = [] # minimal/positive representative of a tangle

    with open("data/up_to_10_group.txt") as f:
        lines = f.readlines()[1:]

        for i, line in enumerate(lines):
            line = eval(line.strip())
            line = [list(col) for col in line]

            for col in line:
                if col[1] == "-":
                    col[1] = col[0]
                print(col)
            conway = [eval("(" + col[1] + ",)") for col in line]

            exit()


            # representative = line[0]
            # name, minimal, sym = representative
            # if minimal == "-": minimal = name
            # names.append(minimal)
            # #minimal = eval("(" + minimal + ",)")
            # #print(eval(minimal))
            # t = nested_to_product(eval(minimal))
            tangles.append(t)
    print("read.")

    exit()
    tangles = [integral(0)] + tangles  # prepend 0 tangle
    names = ["0"] + names  # prepend 0 tangle
    conway = [eval("(" + x + ",)") for x in names]
    names = [n.replace(",", " ") for n in names]

    tangles = [t for t in tangles if crossings(t) <= 7]
    names = names[:len(tangles)]
    conway = conway[:len(tangles)]
    if len(tangles) != len(names):
        raise ValueError("!!")

    # sort
    zp = list(zip(conway, names, tangles))
    #zp = sort_nested_tuples(zp)
    zp = custom_sort(zp)
    conway, names, tangles = zip(*zp)

    generate_plots_to_pdf(tangles, "tangles_sorted.pdf")
    print("pdf.")

    generate_latex_for_pdf(names, "tangles_sorted.pdf", "tangle_table_sorted.tex")
    print("tex.")

    # check minimal crossings
    # for i in range(len(tangles)-1):
    #     t, t_ = tangles[i], tangles[i+1]
    #     c, c_ = crossings(t), crossings(t_)
    #     if c != c_:
    #         print(c, "->", c_)


# ! [('4,1,(5,-1)', '-5,(5,0)', "('e','x','μz','μy')"), ('4,1,(5,-1),0', '-5,(5,0),0', "('ηx','μηy','μηz','η')"), ('5,(4,1,-1),0', '5,(-5,0),0', "('μηx','ηy','ηz','μη')"), ('5,(4,1,-1)', '5,(-5,0)', "('y','z','μ','μx')")]