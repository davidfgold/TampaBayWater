# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 11:26:45 2021
Create figure with subset of realizations to show financial impact of
    high or low demand growth to 2040, for comparison with reliability

@author: dgorelick
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
data_path = 'F:/MonteCarlo_Project/Cornell_UNC/financial_model_output'
sim = 0

# get demand averages and identify which fall into which quantile ranges
demand_averages = pd.read_csv('F:/MonteCarlo_Project/Cornell_UNC/financial_model_input_data/avg_demand_2040.csv', header = None)
demand_quantiles = demand_averages.quantile((0.95,0.9,0.75,0.5,0.25,0.10,0.05)).iloc[:,0]

high_demand_indexes = demand_averages.iloc[:,0].values >= demand_quantiles.iloc[0] # top 5th percentile
low_demand_indexes = demand_averages.iloc[:,0].values <= demand_quantiles.iloc[-1] # bottom 5th percentile

# warning: financial model skips realization ID 95 and doesn't read realization 1000 (bug to fix)
# so adjust data before assigning quantiles for realization selection
financial_demand_averages = demand_averages.iloc[demand_averages.index != 94, 0]
financial_demand_averages = financial_demand_averages.iloc[:-1]

financial_high_demand_indexes = financial_demand_averages.values >= demand_quantiles.iloc[0] # top 5th percentile
financial_low_demand_indexes = financial_demand_averages.values <= demand_quantiles.iloc[-1] # bottom 5th percentile
     
# plot data across simulations/evaluations and select realizations
for run_id in [141]:
    sim_colors = ['g', 'b']; sim_type = ['Hands-Off', '5th %ile Demand Futures']
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey = False, figsize = (10,5))

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
    
    # grab only some realizations with high or low demands
    ur_data_demand_subset = ur_data[financial_low_demand_indexes]
    rc_data_demand_subset = rc_data[financial_low_demand_indexes]
    dc_data_demand_subset = dc_data[financial_low_demand_indexes]
    
    # make plot
    ax1.fill_between(ur_data.columns,
                     np.max(ur_data, axis = 0), 
                     np.min(ur_data, axis = 0), 
                     color = sim_colors[0], 
                     alpha = 0.75,  linewidth = 2,
                     edgecolor = sim_colors[0], label = sim_type[0])
    ax2.fill_between(rc_data.columns, 
                     np.max(rc_data, axis = 0), 
                     np.min(rc_data, axis = 0), 
                     color = sim_colors[0], 
                     alpha = 0.75, 
                     edgecolor = sim_colors[0], label = sim_type[0])
    
    ax1.fill_between(ur_data_demand_subset.columns,
                     np.max(ur_data_demand_subset, axis = 0), 
                     np.min(ur_data_demand_subset, axis = 0), 
                     color = sim_colors[1], 
                     alpha = 0.75,  linewidth = 2,
                     edgecolor = sim_colors[1], label = sim_type[1])
    ax2.fill_between(rc_data_demand_subset.columns, 
                     np.max(rc_data_demand_subset, axis = 0), 
                     np.min(rc_data_demand_subset, axis = 0), 
                     color = sim_colors[1], 
                     alpha = 0.75, 
                     edgecolor = sim_colors[1], label = sim_type[1])
    
    ax2.plot(rc_data.columns, [1.25] * len(rc_data.columns), 
             color = 'k', linewidth = 3, linestyle = '--')
    ax2.legend(loc = 'lower right', title = 'Uniform Rate Policy')
    
    ax1.set_ylim((2,4.5))
    ax2.set_ylim((0,3))
    
    ax1.set_xticks([str(x) for x in range(int(min_year),int(max_year+2),5)])
    ax1.set_xticklabels([str(x) for x in range(int(min_year),int(max_year+2),5)])
    ax2.set_xticks([str(x) for x in range(int(min_year),int(max_year+2),5)])
    ax2.set_xticklabels([str(x) for x in range(int(min_year),int(max_year+2),5)])
    ax1.set_xlabel('Fiscal Year')
    ax2.set_xlabel('Fiscal Year')
    ax1.set_ylabel('$/kgal')
    ax2.set_ylabel('Covenant Ratio')
    ax1.set_title('Uniform Rate')
    ax2.set_title('Rate Covenant')
    plt.savefig(data_path + '/Demand_Quantiles_Results_f' + str(run_id) + '_animated' + str(sim) + '.png', bbox_inches= 'tight', dpi = 800)

    plt.close()
    
    
    
    
