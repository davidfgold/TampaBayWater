import numpy as np
import matplotlib
import matplotlib.cm as cm 
from matplotlib import pyplot as plt
import seaborn as sns
sns.set()

sources = ['Alafia',  'SCH', 'SCH3', 'TBC',  'CWUP', 'BUD',]
source_names = ['Alafia \nRiver',  'South Central \nHillsborough Wells', 
           'South Central \nHillsborough Demand', 'Tampa Bypass Canal',  'Consolidated Well Use', 'BUD',]

scenario = 141

years = np.arange(2021, 2041)

fig = plt.figure(figsize=(12,8), dpi=300)

for i in range(0, 5):
    ax = fig.add_subplot(2,3,i+1)
    source = sources[i]
    mo_ave = np.loadtxt('Magnitude/' + source + '_mov30_' + str(scenario) +'.csv', delimiter=',')
    if i > 1:
        ax.set_xticklabels(range(2020,2045, 5), fontsize=12)
    else:
        ax.set_xticklabels([])
    
    ax.plot(years, mo_ave[:,85], color='lightcoral')
    ax.plot(years, mo_ave[:, 90], color='brown', linestyle='-.')
    ax.plot(years, mo_ave[:,95], color='darkred', linestyle=':')
    
    #plot_quantiles(sources[i], ax, axes_lables, sources_names[i])
   
    ax.set_ylim([0,15])
    ax.set_xlim([2020,2040])
    if i == 0 or i == 3:
        ax.set_ylabel('Shortfall Magnitude (mgd)', fontsize=14)
    
    ax.set_title(source_names[i], fontsize=14)
    #if i == 2:
    #   ax.legend(['15% of simulations', '10% of simulations', 
    #               '5% of simulations'])
    
    
plt.tight_layout()    
plt.savefig('Figures/individual_magnitudes' + str(scenario) + '.png', bbox_inches='tight')