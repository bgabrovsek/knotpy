import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mc

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

num = 1000
sizes = 50 * np.random.random(num)
xy = 10 * np.random.random((num, 2))

patches = [plt.Circle(center, size) for center, size in zip(xy, sizes)]
fig, ax = plt.subplots()

collection = mc.CircleCollection(sizes, offsets=xy, transOffset=ax.transData, color='green')
ax.add_collection(collection)

ax.margins(0.01)

plt.show()