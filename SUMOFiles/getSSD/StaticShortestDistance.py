import csv
import json
import random
from progressbar import *
from collections import defaultdict

from buidTopologyLM import limaG

allNodes = tuple(limaG.nodes.keys())
nodesCount = len(allNodes)


def getLandMarks():
    zoneNodes = defaultdict(list)
    with open('../node.csv', 'r') as nf:
        content = csv.reader(nf)
        next(content)
        cnt = 0
        for line in content:
            nodeID = line[1]
            zoneID = line[2]
            zoneNodes[zoneID].append(nodeID)

    landmarks = []
    for k, v in zoneNodes.items():
        lmID = random.choice(v)
        landmarks.append(lmID)

    return landmarks


def buildDisDict() -> defaultdict(dict):
    disDict = defaultdict(dict)
    for fn in allNodes:
        for tn in allNodes:
            if fn == tn:
                disDict[fn][tn] = 0
            else:
                try:
                    slink = limaG.getLinkByNode(fn, tn)
                    disDict[fn][tn] = slink.length/slink.freeFlowSpeed
                except KeyError:
                    disDict[fn][tn] = 100000

    return disDict


def completeDisDict(disDict: dict):
    total = nodesCount
    widgets = ['Progress: ', Percentage(), ' ', Bar('#'),' ', Timer()]
    pbar = ProgressBar(widgets=widgets).start()
    cnt = 0
    for k in allNodes:
        cnt += 1
        pbar.update(int((cnt/(total-1))*100))
        for i in allNodes:
            for j in allNodes:
                disDict[i][j] = min(disDict[i][j], disDict[i][k] + disDict[k][j])

    return disDict


def writeDisDict(cDD: dict):
    jdataSSD = json.dumps(cDD)
    with open('../SSD.json', 'w') as f:
        f.write(jdataSSD)


if __name__ == '__main__':
    DD = buildDisDict()
    cDD = completeDisDict(DD)
    writeDisDict(cDD)