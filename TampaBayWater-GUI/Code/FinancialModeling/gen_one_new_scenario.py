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


# if user does not want to use default decision variable values
# assign only one DV value to all simulations
KEEP_UNIFORM_RATE_STABLE = 0

if gen_du_dv_sheet['N9'].value == "Yes":
    KEEP_UNIFORM_RATE_STABLE = 1

covenant_threshold_net_revenue_plus_fund_balance = np.full((num_simulations,), gen_du_dv_sheet['N7'].value)
debt_covenant_required_ratio = np.full((num_simulations,), gen_du_dv_sheet['N8'].value)
managed_uniform_rate_increase_rate = np.full((num_simulations,), gen_du_dv_sheet['N10'].value)
managed_uniform_rate_decrease_rate = np.full((num_simulations,), gen_du_dv_sheet['N11'].value)
previous_FY_unaccounted_fraction_of_total_enterprise_fund = np.full((num_simulations,), gen_du_dv_sheet['N12'].value)
debt_service_cap_fraction_of_gross_revenues = np.full((num_simulations,), gen_du_dv_sheet['N13'].value)
rr_fund_floor_fraction_of_gross_revenues = np.full((num_simulations,), gen_du_dv_sheet['N14'].value)
cip_fund_floor_fraction_of_gross_revenues = np.full((num_simulations,), gen_du_dv_sheet['N15'].value)
energy_fund_floor_fraction_of_gross_revenues = np.full((num_simulations,), gen_du_dv_sheet['N16'].value)
reserve_fund_floor_fraction_of_gross_revenues = np.full((num_simulations,), gen_du_dv_sheet['N17'].value)

# fill decision variable matrix
dvs[:,0] = covenant_threshold_net_revenue_plus_fund_balance
dvs[:,1] = debt_covenant_required_ratio
dvs[:,2].fill(KEEP_UNIFORM_RATE_STABLE)
dvs[:,3] = managed_uniform_rate_increase_rate
dvs[:,4] = managed_uniform_rate_decrease_rate
dvs[:,5] = previous_FY_unaccounted_fraction_of_total_enterprise_fund
dvs[:,6] = debt_service_cap_fraction_of_gross_revenues
dvs[:,7] = rr_fund_floor_fraction_of_gross_revenues
dvs[:,8] = cip_fund_floor_fraction_of_gross_revenues
dvs[:,9] = energy_fund_floor_fraction_of_gross_revenues
dvs[:,10] = reserve_fund_floor_fraction_of_gross_revenues

dvs_filepath = local_base_path + local_data_sub_path  + "parameters/financial_model_DVs.csv"
np.savetxt(dvs_filepath, dvs, delimiter=",")

#%%
# DU factors
FOLLOW_CIP_SCHEDULE_TOGGLE = 0
FLEXIBLE_CIP_SCHEDULE_TOGGLE = 0

dufs  = np.zeros((num_simulations,20), dtype=float)
if gen_du_dv_sheet['G25'].value == "Yes":
    FOLLOW_CIP_SCHEDULE_TOGGLE = 1

if gen_du_dv_sheet['G26'].value == "Yes":
    FLEXIBLE_CIP_SCHEDULE_TOGGLE = 1

rate_stabilization_minimum_ratio = np.full((num_simulations,), gen_du_dv_sheet['G7'].value)
rate_stabilization_maximum_ratio = np.full((num_simulations,), gen_du_dv_sheet['G8'].value)
fraction_variable_operational_cost = np.full((num_simulations,), gen_du_dv_sheet['G9'].value)
budgeted_unencumbered_fraction = np.full((num_simulations,), gen_du_dv_sheet['G10'].value)
annual_budget_fixed_operating_cost_inflation_rate = np.full((num_simulations,), gen_du_dv_sheet['G11'].value)
annual_demand_growth_rate = np.full((num_simulations,), gen_du_dv_sheet['G12'].value)
next_FY_budgeted_tampa_tbc_delivery = np.full((num_simulations,), gen_du_dv_sheet['G13'].value)
fixed_op_ex_factor = np.full((num_simulations,), gen_du_dv_sheet['G14'].value)
variable_op_ex_factor = np.full((num_simulations,), gen_du_dv_sheet['G15'].value)
non_sales_rev_factor = np.full((num_simulations,), gen_du_dv_sheet['G16'].value)
rate_stab_transfer_factor = np.full((num_simulations,), gen_du_dv_sheet['G17'].value)
rr_transfer_factor = np.full((num_simulations,), gen_du_dv_sheet['G18'].value)
other_transfer_factor = np.full((num_simulations,), gen_du_dv_sheet['G19'].value)
required_cip_factor = np.full((num_simulations,), gen_du_dv_sheet['G20'].value)
annual_budget_variable_operating_cost_inflation_rate = np.full((num_simulations,), gen_du_dv_sheet['G21'].value)
TAMPA_SALES_THRESHOLD_FRACTION = np.full((num_simulations,), gen_du_dv_sheet['G22'].value)
energy_transfer_factor = np.full((num_simulations,), gen_du_dv_sheet['G23'].value)
utility_reserve_fund_deficit_reduction_fraction = np.full((num_simulations,), gen_du_dv_sheet['G24'].value)

dufs[:,0] = rate_stabilization_minimum_ratio
dufs[:,1] = rate_stabilization_maximum_ratio
dufs[:,2] = fraction_variable_operational_cost
dufs[:,3] = budgeted_unencumbered_fraction
dufs[:,4] = annual_budget_fixed_operating_cost_inflation_rate
dufs[:,5] = annual_demand_growth_rate
dufs[:,6] = next_FY_budgeted_tampa_tbc_delivery
dufs[:,7] = fixed_op_ex_factor
dufs[:,8] = variable_op_ex_factor
dufs[:,9] = non_sales_rev_factor
dufs[:,10] = rate_stab_transfer_factor
dufs[:,11] = rr_transfer_factor
dufs[:,12] = other_transfer_factor
dufs[:,13] = required_cip_factor
dufs[:,14] = annual_budget_variable_operating_cost_inflation_rate
dufs[:,15] = TAMPA_SALES_THRESHOLD_FRACTION
dufs[:,16] = energy_transfer_factor
dufs[:,17] = utility_reserve_fund_deficit_reduction_fraction
dufs[:,18].fill(FLEXIBLE_CIP_SCHEDULE_TOGGLE)
dufs[:,19].fill(FOLLOW_CIP_SCHEDULE_TOGGLE)

dufs_filepath = local_base_path + local_data_sub_path + "parameters/financial_model_DUfactors.csv"
np.savetxt(dufs_filepath, dufs, delimiter=",")
