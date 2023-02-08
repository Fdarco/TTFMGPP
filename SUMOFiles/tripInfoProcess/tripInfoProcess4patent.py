# import xml.etree.ElementTree as ET

import pandas as pd
import seaborn as sns
sns.set_theme(style="ticks",font='simsun',font_scale=2.2)
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


duaType = pd.Series(['duarouter']*duaTravelTime.shape[0])
TMSGPPType = pd.Series(['本发明方法']*TMSGPPTravelTime.shape[0])

travelTimeSerise = pd.concat([duaTravelTime, TMSGPPTravelTime])
timeLossSerise = pd.concat([duaTimeLoss, TMSGPPTimeLoss])
TypeSerise = pd.concat([duaType, TMSGPPType])

# print(travelTimeSerise.describe())
# print(timeLossSerise.describe())

# plt.violinplot([duaTravelTime, TMSGPPTravelTime]) 
# plt.show()


travelTimeDF = pd.DataFrame({'旅行时间 (s)': travelTimeSerise, '模型': TypeSerise})
timeLossDF = pd.DataFrame({'损失时间 (s)': timeLossSerise, '模型': TypeSerise})



# print(travelTimeDF.describe())

# print(timeLossDF.describe())



plt.figure(figsize=(12, 10))
sns.violinplot(
    x="模型", y="旅行时间 (s)", data=travelTimeDF, 
    scale="width", inner="quartile", palette="coolwarm", cut=0
    )
plt.savefig('travelTime-ap.png')
plt.close()
# plt.show()


plt.figure(figsize=(12, 10))
sns.violinplot(
    x='模型', y='损失时间 (s)', data=timeLossDF,
    scale="width", inner="quartile", palette="coolwarm", cut=0
    )
plt.savefig('timeLoss-ap.png')
plt.close()
# plt.show()

