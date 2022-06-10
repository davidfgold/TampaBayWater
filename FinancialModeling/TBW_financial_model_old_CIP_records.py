# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 10:57:48 2022

@author: cmpet
"""
import pandas as pd
import numpy as np
hist_financial_path = 'C:/Users/cmpet/OneDrive/Documents/UNCTBW'

CIP2020_2029 = pd.read_csv(hist_financial_path + '/FY2020-2029_CashFlowAnalysis_Version7.csv')
CIP2020_2029.drop(CIP2020_2029.columns[[0, 4, 5]], axis = 1, inplace = True)
CIP2020_2029_melt = CIP2020_2029.melt(id_vars = ['Project No.', 'Project Name', 'Current Funding Source', 'Total Funds Needed'], value_vars = ['Remaining FY 2019', 'FY 2020', 'FY 2021', 'FY 2022', 'FY 2023', 'FY 2024', 'FY 2025', 'FY 2026', 'FY 2027', 'FY 2028', 'FY 2029', 'Future'], var_name = 'Year Spent', value_name = 'Dollars')
CIP2020_2029_melt['Value'] = CIP2020_2029_melt['Dollars'].str.replace(',', '').str.replace('$', '').astype(float)
CIP2020_2029_melt['Total Dollars']=CIP2020_2029_melt['Total Funds Needed'].str.replace(',', '').str.replace('$', '').astype(float)
#CIP2020_2029_melt.drop(['Total Funds Needed'], axis = 1, inplace = True)

##Break down of small, medium, and large projects - using current FY cut-offs
#Total_Capital_Needed = [(CIP2020_2029_melt['Total Dollars'] > 75000000), \
#                        (CIP2020_2029_melt['Total Dollars'] <= 75000000) & (CIP2020_2029_melt['Total Dollars'] > 10000000), \
#                        (CIP2020_2029_melt['Total Dollars'] <= 10000000)]
#values = ['Large Projects (>$75m)', 'Medium Projects (>$10m, <$75m)', 'Small Projects (<$10m)']
#CIP2020_2029_melt['Total Capital Needed'] = np.select(Total_Capital_Needed, values)

##Break down of small, medium, and large projects - using different cutoff values
Total_Capital_Needed = [(CIP2020_2029_melt['Total Dollars'] > 10000000), \
                        (CIP2020_2029_melt['Total Dollars'] <= 10000000) & (CIP2020_2029_melt['Total Dollars'] > 1000000), \
                        (CIP2020_2029_melt['Total Dollars'] <= 1000000)]
values = ['Large Projects (>$10m)', 'Medium Projects (>$1m, <$10m)', 'Small Projects (<$1m)']
CIP2020_2029_melt['Total Capital Needed'] = np.select(Total_Capital_Needed, values)

##Now want to normalize the data
##Want to isolate each project, select just years where it is funded, re-index 0-x rather than 2019-2029
#CIP2020_2029_normalized = pd.Dataframe()
projects = CIP2020_2029_melt['Project Name'].unique()
project_data = {project : pd.DataFrame() for project in projects}
for key in project_data.keys():
    project_data[key] = CIP2020_2029_melt[:][CIP2020_2029_melt['Project Name'] == key]
for project in project_data:
    for year in project['Year Spent']:
        if project['Project Value'] != 0:
            first_year_funded = min(project['Year Spent'])

    
    #print(project_data)
    #first_year_funded = min()

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

check_CIP_basic_histFY20 = plt.figure(figsize = (15, 7))
plt.bar(CIP2020_2029_melt['Year Spent'], CIP2020_2029_melt['Value'])
plt.title('Check CIP basic histFY20')
plt.xlabel('Fiscal Year')
plt.ylabel('Million USD')
plt.show()






    
