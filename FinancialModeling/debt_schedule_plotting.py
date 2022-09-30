# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 12:08:28 2022

@author: cmpet
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
data_path = 'C:/Users/cmpet/OneDrive/Documents/UNCTBW'

for run_id in [125]:
    n_sims = 3; bond_colors = ['b', 'r', 'c', 'y', 'm']; sim_type = ['Origianl Planning', 'Higher Interest Rates', 'High Interest Rates and Inflation']
    #add additional total debt colors for additional simulation runs
    total_debt_colors = ['b', 'g', 'm']
    
    total_debt_comparison = pd.DataFrame(columns = sim_type)
    for sim in range(0, n_sims):
        
        #bring the debt service tables in - if only looking at how the initial bonds are set up you only need to bring in the first realization (the same for each realization)
        debt_service_data_names = pd.read_csv(data_path + '/Modeloutput/debt_service_schedule_f' + str(run_id) + '_s' + str(sim) + '_r1.csv', header = None, nrows = 2)
        debt_service_data = pd.read_csv(data_path + '/Modeloutput/debt_service_schedule_f' + str(run_id) + '_s' + str(sim) + '_r1.csv', header = None, index_col = 0, skiprows = 2)
        existing_debt = pd.read_excel(data_path + '/Financialoutputs/Current_Future_BondIssues.xlsx', sheet_name = 'FutureDSTotals', usecols = ['Total'])
        
        existing_debt = existing_debt.squeeze()
        Fiscal_Year = debt_service_data.iloc[:,0]
        Bond_2023_totals = debt_service_data.iloc[:, 4].fillna(0)
        Bond_2_totals = debt_service_data.iloc[:, 12].fillna(0)
        Bond_3_totals = debt_service_data.iloc[:, 20].fillna(0)
        Bond_4_totals = debt_service_data.iloc[:, 28].fillna(0)
        
        #Stack the Bond payments ontop of one another
        debtBYbondFIG = plt.figure(figsize = (15,8))
        plt.bar(Fiscal_Year, existing_debt, color = bond_colors[0], label = 'Existing Debt')
        plt.bar(Fiscal_Year, Bond_2023_totals, bottom = existing_debt, color = bond_colors[1], label = '2023 Bond Issue')
        plt.bar(Fiscal_Year, Bond_2_totals, bottom= existing_debt + Bond_2023_totals, color = bond_colors[2], label = '2025 Bond Issue')
        plt.bar(Fiscal_Year, Bond_3_totals, bottom = existing_debt + Bond_2023_totals + Bond_2_totals, color = bond_colors[3], label = '2027 Bond Issue')
        plt.bar(Fiscal_Year, Bond_4_totals, bottom =existing_debt + Bond_2023_totals + Bond_2_totals + Bond_3_totals, color = bond_colors[4], label = '2029 Bond Issue')
        
        #ax = debtBYbondFIG.add_axes()
        plt.xticks(np.arange(min(Fiscal_Year), max(Fiscal_Year) + 1, 1), rotation = 90, fontsize = 14)
        plt.ylabel('Debt Service ($100 Million)', fontsize = 14)
        plt.xlabel('Fiscal Year', fontsize = 14)
        plt.legend()
        plt.savefig(data_path + '/figures/bond_debt_service_f' + str(run_id) + '_s' + str(sim) + '.png', bbox_inches= 'tight', dpi = 800)
        #plt.show()
        
        total_debt_service = existing_debt + Bond_2023_totals + Bond_2_totals + Bond_3_totals + Bond_4_totals
        TotalDebtFig = plt.figure(figsize = (15,8))
        plt.bar(Fiscal_Year, total_debt_service, color = total_debt_colors[sim], label = sim_type[sim])
        plt.legend()
        plt.savefig(data_path + '/figures/total_debt_service_by_sim_f' + str(run_id) + '_s' + str(sim) + '.png', bbox_inches = 'tight', dpi =800)
        
        total_debt_comparison[sim_type[sim]] = total_debt_service
    
    
    AllTotalDebtFig = plt.figure(figsize = (15,8))
    plt.bar(Fiscal_Year, total_debt_comparison.iloc[:,2], color = total_debt_colors[2], label = sim_type[2])
    plt.bar(Fiscal_Year, total_debt_comparison.iloc[:,1], color = total_debt_colors[1], label = sim_type[1])
    plt.bar(Fiscal_Year, total_debt_comparison.iloc[:,0], color = total_debt_colors[0], label = sim_type[0])
    plt.xticks(np.arange(min(Fiscal_Year), max(Fiscal_Year) + 1, 1), rotation = 90, fontsize = 14)
    plt.ylabel('Debt Service ($100 Million)', fontsize = 14)
    plt.xlabel('Fiscal Year', fontsize = 14)
    plt.legend()
    plt.savefig(data_path + '/figures/total_bond_debt_service_f' + str(run_id) + '.png', bbox_inches= 'tight', dpi = 800)