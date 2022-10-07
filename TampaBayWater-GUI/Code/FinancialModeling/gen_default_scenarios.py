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

GUI = load_workbook('../../Financial_Model_GUI.xlsm')
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
dvs[:,0].fill(1.25)
dvs[:,1].fill(1)
dvs[:,2].fill(np.random.choice([0,1]))
dvs[:,3].fill(np.random.choice([0,0.01]))
dvs[:,4].fill(np.random.choice([0,0.005]))
dvs[:,5].fill(0.27)
dvs[:,6].fill(np.random.choice([0.4,9999]))
dvs[:,7].fill(0.05)
dvs[:,8].fill(0.05)
dvs[:,9].fill(0.01)
dvs[:,10].fill(0.1)

dvs_filepath = local_base_path + local_data_sub_path  + "parameters/financial_model_DVs.csv"
np.savetxt(dvs_filepath, dvs, delimiter=",")

#%%
# DU factors
dufs  = np.zeros((num_simulations,20), dtype=float)

dufs[:,0].fill(0.085)
dufs[:,1].fill(0.3)
dufs[:,2].fill(0.15)
dufs[:,3].fill(0.025)
dufs[:,4].fill(0.033)
dufs[:,5].fill(0.015)
dufs[:,6].fill(2000)
dufs[:,7].fill(0.7)
dufs[:,8].fill(0.9)
dufs[:,9].fill(1.5)
dufs[:,10].fill(1.5)
dufs[:,11].fill(0.3)
dufs[:,12].fill(1)
dufs[:,13].fill(1)
dufs[:,14].fill(0.033)
dufs[:,15].fill(0.02)
dufs[:,16].fill(1)
dufs[:,17].fill(0.75)
dufs[:,18].fill(np.random.choice([0,1]))
dufs[:,19].fill(np.random.choice([0,1]))

dufs_filepath = local_base_path + local_data_sub_path + "parameters/financial_model_DUfactors.csv"
np.savetxt(dufs_filepath, dufs, delimiter=",")
