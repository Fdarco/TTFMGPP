# reading `lima.rou.xml` to get all vehicles travel information(depart time, 
# origin, destination etc.). The using MSRI to plan path for these vehicles.
# output the planned routes to `TMSGPP.rou.xml`.
# run `sumo-gui -n lima.net.xml -r msri.rou.xml`

from TTFM import TTFM, TDshortestPath
from constants import jNodes

import xml.etree.ElementTree as ET
from progressbar import *
import time


def getRouInfo() -> list:
    routeFile = '../SUMOFiles/lima.rou.xml'
    elementTree = ET.ElementTree(file=routeFile)
    root = elementTree.getroot()
    routesInfo = []
    for veh in root:
        departTime = float(veh.attrib['depart'])
        for rou in veh:
            edges = rou.attrib['edges']
            routesInfo.append([departTime, edges])
    
    return routesInfo


def updateTTFM(msri: TTFM, lk: str, currT: float, flag: int):
    currInterval = int(currT / msri.interval)
    if flag:
        msri.ifTable[lk][currInterval] += 1
    else:
        msri.ofTable[lk][currInterval] += 1


def updateTTFMnodeTab(msri: TTFM, nd: str, currT: float, segs: int):
    currInterval = int(currT / msri.interval)
    for i in range(segs):
            msri.jnodeTable[nd][currInterval + i] += 1


def TTFMRun(msri: TTFM, routesInfo: list):
    sTime = time.time()
    total = len(routesInfo)
    widgets = ['Progress: ', Percentage(), ' ', Bar('#'),' ', Timer()]
    pbar = ProgressBar(widgets=widgets).start()
    cnt = 0
    PlannedRoutes = []
    for row in routesInfo:
        dt = row[0]
        rou = row[1].split(' ')
        oriID = rou[0].split('to')[0]
        desID = rou[-1].split('to')[-1]
        try:
            path, sroute = TDshortestPath.searchPath(oriID, desID, dt, msri)
        except Exception as e:
            print(e)
        routeEdges = ' '.join(sroute)
        PlannedRoutes.append([dt, routeEdges])
        rNodes = [rw[0] for rw in path][1:]
        emitTimes = [rw[1] for rw in path][1:]
        inWaits = [rw[2] for rw in path][1:]
        departTimes = [rw[3] for rw in path][1:]
        for i in range(len(rNodes)):
            nd = rNodes[i]
            lk = sroute[i]
            emitime = emitTimes[i]
            inWait = inWaits[i]
            departTime = departTimes[i]
            if nd in jNodes:
                nodeTableSegs = inWait // msri.interval + 1
                updateTTFMnodeTab(msri, nd, dt+emitime, nodeTableSegs)
            
            updateTTFM(msri, lk, dt+emitime+inWait, 1)
            updateTTFM(msri, lk, dt+departTime, 0)
        cnt += 1
        pbar.update(int((cnt/(total-1))*100))
    
    eTime = time.time()
    print('\n')
    print('Run time: %.2f'%(eTime - sTime))

    return PlannedRoutes


def writeRou(vid: str, departTime: float, edges: str) -> str:
    output = '''    <vehicle id="{}" depart="{}">
        <route edges="{}"/>
    </vehicle>'''.format(vid, departTime, edges)
    return output


if __name__ == '__main__':
    # print('\n')
    testTTFM = TTFM('lima', 200000, 5)
    routesInfo = getRouInfo()
    print('Information obtained successfully.')
    plannedRoutes = TTFMRun(testTTFM, routesInfo)

    ErrorPath = set([2662, 5142, 9250, 10285, 11092, 11384])
    with open('../SUMOFiles/TTFMGPP.rou.xml', 'w') as wf:
        print('''<routes>''', file=wf)
        for i in range(len(plannedRoutes)):
            if i not in ErrorPath:
                vid = str(i)
                departTime = float(plannedRoutes[i][0])
                rEdges = plannedRoutes[i][1]
                vRou = writeRou(vid, departTime, rEdges)
                print(vRou, file=wf)
        print('''</routes>''', file=wf)