import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
from glob import glob
import seaborn as sns
import os
import csv
sns.set()


demand_predictions = np.loadtxt('demand_predictions_with_actual.csv', delimiter=',', skiprows=1)

year = demand_predictions[:,0]
fifthpercentile = demand_predictions[:,1]
twentyfifthpercentile = demand_predictions[:,2]
fiftiethpercentile =  demand_predictions[:,3]
seventyfifthpercentile = demand_predictions[:,4]
ninetyfifthpercentile = demand_predictions[:,5]

# plot
fig, ax1 = plt.subplots(1,1, figsize = (8,6))
ax1.plot(year, fiftiethpercentile, c='blue', alpha=.8)
ax1.fill_between(year, fifthpercentile, ninetyfifthpercentile, color='blue', alpha=.2)
#ax1.plot(year, fifthpercentile, alpha = .5, c='blue', linewidth=0.5)
#ax1.plot(year, ninetyfifthpercentile, alpha = .5, c='blue', linewidth=0.5)
ax1.plot(year, np.ones(len(year))*220, c='black', linestyle='--')
ax1.set_ylim([0,300])
ax1.set_xlim([2018,2045])
ax1.set_ylabel('Regional Demand (MDG)')
for item in ([ax1.title, ax1.xaxis.label, ax1.yaxis.label]):
    item.set_fontsize(16)
for item in (ax1.get_xticklabels() + ax1.get_yticklabels()):
	item.set_fontsize(14)
plt.show()
#ax1.set_ylabel('Days of Groundwater Overage')
#ax1.set_xlabel('Average Annual Demand')
#ax1.set_ylim([0,7400])

'''ax2.scatter(demand_values, costmetric[:,2], edgecolors='none', c=costmetric[:,2], alpha = .7, cmap='PuOr_r', s=100)
ax2.set_ylabel('Average TRG Offset')
ax2.set_xlabel('Average Annual Demand')    
#plt.show()
fig.savefig('August_demand_relationships.png', bbox_inches='tight', format='png')
'''