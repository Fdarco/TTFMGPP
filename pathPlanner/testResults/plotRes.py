import json
from matplotlib import pyplot as plt


def getData(fileName):
    with open(fileName, 'r') as f:
        content = f.read()
        return json.loads(content)


def segCum(inList, cumStep):
    outList = []
    segs = 0
    cnt = 0
    for elem in inList:
        segs += elem
        cnt += 1
        if cnt % cumStep == 0:
            outList.append(segs)
            segs = 0
    return outList


def plotRes(l1, l2, eID, flag, pidx, fidx):
    xx = list(range(pidx))
    plt.subplot(2, 2, fidx)
    plt.plot(xx, l1[:pidx], color='blue')
    plt.plot(xx, l2[:pidx], color='red')
    plt.legend(['TTFM', 'SUMO'])
    plt.xlabel('time')
    plt.ylabel('vehicle numbers')
    plt.title('edge {} {}'.format(eID, flag))


efiMSRI = getData('efiMSRI.json')
efoMSRI = getData('efoMSRI.json')
efiSUMO = getData('efiSUMO.json')
efoSUMO = getData('efoSUMO.json')
edgesList = tuple(efiMSRI.keys())

# inflow plot
plt.figure(figsize=(16, 11))
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

# outflow plot
plt.figure(figsize=(16, 11))
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