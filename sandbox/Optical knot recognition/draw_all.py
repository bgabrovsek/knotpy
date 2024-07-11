# draw all diagrams

import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm

import knotpy as kp

plot_folder = Path("plots")

with open("pd.txt", 'r') as file:
    lines = file.readlines()

knots = [kp.from_pd_notation(line.strip().split(" - ")[3]) for line in lines][:20]

print("Plotting diagrams")
for index, k in enumerate(tqdm(knots)):
    plt.close()
    kp.draw(k)
    plt.savefig(plot_folder / f"{index:04}.png")
