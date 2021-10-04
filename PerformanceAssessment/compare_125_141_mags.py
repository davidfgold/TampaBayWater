# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 10:35:31 2021

@author: dgold
"""

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
    
    source = sources[i]
    mo_ave_141 = np.loadtxt(source + '_mov30_' + str(141) +'.csv', delimiter=',')
    mo_ave_125 = np.loadtxt(source + '_mov30_' + str(125) +'.csv', delimiter=',')

    ax = fig.add_subplot(2,3,i+1)
    if i > 1:
        ax.set_xticklabels(range(2020,2045, 5), fontsize=12)
    else:
        ax.set_xticklabels([])
    ax.plot(years, mo_ave_141[:,85], color='lightcoral')
    ax.plot(years, mo_ave_141[:, 90], color='brown', linestyle='-.')
    ax.plot(years, mo_ave_141[:,95], color='darkred', linestyle=':')
    ax.plot(years, mo_ave_125[:,85], color='lightsteelblue')
    ax.plot(years, mo_ave_125[:, 90], color='cornflowerblue', linestyle='-.')
    ax.plot(years, mo_ave_125[:,95], color='royalblue', linestyle=':')
    
    #plot_quantiles(sources[i], ax, axes_lables, sources_names[i])
    if i == 3:
        ax.set_ylim([0,35])
    else:
        ax.set_ylim([0,15])
    ax.set_xlim([2020,2040])
    if i == 0 or i == 3:
        ax.set_ylabel('Shortfall Magnitude (mgd)', fontsize=14)
    
    ax.set_title(source_names[i], fontsize=14)
    #if i == 2:
    #   ax.legend(['15% of simulations', '10% of simulations', 
    #               '5% of simulations'])
    
    
plt.tight_layout()    
plt.savefig('compare_magnitudes_125_141.png', bbox_inches='tight')