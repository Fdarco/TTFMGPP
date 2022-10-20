# 有关 CV 渗透率 p 的实验，将纯 HV 作为历史流量
# 用历史流量乘以 (1-p) 作为路段上的 HV 交通流

from TTFM import TTFM, edgeInfo, TDshortestPath
from constants import jNodes

import xml.etree.ElementTree as ET

import random
import time
from progressbar import *
import sys


def getRouInfo(rf: str):
    if not rf:
        routeFile = '../SUMOFiles/lima.rou.xml'
    else:
        routeFile = rf
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

# aftering applying node model, the node table should update each step
# interval = 5 seconds
def TTFMRes(testMSRI, routesInfo):
    for row in routesInfo:
        dt = row[0]
        rou = row[1].split(' ')
        for lk in rou:
            lkEI = edgeInfo(lk, testMSRI)
            inwait = 0
            while not lkEI.canFlowIn(dt + inwait):
                inwait += 1
            # if vehicle flow out upstream link, and can't flow into the downstream link
            # it will stay in the end node of the upstream link i.e. the 
            # start node of the downstream link
            nodeID = lk.split('to')[0]
            if nodeID in jNodes:
                nodeTableSegs = inwait // testMSRI.interval + 1
                updateTTFMnodeTab(testMSRI, nodeID, dt, nodeTableSegs)
            dt += inwait
            updateTTFM(testMSRI, lk, dt, 1)
            FFTT = lkEI.length / lkEI.freeSpeed
            dt += FFTT
            outWait = 0
            while not lkEI.canFlowOut(dt + outWait):
                outWait += 1
            dt += outWait
            updateTTFM(testMSRI, lk, dt, 0)


def penRedunction(tm: TTFM, penetration: float) -> TTFM:
    hp = 1 - penetration
    ntm = TTFM('pen%f'%penetration, 10000, 5)
    for ki, vi in tm.ifTable.items():
        nvi = [ei * hp for ei in vi]
        ntm.ifTable[ki] = nvi
    for ko, vo in tm.ofTable.items():
        nvo = [eo * hp for eo in vo]
        ntm.ofTable[ko] = nvo
    for kn, vn in tm.jnodeTable.items():
        nvn = [en * hp for en in vn]
        ntm.jnodeTable[kn] = nvn

    return ntm


def TTFMPenRun(tm: TTFM, routesInfo: list, penetration: float):
    print('\nRoutes are planning with CV penetration %.1f'%penetration)
    sTime = time.time()
    plannedRoutes = []
    cnt = 0
    for row in routesInfo:
        rnum = random.uniform(0, 1)
        # 当随机数小于渗透率就认为这辆车是 CV 
        if rnum < penetration:
            dt = row[0]
            rou = row[1].split(' ')
            oriID = rou[0].split('to')[0]
            desID = rou[-1].split('to')[-1]
            try:
                path, sroute = TDshortestPath.searchPath(oriID, desID, dt, tm)
            except Exception as e:
                # print(e)
                pass
            routeEdges = ' '.join(sroute)
            plannedRoutes.append([dt, routeEdges])
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
                    nodeTableSegs = inWait // tm.interval + 1
                    updateTTFMnodeTab(tm, nd, dt+emitime, nodeTableSegs)
                
                updateTTFM(tm, lk, dt+emitime+inWait, 1)
                updateTTFM(tm, lk, dt+departTime, 0)
        else:
            plannedRoutes.append(row)
        cnt += 1
        sys.stdout.write('\r' + 'Processing: ' + str(round(cnt/len(routesInfo), 4)))
        sys.stdout.flush()

    eTime = time.time()
    print('\nRoutes has been planned with CV penetration %.1f, planning time: %.2f'%(penetration, (eTime - sTime)))
    return plannedRoutes


def writeRou(vid: str, departTime: float, edges: str) -> str:
    output = '''    <vehicle id="{}" depart="{}">
        <route edges="{}"/>
    </vehicle>'''.format(vid, departTime, edges)
    return output


if __name__ == '__main__':
    from copy import deepcopy

    # 纯 HV 环境下的背景交通流
    routesInfo = getRouInfo('../SUMOFiles/lima.rou.xml')
    print('Route infomation extracted sucessfully.')
    # full HV historical TTFM
    fullHVTTFM = TTFM('lima', 25000, 5)
    TTFMRes(fullHVTTFM, routesInfo)
    print('Full HV background TTFM generated successfully.')

    for i in range(1, 10):
        penetration = round(i/10, 1)
        pTTFM = penRedunction(fullHVTTFM, penetration)
        plannedRoutes = TTFMPenRun(pTTFM, routesInfo, penetration)
        # the topology generated by `buildTopologyM.py` is a little different from 
        # that of SUMO. The below roads can't find a valid connections, so we should
        # remove them. But this will not make big impacts to the final results.
        # we finally generate 31855 vehicles in `TTFMGPP.rou.xml` which have the 
        # same start point, end point and departure time as those in `lima.rou.xml`. 
        # The number of vehicles in `lima.rou.xml` is 31861, so these roads cause few impacts.
        ErrorPath = set([2662, 5142, 9250, 10285, 11092, 11384])
        with open('../SUMOFiles/penetrationEXP/pen%.1f.rou.xml'%penetration, 'w') as wf:
            print('''<routes>''', file=wf)
            for i in range(len(plannedRoutes)):
                if i not in ErrorPath:
                    vid = str(i)
                    departTime = float(plannedRoutes[i][0])
                    rEdges = plannedRoutes[i][1]
                    vRou = writeRou(vid, departTime, rEdges)
                    print(vRou, file=wf)
            print('''</routes>''', file=wf)