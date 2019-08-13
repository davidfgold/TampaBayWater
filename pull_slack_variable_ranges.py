import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import matplotlib.style as style
from glob import glob
import seaborn as sns
import os
import re
sns.set(style='whitegrid')
style.use('bmh')

# READS .LOG FILES TO IDENTIFY RANGES OF SYSTEM PARAMETERS
# THEN CHECKS AGAINST .CSV FILES TO LOCATE VIOLATIONS OF BOUNDS/SLACK 
# D Gorelick (Jul 2019)

os.chdir('C:\\Users\\dgorelic\\OneDrive - University of North Carolina at Chapel Hill\\UNC\\Research\\TBW\\Code\\Visualization')
from analysis_functions import read_AMPL_log_variable_constraints

# set parent directory
os.chdir('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data')


# create a list of all realization file names in this working directory
files = glob("csv_files/ampl_*.csv")

# get single realization pair of output files
for fn in range(len(files)):
    var_ranges = read_AMPL_log_variable_constraints('log_files/' + files[fn][10:19] + '.LOG')
    csv_out    = pd.read_csv('cleaned_AMPLcsvfiles/' + files[fn][10:19] + '.csv')
    
    # following two loop sets breaks down variable names to locate matches between 
    # slack info and tracked AMPL output file daily data 
    varnames = [str(x) for x in var_ranges.Variable]
    nameset = []; locset = []
    for n in varnames:
        nset = re.split('\[|\]|\,', n) # split out the variable or constraint name components
    
        nameset.append(nset[0])
        if len(nset) > 1:
            locset.append(nset[1])
        else:
            locset.append('')
    
    cnameset = []; clocset = []
    for c in csv_out.columns:
        cset = re.split('\__', c) # split the column names from the csv data to match
        
        cnameset.append(cset[0])
        if len(cset) > 1:
            clocset.append(cset[1])
        else:
            clocset.append('')
     
    # track number of matches made and        
    csv_match_index = []; log_match_index = []
    for i in range(len(csv_out.columns)):
        for j in range(len(varnames)):
            if cnameset[i] == nameset[j]:
                if locset[j] == '\'' + clocset[i] + '\'':
                    csv_match_index.append(i)
                    log_match_index.append(j)
                    
    # run daily values of csv files to see if they violate
    # constraints and generate output file with this info
    lower_slack_violations = np.empty((len(csv_out),len(csv_match_index)))
    upper_slack_violations = np.empty((len(csv_out),len(csv_match_index)))
    for i in range(len(csv_match_index)):
        data = csv_out.iloc[:,csv_match_index[i]]
        
        lb = float(var_ranges.iloc[log_match_index[i],1]) 
        ub = float(var_ranges.iloc[log_match_index[i],2])
    
        lower_slack_violations[:,i] = data < lb
        upper_slack_violations[:,i] = data > ub
        
        if sum(data < lb) > 0:
            print('lower bound violated in ' + files[fn][10:19] + ' by variable ' + csv_out.columns[csv_match_index[i]])
            
        if sum(data > ub) > 0:
            print('upper bound violated in ' + files[fn][10:19] + ' by variable ' + csv_out.columns[csv_match_index[i]])
        
    lower_outs = pd.DataFrame(lower_slack_violations); lower_outs.columns = csv_out.columns[csv_match_index]
    upper_outs = pd.DataFrame(upper_slack_violations); upper_outs.columns = csv_out.columns[csv_match_index]    
    
    pd.DataFrame.to_csv(lower_outs, 'generated_files/' + files[fn][10:19] + '_lower_constraint_violations_csv_variables.csv')        
    pd.DataFrame.to_csv(upper_outs, 'generated_files/' + files[fn][10:19] + '_upper_constraint_violations_csv_variables.csv') 
            
            
        