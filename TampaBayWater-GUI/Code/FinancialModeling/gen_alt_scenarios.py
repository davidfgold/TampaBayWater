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
err = open('../../Output/error_files/err_generate_scenarios.txt', 'w')

num_simulations = run_model_sheet['D35'].value
if num_simulations <= 1:
    err.write("ERROR: Too few simulations. \nPlease use two or more simulations if generating more than one alternative scenario.")

# decision variables
dvs = np.zeros((num_simulations,11), dtype=float)

KEEP_UNIFORM_RATE_STABLE = 0

if gen_du_dv_sheet['N9'].value == "Yes":
    KEEP_UNIFORM_RATE_STABLE = 1

#%%
# if user does not want to use default decision variable values
# set decision variables
covenant_threshold_net_revenue_plus_fund_balance = np.random.uniform(low=float(covenant_threshold_low.get()),
                                                     high=float(covenant_threshold_high.get()),
                                                     size=(num_simulations,))

debt_covenant_required_ratio = np.random.uniform(low=float(debt_covenant_threshold_low.get()),
                                                     high=float(debt_covenant_threshold_high.get()),
                                                     size=(num_simulations,))

managed_uniform_rate_increase_rate = np.random.uniform(low=float(managed_uniform_incr_low.get()),
                                                     high=float(managed_uniform_incr_high.get()),
                                                     size=(num_simulations,))

managed_uniform_rate_decrease_rate = np.random.uniform(low=float(managed_uniform_decr_low.get()),
                                                     high=float(managed_uniform_decr_high.get()),
                                                     size=(num_simulations,))

previous_FY_unaccounted_fraction_of_total_enterprise_fund = np.random.uniform(low=float(prev_unacc_low.get()),
                                                     high=float(prev_unacc_high.get()),
                                                     size=(num_simulations,))

debt_service_cap_fraction_of_gross_revenues = np.random.uniform(low=float(debt_service_cap_low.get()),
                                                     high=float(debt_service_cap_high.get()),
                                                     size=(num_simulations,))

rr_fund_floor_fraction_of_gross_revenues = np.random.uniform(low=float(rr_fraction_low.get()),
                                                     high=float(rr_fraction_high.get()),
                                                     size=(num_simulations,))

cip_fund_floor_fraction_of_gross_revenues = np.random.uniform(low=float(cip_fund_fraction_low.get()),
                                                     high=float(cip_fund_fraction_high.get()),
                                                     size=(num_simulations,))

energy_fund_floor_fraction_of_gross_revenues = np.random.uniform(low=float(energy_fund_fraction_low.get()),
                                                     high=float(energy_fund_fraction_high.get()),
                                                     size=(num_simulations,))

reserve_fund_floor_fraction_of_gross_revenues = np.random.uniform(low=float(rf_fund_fraction_low.get()),
                                                     high=float(rf_fund_fraction_high.get()),
                                                     size=(num_simulations,))

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
dvs[:,9] = cip_fund_floor_fraction_of_gross_revenues
dvs[:,10] = reserve_fund_floor_fraction_of_gross_revenues

dvs_filepath = local_base_path + local_data_sub_path  + "parameters/financial_model_DVs.csv"
np.savetxt(dvs_filepath, dvs, delimiter=",")

#%%
# DU factors
dufs  = np.zeros((num_simulations,20), dtype=float)

FLEXIBLE_CIP_SCHEDULE_TOGGLE = 0
FOLLOW_CIP_SCHEDULE_TOGGLE = 0

# if user does not want to use default DU factor values
# set decision variables
rate_stabilization_minimum_ratio = np.random.uniform(low=float(rate_stable_min_low.get()),
                                                     high=float(rate_stable_min_high.get()),
                                                     size=(num_simulations,))

rate_stabilization_maximum_ratio = np.random.uniform(low=float(rate_stable_max_low.get()),
                                                     high=float(rate_stable_max_high.get()),
                                                     size=(num_simulations,))

fraction_variable_operational_cost = np.random.uniform(low=float(var_cost_low.get()),
                                                     high=float(var_cost_high.get()),
                                                     size=(num_simulations,))

budgeted_unencumbered_fraction = np.random.uniform(low=float(unemcum_budget_low.get()),
                                                     high=float(unencum_budget_high.get()),
                                                     size=(num_simulations,))

annual_budget_fixed_operating_cost_inflation_rate = np.random.uniform(low=float(opex_fixed_low.get()),
                                                     high=float(opex_fixed_high.get()),
                                                     size=(num_simulations,))

annual_demand_growth_rate = np.random.uniform(low=float(demand_growth_low.get()),
                                                     high=float(demand_growth_high.get()),
                                                     size=(num_simulations,))

next_FY_budgeted_tampa_tbc_delivery = np.random.uniform(low=float(next_fy_low.get()),
                                                     high=float(next_fy_high.get()),
                                                     size=(num_simulations,))

fixed_op_ex_factor = np.random.uniform(low=float(fixed_opex_factor_low.get()),
                                                     high=float(fixed_opex_factor_high.get()),
                                                     size=(num_simulations,))

variable_op_ex_factor = np.random.uniform(low = float(var_opex_factor_low.get()),
                                                     high=float(var_opex_factor_high.get()),
                                                     size=(num_simulations,))

non_sales_rev_factor = np.random.uniform(low = float(non_sale_rev_low.get()),
                                                     high=float(non_sale_rev_high.get()),
                                                     size=(num_simulations,))

rate_stab_transfer_factor = np.random.uniform(low = float(rate_stab_factor_low.get()),
                                                     high=float(rate_stab_factor_high.get()),
                                                     size=(num_simulations,))

rr_transfer_factor = np.random.uniform(low = float(rr_transfer_low.get()),
                                                     high=float(rr_transfer_high.get()),
                                                     size=(num_simulations,))

other_transfer_factor = np.random.uniform(low = float(other_transfer_low.get()),
                                                     high=float(other_transfer_high.get()),
                                                     size=(num_simulations,))

required_cip_factor = np.random.uniform(low = float(cip_factor_low.get()),
                                                     high=float(cip_factor_high.get()),
                                                     size=(num_simulations,))

annual_budget_variable_operating_cost_inflation_rate = np.random.uniform(low=float(opex_var_low.get()),
                                                     high=float(opex_var_high.get()),
                                                     size=(num_simulations,))

TAMPA_SALES_THRESHOLD_FRACTION = np.random.uniform(low=float(sales_threshold_low.get()),
                                                     high=float(sales_threshold_high.get()),
                                                     size=(num_simulations,))

energy_transfer_factor = np.random.uniform(low=float(energy_transfer_low.get()),
                                                     high=float(energy_transfer_high.get()),
                                                     size=(num_simulations,))

utility_reserve_fund_deficit_reduction_fraction = np.random.uniform(low=float(urf_deficit_low.get()),
                                                     high=float(urf_deficit_high.get()),
                                                     size=(num_simulations,))

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

err.write('End error file.')
err.close()
