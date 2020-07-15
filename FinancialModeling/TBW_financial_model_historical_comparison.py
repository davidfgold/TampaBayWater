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
hist_rate_covenant = [1.43,1.48,1.49,1.51,1.58] # from FY15 -> 19
hist_debt_covenant = [1.0,1.01,1.0,1.11,1.16] # from FY15 -> 19

# read modeled data
sim = 1; r_id = 1
model_actuals = pd.read_csv(data_path + '/budget_actuals_s' + str(sim) + '_r' + str(r_id) + '.csv')
model_budgets = pd.read_csv(data_path + '/budget_projections_s' + str(sim) + '_r' + str(r_id) + '.csv')
model_water_delivery_sales = pd.read_csv(data_path + '/water_deliveries_revenues_s' + str(sim) + '_r' + str(r_id) + '.csv')
model_metrics = pd.read_csv(data_path + '/financial_metrics_s' + str(sim) + '_r' + str(r_id) + '.csv')


# organize comparisons, plot and export
for col in [x for x in model_actuals.columns[2:].values]:
    data_to_plot = pd.DataFrame({'Fiscal Year': model_actuals['Fiscal Year'].values, 
                                 'Historic': hist_actuals[col].values, 
                                 'Modeled': model_actuals[col].values})
    data_to_plot.set_index('Fiscal Year').plot(title = col + '- Actuals Comparison').get_figure().savefig(data_path + '/' + col + '_actual_historic_comp.png')
    
for col in [x for x in model_budgets.columns[2:].values]:
    data_to_plot = pd.DataFrame({'Fiscal Year': model_budgets['Fiscal Year'].values, 
                                 'Historic': hist_budgets[col].values, 
                                 'Modeled': model_budgets[col].values})
    data_to_plot.set_index('Fiscal Year').plot(title = col + '- Budget Comparison').get_figure().savefig(data_path + '/' + col + '_budget_historic_comp.png')
    
modeled_sum = 0; historic_sum = 0    
for col in [x for x in model_water_delivery_sales.columns[2:22].values]:
    data_to_plot = pd.DataFrame({'Fiscal Year': model_water_delivery_sales['Fiscal Year'].values, 
                                 'Historic': hist_water_delivery_sales[col].values, 
                                 'Modeled': model_water_delivery_sales[col].values}).groupby('Fiscal Year').sum()
    data_to_plot.plot(title = col + ' Comparison').get_figure().savefig(data_path + '/' + col + '_delivery_historic_comp.png')
    
    # plot of aggregated fixed water sales
    if col in ['Fixed Water Sales - City of St. Petersburg',
               'Fixed Water Sales - Pinellas County',
               'Fixed Water Sales - City of Tampa (Uniform)',
               'Fixed Water Sales - Hillsborough County',
               'Fixed Water Sales - Pasco County',
               'Fixed Water Sales - City of New Port Richey']:
        modeled_sum += model_water_delivery_sales[col].values 
        historic_sum += hist_water_delivery_sales[col].values 
        if col == 'Fixed Water Sales - City of New Port Richey':
                data_to_plot = pd.DataFrame({'Fiscal Year': model_water_delivery_sales['Fiscal Year'].values, 
                                             'Historic': historic_sum, 
                                             'Modeled': modeled_sum}).groupby('Fiscal Year').sum()
                data_to_plot.plot(title = 'Total Fixed Sales Comparison').get_figure().savefig(data_path + '/total_fixed_sales_historic_comp.png')
    

# exceptions for covenants
DC = pd.DataFrame({'Fiscal Year': model_metrics['Fiscal Year'].values, 
                   'Historic': hist_debt_covenant, 
                   'Modeled': model_metrics['Debt Covenant Ratio'].values})
RC = pd.DataFrame({'Fiscal Year': model_metrics['Fiscal Year'].values, 
                   'Historic': hist_rate_covenant, 
                   'Modeled': model_metrics['Rate Covenant Ratio'].values})
DC.set_index('Fiscal Year').plot(title = 'Debt Covenant Comparison').get_figure().savefig(data_path + '/DC_historic_comp.png')
RC.set_index('Fiscal Year').plot(title = 'Rate Covenant Comparison').get_figure().savefig(data_path + '/RC_historic_comp.png')