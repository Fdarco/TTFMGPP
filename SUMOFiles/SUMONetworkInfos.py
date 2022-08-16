import xml.etree.ElementTree as ET
import json
import csv
import re


def getLanesLength():
    lanesLength = {}
    tree = ET.parse('lima.net.xml')
    root = tree.getroot()
    for child in root:
        if child.tag == 'edge':
            edgeID = child.attrib['id']
            if not re.match(':', edgeID):
                for grandChild in child:
                    laneID = grandChild.attrib['id']
                    laneLength = grandChild.attrib['length']
                    lanesLength[laneID] = float(laneLength)
    
    jdatall = json.dumps(lanesLength)
    with open('lanesLength.json', 'w') as jf:
        jf.write(jdatall)

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
def getEdgesInfo():
    edgesInfo = {}
    with open('link.csv', 'r') as lf:
        content = csv.reader(lf)
        next(content)
        for line in content:
            fnID = line[2]
            tnID =  line[3]
            lid = fnID + 'to' + tnID
            capacity = float(line[8])
            if capacity == 1800.0:
                capacity -= 1000
            nlanes = int(line[7])
            freeSpeed = float(line[9]) / 3.6
            edgesInfo[lid]= [capacity, nlanes, freeSpeed]

    jdataEI = json.dumps(edgesInfo)
    with open('edgesInfoFromNodecsv.json', 'w') as eif:
        eif.write(jdataEI)


def SUMOJunctionInfo():
    sumoJuncIDs = []
    sumoJuncTypes = []
    sumoJuncReqNum = []
    tree = ET.parse('lima.net.xml')
    root = tree.getroot()
    for child in root:
        if child.tag == 'junction':
            if not re.match(':', child.attrib['id']):
                sumoJuncIDs.append(child.attrib['id'])
                sumoJuncTypes.append(child.attrib['type'])
                requestNum = 0
                for gc in child:
                    requestNum += 1
                sumoJuncReqNum.append(requestNum)


    return sumoJuncIDs, sumoJuncTypes, sumoJuncReqNum


if __name__ == '__main__':
    getLanesLength()
    getEdgesInfo()
    # sjIDs = set(sjIDs)
    # nodeIDs = set()
    # with open('node.csv', 'r') as f:
    #     content = csv.reader(f)
    #     next(content)
    #     for line in content:
    #         nodeIDs.add(line[1])

    # print(nodeIDs - sjIDs)
    # print(sjIDs - nodeIDs)
    # modelNodes = []
    # sjIDs, sjTypes, sjReqNums = SUMOJunctionInfo()
    # for i in range(len(sjIDs)):
    #     if sjReqNums[i] > 2:
    #         modelNodes.append(sjIDs[i])

    # modelNodes = set(modelNodes)
    # print(nodeIDs - modelNodes)