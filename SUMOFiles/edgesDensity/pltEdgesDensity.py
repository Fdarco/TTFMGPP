from random import random
from turtle import color
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
# plt.style.use('bmh')
plt.rc('font',family='Times New Roman', size=20) 
from collections import defaultdict
import numpy as np


randomFile = '../duarouter.edgesinfo.xml'
PPPFile = '../PPP.edgesinfo.xml'
ARNMFile = '../TTFMGPP.edgesinfo.xml'


def getEdgesDensity(eif: str) -> dict:
    edgesDensity = defaultdict(list)
    elementTree = ET.parse(eif)
    root = elementTree.getroot()
    for interval in root:
        for edge in interval:
            eid = edge.attrib['id']
            try:
                # some edges don't have attribute 'density'
                eden = float(edge.attrib['density'])
                edgesDensity[eid].append(eden)
            except:
                pass

    return edgesDensity


def writeFile():
    randomEMD = getEdgesDensity(randomFile)
    PPPEMD = getEdgesDensity(PPPFile)
    ARNMEMD = getEdgesDensity(ARNMFile)

    randomKeys = set(randomEMD.keys())
    ARNMKeys = set(ARNMEMD.keys())
    PPPKeys = set(PPPEMD.keys())

    intersectionKeys = randomKeys & ARNMKeys & PPPKeys

    randomAvgDen = []
    for rk, rv in randomEMD.items():
        if rk in intersectionKeys:
            randomAvgDen.append(np.max(rv))

    ARNMAvgDen = []
    for tk, tv in ARNMEMD.items():
        if tk in intersectionKeys:
            ARNMAvgDen.append(np.max(tv))

    PPPAvgDen = []
    for pk, pv in PPPEMD.items():
        if pk in intersectionKeys:
            PPPAvgDen.append(np.max(pv))

    randomAvgDen.sort()
    ARNMAvgDen.sort()
    PPPAvgDen.sort()

    np.array(randomAvgDen).tofile('duarouterEMD.bin')
    np.array(ARNMAvgDen).tofile('ARNMEMD.bin')
    np.array(PPPAvgDen).tofile('PPPEMD.bin')


def readFile():
    npRand = np.fromfile('duarouterEMD.bin')
    npARNM = np.fromfile('ARNMEMD.bin')
    npPPP = np.fromfile('PPPEMD.bin')
    return npRand, npARNM, npPPP


def pltshow(npRandomEMD, npARNMEMD, npPPPEMD):
    diff_1 = npRandomEMD - npARNMEMD
    diff_2 = npPPPEMD - npARNMEMD
    xx = list(range(len(npRandomEMD)))
    plt.figure(figsize=(8, 9.2))
    plt.subplot(2, 1, 1)
    plt.plot(xx, npRandomEMD)
    plt.plot(xx, npPPPEMD, color='gray')
    plt.plot(xx, npARNMEMD)

    plt.gca().xaxis.set_major_locator(plt.NullLocator())

    # plt.fill_between(xx, npRandomEMD, npARNMEMD, alpha=0.5)
    plt.ylabel('Density (veh/km)')
    plt.legend(['duarouter', 'PPP', 'ARNM'])

    plt.subplot(2, 1, 2)
    zeroLine = np.zeros((len(npRandomEMD), ))
    plt.plot(xx, diff_1, color='#45aaf2')
    shadow1 = plt.fill_between(xx, zeroLine, diff_1, color='#45aaf2', alpha=0.5)
    plt.plot(xx, diff_2, color='#e67e22')
    shadow2 = plt.fill_between(xx, zeroLine, diff_2, color='#e67e22', alpha=0.5)
    plt.legend([shadow1, shadow2], ['duarouter - ARNM', 'PPP - ARNM'])
    plt.xlabel('Edges')
    plt.ylabel('Density difference (veh/km)')
    plt.subplots_adjust(hspace=0.05)

    plt.savefig('maxDensityDiff.png', bbox_inches='tight', pad_inches=0.2)


if __name__ == '__main__':
    writeFile()
    npRandomEMD, npARNMEMD, npPPPEMD = readFile()
    # print(len(npRandomEMD))
    pltshow(npRandomEMD[-500:], npARNMEMD[-500:], npPPPEMD[-500:])