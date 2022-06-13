# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 16:46:51 2020
TAMPA BAY WATER AUTHORITY FINANCIAL MODEL
compare historic vs modeled hind-cast results
@author: dgorelic
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

data_path = 'C:/Users/cmpet/OneDrive/Documents/UNCTBW/Modeloutput/historical_comparison'
#data_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/local_results/historical_validation'


# read historic data
# hard-coded covenant values from budget spreadsheets shared by TBW (Fy2019 Table 12)/reports
# NOTE: UPDATED TO INCLUDE MORE FYS, BUT SCRIPT MAY BE UNSTABLE IF APPENDED AGAIN LATER
hist_actuals = pd.read_csv(data_path + '/historic_actuals.csv')
hist_budgets = pd.read_csv(data_path + '/historic_budgets.csv')
hist_water_delivery_sales = pd.read_csv(data_path + '/historic_sales.csv')

# NOTE: Previously, FY 18 and FY 19 were adjusted by David Gorelick to include 
#   CIP and R&R fund deposits not recorded in Table 12 of CAFR reports as they
#   were in previous years. However, newer CAFR from FY2020 still shows no
#   required deposits for those (or future) FYs, so this adjustment is now
#   removed.
#hist_rate_covenant = [1.44,1.51,1.43,1.48,1.49,1.51,1.58,1.61, 1.61] # from FY13 -> 21 PLACEHOLDER FOR 2021
#hist_debt_covenant = [1.0,1.01,1.0,1.01,1.0,1.11,1.16,1.19, 1.19] # from FY13 -> 21 PLACEHOLDER

hist_rate_covenant = [1.44,1.51,1.43,1.48,1.49,1.51,1.58,1.61] # from FY13 -> 20
hist_debt_covenant = [1.0,1.01,1.0,1.01,1.0,1.11,1.16,1.19] # from FY13 -> 20

# make a set of colors for the plots
n_reals = 10; sim = 0; f_id = 125

# read modeled data
for col in [x for x in hist_actuals.columns[2:].values]:
    data_to_plot = pd.DataFrame({'Fiscal Year': hist_actuals['Fiscal Year'].values})
    fig = plt.figure(figsize = (6,5)); ax = fig.add_subplot(1,1,1)
    for r_id in range(1,n_reals+1):
        model_actuals = pd.read_csv(data_path + '/budget_actuals_f' + str(f_id) + '_s' + str(sim) + '_r' + str(r_id) + '.csv')
        if col in ['Uniform Rate (Full)', 
                   'Uniform Rate (Variable Portion)', 
                   'TBC Sales Rate']:
            y_label = '$/kgal'; y_divider = 1 # plot in $/kgal rate
        else:
            y_divider = 1000000; y_label = '$ Millions' # plot in millions of dollars
        data_to_plot.insert(data_to_plot.shape[1], 'Modeled ' + str(r_id), model_actuals[col]/y_divider)
        
    ax.fill_between(data_to_plot['Fiscal Year'][2:], 
                    np.max(data_to_plot.iloc[2:,1:], axis = 1), 
                    np.min(data_to_plot.iloc[2:,1:], axis = 1), 
                    color = 'm', alpha = 0.75, edgecolor = 'm')
    ax.plot(data_to_plot['Fiscal Year'][2:], 
            hist_actuals[col].values[2:]/y_divider, 
            color = 'k', linewidth = 5)
    ax.set_xticks(range(2014,2022))
    ax.set_xticklabels(range(2014,2022))
    plt.xlabel('Fiscal Year')
    plt.ylabel(y_label)
    plt.title(col + ' - Actuals Comparison')
    plt.savefig(data_path + '/' + col + '_actual_historic_comp.png', bbox_inches= 'tight')
    plt.close()
    
for col in [x for x in hist_budgets.columns[2:].values]:
    data_to_plot = pd.DataFrame({'Fiscal Year': hist_budgets['Fiscal Year'].values})
    fig = plt.figure(figsize = (6,5)); ax = fig.add_subplot(1,1,1)
    for r_id in range(1,n_reals+1):
        model_budgets = pd.read_csv(data_path + '/budget_projections_f' + str(f_id) + '_s' + str(sim) + '_r' + str(r_id) + '.csv')
        if col in ['Uniform Rate', 
                   'Variable Uniform Rate', 
                   'TBC Rate']:
            y_label = '$/kgal'; y_divider = 1 # plot in $/kgal rate
        else:
            y_divider = 1000000; y_label = '$ Millions' # plot in millions of dollars
        data_to_plot.insert(data_to_plot.shape[1], 'Modeled ' + str(r_id), model_budgets[col]/y_divider)

    ax.fill_between(data_to_plot['Fiscal Year'][2:], 
                    np.max(data_to_plot.iloc[2:,1:], axis = 1), 
                    np.min(data_to_plot.iloc[2:,1:], axis = 1), 
                    color = 'm', alpha = 0.75, edgecolor = 'm')
    ax.plot(data_to_plot['Fiscal Year'][2:], 
            hist_budgets[col].values[2:]/y_divider, 
            color = 'k', linewidth = 5)
    
    if col in ['Water Sales Revenue', 'Annual Estimate']:
        ax.set_ylim(bottom = 100, top = 200)
    if col in ['Variable Uniform Rate']:
        ax.set_ylim(bottom = 0.25, top = 0.50)
    ax.set_xticks(range(2015,2022))
    ax.set_xticklabels(range(2015,2022))
    plt.xlabel('Fiscal Year')
    plt.ylabel(y_label)
    plt.title(col + ' - Budget Comparison')
    plt.savefig(data_path + '/' + col + '_budget_historic_comp.png', bbox_inches= 'tight')
    plt.close()
    
y_divider = 1000000; y_label = '$ Millions' # plot in millions of dollars
for col in [x for x in hist_water_delivery_sales.columns[10:22].values]:
    data_to_plot = pd.DataFrame({'Fiscal Year': hist_water_delivery_sales['Fiscal Year'].values})
    fig = plt.figure(figsize = (6,5)); ax = fig.add_subplot(1,1,1)
    for r_id in range(1,n_reals+1):
        model_water_delivery_sales = pd.read_csv(data_path + '/water_deliveries_revenues_f' + str(f_id) + '_s' + str(sim) + '_r' + str(r_id) + '.csv')
        data_to_plot.insert(data_to_plot.shape[1], 'Modeled ' + str(r_id), model_water_delivery_sales[col]/y_divider)
        
    ax.fill_between(np.unique(data_to_plot['Fiscal Year'])[1:], 
                    np.max(data_to_plot.groupby('Fiscal Year').sum().iloc[1:,1:], axis = 1), 
                    np.min(data_to_plot.groupby('Fiscal Year').sum().iloc[1:,1:], axis = 1), 
                    color = 'm', alpha = 0.75, edgecolor = 'm')
    ax.plot(np.unique(data_to_plot['Fiscal Year'])[1:], 
            hist_water_delivery_sales[col].groupby(hist_water_delivery_sales['Fiscal Year']).sum().values[1:]/y_divider, 
            color = 'k', linewidth = 5)
    ax.set_xticks(range(2014,2022))
    ax.set_xticklabels(range(2014,2022))
    plt.xlabel('Fiscal Year')
    plt.ylabel(y_label)
    plt.title(col + ' - Comparison')
    plt.savefig(data_path + '/' + col + '_delivery_historic_comp.png', bbox_inches= 'tight')
    plt.close()

# exceptions for covenants
DC = pd.DataFrame({'Fiscal Year': [2015,2016,2017,2018,2019,2020]})
RC = pd.DataFrame({'Fiscal Year': [2015,2016,2017,2018,2019,2020]})
fig, (ax1, ax2) = plt.subplots(1,2, sharey = False, figsize = (12,5))
for r_id in range(1,n_reals+1):
    model_metrics = pd.read_csv(data_path + '/financial_metrics_f' + str(f_id) + '_s' + str(sim) + '_r' + str(r_id) + '.csv')
    Modeled = model_metrics['Debt Covenant Ratio']
    DC.insert(DC.shape[1], 'Modeled ' + str(r_id), Modeled.values)
    
    Modeled = model_metrics['Rate Covenant Ratio']
    RC.insert(RC.shape[1], 'Modeled ' + str(r_id), Modeled.values)

ax1.fill_between(DC['Fiscal Year'], 
                 np.max(DC.iloc[:,1:], axis = 1), 
                 np.min(DC.iloc[:,1:], axis = 1), 
                 color = 'm', alpha = 0.75, edgecolor = 'm')
ax1.plot(DC['Fiscal Year'], hist_debt_covenant[-(len(DC['Fiscal Year'])):], 
        color = 'k', linewidth = 5)
ax2.fill_between(RC['Fiscal Year'], 
                 np.max(RC.iloc[:,1:], axis = 1), 
                 np.min(RC.iloc[:,1:], axis = 1), 
                 color = 'm', alpha = 0.75, edgecolor = 'm')
ax2.plot(RC['Fiscal Year'], hist_rate_covenant[-(len(RC['Fiscal Year'])):], 
        color = 'k', linewidth = 5)

ax1.set_xticks(range(2015,2021))
ax1.set_xticklabels(range(2015,2021))
ax2.set_xticks(range(2015,2021))
ax2.set_xticklabels(range(2015,2021))
ax1.set_xlabel('Fiscal Year')
ax2.set_xlabel('Fiscal Year')
ax1.set_ylabel('Covenant Ratio')
ax1.set_title('Debt Covenant Comparison')
ax2.set_title('Rate Covenant Comparison')
plt.savefig(data_path + '/Covenant_Comparisons.png', bbox_inches= 'tight')
plt.close()

