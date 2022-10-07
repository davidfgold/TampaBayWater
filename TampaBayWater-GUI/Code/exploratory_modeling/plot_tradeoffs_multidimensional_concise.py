import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import matplotlib.style as style
from glob import glob
import seaborn as sns
import os
import time
from performance_metrics import calc_LOS, calc_environmental_burden, find_failure_periods, calc_cost
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
                  'Unmanageable Events (15+ day events)', 'Annual Failures (365+ day events)',
                  'Unmanageable Duration 95th Percentile (days)', 
                  'Unmanageable Severity 95th Percentile (total MG deficit)',
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
        
        # calculate performance metrics

        # level of service
        LOS_All, Total_Violations, Violation_Magnitude = calc_LOS(csv_out)
        
        # environmental burden
        Environmental_Burden = calc_environmental_burden(csv_out, log_out)
        
        # failure periods
        Unmanageable_Event_Count, Annual_Failures, Unmanageable_Severity_95th, \
        Unmanageable_Duration_95th = find_failure_periods(Total_Violantions, Violation_Magnitude)
        
        # capital costs
        Additional_Capital_Costs = calc_cost(run)
        
        # collect data for plotting after the loop
        collected_data[i,:] = [run, j, r, 
                               1-LOS_CWUP, 1-LOS_GW, 1-LOS_SW, 1-LOS_All,
                               Environmental_Burden, 
                               SCH_WF_Production, SCH_1_Demand, SCH_2_Demand,
                               SCH_WF_Production_95th, SCH_1_Demand_95th, SCH_2_Demand_95th,
                               Unmanageable_Event_Count, Annual_Failures,
                               Unmanageable_Duration_95th, Unmanageable_Severity_95th,
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
        
 
        
        
        