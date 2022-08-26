# import xml.etree.ElementTree as ET

from turtle import position
import pandas as pd
import seaborn as sns
sns.set_theme(style="ticks",font='Times New Roman',font_scale=1.4)
from matplotlib import pyplot as plt


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

print(duaTravelTime.describe())
print(duaTimeLoss.describe())
print(TMSGPPTravelTime.describe())
print(TMSGPPTimeLoss.describe())


duaType = pd.Series(['duarouter']*duaTravelTime.shape[0])
TMSGPPType = pd.Series(['TTFMGPP']*TMSGPPTravelTime.shape[0])

travelTimeSerise = pd.concat([duaTravelTime, TMSGPPTravelTime])
timeLossSerise = pd.concat([duaTimeLoss, TMSGPPTimeLoss])
TypeSerise = pd.concat([duaType, TMSGPPType])

# print(travelTimeSerise.describe())
# print(timeLossSerise.describe())

# plt.violinplot([duaTravelTime, TMSGPPTravelTime]) 
# plt.show()


travelTimeDF = pd.DataFrame({'Travel time (s)': travelTimeSerise, 'Types': TypeSerise})
timeLossDF = pd.DataFrame({'Time loss (s)': timeLossSerise, 'Types': TypeSerise})

# print(travelTimeDF.describe())

# print(timeLossDF.describe())


plt.figure(figsize=(9.2, 10))
sns.violinplot(
    x="Types", y="Travel time (s)", data=travelTimeDF, 
    scale="width", inner="quartile", palette="coolwarm", cut=0
    )
plt.savefig('travelTime.png')
plt.close()
# plt.show()


plt.figure(figsize=(9.2, 10))
sns.violinplot(
    x='Types', y='Time loss (s)', data=timeLossDF,
    scale="width", inner="quartile", palette="coolwarm", cut=0
    )
plt.savefig('timeLoss.png')
plt.close()
# plt.show()
