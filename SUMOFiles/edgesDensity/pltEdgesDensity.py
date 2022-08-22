from random import random
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
# plt.style.use('bmh')
plt.rc('font',family='Times New Roman') 
from collections import defaultdict
import numpy as np


randomFile = '../duarouter.edgesinfo.xml'
TMSGPPFile = '../TTFMGPP.edgesinfo.xml'


def getEdgesDensity(eif: str) -> dict:
    edgesDensity = defaultdict(list)
    elementTree = ET.parse(eif)
    root = elementTree.getroot()
    for interval in root:
        for edge in interval:
            eid = edge.attrib['id']
            try:
                # some edges don't have 
                eden = float(edge.attrib['density'])
                edgesDensity[eid].append(eden)
            except:
                pass

    return edgesDensity


def writeFile():
    randomEMD = getEdgesDensity(randomFile)
    TMSGPPEMD = getEdgesDensity(TMSGPPFile)

    randomKeys = set(randomEMD.keys())
    TMSGPPKeys = set(TMSGPPEMD.keys())

    intersectionKeys = randomKeys & TMSGPPKeys

    randomMaxDen = []
    for rk, rv in randomEMD.items():
        if rk in intersectionKeys:
            randomMaxDen.append(np.average(rv))

    TTFMGPPMaxDen = []
    for tk, tv in TMSGPPEMD.items():
        if tk in intersectionKeys:
            TTFMGPPMaxDen.append(np.average(tv))

    randomMaxDen.sort()
    TTFMGPPMaxDen.sort()

    np.array(randomMaxDen).tofile('duarouterEMD.bin')
    np.array(TTFMGPPMaxDen).tofile('TTFMGPPEMD.bin')


def readFile():
    npRand = np.fromfile('duarouterEMD.bin')
    npTMS = np.fromfile('TTFMGPPEMD.bin')
    return npRand, npTMS


def pltshow(npRandomEMD, npTMSGPPEMD):
    diff = npRandomEMD - npTMSGPPEMD
    xx = list(range(len(npRandomEMD)))
    plt.figure(figsize=(9, 10))
    plt.subplot(2, 1, 1)
    plt.plot(xx, npRandomEMD)
    plt.plot(xx, npTMSGPPEMD)
    plt.fill_between(xx, npRandomEMD, npTMSGPPEMD, alpha=0.5)
    plt.ylabel('Density (veh/km)')
    plt.legend(['duarouter', 'TTFMGPP', 'difference'])

    plt.subplot(2, 1, 2)
    zeroLine = np.zeros((len(npRandomEMD), ))
    plt.plot(xx, diff, color='#45aaf2')
    plt.fill_between(xx, zeroLine, diff, alpha=0.5)
    plt.xlabel('Edges')
    plt.ylabel('Density difference (veh/km)')
    plt.savefig('DensityDiff.png')


if __name__ == '__main__':
    # writeFile()
    npRandomEMD, npTMSGPPEMD = readFile()
    pltshow(npRandomEMD, npTMSGPPEMD)