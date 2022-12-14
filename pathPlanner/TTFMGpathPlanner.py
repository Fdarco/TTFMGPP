# reading `lima.rou.xml` to get all vehicles travel information(depart time, 
# origin, destination etc.). The using MSRI to plan path for these vehicles.
# output the planned routes to `TMSGPP.rou.xml`.
# run `sumo-gui -n lima.net.xml -r msri.rou.xml`

from TTFM import TTFM, TDshortestPath
from constants import jNodes, staticSD

import xml.etree.ElementTree as ET
from progressbar import *
from collections import defaultdict
import time
import sys


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
    
    routesInfo.sort(key=lambda x: x[0])
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

# 把路径按照出发时间分批次，每个批次内的车辆都是同时发出请求的
# 批次的定义是 1 秒内
def rouBatch(routeInfo: list):
    batchRoute = [[] for _ in range(3600)]
    for rou in routeInfo:
        dt = rou[0]
        batchRoute[int(dt)].append(rou)

    return batchRoute


def obtainPriority(br: list[list]):
    for row in br:
        rou = row[1].split(' ')
        oriID = rou[0].split('to')[0]
        desID = rou[-1].split('to')[-1]
        p1 = staticSD[oriID][desID]
        row.append(p1)
        p2 = staticSD['100027'][oriID]
        row.append(p2)


# 考虑驾驶员可能“同时”发送路径规划的请求，需要定义驾驶员间的优先关系
# 这里的“同时”我们界定为同一秒内
# “同时”发出请求的车辆按照下面的规则进行优先权的获取
# -- 起点和终点间的 static shortest distance (SSD)： SSD 小的请求优先被处理： 
#    因为 SSD 小的距离目的地更近，进行路段选择的机会更少，
#    所以应该优先被处理，这样可以尽可能减少次序产生的影响；
# -- 对于 SSD 也一样（或接近）的请求，则看请求发出的位置，如果是中心区发出的请求，则优先处理，
#    如果是郊区发送的请求就晚一些处理。因为中心区容易拥堵，用户的选择更少，而郊区选择要多一些。
#    当然，从中心区到郊区的的划分本身也是线性的，假如路网中心点坐标为 (0, 0), 然后发出请求
#    的位置离 (0, 0) 越远则优先级越低，这个距离是直接用 SSD ， 而不是欧式距离
#    PS: the center node is 100027, position is (25434.69,10871.47)
def sortPriority(routesInfo: list):
    batchRoute = rouBatch(routesInfo)
    seqRoutes = []
    for br in batchRoute:
        if len(br) == 0:
            continue
        if len(br) == 1:
            seqRoutes.append(br[0])
            continue
        # 获取每个请求的 p1 和 p2
        obtainPriority(br)
        br.sort(key=lambda x: (x[2], x[3]))
        for rou in br:
            seqRoutes.append(rou)

    return seqRoutes


def TTFMRun(msri: TTFM, routesInfo: list):
    sTime = time.time()
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
            # print(e)
            pass
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
        sys.stdout.write('\r' + 'Processing: ' + str(round(cnt/len(routesInfo), 4)))
        sys.stdout.flush()
    
    eTime = time.time()
    print('\n')
    print('Run time: %.2f'%(eTime - sTime))

    return PlannedRoutes


def writeRou(vid: str, departTime: float, edges: str) -> str:
    output = '''    <vehicle id="{}" depart="{}">
        <route edges="{}"/>
    </vehicle>'''.format(vid, departTime, edges)
    return output


def genConn(fileName: str) -> dict:
    conn = defaultdict(list)
    elementTree = ET.ElementTree(file=fileName)
    root = elementTree.getroot()
    for child in root:
        if child.tag == 'connection':
            fromEdge = child.attrib['from']
            toEdge = child.attrib['to']
            if (':' not in fromEdge) and (':' not in toEdge):
                conn[fromEdge].append(toEdge)
    return conn


def checkRoute(rou: str, conn: dict) -> bool:
    edges = rou.split(' ')
    for i in range(len(edges) - 1):
        fromEdge = edges[i]
        toEdge = edges[i+1]
        if toEdge not in conn[fromEdge]:
            return False
    return True


if __name__ == '__main__':
    # print('\n')
    testTTFM = TTFM('lima', 200000, 5)
    routesInfo = getRouInfo()
    # seqRoutesInfo = sortPriority(routesInfo)
    # print(seqRoutesInfo)

    print('Information obtained successfully.')
    plannedRoutes = TTFMRun(testTTFM, routesInfo)

    validRoutes = []
    invalidCnt = 0
    conn = genConn('../SUMOFiles/lima.net.xml')
    for vid in range(len(plannedRoutes)):
        dt = plannedRoutes[vid][0]  
        rou = plannedRoutes[vid][1]
        if not checkRoute(rou, conn):
            invalidCnt += 1
        else:
            validRoutes.append(plannedRoutes[vid])
    print('invalid route count:', invalidCnt)

    # the topology generated by `buildTopologyM.py` is a little different from 
    # that of SUMO. The below roads can't find a valid connections, so we should
    # remove them. But this will not make big impacts to the final results.
    # we finally generate 31855 vehicles in `TTFMGPP.rou.xml` which have the 
    # same start point, end point and departure time as those in `lima.rou.xml`. 
    # The number of vehicles in `lima.rou.xml` is 31861, so these roads cause few impacts.
    ErrorPath = set([2662, 5142, 9250, 10285, 11092, 11384])
    with open('../SUMOFiles/TTFMGPP.rou.xml', 'w') as wf:
        print('''<routes>''', file=wf)
        for i in range(len(validRoutes)):
            if i not in ErrorPath:
                vid = str(i)
                departTime = float(validRoutes[i][0])
                rEdges = validRoutes[i][1]
                vRou = writeRou(vid, departTime, rEdges)
                print(vRou, file=wf)
        print('''</routes>''', file=wf)


# 100234to101790