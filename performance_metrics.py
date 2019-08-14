import numpy as np
import pandas as pd
from glob import glob
import os
import time


def calc_LOS(csv_file):
	
	# calculate reliability based on slack picked up at Alafia, TBC
	# as well as BUD, CWUP, SCH wells 
    #  FOR WHICH VIOLATIONS OF PERMITS ARE TRACKED CUMULATIVELY AS
    # THE OVERAGE TERM IN THE OUT FILE
    # if the variable wup_mavg_pos__CWUP exists, then according to TBW demands can be met with satisfaction

    CWUP_Violations = 0
    if max(csv_file.columns.str.find('wup_mavg_pos__CWUP')) != -1: # if variable is tracked...
        CWUP_Violations = sum(csv_file['wup_mavg_pos__CWUP'].dropna() > 0)
    
    # track all violations? this should be the 1/0 version of gw_overage
    Total_GW_Violations = 0
    for gw in ['wup_mavg_pos__BUD','wup_mavg_pos__CWUP','wup_mavg_pos__SCH']:
        if max(csv_file.columns.str.find(gw)) != -1: # if variable is tracked...
            Total_GW_Violations += sum(csv_file[gw].dropna() > 0)
    
    # what about surface water slack?
    Total_SW_Violations = 0
    for sw in ['ngw_slack__Alafia','ngw_slack__TBC','ngw_slack__COT_supply']:
        if max(csv_file.columns.str.find(sw)) != -1: # if variable is tracked...
            Total_SW_Violations += sum(csv_file[sw].dropna() > 0) # daily violations

    #Overage = log_file.overage
    #SCHmavg_weekly = csv_file['12mo_mavg__SCH'].dropna()
    #BUDmavg_weekly = csv_file['12mo_mavg__BUD'].dropna()
    #CWUPmavg_weekly = csv_file['12mo_mavg__CWUP'].dropna()
    
    # convert metrics into fraction of time violations occur
    LOS_CWUP = CWUP_Violations / 7304 # divide by number of simulated days
    LOS_GW = Total_GW_Violations / 7304 # divide by number of simulated days
    LOS_SW = Total_SW_Violations / 7304 # divide by number of simulated days
    
    # what about days with any violation? 
    Total_GW_Violations = np.zeros((7304)); Total_SW_Violations = np.zeros((7304))
    for gw in ['wup_mavg_pos__BUD','wup_mavg_pos__CWUP','wup_mavg_pos__SCH']:
        if max(csv_file.columns.str.find(gw)) != -1: # if variable is tracked...
            which_NaN = np.isnan(csv_file[gw]); csv_file[gw][which_NaN] = 0
            Total_GW_Violations = [Total_GW_Violations[a] + (csv_file[gw][a] > 0) for a in range(len(csv_file[gw]))]
            Total_GW_Violations = np.zeros((7304)); Total_SW_Violations = np.zeros((7304))
    for sw in ['ngw_slack__Alafia','ngw_slack__TBC','ngw_slack__COT_supply']:
        if max(csv_file.columns.str.find(sw)) != -1: # if variable is tracked...
            which_NaN = np.isnan(csv_file[sw]); csv_file[sw][which_NaN] = 0
            Total_SW_Violations = [Total_SW_Violations[a] + (csv_file[sw][a] > 0) for a in range(len(csv_file[sw]))]
    
    Total_Violations = [Total_SW_Violations[a] + Total_GW_Violations[a] for a in range(len(Total_SW_Violations))]
    LOS_All = 0
    for a in range(len(Total_Violations)): 
        if Total_Violations[a] > 0: LOS_All += 1
    LOS_All = LOS_All / 7304

    return LOS_All


def calc_environmental_burden(csv_file, log_file):
	
	# calculate environmental impact based on groundwater overuse

    Offset = log_file.tg_offset # future: break this down by well 
    SCH_WF_Production = np.mean(csv_file['wf_prod__SCH']) # offset data not clearly available for SCH wells?
    SCH_1_Demand = np.mean(csv_file['demand__SCH_1']) # keep a variety of SCH data in place of offset values
    SCH_2_Demand = np.mean(csv_file['demand__SCH_2'])
    
    SCH_WF_Production_95th = np.quantile(csv_file['wf_prod__SCH'], 0.95) # offset data not clearly available for SCH wells?
    SCH_1_Demand_95th = np.quantile(csv_file['demand__SCH_1'], 0.95) # keep a variety of SCH data in place of offset values
    SCH_2_Demand_95th = np.quantile(csv_file['demand__SCH_2'], 0.95)
    
    # assume the greatest burden is related to the worst 30-day period (month)
    # so taking the maximum of the moving monthly average for the timeseries
    Environmental_Burden = max(np.convolve(Offset, np.ones((30,))/30, mode='valid'))

    return Environmental_Burden


def calc_cost(run):
	
	# assign the cost of infrastructure for each realization based on 
    # screening from reports on life cycle cost
    # and capital costs ONLY pulled from reports (in millions)

    SWTP_Expansion_Cost = 2 + 12.5 + 6.5 + 10 + 3 + 3.75 + 7.5 # LTMWP p.458
    Desal_Expansion_Cost = 5.9 + 68.25 + 6.06 + 30.6 + 6.18 + 5.7 + 2.5
    SHARP_Cost = 2.6 + 1.125 + 2.1 + 2.2 + 0.8 + 0.78 + 9.375 + 1.5 + \
                 2.5 + 1.32 + 8.286 + 0.314 + 0.133 + 0.26 + 1.5 + 2.2625 + \
                 2.1 + 2.2 # p.466
    Reclaimed_AWTP_Cost = 4.063 + 6.25 + 7.813 + 10.469 + 1.813 + 4.688 + \
                          3.907 + 3.125 + 1.875 + 2.344 + 4.688 + 0.28 + \
                          0.22 + 0.4 + 2.25 + 3.2 
    
    if run == '0079': # baseline status quo infrastructure and operations (SWTP 90 MGD)
        lcc = 0
    elif run == '0080': # expand desal to 30 MGD, run full out always, otherwise follow baseline
        lcc = Desal_Expansion_Cost
    elif run == '0082': # increased SWTP capacity to 110 MGD, operate desal at 20 MGD (config 1)
        lcc = SWTP_Expansion_Cost
    elif run == '0087': # SHARP GW at 7.5 MGD, additional reclaimed water capacity at SWTP of 12.5 MGD (config 6A)
        lcc = SHARP_Cost + Reclaimed_AWTP_Cost
    elif run == '0102': # added second SWTP at surface water reservoir (12.5 MGD)
        lcc = Reclaimed_AWTP_Cost # NOT SURE THIS IS THE RIGHT PROJECT
    elif run == '0103': # new 12.5 MGD SWTP at reservoir + 7.5 MGD SHARP
        lcc = SHARP_Cost + Reclaimed_AWTP_Cost
    
    Additional_Capital_Costs = lcc

    return Additional_Capital_Costs