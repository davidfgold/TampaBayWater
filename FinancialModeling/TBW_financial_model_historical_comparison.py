# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 16:46:51 2020
TAMPA BAY WATER AUTHORITY FINANCIAL MODEL
compare historic vs modeled hind-cast results
@author: dgorelic
"""

import pandas as pd
data_path = 'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/output'

# read historic data
# hard-coded covenant values from budget spreadsheets shared by TBW (Fy2019 Table 12)/reports
# NOTE: THIS SCRIPT WILL BREAK IF NOT DOING FY 2015 - 2019 (5 YEARS)
hist_actuals = pd.read_csv(data_path + '/historic_actuals.csv')
hist_budgets = pd.read_csv(data_path + '/historic_budgets.csv')
hist_water_delivery_sales = pd.read_csv(data_path + '/historic_sales.csv')

# note: FY 18 and 19 debt covenant levels are misleading because they don't
# factor in R&R and CIP Fund required deposits
hist_rate_covenant = [1.43,1.48,1.49,1.51,1.58] # from FY15 -> 19
hist_debt_covenant = [1.0,1.01,1.0,1.11,1.16] # from FY15 -> 19
hist_debt_covenant[3] = 78079017 / (70133615 + 4215354 + 3325468)
hist_debt_covenant[4] = 81451346 / (70122276 + 5509008 + 5356993)

# make a set of colors for the plots
n_reals = 49; sim = 1
my_color_set = ['m'] * (n_reals-1) + ['k']

# read modeled data
for col in [x for x in hist_actuals.columns[2:].values]:
    data_to_plot = pd.DataFrame({'Fiscal Year': hist_actuals['Fiscal Year'].values})
    for r_id in range(1,n_reals):
        model_actuals = pd.read_csv(data_path + '/budget_actuals_s' + str(sim) + '_r' + str(r_id) + '.csv')
        data_to_plot.insert(data_to_plot.shape[1], 'Modeled ' + str(r_id), model_actuals[col])
    data_to_plot.insert(data_to_plot.shape[1], 'Historic', hist_actuals[col].values)
    data_to_plot.set_index('Fiscal Year').loc[[2015,2016,2017,2018,2019]].plot(
            title = col + '- Actuals Comparison', legend = False,
            color = my_color_set, linewidth = 2).get_figure().savefig(data_path + '/' + col + '_actual_historic_comp.png')
    
for col in [x for x in hist_budgets.columns[2:].values]:
    data_to_plot = pd.DataFrame({'Fiscal Year': hist_budgets['Fiscal Year'].values})
    for r_id in range(1,n_reals):
        model_budgets = pd.read_csv(data_path + '/budget_projections_s' + str(sim) + '_r' + str(r_id) + '.csv')
        data_to_plot.insert(data_to_plot.shape[1], 'Modeled ' + str(r_id), model_budgets[col])
    data_to_plot.insert(data_to_plot.shape[1], 'Historic', hist_budgets[col].values)
    data_to_plot.set_index('Fiscal Year').loc[[2016,2017,2018,2019,2020]].plot(
            title = col + '- Budget Comparison', legend = False,
            color = my_color_set, linewidth = 2).get_figure().savefig(data_path + '/' + col + '_budget_historic_comp.png')
    
for col in [x for x in hist_water_delivery_sales.columns[3:22].values]:
    data_to_plot = pd.DataFrame({'Fiscal Year': hist_water_delivery_sales['Fiscal Year'].values})
    for r_id in range(1,n_reals):
        model_water_delivery_sales = pd.read_csv(data_path + '/water_deliveries_revenues_s' + str(sim) + '_r' + str(r_id) + '.csv')
        data_to_plot.insert(data_to_plot.shape[1], 'Modeled ' + str(r_id), model_water_delivery_sales[col])
    data_to_plot.insert(data_to_plot.shape[1], 'Historic', hist_water_delivery_sales[col].values)
    data_to_plot.groupby('Fiscal Year').sum().loc[[2015,2016,2017,2018,2019]].plot(
            title = col + '- Comparison', legend = False,
            color = my_color_set, linewidth = 2).get_figure().savefig(data_path + '/' + col + '_delivery_historic_comp.png')

# exceptions for covenants
DC = pd.DataFrame({'Fiscal Year': [2015,2016,2017,2018,2019]})
RC = pd.DataFrame({'Fiscal Year': [2015,2016,2017,2018,2019]})
for r_id in range(1,n_reals):
    model_metrics = pd.read_csv(data_path + '/financial_metrics_s' + str(sim) + '_r' + str(r_id) + '.csv')
    Modeled = model_metrics['Debt Covenant Ratio']
    DC.insert(DC.shape[1], 'Modeled ' + str(r_id), Modeled.values)
    
    Modeled = model_metrics['Rate Covenant Ratio']
    RC.insert(RC.shape[1], 'Modeled ' + str(r_id), Modeled.values)

# append historic record last so it is plotted on top
DC.insert(DC.shape[1], 'Historic', hist_debt_covenant)
RC.insert(RC.shape[1], 'Historic', hist_rate_covenant)
DC.set_index('Fiscal Year').plot(title = 'Debt Covenant Comparison', linewidth = 2,
            color = my_color_set, legend = False).get_figure().savefig(data_path + '/DC_historic_comp.png')
RC.set_index('Fiscal Year').plot(title = 'Rate Covenant Comparison', linewidth = 2,
            color = my_color_set, legend = False).get_figure().savefig(data_path + '/RC_historic_comp.png')

