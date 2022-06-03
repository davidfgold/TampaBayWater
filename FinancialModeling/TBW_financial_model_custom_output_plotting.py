# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 15:37:05 2022
Master plotting script to compare financial model simulation runs
    The idea here is that for any simulation/formulation/number of realizations
    here we can plot any number of specific output timeseries, if referred to 
    by name
@author: dgorelic
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
data_path = "C:/Users/cmpet/OneDrive/Documents/UNCTBW/Modeloutput"
dv_path = 'C:/Users/cmpet/OneDrive/Documents/UNC Chapel Hill/TBW/Code/TampaBayWater/FinancialModeling'

# AVAILABLE DATA TO PLOT, BY OUTPUT FILE TYPE
# IF CHOOSING VARIABLES TO PLOT WITH SAME NAME IN DIFFERENT FILES,
# WILL DEFAULT TO PRIORITY PLOTTING ORDER (A) ACTUALS (B) BUDGET (C) METRICS
ACTUAL_VARIABLES = ['Fiscal Year', 'Uniform Rate (Full)', 'Uniform Rate (Variable Portion)',
                       'TBC Sales Rate', 'Interest Income', 'Gross Revenues', 'Debt Service',
                       'Acquisition Credits', 'Fixed Operational Expenses',
                       'Variable Operational Expenses', 'Utility Reserve Fund Balance (Total)',
                       'R&R Fund (Total)', 'R&R Fund (Deposit)', 'R&R Fund (Transfer In)',
                       'Rate Stabilization Fund (Deposit)', 'Rate Stabilization Fund (Total)',
                       'Rate Stabilization Fund (Transfer In)', 'Unencumbered Funds',
                       'CIP Fund (Total)', 'CIP Fund (Deposit)', 'CIP Fund (Transfer In)',
                       'Misc. Income', 'Insurance-Litigation-Arbitrage Income',
                       'Uniform Sales Revenues', 'Energy Savings Fund (Total)',
                       'Energy Savings Fund (Deposit)', 'Energy Savings Fund (Transfer In)']
BUDGET_VARIABLES = ['Fiscal Year', 'Annual Estimate', 'Gross Revenues',
                       'Water Sales Revenue', 'Fixed Operating Expenses',
                       'Variable Operating Expenses', 'Net Revenues', 'Debt Service',
                       'Acquisition Credits', 'Unencumbered Carryover Funds',
                       'R&R Fund Deposit', 'Rate Stabilization Fund Deposit',
                       'Other Funds Deposit', 'Uniform Rate', 'Variable Uniform Rate',
                       'TBC Rate', 'Rate Stabilization Fund Transfers In',
                       'R&R Fund Transfers In', 'Other Funds Transfers In', 'Interest Income',
                       'CIP Fund Transfer In', 'CIP Fund Deposit',
                       'Energy Savings Fund Transfer In', 'Energy Savings Fund Deposit',
                       'Debt Service Deferred']
METRICS_VARIABLES = ['Fiscal Year', 'Debt Covenant Ratio', 'Rate Covenant Ratio',
                       'Partial Debt Covenant Failure', 'Partial Rate Covenant Failure',
                       'Reserve Fund Balance Initial Failure',
                       'R&R Fund Balance Initial Failure',
                       'Cap on Rate Stabilization Fund Transfers In',
                       'Rate Stabilization Funds Transferred In', 'Required R&R Fund Deposit',
                       'Required Reserve Fund Deposit',
                       'Necessary Use of Other Funds (Rate Stabilization Supplement)',
                       'Final Net Revenues', 'Fixed Sales Revenue', 'Variable Sales Revenue',
                       'Reserve Fund Balancing Failure', 'Remaining Unallocated Deficit']

# what data do I want to plot? must be same as they are in output files
data_names_to_plot = ['Rate Covenant Ratio', 'Debt Covenant Ratio', 'Uniform Rate', 'Debt Service', 'Debt Service Deferred', 'Remaining Unallocated Deficit',
                      'Utility Reserve Fund Balance (Total)', 'Rate Stabilization Fund (Total)', 'CIP Fund (Total)', 'R&R Fund (Total)', 'Energy Savings Fund (Total)']
formulation_to_plot = [125] # list all
simulation_to_plot = [0,1,2,3,4,5,6,7,8] # list all, IDs start at 0
realization_to_plot = [x for x in range(1,10)] # list which we want, IDs start at 1 not zero
metrics_test_read = pd.read_csv(data_path + '/financial_metrics_f' + str(formulation_to_plot[0]) + '_s' + str(simulation_to_plot[0]) + '_r' + str(realization_to_plot[0]) + '.csv', index_col = 0)


# read in DV and DUF files to identify the conditions under which
# each simulation is running (i.e. fixed UR, capped Debt Service, etc.)
DVs = pd.read_csv(dv_path + '/financial_model_DVs.csv', header = None)
DUFs = pd.read_csv(dv_path + '/financial_model_DUfactors.csv', header = None)

# loop through all results to report data
for f in range(0,len(formulation_to_plot)):
    print('Plotting output for Formulation ' + str(formulation_to_plot[f]))
    for s in range(0,len(simulation_to_plot)):
        print('\tPlotting output for Simulation ' + str(simulation_to_plot[s]))
        
        # identify simulation conditions
        dvs = [x for x in DVs.iloc[simulation_to_plot[s],:]]
        dufs = [x for x in DUFs.iloc[simulation_to_plot[s],:]]
        
        # prepare data structure to hold collected data to plot
        hold_all_data_to_plot = [np.empty(shape = (0, len(metrics_test_read['Fiscal Year'])))] * len(data_names_to_plot)
        
        # cycle through realizations to collect data
        for r in range(0,len(realization_to_plot)):
            print('\t\tCollecting output for Realization ' + str(realization_to_plot[r]))
                
            # read data input files
            actuals = pd.read_csv(data_path + '/budget_actuals_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '_r' + str(realization_to_plot[r]) + '.csv', index_col = 0)
            budgets = pd.read_csv(data_path + '/budget_projections_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '_r' + str(realization_to_plot[r]) + '.csv', index_col = 0)
            metrics = pd.read_csv(data_path + '/financial_metrics_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '_r' + str(realization_to_plot[r]) + '.csv', index_col = 0)

            # collect data we want - reminder that actuals goes from
            # 2 years before first modeled year (so 2019, if starting 2021)
            # and ends at the final year (2039), budgets cover +1 year on 
            # both sides (ex: 2020 to 2040), metrics are exact range (2021-2039)
            # so they need to be trimmed to match up in time with just the
            # modeled period...
            for i in range(0,len(data_names_to_plot)):
                item = data_names_to_plot[i]
                if item in actuals.columns:
                    print('\t\t\tCollecting ' + item + ' from actuals...') if r == 0 else None
                    hold_all_data_to_plot[i] = np.append(hold_all_data_to_plot[i], [actuals[item].values[2:]], axis = 0)
                    
                elif item in budgets.columns:
                    print('\t\t\tCollecting ' + item + ' from budget...') if r == 0 else None
                    hold_all_data_to_plot[i] = np.append(hold_all_data_to_plot[i], [budgets[item].values[1:-1]], axis = 0)
                    
                elif item in metrics.columns:
                    print('\t\t\tCollecting ' + item + ' from metrics...') if r == 0 else None
                    hold_all_data_to_plot[i] = np.append(hold_all_data_to_plot[i], [metrics[item].values[:]], axis = 0)
                    
                else:
                    print('ERROR: CANNOT LOCATE ITEM: ' + item)
           
        # plot a long row of subplots together for as many 
        # variables as have been chosen to visualize
        fig, axs = plt.subplots(1, len(data_names_to_plot), sharey = False, figsize = (5*len(data_names_to_plot),5))
        
        # if plotting a single realization, make a special case
        if len(realization_to_plot) == 1:
            for ax, y_data, series_name in zip(axs.flat, hold_all_data_to_plot, data_names_to_plot):
                ax.plot(metrics['Fiscal Year'].values, y_data[0,:])
                ax.set_title(series_name)
                ax.set_xticklabels([int(x) for x in metrics['Fiscal Year'].values], rotation = 90)
        else:
            for ax, y_data, series_name in zip(axs.flat, hold_all_data_to_plot, data_names_to_plot):
                ax.boxplot(y_data[:,:])
                ax.set_title(series_name)
                ax.set_xticklabels([int(x) for x in metrics['Fiscal Year'].values], rotation = 90)
                
        # output and close figure to avoid overloading memory
        plt.savefig(data_path + '/Custom_Outputs_Plot_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + (('_SINGLE_REALIZATION_r' + str(realization_to_plot[r])) if len(realization_to_plot) == 1 else '') + '.png', bbox_inches= 'tight', dpi = 400)
        plt.close()
                
  
            
              
                
                
                
                
                
                
        