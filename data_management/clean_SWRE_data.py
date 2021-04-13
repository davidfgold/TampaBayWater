# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 10:40:24 2021

@author: dgorelick
"""

# Script to read and clean SWRE output and dump to folder
import numpy as np
import pandas as pd
import re
import os
import glob

os.chdir("F:/SWRE/Output//")
for run in ['0141', '0142', '0143', '0144']:
    for filename in glob.glob("rrv_" + run + "//*.csv"):
        csv_out = pd.read_csv(filename, sep = ',') # about a year is 50,000 rows
        realization = filename[-8:-4]
        print(filename)
        
        # collect the file data and organize such that each column is a unique variable timeseries
        uniquevars = csv_out[['VariableName','VariableIndex']].drop_duplicates()
        numrows = len(np.unique(csv_out['DayNumber']))
        csvdata = np.empty((numrows,len(uniquevars))); csvdata[:] = np.nan
        for v,j in zip(uniquevars.values,range(0,len(uniquevars.values))):
            vday  = csv_out['DayNumber'][(csv_out['VariableIndex'] == v[1]) & (csv_out['VariableName'] == v[0])]
            vdata = csv_out['Value'][(csv_out['VariableIndex'] == v[1]) & (csv_out['VariableName'] == v[0])]
            csvdata[vday.values-1,j] = vdata.values
        
        # format data
        uniquecols = uniquevars.values[:,0] + '__' + uniquevars.values[:,1]
        ampl_out = pd.DataFrame(csvdata)
        ampl_out.columns = uniquecols
        
        # export new file
        pd.DataFrame.to_csv(ampl_out,'F:/MonteCarlo_Project/Cornell_UNC/cleaned_AMPL_files/run' + run + '/ampl_' + realization + ".csv")
