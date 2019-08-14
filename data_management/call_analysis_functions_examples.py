# SCRIPT TO DEMO FUNCTIONS IN ANALYSIS_FUNCTIONS.PY FOR READING AMPL DATA
# AND GENERATION OF CORRELATION MATRICES AND PLOTS USING IT
# D GORELICK (APR 2019)

import os

# read in files from analysis_functions.py
os.chdir('C:\\Users\\David\\OneDrive - University of North Carolina at Chapel Hill\\UNC\\Research\\TBW\\Code\\Visualization')
from analysis_functions import read_AMPL_out, read_AMPL_log, read_AMPL_csv

# revert to working directory that contains data
os.chdir('C:\\Users\\David\\Desktop\\TBWData\\AMPL_output')
f = 'ampl_0101'
data_log = read_AMPL_log(f + '.log')
data_csv = read_AMPL_csv(f + '.csv')
data_out = read_AMPL_out(f + '.out')

# plot to see if data is in correct form
import matplotlib.pyplot as plt
plt.plot(data_log['wf_term'])
plt.plot(data_csv['demand__COT'])
plt.plot(data_out['GW'])

# check correlations across all variables?
import pandas as pd
alldata = pd.concat([data_log, data_out, data_csv], axis = 1)

corr = alldata.corr()
#plt.matshow(correlationmatrix)

import numpy as np
mask = np.zeros_like(corr.iloc[1:9,1:9])
mask[np.triu_indices_from(mask)] = True

import seaborn as sns
sns.heatmap(corr.iloc[1:9,1:9], mask = mask,
            cmap='RdBu', vmin = -1, vmax = 1) # objective comps

sns.heatmap(corr[data_log.columns.values], 
            cmap='RdBu', vmin = -1, vmax = 1) # objective comps

sns.set(font_scale = 0.7)
sns.heatmap(corr.iloc[9:39,1:9], 
            cmap='RdBu', vmin = -1, vmax = 1) # objective comps

for p in range(0,22):
    plt.subplots(figsize = (8,15))
    prangelow = 20*p + 39; prangehigh = 20*p + 60
    ax = sns.heatmap(corr.iloc[prangelow:prangehigh,1:9], 
                cmap='RdBu', vmin = -1, vmax = 1) # objective comps 
    plt.savefig('objective_correlations_' + str(p) + '.png')
