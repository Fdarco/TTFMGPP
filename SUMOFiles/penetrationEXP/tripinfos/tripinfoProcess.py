from cProfile import label
import pandas as pd
import seaborn as sns
sns.set_theme(style="ticks",font='Times New Roman',font_scale=1.4)
from matplotlib import pyplot as plt
import numpy as np


travelTimeList = []
travelTimeMeans = []
travelTimeMedians = []
timeLossList = []
timeLossMeans = []
timeLossMedians = []
plannerTypes = []
for i in range(11):
    print('File %i reading...'%i)
    penetration = i/10
    fileName = 'pen%.1f.tripinfo.xml' % penetration
    df = pd.read_xml(fileName)
    dfTravelTime = df['duration'].copy()
    dfTimeLoss = df['timeLoss'].copy()
    pType = pd.Series(['%.1f'%penetration]*df.shape[0])
    plannerTypes.append(pType)
    travelTimeMeans.append(dfTravelTime.mean())
    timeLossMeans.append(dfTimeLoss.mean())
    travelTimeMedians.append(dfTravelTime.median())
    timeLossMedians.append(dfTimeLoss.median())
    travelTimeList.append(dfTravelTime)
    timeLossList.append(dfTimeLoss)


print('File reading finished.')
print('travel time mean:', travelTimeMeans)
print('travel time median:', travelTimeMedians)
print('time loss mean:', timeLossMeans)
print('time loss median:', timeLossMedians)


# travelTimeMeans = [2487.0817927874205, 2003.6220373567728, 1647.3717155862503, 1440.2339664102967, 1310.9976455815413, 1273.4683409197928, 1143.3218960916654, 1102.5818552817454, 1048.2497881023387, 1040.6652644796736, 995.3146130905666]
# travelTimeMeans = list(map(int, travelTimeMeans))

# travelTimeMedians = [1167.0, 1017.0, 932.0, 872.0, 851.0, 801.0, 758.0, 726.0, 693.0, 675.0, 645.0]
# travelTimeMedians = list(map(int, travelTimeMedians))

# timeLossMeans = [1742.5608596716988, 1276.1604981949458, 934.7804420028253, 742.2326444828128, 638.9934496939258, 613.2505462250823, 495.4223406058704, 466.7940938628159, 424.72443289907386, 430.2089963898917, 396.018933291477]
# timeLossMeans = list(map(int, timeLossMeans))

# timeLossMedians = [197.67, 160.62, 146.08, 132.86, 131.06, 121.64, 114.85, 108.56, 103.3, 99.07, 92.9]
# timeLossMedians = list(map(int, timeLossMedians))

width = 0.4
labels = [round(e/10, 1) for e in range(11)]


fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)
ax_t = ax.twinx()
ttx = np.arange(len(travelTimeMeans))
ttmean = ax.bar(ttx - width/2, travelTimeMeans, width, color='#2980b9')
ttmedian = ax_t.bar(ttx + width/2, travelTimeMedians, width, color='#e67e22')
ax.set_xlabel('Penetration')
ax.set_xticks(ttx)
ax.set_xticklabels(labels)
ax.set_ylabel('Mean (s)')
# ax.bar_label(ttmean, travelTimeMeans)
ax_t.set_ylabel('Median (s)')
# ax_t.bar_label(ttmedian, travelTimeMedians)
# plt.title('Travel time')
plt.legend([ttmean, ttmedian], ['Mean of travel time', 'Median of travel time'])
plt.savefig('travelTimeBar.png')
plt.close()
# plt.show()


fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)
ax_t = ax.twinx()
ttx = np.arange(len(timeLossMeans))
ttmean = ax.bar(ttx - width/2, timeLossMeans, width, color='#2980b9')
ttmedian = ax_t.bar(ttx + width/2, timeLossMedians, width, color='#e67e22')
ax.set_xlabel('Penetration')
ax.set_xticks(ttx)
ax.set_xticklabels(labels)
ax.set_ylabel('Mean (s)')
# ax.bar_label(ttmean, timeLossMeans)
ax_t.set_ylabel('Median (s)')
# ax_t.bar_label(ttmedian, timeLossMedians)
# plt.title('Time loss')
plt.legend([ttmean, ttmedian], ['Mean of time loss', 'Median of time loss'])
plt.savefig('timeLossBar.png')
plt.close()
# plt.show()


print('DataFrame building...')
travelTimeSeries = pd.concat(travelTimeList)
timeLossSeries = pd.concat(timeLossList)
typesSeries = pd.concat(plannerTypes)


travelTimeDF = pd.DataFrame({
    'Travel time (s)': travelTimeSeries,
    'Penetration': typesSeries
})

timeLossDF = pd.DataFrame({
    'Time loss (s)': timeLossSeries,
    'Penetration': typesSeries
})
print('DataFrame building finished.')


plt.figure(figsize=(9.2, 10))
sns.violinplot(
    x="Penetration", y="Travel time (s)", data=travelTimeDF, 
    scale="width", inner="quartile", palette="coolwarm", cut=0
    )
# 这里要加一个 ',' 不然不出图例，我也不知道为啥
lntt, = plt.plot(list(range(len(travelTimeMeans))), travelTimeMeans, color='#8e44ad', marker='2')
plt.legend([lntt], ['Average travel time'])
plt.savefig('Traveltime.png')
plt.close()
# plt.show()


plt.figure(figsize=(9.2, 10))
sns.violinplot(
    x="Penetration", y="Time loss (s)", data=timeLossDF, 
    scale="width", inner="quartile", palette="coolwarm", cut=0
    )
# 这里要加一个 ',' 不然不出图例，我也不知道为啥
lntt, = plt.plot(list(range(len(travelTimeMeans))), travelTimeMeans, color='#8e44ad', marker='2')
plt.legend([lntt], ['Average time loss'])
plt.savefig('Timeloss.png')
plt.close()
# plt.show()
