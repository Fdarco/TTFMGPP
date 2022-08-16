# using `lima.rou.xml` build MSRI and get TDSP (Time-dependent shortest path)

from TTFM import TTFM, edgeInfo, TDshortestPath
from constants import jNodes

import xml.etree.ElementTree as ET


def getRouInfo():
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

# aftering applying node model, the node table should update each step
# interval = 5 seconds
def TTFMrun(testMSRI, routesInfo):
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


# using TDshortestpath finding path
# using traci to test it
if __name__ == '__main__':
    import traci
    import time

    routesInfo = getRouInfo()
    testMSRI = TTFM('lima', 10000, 5)
    TTFMrun(testMSRI, routesInfo)

    def getRouteCost(route):
        rc = 0
        for rou in route:
            rc += traci.edge.getTraveltime(rou)
        return rc

    traci.start(
        [
            'sumo', '-n', '../SUMOFiles/lima.net.xml',
            '-r', '../SUMOFiles/lima.rou.xml'
        ]
    )

    baseRoute = "104121to104125 104125to104121 104121to104113 104113to104118 104118to104127 104127to104115 104115to104112 104112to104130 104130to104133 104133to104119 104119to104087 104087to100661 100661to100660 100660to100659 100659to100656 100656to100655 100655to100653 100653to100652 100652to100651 100651to100650 100650to100127 100127to100113 100113to100307 100307to100112 100112to102521 102521to102519 102519to102517 102517to101958 101958to101959 101959to101953 101953to100219 100219to101962 101962to101963 101963to101951 101951to101950 101950to101935 101935to101933 101933to101927 101927to101925 101925to101924 101924to101923 101923to101922 101922to101921 101921to101912 101912to102553 102553to101910 101910to104041 104041to104044 104044to104045 104045to104026 104026to104031 104031to103588 103588to103587 103587to103950 103950to103893 103893to103892 103892to103931 103931to103936 103936to103937 103937to103939 103939to103887".split(' ')
    oriNodeID = '104121'
    desNodeID = '103887'
    baseRouteFormat = '->'.join(baseRoute)
    timestep = 0
    while timestep < 500:
        traci.simulationStep()
        sTime = time.time()
        path, sRoute = TDshortestPath.searchPath(oriNodeID, desNodeID, timestep, testMSRI)
        eTime = time.time()
        sRouteFormat = '->'.join(sRoute)
        print('Base Route:', baseRouteFormat)
        print('Base Cost:', getRouteCost(baseRoute))
        print('Current Route:', sRouteFormat)
        print('Current Cost:', getRouteCost(sRoute))
        print('Search Time:', eTime - sTime)
        print('='*20)
        timestep += 1

    traci.close()



