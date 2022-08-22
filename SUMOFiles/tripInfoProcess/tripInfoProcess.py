# import xml.etree.ElementTree as ET

import pandas as pd
import seaborn as sns
sns.set_theme(style="whitegrid")
from matplotlib import pyplot as plt
plt.style.use('classic')
plt.rc('font',family='Times New Roman') 


# Index(['id', 'depart', 'departLane', 'departPos', 'departSpeed', 'departDelay',
#        'arrival', 'arrivalLane', 'arrivalPos', 'arrivalSpeed', 'duration',
#        'routeLength', 'waitingTime', 'waitingCount', 'stopTime', 'timeLoss',
#        'rerouteNo', 'devices', 'vType', 'speedFactor', 'vaporized'],
#       dtype='object')


duarouterTripInfo = pd.read_xml('../duarouter.tripinfo.xml', )
TMSGPPTripInfo = pd.read_xml('../TTFMGPP.tripinfo.xml')


duaTravelTime = duarouterTripInfo['duration'].copy()   # pd.Serise
duaTimeLoss = duarouterTripInfo['timeLoss'].copy()
TMSGPPTravelTime = TMSGPPTripInfo['duration'].copy()
TMSGPPTimeLoss = TMSGPPTripInfo['timeLoss'].copy()


duaType = pd.Series(['duarouter']*duaTravelTime.shape[0])
TMSGPPType = pd.Series(['TTFMGPP']*TMSGPPTravelTime.shape[0])

travelTimeSerise = pd.concat([duaTravelTime, TMSGPPTravelTime])
timeLossSerise = pd.concat([duaTimeLoss, TMSGPPTimeLoss])
TypeSerise = pd.concat([duaType, TMSGPPType])


travelTimeDF = pd.DataFrame({'Travel time (s)': travelTimeSerise, 'Types': TypeSerise})
timeLossDF = pd.DataFrame({'Time loss (s)': timeLossSerise, 'Types': TypeSerise})


plt.figure(figsize=(9, 10))
sns.violinplot(
    x="Types", y="Travel time (s)", data=travelTimeDF, 
    cale="count", inner="quartile", palette="pastel"
    )
plt.savefig('travelTime.png')
# plt.show()


plt.figure(figsize=(9, 10))
sns.violinplot(
    x='Types', y='Time loss (s)', data=timeLossDF,
    scale="count", inner="quartile", palette="pastel"
    )
plt.savefig('timeLoss.png')
# plt.show()
