# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 04:41:09 2023

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
simulation_to_plot = [4, 5] #list all, First ID starts at 0 (Maybe also needs to be listed as a string?)
realization_to_plot = [x for x in range(1, 200)] #list realizations being analyzed, IDs start at 1 not 0

#read in tables - bring in debt covenant table

for f in range(0, len(formulation_to_plot)):
    print('Plotting output for Formulation ' + str(formulation_to_plot[f]))
    for s in range(0, len(simulation_to_plot)):
        print('\tPlotting output for Simulation ' + str(simulation_to_plot[s]))
        
        #read in data tables - while working this out, maybe think about appending these as tables to dictionaries?
        #dc_data = pd.read_csv(data_path + '/DC_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '.csv', index_col = 0)
        #rc_data = pd.read_csv(data_path + '/RC_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '.csv', index_col = 0)
        ur_data = pd.read_csv(data_path + '/UR_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '.csv', index_col = 0)
        
        #delete the first two years of UR so that it starts at the modeled year
        ur_data = ur_data.iloc[:,2:]
        
        #divide each previous row to determine rate change from year to year
        ur_percent_change = pd.DataFrame(columns = ur_data.columns)
        ur_percent_change = ur_percent_change.iloc[:,1:]
       
        #loop over each row (realization)
        for realization in ur_data.index:
            #Now loop over columns
            for y, year in enumerate(ur_data.columns[:-1]):
                ur_percent_change.iloc[:,y] = (((ur_data.iloc[:,y+1]) - ur_data.iloc[:,y])/ ur_data.iloc[:,y]) * 100
        
        #Make a plot of the percent of realizations against the year
        
    
        fig, axs = plt.subplots(1, len(simulation_to_plot), sharey = False, figsize = (5*len(simulation_to_plot), 5))
        fiscal_years = list(ur_data.columns)
        for ax, scenario in zip(axs.flat, simulation_to_plot):
            ax.fill_between(ur_percent_change.columns,
                        np.max(ur_percent_change, axis = 0),
                        np.min(ur_percent_change, axis = 0),
                        color = 'b',
                        alpha = 0.4, linewidth = 2,
                        edgecolor = 'b')
        ax.set_xticklabels([int(x) for x in fiscal_years], rotation = 90) 