import numpy as np
import matplotlib
import matplotlib.cm as cm 
from matplotlib import pyplot as plt
import seaborn as sns
sns.set()

##########################################################################
# my data (30 day failure requirement)

scenario = 142
failure_percent30 = np.loadtxt('Reliability/reliability_1mgd_30_day_no_sch_' + str(scenario) + '.csv', delimiter=',')
years = np.arange(2021, 2041)


#SCH = failure_criteria_percent30 = np.loadtxt('Reliability/reliability_only_SCH_' + str(scenario) + '.csv', delimiter=',')
#reliability_SCH = reliability_30 = (1-SCH)*100
# from stackoverflow: https://stackoverflow.com/questions/36271302/changing-color-scale-in-seaborn-bar-plot
def colors_from_values(values, palette_name):
    # normalize the values to range [0, 1]
    normalized = (values - .2) / .8
    # convert to indices
    indices = np.round(normalized * (len(values) - 1)).astype(np.int32)
   # use the indices to get the colors
    palette = sns.color_palette(palette_name, len(values))
    return np.array(palette).take(indices, axis=0)

# bar plot of reliability
reliability_30 = (1-failure_percent30)*100
fig = plt.figure(figsize = (12,6))
ax = fig.add_subplot(111)
sns.barplot(years, reliability_30, 
palette=(colors_from_values(1-failure_percent30, "YlOrRd_r")), ax=ax, 
edgecolor='#838383')
ax.set_ylim([0,101])
ax.set_ylabel('Percent of Simulations without \nsupply shortfall', fontsize=14)
ax.set_xticklabels(years, rotation=90, fontsize=14)
#ax.set_yticklabels(['50', '60', '70', '80', '90', '100'], fontsize=14)

plt.savefig('Figures/Reliability_1mgd_no_sch' + str(scenario) + '.png')

##############

failure_periods_30_percent = np.loadtxt('Severity/failure_duration_quantiles_30_day_run' + str(scenario) + '.csv',
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


plt.step(range(2021,2041), failure_periods_30_percent[95]*30, 
         color='darkred')
plt.step(range(2021,2041), failure_periods_30_percent[90]*30, 
         color='brown', linestyle='--')
plt.step(range(2021,2041), failure_periods_30_percent[50]*30, 
         color='#929591', linestyle=':')

#plt.plot(range(2021,2041), failure_periods_30_percent[90]*30+5, 
#         color='brown', linestyle='-.')
#plt.plot(range(2021,2041), failure_periods_30_percent[95]*30+5, 
#         color='darkred', linestyle='--')
ax.set_xticks(range(2021,2041))
ax.set_xticklabels(years, rotation=90, fontsize=14)
ax.set_yticks(np.linspace(0,6,7)*60)
ax.set_yticklabels(['0', '60', '120', '180', '240', '300', '360'], 
fontsize=14)
ax.set_xlim([2021,2040])
ax.set_ylim([0,370])
ax.set_ylabel('Shortfall Severity \n(Days)', 
              fontsize=14)
plt.legend(['95th percentile', '90th percentile', '50th percentile'], fontsize=14, loc='upper right')

#plt.savefig('Figures/Severity_1mgd_95_90_50p' + str(scenario) + '.png', bbox_inches='tight')
