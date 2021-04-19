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
data_path = 'F:/MonteCarlo_Project/Cornell_UNC/financial_model_output'

# plot data across simulations/evaluations and all realizations
for run_id in [125,126,128]:
    n_sims = 3; sim_colors = ['g', 'b', 'r']; sim_type = ['Un-Managed', 'Fixed', 'Controlled Growth']
    fig, (ax1, ax2, ax3) = plt.subplots(1,n_sims, sharey = False, figsize = (14,5))
    for sim in range(0,n_sims):
        # read data
        ur_data = pd.read_csv(data_path + '/UR_f' + str(run_id) + '_s' + str(sim) + '.csv', index_col = 0)
        rc_data = pd.read_csv(data_path + '/RC_f' + str(run_id) + '_s' + str(sim) + '.csv', index_col = 0)
        dc_data = pd.read_csv(data_path + '/DC_f' + str(run_id) + '_s' + str(sim) + '.csv', index_col = 0)
        
        # trim to start/end on same years
        min_year = np.max([float(min(ur_data.columns)), float(min(rc_data.columns)), float(min(dc_data.columns))])
        max_year = np.min([float(max(ur_data.columns)), float(max(rc_data.columns)), float(max(dc_data.columns))])
        
        col_range = [str(x) for x in range(int(min_year),int(max_year+1))]
        ur_data = ur_data[col_range]
        rc_data = rc_data[col_range]
        dc_data = dc_data[col_range]
        
        # make plot
        ax1.fill_between(ur_data.columns,
                         np.max(ur_data, axis = 0), 
                         np.min(ur_data, axis = 0), 
                         color = sim_colors[sim], 
                         alpha = 0.75,  linewidth = 2,
                         edgecolor = sim_colors[sim], label = sim_type[sim])
        ax2.fill_between(dc_data.columns, 
                         np.max(dc_data, axis = 0), 
                         np.min(dc_data, axis = 0), 
                         color = sim_colors[sim], 
                         alpha = 0.75, 
                         edgecolor = sim_colors[sim], label = sim_type[sim])
        ax3.fill_between(rc_data.columns, 
                         np.max(rc_data, axis = 0), 
                         np.min(rc_data, axis = 0), 
                         color = sim_colors[sim], 
                         alpha = 0.75, 
                         edgecolor = sim_colors[sim], label = sim_type[sim])
        
        ax2.plot(dc_data.columns, [1] * len(dc_data.columns), 
                 color = 'k', linewidth = 3, linestyle = '--')
        ax3.plot(rc_data.columns, [1.25] * len(rc_data.columns), 
                 color = 'k', linewidth = 3, linestyle = '--')
        ax3.legend(loc = 'lower right', title = 'Uniform Rate Policy')
        
        ax1.set_ylim((2,4))
        ax2.set_ylim((0,2))
        ax3.set_ylim((0,3))
        
        ax1.set_xticks([str(x) for x in range(int(min_year),int(max_year+2),5)])
        ax1.set_xticklabels([str(x) for x in range(int(min_year),int(max_year+2),5)])
        ax2.set_xticks([str(x) for x in range(int(min_year),int(max_year+2),5)])
        ax2.set_xticklabels([str(x) for x in range(int(min_year),int(max_year+2),5)])
        ax3.set_xticks([str(x) for x in range(int(min_year),int(max_year+2),5)])
        ax3.set_xticklabels([str(x) for x in range(int(min_year),int(max_year+2),5)])
        ax1.set_xlabel('Fiscal Year')
        ax2.set_xlabel('Fiscal Year')
        ax3.set_xlabel('Fiscal Year')
        ax1.set_ylabel('$/kgal')
        ax2.set_ylabel('Covenant Ratio')
        ax1.set_title('Uniform Rate')
        ax2.set_title('Debt Covenant')
        ax3.set_title('Rate Covenant')
        plt.savefig(data_path + '/Simulation_Covenant_Comparisons_f' + str(run_id) + '_animated' + str(sim) + '.png', bbox_inches= 'tight')
    
    plt.close()
    
    # quick plot to show difference in debt schedule between existing debt
    # and future with SHC pipeline added
    sim = 1; real = 1
    modeled_data = pd.read_csv(data_path + '/budget_actuals_f' + str(run_id) + '_s' + str(sim) + '_r' + str(real) + '.csv', index_col = 0)
    historic_data = pd.read_excel('f:/MonteCarlo_Project/Cornell_UNC/financial_model_input_data/model_input_data' + '/Current_Future_BondIssues.xlsx', sheet_name = 'FutureDSTotals')
    
    # make plot
    fig, ax = plt.subplots(1,1, sharey = False, figsize = (5,5))
    ax.fill_between(modeled_data['Fiscal Year'].iloc[2:], modeled_data['Debt Service'].iloc[2:]/1000000, 
                    color = 'b', label = 'Infrastructure added in 2028')
    ax.fill_between(historic_data['Fiscal Year'].iloc[:-1], historic_data['Total'].iloc[:-1]/1000000, 
                    color = 'k', alpha = 0.7, label = 'Existing Debt')
    ax.set_xlabel('Fiscal Year')
    ax.set_ylabel('$ Millions')
    ax.set_title('Debt Service')
    ax.legend(loc = (0.1,0.1), title = 'Debt Service')
    
    plt.savefig(data_path + '/DebtService_Sample_Comparison_f' + str(run_id) + '.png', bbox_inches= 'tight')
    plt.close()

    ax2.plot(dc_data.columns, [1] * len(dc_data.columns), 
             color = 'k', linewidth = 3, linestyle = '--')
    ax3.plot(rc_data.columns, [1.25] * len(rc_data.columns), 
             color = 'k', linewidth = 3, linestyle = '--')
    ax3.legend(loc = 'lower right', title = 'Uniform Rate Policy')
    
    ax1.set_ylim((2,4))
    ax2.set_ylim((0,2))
    ax3.set_ylim((0,3))
    
    ax1.set_xticks([str(x) for x in range(int(min_year),int(max_year+2),5)])
    ax1.set_xticklabels([str(x) for x in range(int(min_year),int(max_year+2),5)])
    ax2.set_xticks([str(x) for x in range(int(min_year),int(max_year+2),5)])
    ax2.set_xticklabels([str(x) for x in range(int(min_year),int(max_year+2),5)])
    ax3.set_xticks([str(x) for x in range(int(min_year),int(max_year+2),5)])
    ax3.set_xticklabels([str(x) for x in range(int(min_year),int(max_year+2),5)])
    ax1.set_xlabel('Fiscal Year')
    ax2.set_xlabel('Fiscal Year')
    ax3.set_xlabel('Fiscal Year')
    ax1.set_ylabel('$/kgal')
    ax2.set_ylabel('Covenant Ratio')
    ax1.set_title('Uniform Rate')
    ax2.set_title('Debt Covenant')
    ax3.set_title('Rate Covenant')
    plt.savefig(data_path + '/Simulation_Covenant_Comparisons' + '_animated' + str(sim) + '.png', bbox_inches= 'tight')

plt.close()

# quick plot to show difference in debt schedule between existing debt
# and future with SHC pipeline added
sim = 1; real = 1
modeled_data = pd.read_csv(data_path + '/budget_actuals_s' + str(sim) + '_r' + str(real) + '.csv', index_col = 0)
historic_data = pd.read_excel('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/model_input_data' + '/Current_Future_BondIssues.xlsx', sheet_name = 'FutureDSTotals')

# make plot
fig, ax = plt.subplots(1,1, sharey = False, figsize = (5,5))
ax.fill_between(modeled_data['Fiscal Year'].iloc[2:], modeled_data['Debt Service'].iloc[2:]/1000000, 
                color = 'b', label = 'Balm area (SCH) Pipeline')
ax.fill_between(historic_data['Fiscal Year'].iloc[:-1], historic_data['Total'].iloc[:-1]/1000000, 
                color = 'k', alpha = 0.7, label = 'Existing Debt')
ax.set_xlabel('Fiscal Year')
ax.set_ylabel('$ Millions')
ax.set_title('Debt Service')
ax.legend(loc = (0.1,0.1), title = 'Debt Service')

plt.savefig(data_path + '/DebtService_Sample_Comparison.png', bbox_inches= 'tight')
plt.close()
