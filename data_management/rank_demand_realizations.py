# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 10:47:48 2021
Index SWRE realizations by demand percentile for quantile plotting
Demands should roughly be the same across each different infrastructure 
    scenario's realizations set, so using run 0141 (baseline infra config)
    to get demand trends for all recent runs

@author: dgorelick
"""

import pandas as pd
import numpy as np
data_path = 'F:/MonteCarlo_Project/Cornell_UNC/cleaned_AMPL_files/run0141'

ten_thousand_added_to_read_files = 10000; n_realizations = 1000
demand_averages = []
for realization_id in range(1,n_realizations+1):
    AMPL_cleaned_data = pd.read_csv(data_path + '/ampl_' + str(ten_thousand_added_to_read_files + realization_id)[1:] + '.csv')
    demand_averages.append(AMPL_cleaned_data['total_demand__none'].iloc[-365:].mean())
    
pd.Series(demand_averages).to_csv('F:/MonteCarlo_Project/Cornell_UNC/financial_model_input_data/avg_demand_2040.csv', index = False, header = None)
