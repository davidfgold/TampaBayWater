# -*- coding: utf-8 -*-
"""
Created on Aug 3 2020
TAMPA BAY WATER AUTHORITY FINANCIAL MODEL
compare results across model evaluations and/or realizations
@author: dgorelic
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
data_path = 'C:/Users/dgorelic/Desktop/TBWruns/vgrid_financial_output'

# plot data across simulations/evaluations and all realizations
n_metrics = 2
n_sims = 3; sim_colors = ['g', 'b', 'r']; sim_type = ['Un-Managed', 'Fixed', 'Controlled Growth']
n_formulations = 3; f_type = ['Baseline', 'w/SWTP 20 MGD exp.', 'w/SWTP 30 MGD exp.']; f_num = [125,126,128]
fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(n_formulations, n_metrics, sharey = False, figsize = (8,10))
for f in f_num:
    dc_plotting_index_set = 19 * [0]
    rc_plotting_index_set = 19 * [0]
    for sim in range(0,n_sims):
        # read data
        rc_data = pd.read_csv(data_path + '/RC_f' + str(f) + '_s' + str(sim) + '.csv', index_col = 0)
        dc_data = pd.read_csv(data_path + '/DC_f' + str(f) + '_s' + str(sim) + '.csv', index_col = 0)
        
        # convert to T/F based on violation of criteria
        rc_violation = rc_data.iloc[:,1:] < 1.25
        dc_violation = dc_data.iloc[:,1:] < 1.0
        
        # count realizations per year in violation, post FY 2020
        rcv_years = rc_violation.iloc[:,1:].sum()
        dcv_years = dc_violation.iloc[:,1:].sum()
        
        # make plot - stacked bar plot showing violation count for each formulation 
        # 3x2 plot - 3 rows (infra formulations) by 2 covenants
        if f == 125:
            ax1.bar(dcv_years.keys().values, dcv_years.values, bottom = dc_plotting_index_set, color = sim_colors[sim])
            ax2.bar(rcv_years.keys().values, rcv_years.values, bottom = rc_plotting_index_set, color = sim_colors[sim])
        elif f == 126:
            ax3.bar(dcv_years.keys().values, dcv_years.values, bottom = dc_plotting_index_set, color = sim_colors[sim])
            ax4.bar(rcv_years.keys().values, rcv_years.values, bottom = rc_plotting_index_set, color = sim_colors[sim])
        else:
            ax5.bar(dcv_years.keys().values, dcv_years.values, bottom = dc_plotting_index_set, color = sim_colors[sim])
            ax6.bar(rcv_years.keys().values, rcv_years.values, bottom = rc_plotting_index_set, color = sim_colors[sim])
            
        dc_plotting_index_set += dcv_years.values
        rc_plotting_index_set += rcv_years.values
        
    # adjust plot limits
    ax1.set_ylim((0,1100))    
    ax2.set_ylim((0,550))   
    ax3.set_ylim((0,1100))   
    ax4.set_ylim((0,550))   
    ax5.set_ylim((0,1100))   
    ax6.set_ylim((0,550))   
    
    # adjust ticks and labels
    ax1.set_xticks([-1, 4, 9, 14, 19])
    ax1.set_xticklabels([])
    ax2.set_xticks([-1, 4, 9, 14, 19])
    ax2.set_xticklabels([])
    ax3.set_xticks([-1, 4, 9, 14, 19])
    ax3.set_xticklabels([])
    ax4.set_xticks([-1, 4, 9, 14, 19])
    ax4.set_xticklabels([])
    ax5.set_xticks([-1, 4, 9, 14, 19])
    ax5.set_xticklabels([str(x) for x in range(2020,2041,5)])
    ax6.set_xticks([-1, 4, 9, 14, 19])
    ax6.set_xticklabels([str(x) for x in range(2020,2041,5)])
    
    # add legend
    ax2.legend(loc = 'upper right', title = 'Uniform Rate Policy', labels = sim_type)
        
    # add other labels
    ax5.set_xlabel('Fiscal Year')
    ax6.set_xlabel('Fiscal Year')
    ax1.set_ylabel('Scenario 1:\nSCH Pipeline')
    ax3.set_ylabel('Realizations Violating Covenant Threshold\n\nScenario 2:\nSCH Pipeline + 20 MGD SWTP')
    ax5.set_ylabel('Scenario 3:\nSCH Pipeline + 30 MGD SWTP')
    ax1.set_title('Debt Covenant')
    ax2.set_title('Rate Covenant')
    plt.savefig(data_path + '/Simulation_Covenant_Comparisons' + '_animated_' + str(sim) + '.png', bbox_inches= 'tight')

plt.close()
