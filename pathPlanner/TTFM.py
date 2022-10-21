# MSRI for Mesoscopic Simulation Road Information

import heapq

from buildTopologyM import limaG, JnodeCap, Node
from constants import sEdgesInfo, getEdgeLength, jNodes, staticSD


linksTuple = tuple(limaG.links.keys())

# the capacity is smaller than 1800, so the time interval should not be 1
# otherwise, the capacity in one time interval will be less than 0.5
# no vehicle can drive into the edges
class TTFM:
    def __init__(self, name: str, simTime: int, interval: int = 5) -> None:
        self.name = name
        self.interval = interval   # default 5
        self.ifTable = {}
        self.ofTable = {}
        self.jnodeTable = {}
        self.totalIntervals = int(simTime / interval)
        for lk in linksTuple:
            self.ifTable[lk] = [0]*self.totalIntervals
            self.ofTable[lk] = [0]*self.totalIntervals

        # here we should only consider junction node
        for nod in jNodes:
            self.jnodeTable[nod] = [0]*self.totalIntervals

    # if vehicles change their destination, this function will be applied.
    def revoke(self):
        raise NotImplementedError

# shockwave speed: 19 km/h
# jam density: 220 veh/mile
class edgeInfo:
    def __init__(self, id: str, msri: TTFM) -> None:
        self.id = id
        self.msri = msri
        self.DeltaT = msri.interval
        self.length = getEdgeLength(self.id)
        self.capacity = sEdgesInfo[self.id][0] / 3600 * self.DeltaT
        if self.capacity <= 2:
            self.capacity = 2.1
        self.nlanes = sEdgesInfo[self.id][1]
        self.freeSpeed = sEdgesInfo[self.id][2]
        self.backwardSpeed = 5.28
        self.jamDensity = (220 / 1609)

    # vehicles can flow in except the road is jam
    def canFlowIn(self, currT: float) -> bool:
        if self.length < 10:
            return True
        currInterval = int(currT / self.DeltaT)
        # print('curr in interval:', currInterval)
        backwardTT = int(self.length / self.backwardSpeed / self.DeltaT)
        if currInterval - backwardTT >= 0:
            flowOutVacancy = self.msri.ofTable[self.id][currInterval - backwardTT]
        else:
            flowOutVacancy = 0
        # A^{max}(l, t)
        RoadVacancy = flowOutVacancy + self.jamDensity * self.length * self.nlanes
        if currInterval > 1:
            capIn = RoadVacancy - self.msri.ifTable[self.id][currInterval - 1]
        else:
            capIn = RoadVacancy - self.msri.ifTable[self.id][currInterval]
        if capIn > 1:
            return True
        else:
            return False

    # vehicles will stay at the node after departing the link
    # rather than arrive the next link
    def canFlowOut(self, currT: float) -> bool:
        currInterval = int(currT / self.DeltaT)
        toNodeID = self.id.split('to')[-1]
        if toNodeID in jNodes:
            toNodeCap = JnodeCap[toNodeID] * self.DeltaT / 3600
            if toNodeCap <= 2:
                toNodeCap = 2.1
            try:
                currNodeCum = self.msri.jnodeTable[toNodeID][currInterval]
            except IndexError:
                print(toNodeCap)
                print(self.capacity)
                raise IndexError
            # node capacity calibration to fit sumo simulation
            nodeVacancy = toNodeCap - 1 - currNodeCum

        else:
            nodeVacancy = 100   # represent a very large number
        if nodeVacancy >= 1:
            currOutFlow = self.msri.ofTable[self.id][currInterval]
            # print(self.id, ':', self.capacity)
            # capacity calibration to fit sumo simulation
            if currOutFlow + 1 <= self.capacity - 1:
            # if currOutFlow + 1 <= self.capacity:
                return True
            else:
                return False
        else:
            return False


    # F(l, t) = arr(l, t) + travel(l, t)
    def getOutTime(self, currT: float) -> int:
        inWait = 0
        while not self.canFlowIn(currT + inWait):
            inWait += 1
        freeTravelTime = self.length/self.freeSpeed
        preOutTime = currT + inWait + freeTravelTime
        outWait = 0
        while not self.canFlowOut(preOutTime + outWait):
            outWait += 1
        realOutTime = currT + inWait + freeTravelTime + outWait
        return realOutTime - currT, inWait


class Point:
    def __init__(self, id: str) -> None:
        self.id = id
        self.parent = None
        # travelCost = edgeTravelCost + parent.travelCost
        self.travelCost = 0
        self.totalCost = 0
        # `self.inWait` used to update MSRI.jnodeTable
        self.inWait = 0


    def getH(self, dest: Node):
        return staticSD[self.id][dest.id]


    def __lt__(self, other):
        return self.totalCost < other.totalCost


    def __hash__(self) -> int:
        return hash(self.id)


    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, self.__class__):
            return self.id == __o.id
        else:
            return False

    
    def __str__(self) -> str:
        return 'id: {}'.format(self.id)


class SearchError(Exception):
    def __init__(self, value: str) -> None:
        self.value = value


    def __str__(self) -> str:
        return repr(self.value)


class SettingError(Exception):
    def __init__(self, value: str) -> None:
        self.value = value


    def __str__(self) -> str:
        return repr(self.value)


class TDshortestPath:
    @staticmethod
    def buildPath(ep: Point): 
        if not ep.parent:
            # raise SettingError('    Destination is origin!')
            return
        path = []   
        currP = ep
        # edge, emitTime, inWait
        path.append([currP.id, currP.parent.travelCost, currP.inWait, currP.travelCost])
        while currP.parent:
            currP = currP.parent
            if currP.parent:
                path.append([currP.id, currP.parent.travelCost, currP.inWait, currP.travelCost])
            else:
                path.append([currP.id, 0, currP.inWait, currP.travelCost])
            
        path.reverse()
        npath = [nd[0] for nd in path]
        sroute = []
        for i in range(len(npath)-1):
            fnid = npath[i]
            tnid = npath[i+1]
            sroute.append(limaG.getLinkByNode(fnid, tnid).id)
        return path, sroute


    @staticmethod
    def searchPath(ori: str, des: str, dTime: float, msri: TTFM):
        # dTime: vehicle depart time
        desN = limaG.getNode(des)
        openSet = []
        oriP = Point(ori)
        heapq.heappush(openSet, oriP)
        closet = set()

        while True:
            if len(openSet) == 0:
                raise SearchError('No valid path found!')

            popP = heapq.heappop(openSet)
            if popP.id == des:
                try:
                    TDshortestPath.buildPath(popP)
                    return TDshortestPath.buildPath(popP)
                except SettingError as e:
                    print(e)
                    return

            currNode = limaG.getNode(popP.id)

            for link in currNode.outLink:
                toNode = link.toNode
                # should update Point's inWait time
                toNodeID = toNode.id
                toPoint = Point(toNodeID)
                retrieveTime = dTime + popP.travelCost
                toPoint.parent = popP
                eInfo = edgeInfo(link.id, msri) 
                edgeTravelCost, inWait = eInfo.getOutTime(retrieveTime)
                if toPoint not in closet:
                    toPoint.travelCost = toPoint.parent.travelCost + edgeTravelCost
                    toPoint.totalCost = toPoint.getH(desN) + toPoint.travelCost
                    toPoint.inWait = inWait
                    heapq.heappush(openSet, toPoint)
                elif toPoint in closet and toPoint.travelCost > popP.travelCost + edgeTravelCost:
                    toPoint.travelCost = toPoint.parent.travelCost + edgeTravelCost
                    toPoint.totalCost = toPoint.getH(desN) + toPoint.travelCost
                    toPoint.inWait = inWait
                    heapq.heappush(openSet, toPoint)
            closet.add(popP)