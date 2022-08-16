# used for A* heuristics function
# only record the topoly of the network
import csv
from pyproj import Proj


class Node:
    def __init__(self, id: str, x: float, y: float) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.inLink: list[Link] = []
        self.outLink: list[Link] = []


class Link:
    def __init__(self, id, fromNode: Node, toNode: Node, length: float, ffs: float) -> None:
        self.id = id
        self.fromNode = fromNode
        self.toNode = toNode
        self.length = length
        self.freeFlowSpeed = ffs


class Graph:
    def __init__(self, name) -> None:
        self.name = name
        self.nodes = {}
        self.links = {}


    def addNode(self, nid: str, node: Node) -> None:
        self.nodes[nid] = node


    def addLink(self, lid: str, link: Link) -> None:
        self.links[lid] = link


    def getNode(self, nid: str) -> Node:
        return self.nodes[nid]


    def getLink(self, lid: str) -> Link:
        return self.links[lid]


    def getLinkByNode(self, fnid: str, tnid: str) -> Link:
        linkID = fnid + 'to' + tnid
        return self.getLink(linkID)


limaG = Graph('lima')
projWGS84 = Proj('+proj=aea +lat_1=25 +lat_2=47 +lon_0=105 +datum=WGS84') 

# move the mini point of the network to (0, 0)
minX = 8136292.760690171
minY = 13848313.414035358


with open('../node.csv', 'r') as nf:
    content = csv.reader(nf)
    next(content)
    for line in content:
        nodeID = line[1]
        zoneID = line[2]
        lon = float(line[5])
        lat = float(line[6])
        rawx, rawy = projWGS84(lon, lat)
        rawx -= minX
        rawy -= minY
        # sx, sy for (x, y) coordination in SUMO
        sx = rawy
        sy = -rawx
        nod = Node(nodeID, sx, sy)
        limaG.addNode(nodeID, nod)

# the linkID is formatted as fromNodeID + 'to' + toNodeID
# for search link more easily
with open('../link.csv') as lf:
    # 0 name
    # 1 link_id
    # 2 from_node_id
    # 3 to_node_id
    # 4 facility_type
    # 5 dir_flag
    # 6 length
    # 7 lanes
    # 8 capacity
    # 9 free_speed
    # 10 link_type
    # 11 cost
    # 12 VDF_cap1
    # 13 VDF_alpha1
    # 14 VDF_beta1
    # 15 VDF_PHF1
    # 16 VDF_gamma1
    # 17 VDF_mu1
    content = csv.reader(lf)
    next(content)
    for line in content:
        # linkID = line[1]
        fromNodeID = line[2]
        toNodeID = line[3]
        length = float(line[6])*1000
        ffs = float(line[9])/3.6
        linkID = fromNodeID + 'to' + toNodeID

        fromNode = limaG.getNode(fromNodeID)
        toNode = limaG.getNode(toNodeID)
        lin = Link(linkID, fromNode, toNode, length, ffs)
        fromNode.outLink.append(lin)
        toNode.inLink.append(lin)
        limaG.addLink(linkID, lin)


if __name__ == '__main__':
    tn = limaG.getNode('218')
    tnol = tn.outLink
    for ol in tnol:
        print(ol.id)