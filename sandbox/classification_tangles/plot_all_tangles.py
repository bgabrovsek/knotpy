from knotpy.drawing.draw_tangle import TangleProduct, integral, draw_smooth, draw
import matplotlib.pyplot as plt
from time import time
import re
from tqdm import tqdm
from matplotlib.backends.backend_pdf import PdfPages


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


def bartosz_order():
    T = "3,(2,(2,0));2,(3,(2,0));" \
        "2,(2,(2,-1)),-1;                2,(2,(-2,0)),-1;"\
        "2,(2,-1);                       2,(-2,0);"\
        "3,(2,(2,1,-1)),-1;              3,(2,(-3,0)),-1;"\
        "2,(3,(2,1,-1),(2,-1));          2,(3,(-3,0),(-2,0));"\
        "3,(2,1,-1),(2,1,(3,-1),0);      3,(-3,0),(-3,(3,0),0);"\
        "2,(2,(2,(2,-2))),(2,0),-1;      2,(2,(-2,(-2,0))),(2,0),-1;"\
        "2,(2,(2,-2)),2,(2,-1);          2,(-2,(-2,0)),2,(-2,0);"\
        "3,(2,1,-1);                     3,(-3,0);"\
        "2,(3,(2,1,-1),-1),2,(2,-1);     2,(3,(-3,0),-1),2,(-2,0);"\
        "2,(3,(2,1,-1),(2,-1));          2,(3,(-3,0),(-2,0));"\
        "2,(3,(2,1,-1),0),-1;            2,(3,(-3,0),0),-1;"\
        "3,(2,1,-1),(2,(2,-1));          3,(-3,0),(2,(-2,0))"
    T = [x.strip() for x in T.split(";")]
    for t in T:
        print(t)

    with PdfPages('tangles-bartosz3.pdf') as pdf:

        for i, x in enumerate(T):
                # parse

                tangle_can = eval(x)
                #tangle_min = eval(str_min) if str_min != "-" else tangle_can
                t = nested_to_product(tangle_can)
                #print(tangle_can, "->", t)

                # plot
                plt.figure()
                draw_smooth(t)

                plt.title(x + (" - can" if i % 2 == 0 else " - min") )
                # save
                #filename = "plots/" + str_can.replace(" ", "") + ".png"
                #plt.savefig(filename, format='png', bbox_inches='tight', pad_inches=0)
                pdf.savefig(bbox_inches='tight', pad_inches=0)
                plt.close()



if __name__ == "__main__":

    bartosz_order()

    #exit()
    max_tangles = 1000

    star_time = time()

    with open("data/up_to_10_group.txt") as f:

        f.readline()  # read header
        with PdfPages('algebraic-tangles_v2_temp.pdf') as pdf:

            for i in tqdm(range(max_tangles), desc="Tangles", ascii=False, ncols=100):

                # parse
                line = f.readline()
                if not line:
                    break

                line = re.sub(r'\s+', ' ', line).strip().split(" ")  # tangle string
                str_can = line[0]
                str_min = line[5]
                tangle_can = eval(str_can)
                #tangle_min = eval(str_min) if str_min != "-" else tangle_can
                t = nested_to_product(tangle_can)
                #print(tangle_can, "->", t)

                # plot
                plt.figure()
                draw(t)

                #plt.title(str_can)
                # save
                filename = "plots/" + str_can.replace(" ", "") + "_.svg"
                plt.savefig(filename, format='svg', bbox_inches='tight', pad_inches=0)
                pdf.savefig(bbox_inches='tight', pad_inches=0)
                plt.close()


    print(f"Time: {time()-star_time:.1f}s ({max_tangles/(time()-star_time):.1f} plots per second)")
