import numpy as np
import pandas as pd

# FUNCTIONS TO READ AMPL OUTPUT AND EXTRACT OBJECTIVE-BASED STATISTICS
# FOR A GIVEN REALIZATION, TO BE USED WITH A LOOP LATER TO CALCULATE 
# MODEL SIMULATION/RUN OBJECTIVES IN A MASTER SCRIPT
# D Gorelick (Jan 2020)

def getGWPermitViolations(AMPL_cleaned_data):
    # names of GW permit violation variables (if tracked)
    Slack_Variable_Names = ['wup_mavg_pos__CWUP',
                            'wup_mavg_pos__SCH',
                            'wup_mavg_pos__BUD']
    
    # initialize vectors of NaN for each variable
    daily_overage_matrix = np.zeros([len(AMPL_cleaned_data),
                                     len(Slack_Variable_Names)])
    daily_overage_matrix[:] = np.nan
    
    # loop to collect data of interest
    for i in range(len(Slack_Variable_Names)):
        if Slack_Variable_Names[i] in AMPL_cleaned_data.columns:
            daily_overage_matrix[:,i] = AMPL_cleaned_data[Slack_Variable_Names[i]]
        else:
            daily_overage_matrix[:,i] = 0
    
    # rename for clarity and return
    daily_CWUP_overage_vector = daily_overage_matrix[:,0]
    daily_SCH_overage_vector  = daily_overage_matrix[:,1]
    daily_BUD_overage_vector  = daily_overage_matrix[:,2]
    
    return [daily_CWUP_overage_vector, 
            daily_SCH_overage_vector, 
            daily_BUD_overage_vector]


def getSWPermitViolations(AMPL_cleaned_data):
    # names of GW permit violation variables (if tracked)
    Slack_Variable_Names = ['ngw_slack__Alafia',
                            'ngw_slack__Reservoir',
                            'ngw_slack__TBC']
    
    # initialize matrix of NaN for variables
    daily_slack_matrix = np.zeros([len(AMPL_cleaned_data),
                                   len(Slack_Variable_Names)])
    daily_slack_matrix[:] = np.nan
    
    # loop to collect data of interest
    for i in range(len(Slack_Variable_Names)):
        if Slack_Variable_Names[i] in AMPL_cleaned_data.columns:
            daily_slack_matrix[:,i] = AMPL_cleaned_data[Slack_Variable_Names[i]]
    
    # rename for clarity and return
    daily_Alafia_slack_vector    = daily_slack_matrix[:,0]
    daily_Reservoir_slack_vector = daily_slack_matrix[:,1]
    daily_TBC_slack_vector       = daily_slack_matrix[:,2]
    
    return [daily_Alafia_slack_vector, 
            daily_Reservoir_slack_vector, 
            daily_TBC_slack_vector]
    
    
def getMonitoringWellViolations(AMPL_cleaned_data, 
                                SAS_well_attributes):
    # collect SAS well info
    monitoring_wells     = SAS_well_attributes['PointName']
    associated_wellfield = SAS_well_attributes['WFCode']
    
    # build empty dataset to hold wellfield outcomes
    daily_wellfield_average_monitoring_violation_matrix = np.zeros([
            len(AMPL_cleaned_data),
            len(np.unique(associated_wellfield))])

    # count wells in each wellfield
    from collections import Counter
    wellfields_dict = Counter(associated_wellfield).keys()
    wells_per_field_dict = Counter(associated_wellfield).values()
    
    wellfields = []
    for key in wellfields_dict:
        wellfields.append(key)
        
    wells_per_field = []
    for val in wells_per_field_dict:
        wells_per_field.append(val)
    
    # loop through recorded data to assign violations to each wellfield
    for well in range(len(monitoring_wells)):
        wellfield = associated_wellfield[well]
        if 'targetoffset_neg__' + monitoring_wells[well] in AMPL_cleaned_data.columns:
            # add violations to wellfield, divided by total number of wells 
            well_violations = AMPL_cleaned_data['targetoffset_neg__' + 
                                                monitoring_wells[well]].fillna(0)
            daily_wellfield_average_monitoring_violation_matrix[
                    :,wellfields.index(wellfield)] += well_violations / wells_per_field[
                                    wellfields.index(wellfield)]
    
    # convert days without data to NaN
    daily_wellfield_average_monitoring_violation_matrix = \
        pd.DataFrame(daily_wellfield_average_monitoring_violation_matrix) \
        .replace({0:np.nan})
    daily_wellfield_average_monitoring_violation_matrix.columns = wellfields
    
    # pull production data
    daily_wellfield_total_production_matrix = np.zeros([
            len(AMPL_cleaned_data),
            len(np.unique(associated_wellfield))])
    
    for wellfield in range(len(wellfields)):
        daily_wellfield_total_production_matrix[:,wellfield] = AMPL_cleaned_data[
                'wf_prod__' + wellfields[wellfield]]
    
    # name and convert to dataframe
    daily_wellfield_total_production_matrix = pd.DataFrame(daily_wellfield_total_production_matrix)
    daily_wellfield_total_production_matrix.columns = wellfields
    
    # collect water quality well levels 
    WQ_wells = [x[9:] for x in AMPL_cleaned_data.columns if 'ufas_wl' in x]
    daily_upper_floridian_well_violation_matrix = np.zeros([
            len(AMPL_cleaned_data),
            len(np.unique(WQ_wells))])
    
    for well in range(len(WQ_wells)):
        if 'regwell_viol__' + WQ_wells[well] in AMPL_cleaned_data.columns:
            daily_upper_floridian_well_violation_matrix[:,well] = AMPL_cleaned_data[
                    'regwell_viol__' + WQ_wells[well]]
        
    # name and convert to dataframe
    daily_upper_floridian_well_violation_matrix = pd.DataFrame(daily_upper_floridian_well_violation_matrix).replace({0:np.nan})
    daily_upper_floridian_well_violation_matrix.columns = WQ_wells
    
    return [daily_wellfield_average_monitoring_violation_matrix, 
            daily_upper_floridian_well_violation_matrix,
            daily_wellfield_total_production_matrix]


def getInfrastructurePathway(AMPL_cleaned_data):
    # THIS DOESN'T EXIST YET BECAUSE INFRASTRUCTURE IS NOT TRACKED OR
    # DYNAMIC WITHIN THE MODEL
    
    return [daily_capital_cost_for_new_infrastructure, 
            daily_debt_service]
 
    
def calculateLevelOfService(AMPL_cleaned_data):
    # call "get" functions to pull data necessary to calculate objective
    # statistics for the realization
    daily_CWUP_overage_vector, \
    daily_SCH_overage_vector, \
    daily_BUD_overage_vector = getGWPermitViolations(AMPL_cleaned_data)
    
    daily_Alafia_slack_vector, \
    daily_Reservoir_slack_vector, \
    daily_TBC_slack_vector = getSWPermitViolations(AMPL_cleaned_data)
    
    # calculate reliability as the fraction of days without permit violations
    # and take count of longest stretch of consecutive days of violation 
    # (if greater than 365, entire realization is a failure, which is a good 
    # way to track firm yield on the supply under stationary demand realizations
    # but may not function well under transient conditions to track failure)
    violation_tracker = np.stack((daily_CWUP_overage_vector, 
                                  daily_SCH_overage_vector, 
                                  daily_BUD_overage_vector, 
                                  daily_Alafia_slack_vector, 
                                  daily_Reservoir_slack_vector, 
                                  daily_TBC_slack_vector), axis = 1)
    
    
    # total daily violations for the region
    daily_violation_sum = np.nansum(violation_tracker, axis = 1)
    
    # calculate basic ratio of days in violation to total days
    realization_level_of_service_reliability = sum(
            daily_violation_sum > 0) / len(daily_violation_sum)
    
    # length of all violation events
    import itertools
    length_of_events = [sum(1 for _ in group) \
                        for key, group in \
                        itertools.groupby(daily_violation_sum > 0) if key]
    
    # check if largest event is at least 365 days
    if len(length_of_events) > 0:
        if max(length_of_events) > 364:
            print('Realization in failure')
    
    # calculate number of failure events (14+ consec days of failure)
    realization_count_of_failure_events_vulnerability = len(
            [True for x in length_of_events if x > 13])
    
    return [realization_level_of_service_reliability, 
            realization_count_of_failure_events_vulnerability]


def calculateEnvironmentalSustainability(AMPL_cleaned_data, 
                                         SAS_well_attributes):
    # call "get" functions to pull data necessary to calculate objective
    # statistics for the realization
    daily_wellfield_average_monitoring_violation_matrix, \
    daily_upper_floridian_well_violation_matrix, \
    daily_wellfield_total_production_matrix = \
        getMonitoringWellViolations(AMPL_cleaned_data, SAS_well_attributes)
    
    # count of weekly violations by wellfield each 365 day period
    realization_GW_violation_annual_count_by_wellfield = \
        (daily_wellfield_average_monitoring_violation_matrix. \
             fillna(0) > 0).rolling(window = 365).sum().iloc[365:,:]
        
    # for objective statistic, find weeks in violation in each rolling period
    # for worst-performing wellfield and take the average of those values
    realization_GW_worst_case_year_total_weekly_violations = \
        realization_GW_violation_annual_count_by_wellfield.max(axis = 1).mean()
    
    # track relative size of well level violation to wellfield production
    # for 7-day rolling window, don't report but record for interest
    # (not an easily-interpretable statistic)
    
    # correct near-zero or negative demand values
    daily_wellfield_total_production_matrix[
            daily_wellfield_total_production_matrix < 1e-4] = 0
    
    seven_day_rolling_sum_violation_to_production_ratio_by_wellfield = \
        daily_wellfield_average_monitoring_violation_matrix.fillna(0). \
            rolling(window = 7, axis = 0).sum() / \
                daily_wellfield_total_production_matrix.fillna(0). \
                rolling(window = 7, axis = 0).sum()
    
    realization_GW_violation_magnitude_to_production_ratio = \
        seven_day_rolling_sum_violation_to_production_ratio_by_wellfield. \
            iloc[7:,:].median()
            
    # for reporting long-term sustainability, report wellfield average
    # violation deficit over a 365-day rolling average
    # because reporting is only done weekly, do a rolling average of the 
    # rolling weekly sum 
    seven_day_rolling_violation_sums = \
        daily_wellfield_average_monitoring_violation_matrix.fillna(0). \
            rolling(window = 7, axis = 0).sum().iloc[7:,:]
    annual_average_weekly_violation = \
        seven_day_rolling_violation_sums.rolling(
                window = 365).mean().iloc[365:,:]
    
    # from this annual moving average of weekly average wellfield violations
    # take the average across sites "daily" and find the 95th percentile 
    # violation in time to get a sense of sustainability
    regional_worst_case_annual_average_weekly_wellfield_violation_depth = \
        annual_average_weekly_violation.mean(axis = 1).quantile(q = 0.95)
    
    # similarly, get weekly Upper Floridian frequency of violation
    # summarized across all wells, tracked as moving sum of daily violation
    # frequency over annual periods
    # I THINK THIS IS TRACKED WEEKLY FOR ALL SITES SO THIS SHOULD MAX OUT AT 52
    # VIOLATIONS PER ANNUAL PERIOD?
    regional_worst_case_moving_sum_annual_total_UFGW_violation_frequency = \
        (daily_upper_floridian_well_violation_matrix.sum(
                axis = 1) > 0).rolling(window = 365).sum().quantile(q = 0.95)
    
    return [realization_GW_worst_case_year_total_weekly_violations, 
            regional_worst_case_annual_average_weekly_wellfield_violation_depth,
            regional_worst_case_moving_sum_annual_total_UFGW_violation_frequency]


def calculateCosts(AMPL_cleaned_data):
    # call "get" functions to pull data necessary to calculate objective
    # statistics for the realization
    daily_CWUP_overage_vector, daily_SCH_overage_vector, daily_BUD_overage_vector = getGWPermitViolations(AMPL_cleaned_data)
    daily_Alafia_slack_vector, daily_Reservoir_slack_vector, daily_TBC_slack_vector = getSWPermitViolations(AMPL_cleaned_data)
#    getInfrastructurePathway(AMPL_cleaned_data)
    
    # TO BE DEVELOPED WHEN INFRASTRUCTURE COSTS ARE INCLUDED IN THE MODELING?
    
    return [realization_infrastructure_investment, 
            realization_demand_curtailment_conservation_proxy]









