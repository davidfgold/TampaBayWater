# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 13:55:29 2023

@author: cpetagna
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
#data_path = 'C:/Users/cmpet/OneDrive/Documents/UNCTBW/Modeloutput'
data_path = 'F:/MonteCarlo_Project/Cornell_UNC/board_meeting_model_outputs' #vgrid pathway

formulation_to_plot = [147] #needs to be listed as a string?
simulation_to_plot = [0, 1] #list all, First ID starts at 0 (Maybe also needs to be listed as a string?)
realization_to_plot = [x for x in range(1, 200)] #list realizations being analyzed, IDs start at 1 not 0

#read in tables - bring in debt covenant table

for f in range(0, len(formulation_to_plot)):
    print('Plotting output for Formulation ' + str(formulation_to_plot[f]))
    for s in range(0, len(simulation_to_plot)):
        print('\tPlotting output for Simulation ' + str(simulation_to_plot[s]))
        
        #read in data tables - while working this out, maybe think about appending these as tables to dictionaries?
        dc_data = pd.read_csv(data_path + '/DC_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '.csv', index_col = 0)
        rc_data = pd.read_csv(data_path + '/RC_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '.csv', index_col = 0)
        ur_data = pd.read_csv(data_path + '/UR_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '.csv', index_col = 0)
        
        #figure out how many realizations have a debt covenant equal to or greater than 1.
        dc_successes = []
        for year in dc_data:
            annual_dc_success_rate = (dc_data[year] >= 1).sum()
            dc_successes.append(annual_dc_success_rate)
        
        #grab the number of realizations:
        realization_total = len(realization_to_plot)
        
        #find the percent of realizations that are >=1
        dc_success_percent = [x / realization_total for x in dc_successes]
        
        #Make a plot of the percent of realizations against the year
        
    
        fig, axs = plt.subplots(1, len(simulation_to_plot), sharey = False, figsize = (5*len(simulation_to_plot), 5))
        fiscal_years = list(dc_data.columns)
        for ax, scenario in zip(axs.flat, simulation_to_plot):
            ax.bar(fiscal_years, dc_success_percent, color = 'r')
            ax.set_xticklabels([int(x) for x in fiscal_years], rotation = 90) 
