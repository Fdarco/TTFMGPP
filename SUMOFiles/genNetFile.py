import csv
from pyproj import Proj
import pandas as pd
import json


projWGS84 = Proj('+proj=aea +lat_1=25 +lat_2=47 +lon_0=105 +datum=WGS84') 


def writeNodeXML():
    nodeData = []
    with open('node.csv', 'r') as nf:
        content = csv.reader(nf)
        next(content)
        for line in content:
            nodeID = line[1]
            zoneID = line[2]
            lon = float(line[5])
            lat = float(line[6])
            x, y = projWGS84(lon, lat)
            nodeData.append([nodeID, zoneID, x, y])


    nodeDF = pd.DataFrame(nodeData, columns=['nodeID', 'zoneID', 'x', 'y'])
    minX = nodeDF['x'].min()
    minY = nodeDF['y'].min()
    print(minX)
    print(minY)
    nodeDF['x'] = nodeDF['x'].apply(lambda x: x-minX)
    nodeDF['y'] = nodeDF['y'].apply(lambda y: y-minY)


    nodeList = nodeDF.values.tolist()
    with open('lima.nod.xml', 'w', newline='') as nfw:
        print('''<nodes>''', file=nfw)
        for nd in nodeList:
            print(
                '''   <node id="{}" x="{}" y="{}"/>'''.format(nd[0], nd[3], -nd[2]), 
                file=nfw
                )
        print('''</nodes>''', file=nfw)

# the linkID in our project is different from that of NEXTA
# linkID formath is from_node_id + 'to' + to_node_id
# so we can use nodeid to find link more easily
def writeLinkXML():
    with open('link.csv', 'r') as lf:
        content = csv.reader(lf)
        lheader = next(content)
        ldata = list(content)
        
    rawDF = pd.DataFrame(ldata, columns=lheader)
    linkDF = rawDF[['link_id', 'from_node_id', 'to_node_id', 'lanes', 'capacity', 'free_speed']]
    linkList = linkDF.values.tolist()
    
    with open('lima.edge.xml', 'w', newline='') as lfw:
        print('''<edges>''', file=lfw)
        for lk in linkList:
            ffs = round(float(lk[5])/3.6, 2)
            linkID = lk[1] + 'to' + lk[2]
            print(
                '''   <edge id="{}" from="{}" to="{}" numLanes="{}" speed="{}"/>'''.format(linkID, lk[1], lk[2], lk[3], ffs),
                file=lfw
                )
        print('''</edges>''', file=lfw)


def writeLinkFFS():
    with open('link.csv', 'r') as lf:
        content = csv.reader(lf)
        lheader = next(content)
        ldata = list(content)
        
    rawDF = pd.DataFrame(ldata, columns=lheader)
    linkFFSDF = rawDF[['link_id', 'free_speed']]
    linkFFSList = linkFFSDF.values.tolist()
    linkFFSDict = {}
    for l in linkFFSList:
        linkFFSDict[l[0]] = round(float(l[1])/3.6, 2)
    jsonlinkFFS = json.dumps(linkFFSDict)
    with open('linkFFS.json', 'w') as lffsw:
        lffsw.write(jsonlinkFFS)


def genLinkDictionary():
    with open('link.csv', 'r') as lf:
        content = csv.reader(lf)
        lheader = next(content)
        ldata = list(content)

    rawDF = pd.DataFrame(ldata, columns=lheader)
    linkInfo = rawDF[['link_id', 'from_node_id', 'to_node_id']]
    linkInfoList = linkInfo.values.tolist()
    linkInfoDict = {}
    for li in linkInfoList:
        tpLinkID = li[1] + 'to' + li[2]
        linkInfoDict[tpLinkID] = li[0]

    jsonLinkDic = json.dumps(linkInfoDict)
    with open('linkDictionary.json', 'w') as ldf:
        ldf.write(jsonLinkDic)



if __name__ == '__main__':
    # writeNodeXML()
    # writeLinkXML()
    # writeLinkFFS()
    genLinkDictionary()