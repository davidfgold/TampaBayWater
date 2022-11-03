# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 09:51:24 2022

@author: lbl59
"""
#%%
# default macro run
import pandas as pd
import numpy as np
from openpyxl import load_workbook
import os
from tkinter import *

GUI = load_workbook('../../Finanical_Model_GUI.xlsm')
BAR = '/'
run_model_sheet = GUI['3-Run Model']
gen_du_dv_sheet = GUI['2-Gen alt scenarios']

local_base_path = run_model_sheet['D6'].value + BAR
local_data_sub_path = 'Data' + BAR
local_code_sub_path = 'Code' + BAR

#%%
num_simulations = run_model_sheet['D35'].value
dvs = np.zeros((num_simulations,11), dtype=float)

# if chose to use default, fill decision variable matrix with default values
# reference: original DV variable file (now "financial_model_DVs.csv")

dvs[:,0].fill(1.25) #covenant_threshold_net_revenue_plus_fund_balance
dvs[:,1].fill(1) #debt_covenant_required_ratio
dvs[:,2].fill(np.random.choice([0,1])) #KEEP_UNIFORM_RATE_STABLE
dvs[:,3].fill(np.random.choice([0,0.01])) #managed_uniform_rate_increase_rate
dvs[:,4].fill(np.random.choice([0,0.005])) #managed_uniform_rate_decrease_rate
dvs[:,5].fill(0.27) #previous_FY_unaccounted_fraction_of_total_enterprise_fund
dvs[:,6].fill(0.4) #debt_service_cap_fraction_of_gross_revenues
dvs[:,7].fill(0.05) #rr_fund_floor_fraction_of_gross_revenues
dvs[:,8].fill(0.05) #cip_fund_floor_fraction_of_gross_revenues
dvs[:,9].fill(0.01) #energy_fund_floor_fraction_of_gross_revenues
dvs[:,10].fill(0.1) #reserve_fund_floor_fraction_of_gross_revenues

dvs_filepath = local_base_path + local_data_sub_path  + "parameters/financial_model_DVs.csv"
np.savetxt(dvs_filepath, dvs, delimiter=",")

#%%
# DU factors
dufs  = np.zeros((num_simulations,20), dtype=float)

dufs[:,0].fill(0.085) #rate_stabilization_minimum_ratio
dufs[:,1].fill(0.3) #rate_stabilization_maximum_ratio
dufs[:,2].fill(0.15) #fraction_variable_operational_cost
dufs[:,3].fill(0.025) #budgeted_unencumbered_fraction
dufs[:,4].fill(0.033) #annual_budget_fixed_operating_cost_inflation_rate
dufs[:,5].fill(0.015) #annual_demand_growth_rate
dufs[:,6].fill(2021) #next_FY_budgeted_tampa_tbc_delivery
dufs[:,7].fill(0.7) #fixed_op_ex_factor
dufs[:,8].fill(0.9) #variable_op_ex_factor
dufs[:,9].fill(1.5) #non_sales_rev_factor
dufs[:,10].fill(1.5) #rate_stab_transfer_factor
dufs[:,11].fill(0.3) #rr_transfer_factor
dufs[:,12].fill(1) #other_transfer_factor
dufs[:,13].fill(1) #required_cip_factor
dufs[:,14].fill(0.033) #annual_budget_variable_operating_cost_inflation_rate
dufs[:,15].fill(0.02) #TAMPA_SALES_THRESHOLD_FRACTION
dufs[:,16].fill(1) #energy_transfer_factor
dufs[:,17].fill(0.75) #utility_reserve_fund_deficit_reduction_fraction
dufs[:,18].fill(np.random.choice([0,1])) #FLEXIBLE_CIP_SCHEDULE_TOGGLE
dufs[:,19].fill(np.random.choice([0,1])) #FOLLOW_CIP_SCHEDULE_TOGGLE

dufs_filepath = local_base_path + local_data_sub_path + "parameters/financial_model_DUfactors.csv"
np.savetxt(dufs_filepath, dufs, delimiter=",")
