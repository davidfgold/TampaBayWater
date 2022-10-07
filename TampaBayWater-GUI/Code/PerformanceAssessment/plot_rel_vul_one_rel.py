import numpy as np
import matplotlib
import matplotlib.cm as cm 
from matplotlib import pyplot as plt
import seaborn as sns
sns.set()

##########################################################################
# my data (30 day failure requirement)

#scenario = 143

failure_141 = np.loadtxt('failure_duration_real_378_noSCH_141.csv',
 delimiter=',')

failure_143 = np.loadtxt('failure_duration_real_378_noSCH_143.csv',
 delimiter=',')

# plot time varying distribution    
cmap = matplotlib.cm.get_cmap("RdBu_r")
fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot(1,1,1)
#for i in np.linspace(5,95,19):
#    i = int(i)
#    ax.fill_between(range(2021,2041), failure_criteria_periods_30_percent[i-5,:]*30, 
#    failure_criteria_periods_30_percent[i,:]*30, color=cm.RdBu(((i-61)/100.0)), 
#    alpha=0.75, edgecolor='none')
plt.step(range(2021,2041), failure_141*30, 
         color='darkred')

#plt.step(range(2021,2041), failure_144*30+5, color='royalblue')
ax.set_xticks(range(2021,2041))
#ax.set_xticklabels(years, rotation=90, fontsize=14)
ax.set_yticks(np.linspace(0,6,7)*60)
ax.set_yticklabels(['0', '60', '120', '180', '240', '300', '360'], 
fontsize=14)
ax.set_xlim([2021,2040])
ax.set_ylim([0,370])
ax.set_ylabel('Shortfall Severity \n(Days of continuous supply shortfall per year)', 
              fontsize=14)
#plt.legend(['15% of simulations', '10% of simulations', '5% of simulations'], fontsize=14, loc='lower right')

#plt.savefig('Figures/Severity_only_sch' + str(scenario) + '.png', bbox_inches='tight')
