import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import matplotlib.style as style
from glob import glob
import seaborn as sns
import os
import time
sns.set(style='whitegrid')
style.use('bmh')

# COMPARES REALIZATION-LEVEL RELIABILITY, ENVIRONMENTAL IMPACT, DROUGHT MITIGATION COSTS, INFRASTRUCTURE COSTS
# FIRST THREE "OBJECTIVES" CALCULATED FROM OUTPUTS, INFRA COSTS FROM REPORTS
# D Gorelick (Aug 2019)

os.chdir('C:\\Users\\dgorelic\\OneDrive - University of North Carolina at Chapel Hill\\UNC\\Research\\TBW\\Code\\Visualization')
from analysis_functions import read_AMPL_log, read_AMPL_out

# set parent directory
os.chdir('C:/Users/dgorelic/Desktop/TBWruns')
#os.chdir('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data')

# read in screening data
screening_data = pd.read_csv('fine_grain_screening.csv')

# 0079 is base run, plan Z2
# 0080 is a slight change on base run, plan A2
# 0082 is concept 1
# 0087 is concept 6A
# 0102 is plan X4
# 0103 is plan X5

# calculate objective statistics for each realization for each run
# each simulation takes about 23 min
simulations = ['0079','0080','0082','0087','0102','0103']
#simulations = ['0079','0080','0082','0087']

Variable_Names = ['Simulation', 'SimOrder', 'Realization', 
                  'Level of Service (CWUP only)', 'Level of Service (all GW)', 
                  'Level of Service (SW only)', 'Level of Service (all)',
                  'Environmental Burden (target offset)', 
                  'Average SCH Production (MGD)', 'Average SCH Node 1 Demand (MGD)', 'Average SCH Node 2 Demand (MGD)',
                  '95th Percentile SCH Production', '95th Percentile SCH Node 1 Demand', '95th Percentile SCH Node 2 Demand',
                  'Unmanageable Events (15+ day events)', 'Unmanageable Event Median Duration (days)', 
                  'Unmanageable Event 95th Percentile Severity (MG deficit per day)',
                  'Capital Costs ($MM)']
collected_data = np.zeros([len(simulations)*334,len(Variable_Names)]); i = 0; j = 0
for run in simulations:
    t = time.time()
    print("Running simulation ", run)
    # create a list of all realization file names in this working directory
    csv_files = glob('cleaned_' + run + "/*.csv")
    log_files = glob('cleaned_' + run + "/ampl_*.log")
    out_files = glob('cleaned_' + run + "/ampl_*.out")
    for r in range(len(csv_files)):
    #for r in range(20):
        print("Realization ", r)
        ### read in realization data
        log_out = read_AMPL_log(log_files[r])
        csv_out = pd.read_csv(csv_files[r])
        out_out = read_AMPL_out(out_files[r])
        
        ### calculate reliability based on slack picked up at Alafia, TBC
        # as well as BUD, CWUP, SCH wells 
        #  FOR WHICH VIOLATIONS OF PERMITS ARE TRACKED CUMULATIVELY AS
        #  THE OVERAGE TERM IN THE OUT FILE
        # if the variable wup_mavg_pos__CWUP exists, then according to TBW demands can be met with satisfaction
        CWUP_Violations = 0
        if max(csv_out.columns.str.find('wup_mavg_pos__CWUP')) != -1: # if variable is tracked...
            CWUP_Violations = sum(csv_out['wup_mavg_pos__CWUP'].dropna() > 0)
        
        # track all violations? this should be the 1/0 version of gw_overage
        Total_GW_Violations = 0
        for gw in ['wup_mavg_pos__BUD','wup_mavg_pos__CWUP','wup_mavg_pos__SCH']:
            if max(csv_out.columns.str.find(gw)) != -1: # if variable is tracked...
                Total_GW_Violations += sum(csv_out[gw].dropna() > 0)
        
        # what about surface water slack?
        Total_SW_Violations = 0
        for sw in ['ngw_slack__Alafia','ngw_slack__TBC','ngw_slack__COT_supply']:
            if max(csv_out.columns.str.find(sw)) != -1: # if variable is tracked...
                Total_SW_Violations += sum(csv_out[sw].dropna() > 0) # daily violations

        #Overage = log_out.overage
        #SCHmavg_weekly = csv_out['12mo_mavg__SCH'].dropna()
        #BUDmavg_weekly = csv_out['12mo_mavg__BUD'].dropna()
        #CWUPmavg_weekly = csv_out['12mo_mavg__CWUP'].dropna()
        
        # convert metrics into fraction of time violations occur
        LOS_CWUP = CWUP_Violations / 7304 # divide by number of simulated days
        LOS_GW = Total_GW_Violations / 7304 # divide by number of simulated days
        LOS_SW = Total_SW_Violations / 7304 # divide by number of simulated days
        
        # what about days with any violation? 
        Total_GW_Violations = np.zeros((7304)); Total_SW_Violations = np.zeros((7304))
        for gw in ['wup_mavg_pos__BUD','wup_mavg_pos__CWUP','wup_mavg_pos__SCH']:
            if max(csv_out.columns.str.find(gw)) != -1: # if variable is tracked...
                which_NaN = np.isnan(csv_out[gw]); csv_out[gw][which_NaN] = 0
                Total_GW_Violations = [Total_GW_Violations[a] + (csv_out[gw][a] > 0) for a in range(len(csv_out[gw]))]
                Total_GW_Violations = np.zeros((7304)); Total_SW_Violations = np.zeros((7304))
        for sw in ['ngw_slack__Alafia','ngw_slack__TBC','ngw_slack__COT_supply']:
            if max(csv_out.columns.str.find(sw)) != -1: # if variable is tracked...
                which_NaN = np.isnan(csv_out[sw]); csv_out[sw][which_NaN] = 0
                Total_SW_Violations = [Total_SW_Violations[a] + (csv_out[sw][a] > 0) for a in range(len(csv_out[sw]))]
        
        Total_Violations = [Total_SW_Violations[a] + Total_GW_Violations[a] for a in range(len(Total_SW_Violations))]
        LOS_All = 0
        for a in range(len(Total_Violations)): 
            if Total_Violations[a] > 0: LOS_All += 1
        LOS_All = LOS_All / 7304
        
        ### calculate environmental impact based on groundwater overuse
        Offset = log_out.tg_offset # future: break this down by well 
        SCH_WF_Production = np.mean(csv_out['wf_prod__SCH']) # offset data not clearly available for SCH wells?
        SCH_1_Demand = np.mean(csv_out['demand__SCH_1']) # keep a variety of SCH data in place of offset values
        SCH_2_Demand = np.mean(csv_out['demand__SCH_2'])
        
        SCH_WF_Production_95th = np.quantile(csv_out['wf_prod__SCH'], 0.95) # offset data not clearly available for SCH wells?
        SCH_1_Demand_95th = np.quantile(csv_out['demand__SCH_1'], 0.95) # keep a variety of SCH data in place of offset values
        SCH_2_Demand_95th = np.quantile(csv_out['demand__SCH_2'], 0.95)
        
        # assume the greatest burden is related to the worst 30-day period (month)
        # so taking the maximum of the moving monthly average for the timeseries
        Environmental_Burden = max(np.convolve(Offset, np.ones((30,))/30, mode='valid'))
        
        ### calculate cost of drought mitigation based on unmet demands 
        # compared to actual demands (this is biased because the optimization)
        # already slacks to avoid any prolonged failure to meet demand
        #   calculate demand deficit (daily demands don't match supply)
        #   supply can come from groundwater, desalination, ...
        #   ... alafia river pump station, tampa bypass canal pump station, or c.w. bill young reservoir
        # dont forget to include new sources...
        New_Supply = np.zeros((7304))
        for source in ['ngw_supply__ResWTP','ngw_supply__SHARP','ngw_supply__none']:
            if max(csv_out.columns.str.find(source)) != -1: # if variable is tracked...
                New_Source = csv_out[source]
                where_NaNs = np.isnan(New_Source) # correct for missing vals
                New_Source[where_NaNs] = 0

                New_Supply = [New_Supply[a] + New_Source[a] for a in range(len(New_Source))]

        # total of all supply (gw + desal treated water + flow from alafia + flow from tbc + flow to/from reservoir + new supply)
        # versus total non-CoT demand total
        # negative value to Deficit means daily demand was not completely met
        
        # HEADS UP: THIS IS WRONG - THEY USE THE SLACK VIOLATIONS TO DETERMINE WHAT EVENTS ARE UNMANAGEABLE...
        Deficit = out_out['GW'] + csv_out['wtp_eff__DS'] + csv_out['pflow__ARPS'] + \
                  csv_out['pflow__TBPS'] + csv_out['pflow__CWBY'] + New_Supply - \
                  (csv_out['total_demand__none'] - csv_out['pflow__J_COT'])
        
        # determine periods of unmet demand
        failureconditions = 0; counter = 0; length_of_fail = []; magnitude_of_fail = []; magnitude_count = 0
        C = 0 # assume 5 mgd deficit is "manageable", see appendix p.157 on use of C
        # based on Deficit results, 5 MG deficit is routine, but use 0 here to track all deficits
        for k in range(len(Deficit)):
            # keep track of consecutive days of unmet demand
            if (Deficit[k] + C) < 0: 
                magnitude_count -= Deficit[k] # "add" all days of event deficit
                counter += 1
            else:
                if counter > 14: # how bad was the event?
                    length_of_fail.append(counter)
                    magnitude_of_fail.append(magnitude_count)
                counter = 0
                magnitude_count = 0 # reset
            
            # if failure occurs long enough to be an issue for reliability
            # treat each event the same: a 15-day unmanageable event
            # counted the same as a 100-day one... 
            if counter == 15: failureconditions += 1
        
        # use the number of 2+ week-long periods where demands cannot be met
        # as a proxy for the need for short-term mitigation
        Unmanageable_Event_Count = failureconditions
        
        Unmanageable_Severity_Per_Day_95th = 0
        Unmanageable_Event_Median_Duration = 0
        if len(length_of_fail) > 0:
            Unmanageable_Event_Median_Duration = np.median(length_of_fail)
            Unmanageable_Severity_Per_Day_95th = np.quantile([magnitude_of_fail[a]/length_of_fail[a] for a in range(len(magnitude_of_fail))], 0.95)
        
        ### assign the cost of infrastructure for each realization based on 
        # screening from reports on life cycle cost
        # and capital costs ONLY pulled from reports (in millions)
        SWTP_Expansion_Cost = 2 + 12.5 + 6.5 + 10 + 3 + 3.75 + 7.5 # LTMWP p.458
        Desal_Expansion_Cost = 5.9 + 68.25 + 6.06 + 30.6 + 6.18 + 5.7 + 2.5
        SHARP_Cost = 2.6 + 1.125 + 2.1 + 2.2 + 0.8 + 0.78 + 9.375 + 1.5 + \
                     2.5 + 1.32 + 8.286 + 0.314 + 0.133 + 0.26 + 1.5 + 2.2625 + \
                     2.1 + 2.2 # p.466
        Reclaimed_AWTP_Cost = 4.063 + 6.25 + 7.813 + 10.469 + 1.813 + 4.688 + \
                              3.907 + 3.125 + 1.875 + 2.344 + 4.688 + 0.28 + \
                              0.22 + 0.4 + 2.25 + 3.2 # p.478
        
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
        
        # collect data for plotting after the loop
        collected_data[i,:] = [run, j, r, 
                               1-LOS_CWUP, 1-LOS_GW, 1-LOS_SW, 1-LOS_All,
                               Environmental_Burden, 
                               SCH_WF_Production, SCH_1_Demand, SCH_2_Demand,
                               SCH_WF_Production_95th, SCH_1_Demand_95th, SCH_2_Demand_95th,
                               Unmanageable_Event_Count, Unmanageable_Event_Median_Duration, 
                               Unmanageable_Severity_Per_Day_95th,
                               Additional_Capital_Costs]
        i += 1
    
    j += 1
    print("Simulation ", run, " is complete after ", (time.time() - t)/60, " minutes")

# final data output
all_out = pd.DataFrame(collected_data)
all_out.columns = Variable_Names        
        
pd.DataFrame.to_csv(all_out,'tradeoff_plot_statistics.csv')

# plot some of the data
markers = ['.','^','s','p','*','+']
temp_list = [int(x) for x in all_out['SimOrder']]
marker_vector = [markers[i] for i in temp_list]
ptsize = 8

for i in [0,1,2,3,4,5]:
    plot_out = all_out[all_out['SimOrder'] == i]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize = (12,12))
    
    scatter_plot = ax1.scatter(plot_out['Unmanageable Events (15+ day events)'], 
                               plot_out['Environmental Burden (target offset)'], 
                               c = plot_out['Level of Service (CWUP only)'], s = ptsize, cmap="jet")
    ax1.set_ylabel('Environmental Burden (target offset)')
    ax1.set_xlabel('Unmanageable Events (15+ day events)')
    #ax1.colorbar(label = 'Unmanageable Events (15+ day events)')
    ax1.set_xlim([-5, 110])
    ax1.set_ylim([100, 375])
    
    scatter_plot = ax4.scatter(plot_out['Level of Service (CWUP only)'], 
                               plot_out['Level of Service (all)'], 
                               c = plot_out['Level of Service (CWUP only)'], s = ptsize, cmap="jet")
    ax4.set_ylabel('Level of Service (all)')
    ax4.set_xlabel('Level of Service (CWUP only)')
    #ax2.colorbar(label = 'Level of Service (SW only)')
    ax4.set_xlim([0.85, 1.01])
    ax4.set_ylim([0.58, 1.01])
    
    scatter_plot = ax3.scatter(plot_out['Unmanageable Events (15+ day events)'], 
                               plot_out['Average SCH Node 2 Demand (MGD)'], 
                               c = plot_out['Level of Service (CWUP only)'], s = ptsize, cmap="jet")
    ax3.set_ylabel('Average SCH Node 2 Demand (MGD)')
    ax3.set_xlabel('Unmanageable Events (15+ day events)')
    #ax3.colorbar(label = 'Unmanageable Event 95th Percentile Severity (MG deficit per day)')
    ax3.set_xlim([-5, 110])
    #ax3.set_ylim([-2, 11])
    
    scatter_plot = ax2.scatter(plot_out['Level of Service (CWUP only)'], 
                               plot_out['Environmental Burden (target offset)'], 
                               c = plot_out['Level of Service (CWUP only)'], s = ptsize, cmap="jet")
    ax2.set_ylabel('Environmental Burden (target offset)')
    ax2.set_xlabel('Level of Service (CWUP only)')
    #ax4.colorbar(label = 'Unmanageable Event 95th Percentile Severity (MG deficit per day)')
    ax2.set_xlim([0.85, 1.01])
    ax2.set_ylim([100, 375])
    
    #ax4.legend(all_out['SimOrder'], loc = 'upper left')
        
    fig.subplots_adjust(wspace = 0.25, hspace = 0.3)     
    fig.savefig('tradeoff_plots' + simulations[i] + '.png', bbox_inches='tight', format='png')       

    # 
    plot_out = all_out[all_out['SimOrder'] <= i]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize = (12,12))
    
    scatter_plot = ax1.scatter(plot_out['Unmanageable Events (15+ day events)'], 
                               plot_out['Environmental Burden (target offset)'], 
                               c = plot_out['Capital Costs ($MM)'], s = ptsize, cmap="jet")
    ax1.set_ylabel('Environmental Burden (target offset)')
    ax1.set_xlabel('Unmanageable Events (15+ day events)')
    #ax1.colorbar(label = 'Unmanageable Events (15+ day events)')
    ax1.set_xlim([-5, 110])
    ax1.set_ylim([100, 375])
    
    scatter_plot = ax4.scatter(plot_out['Level of Service (CWUP only)'], 
                               plot_out['Level of Service (all)'], 
                               c = plot_out['Capital Costs ($MM)'], s = ptsize, cmap="jet")
    ax4.set_ylabel('Level of Service (all)')
    ax4.set_xlabel('Level of Service (CWUP only)')
    #ax2.colorbar(label = 'Level of Service (SW only)')
    ax4.set_xlim([0.85, 1.01])
    ax4.set_ylim([0.58, 1.01])
    
    scatter_plot = ax3.scatter(plot_out['Unmanageable Events (15+ day events)'], 
                               plot_out['Average SCH Node 2 Demand (MGD)'], 
                               c = plot_out['Capital Costs ($MM)'], s = ptsize, cmap="jet")
    ax3.set_ylabel('Average SCH Node 2 Demand (MGD)')
    ax3.set_xlabel('Unmanageable Events (15+ day events)')
    #ax3.colorbar(label = 'Unmanageable Event 95th Percentile Severity (MG deficit per day)')
    ax3.set_xlim([-5, 110])
    #ax3.set_ylim([-2, 11])
    
    scatter_plot = ax2.scatter(plot_out['Level of Service (CWUP only)'], 
                               plot_out['Environmental Burden (target offset)'], 
                               c = plot_out['Capital Costs ($MM)'], s = ptsize, cmap="jet")
    ax2.set_ylabel('Environmental Burden (target offset)')
    ax2.set_xlabel('Level of Service (CWUP only)')
    #ax4.colorbar(label = 'Unmanageable Event 95th Percentile Severity (MG deficit per day)')
    ax2.set_xlim([0.85, 1.01])
    ax2.set_ylim([100, 375])
    
    #ax4.legend(all_out['SimOrder'], loc = 'upper left')
        
    fig.subplots_adjust(wspace = 0.25, hspace = 0.3)     
    fig.savefig('tradeoff_plots_stacked' + simulations[i] + '.png', bbox_inches='tight', format='png')       
    #fig.savefig('tradeoff_plots_all' + '.png', bbox_inches='tight', format='png')     
        
        
        
        
        
        