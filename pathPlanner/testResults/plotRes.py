import json
from matplotlib import pyplot as plt
plt.rc('font',family='Times New Roman') 
from scipy.interpolate import make_interp_spline

import numpy as np


def getData(fileName):
    with open(fileName, 'r') as f:
        content = f.read()
        return json.loads(content)


def segCum(inList, cumStep):
    outList = []
    segs = []
    cnt = 0
    for elem in inList:
        segs.append(elem)
        cnt += 1
        if cnt % cumStep == 0:
            outList.append([sum(segs), np.std(segs)])
            segs = []
    return outList


def boundLines(ll, pidx, col, lab):
    xx = list(range(pidx))
    l_count = [row[0] for row in ll][:pidx]
    l_std = [row[1] for row in ll][:pidx]
    l_upbound = [l_count[i] + l_std[i] for i in range(len(l_count))]
    l_downbound = [l_count[j] - l_std[j] for j in range(len(l_count))]
    xx_smooth = np.linspace(min(xx), max(xx), 300)
    l_upbound_smooth = make_interp_spline(xx, l_upbound)(xx_smooth)
    l_count_smooth = make_interp_spline(xx, l_count)(xx_smooth)
    l_downbound_smooth = make_interp_spline(xx, l_downbound)(xx_smooth)

    plt.plot(xx_smooth, l_upbound_smooth, color=col, alpha=0)
    plt.plot(xx_smooth, l_count_smooth, color=col, label=lab)
    plt.plot(xx_smooth, l_downbound_smooth, color=col, alpha=0)
    plt.fill_between(xx_smooth, l_count_smooth, l_upbound_smooth, color=col, alpha=0.5)
    plt.fill_between(xx_smooth, l_downbound_smooth, l_count_smooth, color=col, alpha=0.5)


def plotRes(l1, l2, eID, flag, pidx, fidx):
    xx = list(range(pidx))
    plt.subplot(2, 2, fidx)
    boundLines(l1, pidx, '#3498db', 'TTFM')
    boundLines(l2, pidx, '#e74c3c', 'SUMO')
    plt.legend()
    plt.xlabel('time')
    plt.ylabel('vehicle numbers')
    plt.title('{} {}'.format(eID, flag))


efiMSRI = getData('efiMSRI.json')
efoMSRI = getData('efoMSRI.json')
efiSUMO = getData('efiSUMO.json')
efoSUMO = getData('efoSUMO.json')
edgesList = tuple(efiMSRI.keys())


# ed = edgesList[0]
# msriFlowIn = efiMSRI[ed]
# msriFlowInFiveMinutes = segCum(msriFlowIn, 60)
# sumoFlowIn = efiSUMO[ed] 
# sumoFlowInFiveMinutes = segCum(sumoFlowIn, 5)
# plotRes(msriFlowInFiveMinutes, sumoFlowInFiveMinutes, 'edge-%i'%(1), 'flow-in', 30, 1)
# plt.show()


plt.figure(figsize=(16, 11))
plt.grid(linestyle='-.')
for i in range(len(edgesList)):
    ed = edgesList[i]
    msriFlowIn = efiMSRI[ed]
    msriFlowInFiveMinutes = segCum(msriFlowIn, 60)
    sumoFlowIn = efiSUMO[ed] 
    sumoFlowInFiveMinutes = segCum(sumoFlowIn, 5)
    plotRes(msriFlowInFiveMinutes, sumoFlowInFiveMinutes, 'edge-%i'%(i+1), 'flow-in', 25, i+1)

plt.subplots_adjust(wspace=0.2, hspace=0.4)
plt.savefig('flowInCompare.png')
plt.close()
# plt.show()

plt.figure(figsize=(16, 11))
plt.grid(linestyle='-.')
for i in range(len(edgesList)):
    ed = edgesList[i]
    msriFlowOut = efoMSRI[ed]
    msriFlowOutFiveMinutes = segCum(msriFlowOut, 60)
    sumoFlowOut = efoSUMO[ed] 
    sumoFlowOutFiveMinutes = segCum(sumoFlowOut, 5)
    plotRes(msriFlowOutFiveMinutes, sumoFlowOutFiveMinutes, 'edge-%i'%(i+1), 'flow-out', 25, i+1)

plt.subplots_adjust(wspace=0.2, hspace=0.4)
plt.savefig('flowOutCompare.png')
plt.close()
# plt.show()