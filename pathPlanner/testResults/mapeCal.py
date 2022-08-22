import json
from turtle import color
import numpy as np
from matplotlib import pyplot as plt
# plt.style.use('Solarize_Light2')
plt.rc('font',family='Times New Roman') 

from scipy.optimize import curve_fit


def getData(fileName):
    with open(fileName, 'r') as f:
        content = f.read()
        return json.loads(content)


flowinMape = getData('flowinMAPE.json')
flowoutMape = getData('flowoutMAPE.json')


inmape = list(flowinMape.values())
outmape = list(flowoutMape.values())


def func(x, a, b, c):
    return a * np.exp(-b * x) + c


# plt.subplot(2, 1, 1)
# plt.hist(inmape, bins=50, alpha=0.6, color='#e74c3c', range=(0, 10))
# plt.ylabel('Frequency (flow in)')
# plt.subplot(2, 1, 2)
# plt.hist(outmape, bins=50, alpha=0.6, color='#3498db', range=(0, 10))
# plt.ylabel('Frequency (flow out)')
# plt.xlabel('MAE [veh]')
# plt.show()


def maehist(mae, col, ylab):
    hist, bins = np.histogram(mae, 50, range=(0, 4))
    print(hist)
    print(bins)
    hist = hist / sum(hist)
    bc = [(bins[i+1] + bins[i])/2 for i in range(len(bins)-1)]
    plt.bar(bc, hist, width=0.08, color=col, edgecolor='black',alpha=0.6)
    plt.xlabel('MAE [veh]')
    plt.ylabel('Frequency ({})'.format(ylab))


plt.figure(figsize=(10, 10))
plt.subplot(2, 1, 1)
maehist(inmape, '#e74c3c', 'flow in')
plt.subplot(2, 1, 2)
maehist(outmape, '#3498db', 'flow out')
plt.show()
# plt.savefig('histmae.eps')
exit(0)