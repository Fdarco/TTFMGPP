# used for A* heuristics function
# only record the topoly of the network
import csv
from pyproj import Proj

# for each node, can define it's type according to it's `inLink` and `outLink`
# if `len(Node.inLink) > 1`, this Node will be a merge node
# if `len(Node.outLink) > 1`, this Node  will be a diverge node.
class Node:
    def __init__(self, id: str, zoneID: str) -> None:
        self.id = id
        self.zoneID = zoneID
        self.inLink: list[Link] = []
        self.outLink: list[Link] = []

    # the way calculate node capacity is wrong
    # consider this senario: node is not a junction but a connector
    # one direction (e.g. the below one) is jam, it will occupy all this node's capacity
    # then the vehicles in the upper two links can't move on
    # to solve this problem we need to get road connections infomation
    # <----    <----
    #       n
    # ---->    ---->
    # if node is a connector, return next link
    # if node is a junction, return node capacity
    # when node is a connector, the cap^{out} of the link will be:
    # cap^{out}(l, t) = min(q^{max}(l), cap^{in}(l+1, t))
    # when the node is a junction, the cap^{out} of the link will be:
    # cap^{out}(l, t) = min(q^{max}(l), node capacity - node table(t))
    def calCap(self) -> float:
        nCap = 0
        nLinks = len(self.inLink)
        for lk in self.inLink:
            nCap += lk.capacity / nLinks

        return nCap


    def __str__(self) -> str:
        return 'id: {}, zoneID: {}'.format(self.id, self.zoneID)


class Link:
    def __init__(self, id, fromNode: Node, toNode: Node, capacity: float) -> None:
        self.id = id
        self.fromNode = fromNode
        self.toNode = toNode
        self.capacity = capacity


    def __str__(self) -> str:
        return 'id: {}, capacity: {}'.format(self.id, self.capacity)


class Graph:
    def __init__(self, name) -> None:
        self.name = name
        self.nodes: dict(Node) = {}
        self.links: dict(Node) = {}


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


with open('../SUMOFiles/node.csv', 'r') as nf:
    content = csv.reader(nf)
    next(content)
    for line in content:
        nodeID = line[1]
        zoneID = line[2]
        nod = Node(nodeID, zoneID)
        limaG.addNode(nodeID, nod)

# the linkID is formatted as fromNodeID + 'to' + toNodeID
# for search link more easily
with open('../SUMOFiles/link.csv') as lf:
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
        linkID = fromNodeID + 'to' + toNodeID
        capacity = float(line[8])

        fromNode = limaG.getNode(fromNodeID)
        toNode = limaG.getNode(toNodeID)
        lin = Link(linkID, fromNode, toNode, capacity)
        fromNode.outLink.append(lin)
        toNode.inLink.append(lin)
        limaG.addLink(linkID, lin)


def getJnodeCap():
    JnodeCap = {}
    for k, v in limaG.nodes.items():
        JnodeCap[k] = v.calCap()

    # node capacity calibration to fit sumo
    nodeslist = [101790, 101852, 101862, 101758, 101791, 100234, 101792, 100177, 101896, 100171, 101795, 100311]
    for node in nodeslist:
        JnodeCap[str(node)] = 1800
    return JnodeCap


JnodeCap = getJnodeCap()

def genTAZ(Gra: Graph):
    TAZedges = {}
    for v in Gra.nodes.values():
        zoneID = v.zoneID
        TAZedges[zoneID] = [e.id for e in v.outLink]
    
    with open('../SUMOFiles/lima.add.xml', 'w') as af:
        print('''<additional>''', file=af)
        for k, v in TAZedges.items():
            print('''    <taz id="{}" edges="{}"/>'''.format(k, ' '.join(v)), file=af)
        print('''</additional>''', file=af)


if __name__ == '__main__':
    # jamEdges = ['101791to101790', '101792to101791', '100234to101790', '101794to101790']
    # for ed in jamEdges:
    #     el = limaG.getLink(ed)
    #     print(el)
    # genTAZ(limaG)
    nodeslist = [101790, 101852, 101862, 101758, 101791, 100234, 101792, 100177, 101896, 100171, 101795, 100311]
    for node in nodeslist:
        print(node)
        print(JnodeCap[str(node)]/3600*5)


    # for v in limaG.nodes.values():
    #     if v.zoneID == '149':
    #         print(v)