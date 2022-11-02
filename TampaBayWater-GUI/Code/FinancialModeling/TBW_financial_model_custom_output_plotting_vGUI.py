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
from openpyxl import load_workbook
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()


import sys
sys.path.insert(1, '../data_management')

GUI = load_workbook('../../Financial_Model_GUI.xlsm')
BAR = '/'
run_model_sheet = GUI['3-Run Model']
figure_to_plot = run_model_sheet['K15'].value
run_id = run_model_sheet['D31'].value
num_sim = run_model_sheet['D35'].value

local_base_path = run_model_sheet['D6'].value
local_output_sub_path = 'Output' + BAR
local_data_sub_path = 'Data' + BAR
local_code_sub_path = 'Code' + BAR

results_path = local_base_path + local_output_sub_path + 'financial_model_results/'
dv_path = local_base_path + local_data_sub_path + 'parameters/'
figures_out_path = local_base_path + local_output_sub_path + 'output_figures/'

#results_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/local_results'
#dv_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Code/TampaBayWater/FinancialModeling'

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
data_names_to_plot = ['Rate Covenant Ratio', 'Debt Covenant Ratio', 'Uniform Rate',
                      'Debt Service', 'Debt Service Deferred', 'Remaining Unallocated Deficit',
                      'Utility Reserve Fund Balance (Total)', 'Rate Stabilization Fund (Total)',
                      'CIP Fund (Total)', 'R&R Fund (Total)', 'Energy Savings Fund (Total)']

formulation_to_plot = [run_id]
simulation_to_plot = np.arange(0, num_sim, dtype=int)

#formulation_to_plot = [125] # list all
#simulation_to_plot = [0,1,2,3,4,5,6,7,8] # list all, IDs start at 0
#realization_to_plot = [x for x in range(1,num_sim+1)] # list which we want, IDs start at 1 not zero
realization_to_plot = [1]
metrics_test_read = pd.read_csv(results_path + 'financial_metrics_f' + str(formulation_to_plot[0]) +
                                '_s' + str(simulation_to_plot[0]) + '_r' + str(realization_to_plot[0]) + '.csv',
                                index_col = 0)

# read in DV and DUF files to identify the conditions under which
# each simulation is running (i.e. fixed UR, capped Debt Service, etc.)
DVs = pd.read_csv(dv_path + 'financial_model_DVs.csv', header = None)
DUFs = pd.read_csv(dv_path + 'financial_model_DUfactors.csv', header = None)

err = open('../../Output/error_files/err_figures_gen.txt', 'w')

data_name_to_plot = ""

if figure_to_plot == "Rate Covenant Ratio":
    data_name_to_plot = data_names_to_plot[0]
elif figure_to_plot == "Debt Covenant Ratio":
    data_name_to_plot = data_names_to_plot[1]
elif figure_to_plot == "Debt Service":
    data_name_to_plot = data_names_to_plot[3]
elif figure_to_plot == "Debt Service Deferred":
    data_name_to_plot = data_names_to_plot[4]
elif figure_to_plot == "Uniform Rate":
    data_name_to_plot = data_names_to_plot[2]
elif figure_to_plot == "Remaining Unallocated Deficit":
    data_name_to_plot = data_names_to_plot[5]
elif figure_to_plot == "utility Reserve Fund Balance (Total)":
    data_name_to_plot = data_names_to_plot[6]
elif figure_to_plot == "Rate Stabilization Fund (Total)":
    data_name_to_plot = data_names_to_plot[7]
elif figure_to_plot == "CIP Fund (Total)":
    data_name_to_plot = data_names_to_plot[8]
elif figure_to_plot == "R&R Fund (Total)":
    data_name_to_plot = data_names_to_plot[9]
elif figure_to_plot == "Energy Savings Fund (Total)":
    data_name_to_plot = data_names_to_plot[10]

# loop through all results to report data
for f in range(0,len(formulation_to_plot)):
    print('Plotting output for Formulation ' + str(formulation_to_plot[f]))

    for r in range(0,len(realization_to_plot)):
        print('\t\tCollecting output for Realization ' + str(realization_to_plot[r]))

        if realization_to_plot[r] == 95:
            continue
        fig, axs = plt.subplots(1, 1, sharey = False, figsize = (7,7))
        # prepare data structure to hold collected data to plot
        hold_all_data_to_plot = np.zeros((num_sim, len(metrics_test_read['Fiscal Year'])))

        for s in range(0,len(simulation_to_plot)):
            print('\tPlotting output for Simulation ' + str(simulation_to_plot[s]))

            # identify simulation conditions
            #dvs = [x for x in DVs.iloc[simulation_to_plot[s],:]]
            #dufs = [x for x in DUFs.iloc[simulation_to_plot[s],:]]
            # read data input files
            actuals = pd.read_csv(results_path + 'budget_actuals_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '_r' + str(realization_to_plot[r]) + '.csv', index_col = 0)
            budgets = pd.read_csv(results_path + 'budget_projections_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '_r' + str(realization_to_plot[r]) + '.csv', index_col = 0)
            metrics = pd.read_csv(results_path + 'financial_metrics_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '_r' + str(realization_to_plot[r]) + '.csv', index_col = 0)

            # collect data we want - reminder that actuals goes from
            # 2 years before first modeled year (so 2019, if starting 2021)
            # and ends at the final year (2039), budgets cover +1 year on
            # both sides (ex: 2020 to 2040), metrics are exact range (2021-2039)
            # so they need to be trimmed to match up in time with just the
            # modeled period...
            item = data_name_to_plot
            if item in actuals.columns:
                print('\t\t\tCollecting ' + item + ' from actuals...') if r == 0 else None
                hold_all_data_to_plot[s,:] = actuals[item].values[2:]

            elif item in budgets.columns:
                print('\t\t\tCollecting ' + item + ' from budget...') if r == 0 else None
                hold_all_data_to_plot[s,:] = budgets[item].values[1:-1]

            elif item in metrics.columns:
                print('\t\t\tCollecting ' + item + ' from metrics...') if r == 0 else None
                hold_all_data_to_plot[s,:] = metrics[item].values[:]

            else:
                print('ERROR: CANNOT LOCATE ITEM: ' + item)
                err.write('ERROR: CANNOT LOCATE ITEM: ' + item)
                err.write("\n")

        #print(hold_all_data_to_plot)
        # plot a long row of subplots together for as many
        # variables as have been chosen to visualize
        #fig, axs = plt.subplots(1, 1, sharey = False, figsize = (5,5))

        # if plotting a single realization, make a special case
        if len(simulation_to_plot) == 1:
            #for ax, y_data, series_name in zip(axs, hold_all_data_to_plot, data_name_to_plot):
            axs.plot(metrics['Fiscal Year'].values, hold_all_data_to_plot[0])
            axs.set_title(data_name_to_plot)
            axs.set_xticklabels(metrics['Fiscal Year'].values.astype(int), rotation = 90)
        else:
            #for ax, y_data, series_name in zip(axs, hold_all_data_to_plot, data_name_to_plot):
            axs.boxplot(hold_all_data_to_plot[:][:])
            axs.set_title(data_name_to_plot)
            axs.set_xticklabels(metrics['Fiscal Year'].values.astype(int), rotation = 90)

        axs.set_xlabel('Fiscal Year')
        axs.set_ylabel("USD$")
    # output and close figure to avoid overloading memory
    plt.savefig(figures_out_path + data_name_to_plot + '_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + (('_SINGLE_REALIZATION_r' + str(realization_to_plot[r])) if len(realization_to_plot) == 1 else '') + '.png', bbox_inches= 'tight', dpi = 400)
    plt.show()


'''
# loop through all results to report data
for f in range(0,len(formulation_to_plot)):
    print('Plotting output for Formulation ' + str(formulation_to_plot[f]))

    fig, axs = plt.subplots(1, 1, sharey = False, figsize = (5,5))

    for s in range(0,len(simulation_to_plot)):
        print('\tPlotting output for Simulation ' + str(simulation_to_plot[s]))

        # identify simulation conditions
        #dvs = [x for x in DVs.iloc[simulation_to_plot[s],:]]
        #dufs = [x for x in DUFs.iloc[simulation_to_plot[s],:]]

        # prepare data structure to hold collected data to plot
        hold_all_data_to_plot = [np.empty(shape = (0, len(metrics_test_read['Fiscal Year'])))]*1
        # cycle through realizations to collect data

        for r in range(0,len(realization_to_plot)):
            print('\t\tCollecting output for Realization ' + str(realization_to_plot[r]))

            if realization_to_plot[r] == 95:
                continue

            # read data input files
            actuals = pd.read_csv(results_path + 'budget_actuals_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '_r' + str(realization_to_plot[r]) + '.csv', index_col = 0)
            budgets = pd.read_csv(results_path + 'budget_projections_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '_r' + str(realization_to_plot[r]) + '.csv', index_col = 0)
            metrics = pd.read_csv(results_path + 'financial_metrics_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '_r' + str(realization_to_plot[r]) + '.csv', index_col = 0)

            # collect data we want - reminder that actuals goes from
            # 2 years before first modeled year (so 2019, if starting 2021)
            # and ends at the final year (2039), budgets cover +1 year on
            # both sides (ex: 2020 to 2040), metrics are exact range (2021-2039)
            # so they need to be trimmed to match up in time with just the
            # modeled period...
            item = data_name_to_plot
            if item in actuals.columns:
                print('\t\t\tCollecting ' + item + ' from actuals...') if r == 0 else None
                hold_all_data_to_plot = np.append(hold_all_data_to_plot[0], [actuals[item].values[2:]], axis = 0)

            elif item in budgets.columns:
                print('\t\t\tCollecting ' + item + ' from budget...') if r == 0 else None
                hold_all_data_to_plot = np.append(hold_all_data_to_plot[0], [budgets[item].values[1:-1]], axis = 0)

            elif item in metrics.columns:
                print('\t\t\tCollecting ' + item + ' from metrics...') if r == 0 else None
                hold_all_data_to_plot = np.append(hold_all_data_to_plot[0], [metrics[item].values[:]], axis = 0)

            else:
                print('ERROR: CANNOT LOCATE ITEM: ' + item)
                err.write('ERROR: CANNOT LOCATE ITEM: ' + item)
                err.write("\n")
        print(hold_all_data_to_plot)
        # plot a long row of subplots together for as many
        # variables as have been chosen to visualize
        #fig, axs = plt.subplots(1, 1, sharey = False, figsize = (5,5))

        # if plotting a single realization, make a special case
    if len(realization_to_plot) == 1:
        #for ax, y_data, series_name in zip(axs, hold_all_data_to_plot, data_name_to_plot):
        axs.plot(metrics['Fiscal Year'].values, hold_all_data_to_plot[0])
        axs.set_title(data_name_to_plot)
        axs.set_xticklabels(metrics['Fiscal Year'].values, rotation = 90)
    else:
        #for ax, y_data, series_name in zip(axs, hold_all_data_to_plot, data_name_to_plot):
        axs.boxplot(hold_all_data_to_plot[:][:])
        axs.set_title(data_name_to_plot)
        axs.set_xticklabels(metrics['Fiscal Year'].values, rotation = 90)

    # output and close figure to avoid overloading memory
    plt.savefig(figures_out_path + data_name_to_plot + '_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + (('_SINGLE_REALIZATION_r' + str(realization_to_plot[r])) if len(realization_to_plot) == 1 else '') + '.png', bbox_inches= 'tight', dpi = 400)
    plt.show()
'''
err.write("End error file.")
err.close()
