from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot as plt
import numpy as np


networkX = [
    [0, 1500], [0, 1500], [0, 1500], [0, 1500], 
    [0, 0], [500, 500], [1000, 1000], [1500, 1500]
]

networkY = [
    [0, 0], [500, 500], [1000, 1000], [1500, 1500],
    [0, 1500], [0, 1500], [0, 1500], [0, 1500], 
]

routes = [
    [
        [0, 0, 0], [500, 0, 0], [500, 0, 10], [500, 500, 10],
        [500, 500, 20], [1000, 500, 20], [1000, 500, 30], [1000, 1000, 30],
        [1000, 1000, 40], [1500, 1000, 40], [1500, 1000, 50], [1500, 1500, 50]
    ],
    [
        [0, 500, 10], [500, 500, 10], [500, 500, 20], [500, 1000, 20],
        [500, 1000, 30], [1000, 1000, 30], [1000, 1000, 40], [1000, 1500, 40],
        [1000, 1500, 50], [1500, 1500, 50]
    ],
    [
        [0,1000, 10], [500, 1000, 10], [500, 1000, 20], [1000, 1000, 20],
        [1000, 1000, 30], [1000, 1500, 30], [1000, 1500, 40], [1500, 1500, 40]
    ]
]

colors = ['orange', 'green', 'blue']

fig = plt.figure(figsize=(15, 15))
ax = fig.add_subplot(projection='3d')
ax.set_box_aspect((4, 4, 6))
ax.grid(False)
# ax.set_xticks([])
# ax.set_yticks([])
# ax.set_zticks([])
plt.axis('off')

for i in range(6):
    timeZ = i * 10
    for j in range(len(networkX)):
        ax.plot(networkX[j], networkY[j], timeZ, color='gray', linestyle='--')

for k in range(len(routes)):
    ax.plot(*zip(*routes[k]), color=colors[k], alpha=0.8)
plt.show()