import csv
from collections import defaultdict

def genTrips():
    tripsDict = defaultdict(dict)
    with open('demand.csv', 'r') as df:
        content = csv.reader(df)
        next(content)
        for line in content:
            o_zone_id = line[0]
            d_zone_id = line[1]
            volume = int(line[2])
            tripsDict[o_zone_id][d_zone_id] = volume

    with open('lima.od.xml', 'w') as tf:
        print('''<demand>''', file=tf)
        print('''    <actorConfig id="DEFAULT_VEHTYPE">''', file=tf)
        print('''        <timeSlice duration="3600000" startTime="0">''', file=tf)
        for k, v in tripsDict.items():
            for tn, vo in v.items():
                if k != '149' and tn != '149':   # zone id '149' is missing in node.csv
                    print('''            <odPair amount="{}" destination="{}" origin="{}"/>'''.format(
                        vo, tn, k
                    ), file=tf)

        print('''        </timeSlice>''', file=tf)
        print('''    </actorConfig>''', file=tf)
        print('''</demand>''', file=tf)


if __name__ == '__main__':
    genTrips()