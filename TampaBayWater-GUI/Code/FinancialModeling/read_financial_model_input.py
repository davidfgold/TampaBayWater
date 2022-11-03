# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 23:08:42 2022

@author: lilli
"""
import pandas as pd

def read_input_files(file_type, local_base_path, local_data_sub_path, current_year, FY="",
                     local_data_finmod_input="", local_data_dvdu_input=""):
    filepath = ""
    
    if file_type == "Previous year water sales and deliveries":
        filepath = local_base_path + local_data_sub_path + local_data_finmod_input +\
            "/water_sales_and_deliveries_all_" + str(current_year) + ".csv"
        return pd.read_csv(filepath)
    
    if file_type == "Historical estimated budgets":
        filepath = local_base_path + local_data_sub_path + local_data_finmod_input +\
            "/historical_actuals.csv"
        return pd.read_csv(filepath)
    
    if file_type == "Existing debt":
        filepath = local_base_path + local_data_sub_path + local_data_finmod_input +\
            "/existing_debt.csv"
        return pd.read_csv(filepath)
    
    if file_type == "Potential projects":
        filepath = local_base_path + local_data_sub_path + local_data_finmod_input +\
            "/potential_projects.csv"
        return pd.read_csv(filepath)
    
    if file_type == "Current and future bond issues":
        filepath = local_base_path + local_data_sub_path + local_data_finmod_input +\
            "/potential_projects.csv"
        return pd.read_excel(filepath, sheet_name = 'FutureDSTotals')
    
    if file_type == "Original CIP spending (all projects)":
        filepath = local_base_path + local_data_sub_path + local_data_finmod_input +\
            "/original_CIP_spending_all_projects.csv"
        return pd.read_csv(filepath)
    
    if file_type == "Original CIP spending (major projects)":
        filepath = local_base_path + local_data_sub_path + local_data_finmod_input +\
            "/original_CIP_spending_major_projects_fraction.csv"
        return pd.read_csv(filepath)
    
    if file_type == "Normalized CIP spending (major projects)":
        filepath = local_base_path + local_data_sub_path + local_data_finmod_input +\
            "/normalized_CIP_spending_major_projects_fraction.csv"
        return pd.read_csv(filepath)
    
    if file_type == "Projected reserve fund starting balance":
        filepath = local_base_path + local_data_sub_path + local_data_finmod_input +\
            "/projected_" + FY + "reserve_fund_starting_balances.csv"
        return pd.read_csv(filepath)
    
    if file_type == "Projected reserve fund deposits":
        filepath = local_base_path + local_data_sub_path + local_data_finmod_input +\
            "/projected_reserve_fund_deposits.csv"
        return pd.read_csv(filepath)
    
    if file_type == "Decision variables":
        filepath = local_base_path + local_data_sub_path + local_data_dvdu_input +\
            "/financial_model_DVs.csv"
        return pd.read_csv(filepath, header = None)
    
    if file_type == "DU factors":
        filepath = local_base_path + local_data_sub_path + local_data_dvdu_input +\
            "/financial_model_DUfactors.csv"
        return pd.read_csv(filepath, header = None)
    
    
    