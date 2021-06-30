# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 13:36:19 2021

@author: dgold
"""

scenario = 141


years = np.arange(2021, 2041)

# from stackoverflow: https://stackoverflow.com/questions/36271302/changing-color-scale-in-seaborn-bar-plot
def colors_from_values(values, palette_name):
    # normalize the values to range [0, 1]
    normalized = (values - min(values)) / (max(values) - min(values))
    # convert to indices
    indices = np.round(normalized * (len(values) - 1)).astype(np.int32)
    # use the indices to get the colors
    palette = sns.color_palette(palette_name, len(values))
    return np.array(palette).take(indices, axis=0)


failure_criteria_periods_30_percent = np.loadtxt('failure_duration_no_sch_' + str(scenario) + '.csv',
 delimiter=',')

fig = plt.figure(figsize=(15,15))
for i in range(1,21):
    ax = fig.add_subplot(5,4,i)
    ax.plot(np.linspace(1,100,100), failure_criteria_periods_30_percent[:,i-1]*30)
    ax.set_xlabel('Realization Percentile')
    ax.set_ylim([0,400])
    ax.set_title(str(years[i-1]))
    if i == 1 or i == 5 or i == 9 or i == 13 or i == 17:
        ax.set_ylabel('Max days of \ncontinuous shortfall')
        ax.set_yticklabels([0, 100, 200, 300, 400])
    else:
        ax.set_yticklabels([])

plt.tight_layout()








# plot time varying distribution    
cmap = matplotlib.cm.get_cmap("RdBu_r")
fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot(1,1,1)
#for i in np.linspace(5,95,19):
#    i = int(i)
#    ax.fill_between(range(2021,2041), failure_criteria_periods_30_percent[i-5,:]*30, 
#    failure_criteria_periods_30_percent[i,:]*30, color=cm.RdBu(((i-61)/100.0)), 
#    alpha=0.75, edgecolor='none')
plt.plot(range(2021,2041), failure_criteria_periods_30_percent[85]*30+5, 
         color='lightcoral')
plt.plot(range(2021,2041), failure_criteria_periods_30_percent[90]*30+5, 
         color='brown', linestyle='-.')
plt.plot(range(2021,2041), failure_criteria_periods_30_percent[95]*30+5, 
         color='darkred', linestyle='--')
ax.set_xticks(range(2021,2041))
ax.set_xticklabels(years, rotation=90, fontsize=14)
ax.set_yticks(np.linspace(0,6,7)*60)
ax.set_yticklabels(['0', '60', '120', '180', '240', '300', '360'], 
fontsize=14)
ax.set_xlim([2021,2040])
ax.set_ylim([0,370])
ax.set_ylabel('Shortfall Severity \n(Days of continuous supply shortfall per year)', 
              fontsize=14)
plt.legend(['15% of simulations', '10% of simulations', '5% of simulations'], fontsize=14, loc='lower right')

plt.savefig('Severity_' + str(scenario) + '.png', bbox_inches='tight')
