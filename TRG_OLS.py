import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from scipy.stats import t
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

# load summary data
summary_data = np.loadtxt('summary_data.csv', delimiter=',', skiprows=1)

demand = summary_data[:,0]
inflow = summary_data[:,1]
OPRC = summary_data[:,2]
GW_overage = summary_data[:,3]
TRG_offset = summary_data[:,4]
penalty = summary_data[:,5]


# fit linear model of TRG offset from demand
demand = sm.add_constant(demand)
demand_TRG_model = sm.OLS(TRG_offset[4:326]/20,demand[4:326,:])

results = demand_TRG_model.fit()

#print results.params
print results.summary()

prediction = np.ones(len(demand[4:326,:]))

for i in range(0,len(prediction)): 
	prediction[i] = results.params[0] + results.params[1]*demand[i+4,1]

# plot the OLS fit
fig, ax = plt.subplots(1,1, figsize=(9,7))
plt.rc('font', size=16)
ax.scatter(demand[4:326,1], TRG_offset[4:326]/20, c='g', alpha=.7, s=70, edgecolor='none')
ax.plot(demand[4:326,1], prediction, c='black')
ax.set_xlim([140, 280])
ax.set_ylim([200000/20, 800000/20])
#ax.set_xticklabels([140, 160, 180, 200, 220, 240, 260], fontsize=14)
ax.set_xlabel('Average Annual Demand (MGD)', fontsize=16)
ax.set_ylabel('Average Annual Groundwater Target Offset', fontsize=16)
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(20)
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
	item.set_fontsize(18)

plt.show()
plt.savefig('TRG_offset_fit.png', bboxinches='tight', format='png')

# plot predicted TRG_offset over time based on demand projections
# load demand predictions
demand_predictions = np.loadtxt('demand_predictions.csv', delimiter=',', skiprows=1)

year = demand_predictions[:,0]
fifthpercentile = demand_predictions[:,1]
twentyfifthpercentile = demand_predictions[:,2]
fiftiethpercentile =  demand_predictions[:,3]
seventyfifthpercentile = demand_predictions[:,4]
ninetyfifthpercentile = demand_predictions[:,5]


fifthpercentile = sm.add_constant(fifthpercentile)
fifth_sdev, fifth_lower, fifth_upper = wls_prediction_std(results, exog=fifthpercentile, alpha=.1)

fiftiethpercentile = sm.add_constant(fiftiethpercentile)
fiftieth_sdev, fiftieth_lower, fiftieth_upper = wls_prediction_std(results, exog=fiftiethpercentile, alpha=.1)

seventyfifthpercentile = sm.add_constant(seventyfifthpercentile)
seventyfifth_sdev, seventyfifth_lower, seventyfifth_upper = wls_prediction_std(results, exog=seventyfifthpercentile, alpha=.1)

ninetyfifthpercentile = sm.add_constant(ninetyfifthpercentile)
ninetyfifth_sdev, ninetyfifth_lower, ninetyfifth_upper = wls_prediction_std(results, exog=ninetyfifthpercentile, alpha=.1)

fifth_predictions = np.ones(len(fifthpercentile))
fiftieth_predictions = np.ones(len(fiftiethpercentile))
seventyfifth_predictions = np.ones(len(seventyfifthpercentile))
ninetyfifth_predictions = np.ones(len(ninetyfifthpercentile))
for i in range(0, len(year)): 
	fifth_predictions[i] = results.params[0] + results.params[1]*fifthpercentile[i,1]
	fiftieth_predictions[i] = results.params[0] + results.params[1]*fiftiethpercentile[i,1]
	seventyfifth_predictions[i] = results.params[0] + results.params[1]*seventyfifthpercentile[i,1]
	ninetyfifth_predictions[i] = results.params[0] + results.params[1]*ninetyfifthpercentile[i,1]

fig, ax = plt.subplots(1,1, figsize=(9,7))
#ax.fill_between(year, fiftieth_lower, fiftieth_upper, color='green', alpha=.1)
#ax.plot(year, fiftieth_predictions, c='green')
#ax.fill_between(year, seventyfifth_lower, seventyfifth_upper, color='blue', alpha=.1)
#ax.plot(year, seventyfifth_predictions, c='blue')
ax.fill_between(year, fifth_lower, ninetyfifth_upper, color='green', alpha=.1)
ax.plot(year, fiftieth_predictions, c='green')
ax.plot(year, fifth_lower, color='green', alpha=.5,linewidth=.5)
ax.plot(year, ninetyfifth_upper, color='green', alpha=.5,linewidth=.5)
ax.set_ylim([0,35000])
ax.set_ylabel('Average Annual Groundwater Target Offset')
for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
    item.set_fontsize(16)
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
	item.set_fontsize(14)
plt.savefig('TRG_offset_projections.png', bboxinches='tight', format='png')


