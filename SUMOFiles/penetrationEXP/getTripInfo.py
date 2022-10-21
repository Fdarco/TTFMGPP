import subprocess

for i in range(1, 10):
    penetration = i/10
    subprocess.run(
        [
            'sumo-gui', '-n', 'lima.net.xml', 
            '-r', 'pen%.1f.rou.xml'%penetration, 
            '--tripinfo-output', 'tripinfos/pen%.1f.tripinfo.xml'%penetration
        ]
    )