# -*- coding: utf-8 -*-
"""
Time varying metrics for TBW system

@author: dgold
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt 
import matplotlib
import matplotlib.cm as cm 
from analysis_functions import read_AMPL_csv
from objective_calculation_functions import getGWPermitViolations, getSWPermitViolations, getMonitoringWellViolations, calculateLevelOfService, calculateEnvironmentalSustainability
import seaborn as sns
sns.set()

def plotLOSQuantiles(n_rel, figureName):
        
    # load each cleaned AMPL outfile and store in a list
    all_ampl = list()
    
    for rel in range(1,n_rel):
        if rel < 10:
            num_str = '000'+ str(rel)
        elif rel < 100:
            num_str = '00' + str(rel)
        else:
            num_str = '0' + str(rel)
        realization_data = pd.read_csv('Cleaned_zip/cleaned/ampl_' + num_str + 
                                       '.csv')#, usecols=AMPL_cols)
        realization_data.fillna(0, inplace=True)
        
        all_ampl.append(realization_data)
    
    # Calculate LOS metrics for each year (missing leap years, fix later?)
    annual_LOS_rel = np.zeros([n_rel, 20])
    annual_LOS_vul = np.zeros([n_rel, 20])
    
    # loop through each realization
    for rel in range(0, n_rel-1):
        current_rel = all_ampl[rel]
        
        for day in np.linspace(0, 6935, 20):
            day = int(day)
            year = int(day/365)
            current_year = current_rel.iloc[day:day+365]
            annual_LOS_rel[rel, year], annual_LOS_vul[rel, year] = calculateLevelOfService(current_year)
    
    
    # Calculate percentiles across realizations        
    LOS_rel = np.zeros([20,100])
    LOS_vul = np.zeros([20,100])        
    # Extract 90th percentile from each LOS
    for year in range(0,20):
        for p in range(0,100):
            LOS_rel[year,p] = np.percentile(annual_LOS_rel[:,year], (p+1))
            LOS_vul[year,p] = np.percentile(annual_LOS_vul[:,year], (p+1))
    
    
    # plot time varying distribution    
    cmap = matplotlib.cm.get_cmap("RdBu_r")
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(1,1,1)
    for i in np.linspace(5,95,19):
        i = int(i)
        ax.fill_between(range(2020,2040), LOS_rel[:,i-5], LOS_rel[:,i],
                        color=cm.RdBu_r((i-1)/100.0), alpha=0.75, edgecolor='none')
    ax.set_xticks(range(2020,2040))
    ax.set_xticklabels(range(2020,2040), rotation='vertical')
    ax.set_xlim([2020,2039])
    plt.xlabel('years')
    plt.ylabel('Annual failure rate')
    
    plt.savefig(figureName, bbox_inches= 'tight')
    
    return

