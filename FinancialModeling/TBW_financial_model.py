# -*- coding: utf-8 -*-
"""
Created on Tue May 12 16:59:10 2020
TAMPA BAY WATER AUTHORITY FINANCIAL MODEL
meant to dynamically simulate financial flows for TBW based on daily results
from OROP and OMS1 models
@author: dgorelic
"""

# Below is a mostly text description of model assumptions, drawing from
# Raftelis 2018 financial analysis report, TBW 2018 LTMWP, and
# 2019 and 2020 CIP reports, as well as discussion with TBW personnel
# also 2019 CAFR report
# NOTE: the below text descriptions may vary from how code was actually 
#   implemented - see comments throughout code for detail on 
#   specific parts of the model

### Revenue sources for TBW
## UNIFORM RATE - set based on revenue requirements, expected demand
#   (revenue requirements = full costs of supply water each year)
#   primary source of revenue, set as rate per kgal sold
#   must cover O&M + DS + Reserves + R&R costs
#   rate from FY 2012 to FY 2018 was $2.559/kgal
#   fixed component is BILLED MONTHLY to member govts
#       to recover TBW fixed costs, based on prorated 
#       share of production for each govt in last FY
#   variable component also BILLED MONTHLY based on that month's
#       water production to recover variable costs
#   an annual "true-up" of fixed costs is done at end of FY
#       adjusting govt prorated shares of annual fixed costs
#       based on the new fraction of water delivered to each govt
#   Raftelis recalculates Uniform Rate annually in forecast
#       as costs, demands, interest revenues change 
## SALES THROUGH TAMPA BYPASS CANAL
#   an alternate (small) revenue source

### Costs accruing to TBW
## OPERATING AND MAINTENANCE (O&M)
#   typically largest annual expense, fixed and variable components
#   includes labor, benefits, insurance, materials, power, chemicals,
#   maintenance, admin and other costs
#   power, chemicals, and water purchases are typically variable costs
#   FY 2018: $56.9M fixed O&M
#   Raftelis projects 3% inflation increase/yr for fixed O&M
#       variable O&M projected to rise 3%/yr plus any water demand inc.
## DEBT SERVICE
#   outstanding debt as of end FY 2017: $842.105M
#   outstanding as of end of FY 2019: $810.7M
#   annual DS from this is ~$68M until FY 2031, 
#   drops to ~$37M until FY 2038, then zero after that.
#   also owe "acquisition credits" to member governments
#       annual total payment is $10.231558M until FY 2028
## CAPITAL RENEWAL AND REPLACEMENT (R&R)
#   TBW is required to maintain an R&R fund size of
#   at least 5% of prior FY's gross revenues
#   R&R spending on system needs is approved in
#       FY budgets, Raftelis assumes 3% annual increase
#       using FY2018 value as a start
## FUNDING RESERVES
#   Rate Stabilization Account, funded based on 
#       amount established in annual budget or Board of Directors
#       Meant to smooth changes in the uniform rate year to year
#   Utility Reserve Fund
#       must contain at least 10% of Gross Revenue not including
#       government grants, and its balance + net revenues must be
#       at least 125% of next-year debt service due
#       Unencumbered funds from this fund are transferred to the
#           rate stabilization fund at end of FY (how much?)

### Bond Covenants (limitations of debt, 2019 CAFR p.38)
## CRITERIA 1 (Fund refers to Utility Reserve Funds)
#   net revenue over any 12-month period of the 24 months
#   before issuance, plus fund balance on the last day of the
#   12-month period, is at least 125% of debt on outstanding bonds
#   over the same period
## CRITERIA 2
#   net revenue over such a 12-month period as in Crit. 1
#   equal at least 100% of (the sum of?)
#       a. debt service on bonds for the period
#       b. required R&R fund deposits
#       c. required Reserve fund deposits

### Model design (inputs, outputs, parameters, calculations)
## INPUTS (from OROP/OMS1)
# Monthly total water demand by each member government
#   (as summed daily values from connected models)
#   split by uniform rate purchases and
#   secondary purchases from Tampa Bypass Canal (very small)
# Historcal record (updating with model) of full financials
#   see p.104 of TBW 2019 CAFR report as example of financials
# List of potential infrastructure expansion projects
# (below parameters can be pulled from ranges based on CIP reports
#  and historical ranges of values)
#   cost-of-capital
#   first date when available for construction
#   construction time (mostly important for actual routing model)
#   annual operational costs
#   bond term and interest rate (assume fixed payments)
# ID of infrastructure project triggered, if any
#   (can be multiple simultaneously?)
#
## OUTPUTS 
# End of realization timeseries outputs of full monthly financial results
#   includes annual calculation of key covenants, other metrics
# Financial Objectives
#   1. net present investment in NEW infrastructure
#   2. peak annual debt service
#   3. worst annual DSC Ratio (or other ratio) - did it violate covenant?
#   4. worst annual size of key reserve funds (which? does this matter?)
#       alternatively, largest withdrawals from Stabilization Fund
#       to cover lost revenues from drought, etc?
#
## PARAMETERS AND CALCULATIONS 
# calculates 
#   monthly revenue from sales
#   monthly variable costs
#   annual true-up for uniform rate costs for members
#   projection for next-FY uniform rate (and total expenditures)
#       this can also be controlled as a parameter
#       if we wanted to test the effect of fixing the rate, for instance
#   outputs and objectives described above
#   all other financial flows at annual scale
#       including their projections for next FY for proposed budget
# parameters affecting calculation will be random factors
#   applied to any major financial flow based on
#   ranges seen in historical record FYs
#   (i.e. deep uncertainty in demands, costs, funds, more?) 

### ----------------------------------------------------------------------- ###
### BUILD MONTHLY FINANCIAL MODEL
### functions for specific calculations
### ----------------------------------------------------------------------- ###

def estimate_VariableRate(annual_estimate, 
                          estimated_variable_costs,
                          uniform_rate):
    # The variable rate ($/1,000 gallons) is defined as 
    # the ratio of the total budgeted Variable Costs
    # to the total Net Annual Revenue Requirement, 
    # applied to the Uniform Rate.
    return estimated_variable_costs/annual_estimate * uniform_rate

def get_DailySupplySlack(csv_out):
    ### water supply model deliveries do not account for slack, which is
    ### only recorded on the supply side, not the delivery/demand side
    ### so we need to get all slack for the days we are looking at
    import pandas as pd
    slack_source_variables = ['wup_mavg_pos__CWUP',
                              'wup_mavg_pos__SCH',
                              'wup_mavg_pos__BUD', 
                              'ngw_slack__Alafia',
                              'ngw_slack__Reservoir',
                              'ngw_slack__TBC', 
                              'sch_demand__sch3_slack']
    
    # initialize vectors of NaN for each variable
    slack_sources = np.zeros([len(csv_out),
                              len(slack_source_variables)])
    slack_sources[:] = np.nan
    
    # loop to collect data of interest
    for i in range(len(slack_source_variables)):
        if slack_source_variables[i] in csv_out.columns:
            slack_sources[:,i] = csv_out[slack_source_variables[i]]
            
            # if slack variable is a weekly moving average, multiply by 7
            # to account for all days
            if slack_source_variables[i] in ['wup_mavg_pos__CWUP','wup_mavg_pos__SCH','wup_mavg_pos__BUD']:
                slack_sources[:,i] *= 7

    # replace nans with zeroes
    slack_sources = pd.DataFrame(slack_sources).replace(np.nan, 0)
    slack_sources.index = csv_out.index
    return slack_sources

def get_MemberDeliveries(csv_out): # accepts cleaned AMPL csv file
    ### collect quantities of supply that are supposedly equal to 
    ### demands at points of connection in the model 
    ### (see model.amp Demand section as example)
    ### and report deliveries by member government (aggregated PoCs)
    import numpy as np
    
    # NWH
    NWH_1_Supply = csv_out['wf_prod__NWH'] + csv_out['wf_prod__CRW'] + csv_out['pflow__NWPL']
    NWH_2_Supply = csv_out['pflow__THIC'] + csv_out['pflow__LP_NW']
    
    # NPR
    NPR_Supply = csv_out['wtp_eff__MT'] - csv_out['pflow__MT_LR']
    
    # PAS
    PAS_1_Supply = csv_out['wtp_eff__LR']
    PAS_2_Supply = csv_out['wtp_eff__OD']
    PAS_3_Supply = csv_out['pflow__41PS']
    PAS_4_Supply = csv_out['pflow__LBBS']
    PAS_Supply = PAS_1_Supply + PAS_2_Supply + PAS_3_Supply + PAS_4_Supply
    
    # PIN
    PIN_Supply = csv_out['pflow__RPIC']
    
    # SCH
    SCH_1_Supply = csv_out['wtp_eff__CH']
    SCH_2_Supply = csv_out['wtp_eff__LT'] + csv_out['pflow__Q_LT']
    SCH_3_Supply = csv_out['pflow__SCH3'] # new for Run 125
    SCH_3_Supply = SCH_3_Supply.replace(np.nan, 0) # remove nans
    
    # Hillsborough Total
    HBO_Supply = NWH_1_Supply + NWH_2_Supply + SCH_1_Supply + SCH_2_Supply + SCH_3_Supply
    
    # STP
    STP_Supply = csv_out['wtp_eff__CM'] + csv_out['pflow__L_STP']
    
    # COT
    COT_Supply = csv_out['pflow__MBPS'] # + csv_out['pflow__J_COT'] this is self-supply by CoT
    
    # Total
    TDel = STP_Supply + PIN_Supply + COT_Supply + HBO_Supply + PAS_Supply + NPR_Supply
    
    import pandas as pd
    deliveries = pd.DataFrame({'St. Petersburg' : STP_Supply, 
                               'Pinellas County' : PIN_Supply, 
                               'City of Tampa' : COT_Supply, 
                               'Hillsborough County' : HBO_Supply, 
                               'Pasco County' : PAS_Supply, 
                               'New Port Richey' : NPR_Supply, 
                               'Total Deliveries' : TDel})
    
    return deliveries

def get_MemberDemands(csv_out): # accepts cleaned AMPL csv file
    ### collect demands by point of connection
    ### and report deliveries by member government (aggregated PoCs)

    # NWH
    NWH_1_Demand = csv_out['demand__NWH_1']
    NWH_2_Demand = csv_out['demand__NWH_2']
    
    # NPR
    NPR_Demand = csv_out['demand__NPR']
    
    # PAS
    PAS_1_Demand = csv_out['demand__PAS_1']
    PAS_2_Demand = csv_out['demand__PAS_2']
    PAS_3_Demand = csv_out['demand__PAS_3']
    PAS_4_Demand = csv_out['demand__PAS_4']
    PAS_Demand = PAS_1_Demand + PAS_2_Demand + PAS_3_Demand + PAS_4_Demand
    
    # PIN
    PIN_Demand = csv_out['demand__PIN']
    
    # SCH
    SCH_1_Demand = csv_out['demand__SCH_1']
    SCH_2_Demand = csv_out['demand__SCH_2']
    SCH_3_Demand = csv_out['demand__SCH_3'] # new for Run 125
    
    # Hillsborough Total
    HBO_Demand = NWH_1_Demand + NWH_2_Demand + SCH_1_Demand + SCH_2_Demand + SCH_3_Demand
    
    # STP
    STP_Demand = csv_out['demand__STP']
    
    # COT
    COT_Demand = csv_out['demand__COT'] - csv_out['pflow__J_COT'] # demand less self-supply by CoT
    
    # Total
    TDem = STP_Demand + PIN_Demand + COT_Demand + HBO_Demand + PAS_Demand + NPR_Demand
    
    import pandas as pd
    demands = pd.DataFrame({'St. Petersburg' : STP_Demand, 
                            'Pinellas County' : PIN_Demand, 
                            'City of Tampa' : COT_Demand, 
                            'Hillsborough County' : HBO_Demand, 
                            'Pasco County' : PAS_Demand, 
                            'New Port Richey' : NPR_Demand, 
                            'Total Demands' : TDem})
    
    return demands


def get_HarneyAugmentationFromOMS(mat_file_name_path = 'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125' + '/sim_0001.mat', 
                                  ndays_in_realization = 7305, r_id = 1):
    ### find Harney Augmentation (HA) in matlab OMS model output
    ### (HA is raw water purchased from TBC by CoT, not under uniform rate)
    # for testing, mat_file_name_path = orop_oms_output_path + '/sim_0001.mat'
    one_thousand_added_to_read_files = 1000
    
    import h5py
    oms_file = h5py.File(mat_file_name_path)
    all_harney_days = oms_file['sim_0' + str(one_thousand_added_to_read_files + r_id)[1:]]['HRTBC']['HAug'][:]
    daily_harney_augmentation = [all_harney_days[0,d] for d in range(0,ndays_in_realization)]
    
    return daily_harney_augmentation


def add_NewDebt(current_year,
                existing_debt, 
                potential_projects,
                triggered_project_ids,
                FOLLOW_CIP_SCHEDULE = True):
    # check if new debt should be issued for triggered projects 
    # maturity date, year principal payments start, interest rate, 
    # Jan 2022: if CIP schedule is being followed, ignore this step and 
    # adjust debt service based on the major projects schedule
    import numpy as np; import pandas as pd
    FIRST_YEAR_OF_LOW_DEBT_SERVICE = 2032 # if debt issued before 2032, delay repayment
    BOND_LENGTH = 30 # years for debt repayment after issuance
    DEBT_INTEREST_RATE = 4
    debt_colnames = existing_debt.columns
    
    if FOLLOW_CIP_SCHEDULE == False:
        for infra_id in np.unique(triggered_project_ids):
            if infra_id != -1:
                new_debt_issue = [np.max([current_year, FIRST_YEAR_OF_LOW_DEBT_SERVICE]), # year principal payments start
                                  current_year + BOND_LENGTH, # maturity year, assume 30-year amortization schedule
                                  DEBT_INTEREST_RATE, # min or actual interest rate, assume flat 4% rate for future stuff
                                  np.nan, # max (if there is one) interest rate, assume not
                                  potential_projects['Total Capital Cost'].iloc[infra_id], # current/initial principal on bond
                                  potential_projects['Total Capital Cost'].iloc[infra_id], # original principal amount bonded
                                  potential_projects['Project ID'].iloc[infra_id]] # new project ID
                existing_debt = pd.DataFrame(np.vstack((existing_debt, new_debt_issue)))
        
    existing_debt.columns = debt_colnames
    return existing_debt

def check_ForTriggeredProjects(daily_ampl_tracking_variable):
    # read timeseries of daily tracking variable from water supply modeling
    # if it changes from -1 to any other number, that project is triggered in 
    # water supply modeling to change the system configuration and bonds must
    # be issued to cover its capital costs
    # NOTE: ASSUMES IDS OF POTENTIAL PROJECTS ARE ALL not -1
    import numpy as np
    new_project_id = [] # default value, nothing built this month
    for pid in np.unique(daily_ampl_tracking_variable):
        if pid != -1:
            new_project_id.append(pid)

    return new_project_id

def calculate_DebtCoverageRatio(net_revenues, 
                                debt_service, 
                                required_deposits):
    # if ratio < 1, covenant failure
    return net_revenues / (debt_service + required_deposits)

def calculate_RateCoverageRatio(net_revenues, 
                                debt_service,
                                fund_balance):
    # if ratio < 1.25, covenant failure
    return (net_revenues + fund_balance) / (debt_service)

def set_BudgetedDebtService(existing_debt, last_year_net_revenue, 
                            existing_debt_targets, 
                            major_cip_projects_schedule,
                            other_cip_projects_schedule,
                            year = 2021, start_year = 2021,
                            FOLLOW_CIP_SCHEDULE_MAJOR_PROJECTS = True,
                            first_cip_future_debt_issuance_year = 2023):
    import numpy as np
    # read in approximate "caps" on annual debt service out to 2038
    # based on existing debt only - will need to add debt
    # as new projects come online
    total_budgeted_debt_service = \
        existing_debt_targets['Total'].iloc[year - start_year] 
        
    # Jan 2022: now this process is overridden by use of the CIP project 
    #   schedule for major projects, if desired. This will ignore
    #   triggering of specific projects and instead assume the CIP schedule
    #   is followed. Adhere to this schedule post-FY2022, when future revenue
    #   bonds begin to be repaid for new projects according to the schedule.
    if year >= first_cip_future_debt_issuance_year:
        total_budgeted_debt_service = \
            major_cip_projects_schedule['Revenue Bonds (320)'].loc[year - start_year] + \
            major_cip_projects_schedule['Revenue Bonds (350)'].loc[year - start_year] + \
            major_cip_projects_schedule['Revenue Bonds (Future)'].loc[year - start_year] + \
            other_cip_projects_schedule['Revenue Bonds (320)'].loc[year - start_year] + \
            other_cip_projects_schedule['Revenue Bonds (350)'].loc[year - start_year] + \
            other_cip_projects_schedule['Revenue Bonds (Future)'].loc[year - start_year]

    # check for new debt/projects and adjust targets
    # existing debt in 2019 has ID nan, any debt issued
    # during modeling has a real ID
    if FOLLOW_CIP_SCHEDULE_MAJOR_PROJECTS == False:
        for bond in range(0,len(existing_debt['ID'])):
            if ~np.isnan(existing_debt['ID'].iloc[bond]):
                # how much should even annual payments mean to
                # add to this year?            
                total_principal_owed = existing_debt['Original Amount'].iloc[bond]
                repayment_years = existing_debt['Maturity'].iloc[bond] - existing_debt['Principal Payments Start '].iloc[bond]
                interest_rate = existing_debt['Interest Rate (actual or min)'].iloc[bond]/100
                remaining_principal_owed = existing_debt['Outstanding Principal'].iloc[bond]
                
                # calculate even annual payments, including interest
                # TO ADD: CAP IF TOTAL DEBT SERVICE RISES TOO HIGH
                if remaining_principal_owed > 1e4:
                    if existing_debt['Principal Payments Start '].iloc[bond] <= year:
                        level_debt_service_payment = \
                            total_principal_owed * \
                            (interest_rate * (1 + interest_rate)**repayment_years) / \
                            ((1 + interest_rate)**(repayment_years)-1)
                        existing_debt['Outstanding Principal'].iloc[bond] -= \
                            level_debt_service_payment - \
                            interest_rate*remaining_principal_owed
                    else: # only pay interest before principal repayment begins
                        level_debt_service_payment = \
                            remaining_principal_owed * interest_rate
                            
                    total_budgeted_debt_service += level_debt_service_payment
            
    return total_budgeted_debt_service, existing_debt

def add_NewOperationalCosts(possible_projs, 
                            new_projs_this_FY, 
                            fraction_variable_cost = 0.15):
    # if a new bond is issued to cover an infrastructure project
    # add that project's O&M costs to budget
    new_fixed_costs = 0; new_variable_costs = 0
    for proj in range(0,len(possible_projs['Project ID'])):
        if proj in new_projs_this_FY:
            new_fixed_costs += \
                possible_projs['Annual O&M Cost'].iloc[proj] * \
                (1-fraction_variable_cost)
            new_variable_costs += \
                possible_projs['Annual O&M Cost'].iloc[proj] * \
                fraction_variable_cost
    
    return new_fixed_costs, new_variable_costs


def allocate_InitialAnnualCIPSpending(start_year, end_year, first_modeled_fy,
                                      CIP_plan, 
                                      fraction_cip_spending_for_major_projects_by_year_by_source,
                                      generic_CIP_plan,
                                      generic_fraction_cip_spending_for_major_projects_by_year_by_source,
                                      outpath, PRINT_INITIAL_ALLOCATIONS = True):
    # set up estimate of annual capital expenditures schedule 
    # for full modeling period. if running historical period,
    # use normalized cip plan. if running 2021 start date, begin with 
    # true plan and follow with generic/normalized spending after FY2031
    # for building: start_year = start_fiscal_year; end_year = end_fiscal_year
    n_sources_for_cip_spending = len(CIP_plan)
    n_available_generic_years = len(generic_CIP_plan.T)-1
            
    full_period_major_cip_expenditures = np.empty((end_year-start_year+1,n_sources_for_cip_spending+1))
    full_period_major_cip_expenditures[:] = np.nan; full_period_major_cip_expenditures[:,0] = range(start_year,(end_year+1))
    full_period_major_cip_expenditures = pd.DataFrame(full_period_major_cip_expenditures)
    full_period_major_cip_expenditures.columns = ['Fiscal Year'] + [x for x in CIP_plan['Current.Funding.Source'].values]
    
    # separate cip schedules for (1) major water supply projects and (2) all other projs
    full_period_other_cip_expenditures = np.empty((end_year-start_year+1,n_sources_for_cip_spending+1))
    full_period_other_cip_expenditures[:] = np.nan; full_period_other_cip_expenditures[:,0] = range(start_year,(end_year+1))
    full_period_other_cip_expenditures = pd.DataFrame(full_period_other_cip_expenditures)
    full_period_other_cip_expenditures.columns = ['Fiscal Year'] + [x for x in CIP_plan['Current.Funding.Source'].values]
            
    n_total_years_to_use = len(full_period_major_cip_expenditures)        
    if end_year <= first_modeled_fy: 
        # if running historic sim, use generic/normalized cip schedule
        # NOTE: assume that historic simulation is no more than 9 years in 
        #   length (2014 earliest to 2021 latest), otherwise throw error
        assert (end_year-start_year <= n_available_generic_years), \
            "Error in allocate_InitialAnnualCIPSpending: CIP scheduling not designed for historic simulation longer than 9 years"
        
        # beginning at start of generic CIP schedule, fill in historic plan and 
        # multiply by the inverse of the fraction used for major projects only 
        # repeat for major projects schedule, but dont invert fraction multiplier
        full_period_other_cip_expenditures.iloc[:,1:] = \
            generic_CIP_plan.iloc[:,1:(n_total_years_to_use+1)].T.values * \
            (1 - generic_fraction_cip_spending_for_major_projects_by_year_by_source.iloc[:,1:(n_total_years_to_use+1)].T.values)
        full_period_major_cip_expenditures.iloc[:,1:] = \
            generic_CIP_plan.iloc[:,1:(n_total_years_to_use+1)].T.values * \
            (generic_fraction_cip_spending_for_major_projects_by_year_by_source.iloc[:,1:(n_total_years_to_use+1)].T.values)
    else:
        # if running future simulation, ASSUME FY2021 start
        # and follow 2021-2031 schedule, succeeded by normalized
        # schedule post-FY2031
        n_years_initial_cip_plan = (len(CIP_plan.T)-2)
        if n_total_years_to_use > n_years_initial_cip_plan:
            # if the future simulation extends beyond 2031, append generic record afterward
            # if it extends further than 8 years after 2032, repeat the generic schedule again.
            # NOTE: for reading CIP_plan, ignore FY2032 last column because it is really a
            #   placeholder for carry-over funding after the 10-year planning window.
            full_period_other_cip_expenditures.iloc[:n_years_initial_cip_plan,1:(len(CIP_plan)+1)] = \
                CIP_plan.iloc[:,1:-1].T.values * \
                (1 - fraction_cip_spending_for_major_projects_by_year_by_source.iloc[:,1:-1].T.values)
            full_period_major_cip_expenditures.iloc[:n_years_initial_cip_plan,1:(len(CIP_plan)+1)] = \
                CIP_plan.iloc[:,1:-1].T.values * \
                (fraction_cip_spending_for_major_projects_by_year_by_source.iloc[:,1:-1].T.values)
            
            # if additional scheduling is needed, determine how many of those generic years must be applied
            n_generic_years_to_use = min((n_total_years_to_use - n_years_initial_cip_plan), n_available_generic_years)
            full_period_other_cip_expenditures.iloc[n_years_initial_cip_plan:(n_years_initial_cip_plan + n_generic_years_to_use),1:] = \
                generic_CIP_plan.iloc[:,1:(n_total_years_to_use+1)].T.values * \
                (1 - generic_fraction_cip_spending_for_major_projects_by_year_by_source.iloc[:,1:(n_total_years_to_use+1)].T.values)
            full_period_major_cip_expenditures.iloc[n_years_initial_cip_plan:(n_years_initial_cip_plan + n_generic_years_to_use),1:] = \
                generic_CIP_plan.iloc[:,1:(n_total_years_to_use+1)].T.values * \
                (generic_fraction_cip_spending_for_major_projects_by_year_by_source.iloc[:,1:(n_total_years_to_use+1)].T.values)
            
            # if more than one iteration of generic CIP schedule is needed, determine how much and apply
            # NOTE: this assumes the planning period is not longer than 11 + 9 + 9 = 29 years (2021-2049)
            if (n_total_years_to_use - n_years_initial_cip_plan) > n_available_generic_years:
                n_remaining_years_to_fill = (n_total_years_to_use - n_years_initial_cip_plan) - n_available_generic_years
                full_period_other_cip_expenditures.iloc[-n_remaining_years_to_fill:,1:] = \
                    generic_CIP_plan.iloc[:,1:(n_remaining_years_to_fill+1)].T.values * \
                    (1 - generic_fraction_cip_spending_for_major_projects_by_year_by_source.iloc[:,1:(n_remaining_years_to_fill+1)].T.values)
                full_period_major_cip_expenditures.iloc[-n_remaining_years_to_fill:,1:] = \
                    generic_CIP_plan.iloc[:,1:(n_remaining_years_to_fill+1)].T.values * \
                    (generic_fraction_cip_spending_for_major_projects_by_year_by_source.iloc[:,1:(n_remaining_years_to_fill+1)].T.values)
            
            # NOTE: remove past-due revenue bond expenditures from future spending schedule
            full_period_other_cip_expenditures['Revenue Bonds (320)'].loc[n_years_initial_cip_plan:] = 0
            full_period_other_cip_expenditures['Revenue Bonds (350)'].loc[n_years_initial_cip_plan:] = 0
        else:
            # if doing a short future simulation (stops before 2032), no need to
            # append generic normalized cip schedule.
            full_period_other_cip_expenditures.iloc[:n_total_years_to_use,1:(len(CIP_plan)+1)] = \
                CIP_plan.iloc[:,1:(n_total_years_to_use+1)].T.values * \
                (1 - fraction_cip_spending_for_major_projects_by_year_by_source.iloc[:,1:(n_total_years_to_use+1)].T.values)
            full_period_major_cip_expenditures.iloc[:n_total_years_to_use,1:(len(CIP_plan)+1)] = \
                CIP_plan.iloc[:,1:(n_total_years_to_use+1)].T.values * \
                (fraction_cip_spending_for_major_projects_by_year_by_source.iloc[:,1:(n_total_years_to_use+1)].T.values)
    
    # getting errors here from printing?    
    #if PRINT_INITIAL_ALLOCATIONS:
    #    full_period_major_cip_expenditures.to_csv(outpath + '/baseline_CIP_major_expenditures.csv')
    #    full_period_other_cip_expenditures.to_csv(outpath + '/baseline_CIP_other_expenditures.csv')
    return full_period_major_cip_expenditures, full_period_other_cip_expenditures


def update_MajorSupplyInfrastructureInvestment(FOLLOW_CIP_SCHEDULE,
                                               FY, 
                                               first_modeled_fy, 
                                               last_fy_month, 
                                               Month, 
                                               Year, 
                                               formulation_id,
                                               AMPL_cleaned_data,
                                               actual_major_cip_expenditures_by_source_full_model_period):
    # initialize empty list to fill if capital projects are triggered
    new_projects_to_finance = []
    
    if FOLLOW_CIP_SCHEDULE:
        # Nov 2021: default to use of major CIP schedule
        # currently no action needed, print an acknowledgement 
        if FY == first_modeled_fy+1:
            print("Following CIP schedule over modeling period.")
    else:
        # track if new infrastructure is triggered in the current FY
        if ((len(AMPL_cleaned_data) > 1) and (FY > first_modeled_fy)): # if using model data
            model_index = [(int(Month[d]) <= last_fy_month and int(Year[d]) == FY) or (int(Month[d]) > last_fy_month and int(Year[d]) == (FY-1)) for d in range(0,len(AMPL_cleaned_data))]
            model_index_subset = [(int(Month[d]) == last_fy_month and int(Year[d]) == FY) or (int(Month[d]) > last_fy_month and int(Year[d]) == (FY-1)) for d in range(0,len(AMPL_cleaned_data))]
            
            # for initial tests and model runs, "artificially" include
            # SHC Balm pipeline debt starting 3 years before FY2028
            # when it is expected to be built, for now hard-coded at
            # 2025 to trigger project ID 5, which is the 36in diameter pipe
            # supplying a max capacity of 12.5 MGDs
            
            # Nov 2020: depending on infrastructure scenario, trigger different projects
            # NOTE: PROJECTS USED FOR 126 AND 128 FINANCING MAY NOT BE EXACT ONES FROM SWRM MODEL
            #   NOTES ON MODEL RUNS SAY 126 IS SWTP EXPANSION TO 110MGD, 128 IS EXP. TO 120MGD
            # run 125: proj ID 5 (small balm pipeline) in 2025
            # run 126: ID 5 in 2025, ID 3 in 2025 (SWTP expansion by 10 MGD)
            # run 128: ID 5 in 2025, ID 4 in 2025 (SWTP expansion by 12.5 MGD)
            if FY == 2025:
                AMPL_cleaned_data['Trigger Variable'].loc[model_index] = 5
                
                # assuming model_index is a vector of all days in current FY,
                # if a run triggers more than one project, change the trigger variable of the final
                # index month to the second project ID
                if formulation_id == 126:
                    AMPL_cleaned_data['Trigger Variable'].loc[model_index_subset] = 3
                if formulation_id == 128:
                    AMPL_cleaned_data['Trigger Variable'].loc[model_index_subset] = 4
                    
                # APRIL 2021: add projects for runs 141-144
                if formulation_id == 143: # Balm + SWTP expansion
                    AMPL_cleaned_data['Trigger Variable'].loc[model_index_subset] = 4
                if formulation_id == 144: # Balm + SWTP expansion (off-site)
                    AMPL_cleaned_data['Trigger Variable'].loc[model_index_subset] = 4
            
            if FY == 2022:
                # APRIL 2021: add projects for runs 141-144
                # TECO project in CIP report (ID 07033) expects to rely on about
                # $12M total in capital costs, but only about $8M in bonds
                if formulation_id == 142: # TECO Tunnel 1 connector project phase 2
                    AMPL_cleaned_data['Trigger Variable'].loc[model_index_subset] = 8
                if formulation_id == 143: # TECO Tunnel 1 connector project phase 2
                    AMPL_cleaned_data['Trigger Variable'].loc[model_index_subset] = 8
                if formulation_id == 144: # TECO Tunnel 1 connector project phase 2
                    AMPL_cleaned_data['Trigger Variable'].loc[model_index_subset] = 8
                    
            triggered_project_ids = \
                check_ForTriggeredProjects(
                        AMPL_cleaned_data['Trigger Variable'].loc[model_index])
            for p_id in triggered_project_ids:
                new_projects_to_finance.append(p_id) # multiple projects can be triggered in same FY
                
    return actual_major_cip_expenditures_by_source_full_model_period, new_projects_to_finance, AMPL_cleaned_data


def estimate_UniformRate(annual_estimate, 
                         demand_estimate,
                         current_uniform_rate,
                         rs_transfer_in,
                         rs_fund_total,
                         high_rate_bound = 0.01,
                         low_rate_bound = 0.01,
                         MANAGE_RATE = False,
                         DEBUGGING = False):
    import numpy as np
    n_days_in_year = 365; convert_kgal_to_MG = 1000
    
    # if the rates of increase and decrease allowed are very close to zero,
    # assume the goal is to maintain the UR and skip all below calcs
    # no change to Annual Estimate because that is sum of expenditures,
    # which will not change if UR changes
    assert (high_rate_bound >= low_rate_bound), \
        "Uniform Rate high management bound must be >= lower bound"
    
    if (MANAGE_RATE) and (high_rate_bound == 0) and (low_rate_bound == 0):
        uniform_rate = current_uniform_rate
        
        # this may require change in fund transfers
        # here, negative shift means the fixed rate will more than cover costs
        # if positive, need to increase RS transfer in as revenue to cover
        expected_revenue = uniform_rate * (demand_estimate * n_days_in_year) * convert_kgal_to_MG
        rs_transfer_in_shift = annual_estimate - expected_revenue

        # be sure that transfer doesn't get too large or small
        if rs_transfer_in_shift <= 0:
            rs_transfer_in += np.max([rs_transfer_in_shift, -rs_transfer_in])
        else:
            rs_transfer_in += np.min([rs_transfer_in_shift, rs_fund_total])
    elif MANAGE_RATE:
        # the decrease and increase rates can be either positive or negative,
        # think of them as bounds around what the next year's rate can be
        # (i.e. if high bound is 3% and low is 1%, the next year rate must
        #  be between 1-3% greater than this year's rate)
        high_capped_next_FY_uniform_rate = current_uniform_rate * (1 + high_rate_bound)
        low_capped_next_FY_uniform_rate = current_uniform_rate * (1 + low_rate_bound)
        uncapped_next_FY_uniform_rate = annual_estimate / (demand_estimate * n_days_in_year) / convert_kgal_to_MG
        
        # based on bounds, determine what next year's rate should be
        uniform_rate = np.min([high_capped_next_FY_uniform_rate,
                               np.max([uncapped_next_FY_uniform_rate, 
                                       low_capped_next_FY_uniform_rate])])
        if DEBUGGING:
            print(current_uniform_rate)
            print(uniform_rate)
        
        # update the rate stabilization transfers and annual estimate
        # if rate is higher than expected, reduce RS transfer in
        if uniform_rate > uncapped_next_FY_uniform_rate:
            rs_transfer_in_shift = -1 * \
                np.min([rs_transfer_in, \
                        (uniform_rate - uncapped_next_FY_uniform_rate) * \
                        (demand_estimate * n_days_in_year) * convert_kgal_to_MG])
        # if lower than expected, increase RS transfer in
        else:
            rs_transfer_in_shift = \
                np.min([rs_fund_total - rs_transfer_in, \
                        (uncapped_next_FY_uniform_rate - uniform_rate) * \
                        (demand_estimate * n_days_in_year) * convert_kgal_to_MG])
          
        rs_transfer_in += rs_transfer_in_shift
        if DEBUGGING:
            print(rs_transfer_in)
    else:
        uniform_rate = annual_estimate / \
            (demand_estimate * n_days_in_year) / convert_kgal_to_MG
    
    # NOTE: updated annual estimate is only used to estimate new UR,
    #       a change in the UR will not impact expenditures other than
    #       potential TBW fund transfers (RS fund transfers in)
    return uniform_rate, annual_estimate, rs_transfer_in


def calculate_TrueDeliveriesWithSlack(m_index, m_month, AMPL_data, TBC_data):
    import pandas as pd
    
    # collect monthly modeled data
    deliveries = get_MemberDeliveries(AMPL_data.iloc[m_index,:]).groupby(m_month).sum()
    TBC_deliveries = pd.Series(TBC_data).iloc[m_index].groupby(m_month).sum()
    slack = get_DailySupplySlack(AMPL_data.iloc[m_index,:]).groupby(m_month).sum()
    
    # when grouping is done, indices get reset - need to re-order for FY
    index_order = [4,5,6,7,8,9,10,11,12,1,2,3][:len(TBC_deliveries)]
    TBC_deliveries.index = index_order; TBC_deliveries = TBC_deliveries.sort_index()
    deliveries.index = index_order; deliveries = deliveries.sort_index()
    slack.index = index_order; slack = slack.sort_index()
    
    # distribute slack, remove it from deliveries
    # slack distributed based on fraction of total delivery to 
    # each member government
    slack_by_member = \
        pd.DataFrame([[i for i in (slack.sum(axis = 1).iloc[m] * \
          (deliveries.iloc[:,:-1].sum() / \
           deliveries.iloc[:,:-1].sum().sum()))] \
         for m in range(0,len(np.unique(m_month)))])
    deliveries.iloc[:,:-1] -= slack_by_member.values
    deliveries.iloc[:,-1] -= slack_by_member.sum(axis = 1).values
    deliveries[deliveries < 0] = 0 # catch negative values (should only happen for CoT and be negligible)
    
    return deliveries, TBC_deliveries


def collect_ExistingRecords(annual_actuals, annual_budgets, water_delivery_sales,
                            annual_budget, budget_projections, water_deliveries_and_sales, 
                            CIP_plan, reserve_balances, reserve_deposits,
                            AMPL_cleaned_data, TBC_raw_sales_to_CoT, Month, Year,
                            fiscal_years_to_keep, first_modeled_fy, n_months_in_year, 
                            annual_demand_growth_rate, last_fy_month,
                            outpath, 
                            keep_extra_fy_of_approved_budget_data = True):
    
    earliest_fy_budget_available = min(budget_projections['Fiscal Year'])
    earliest_fy_actuals_available = min(annual_budget['Fiscal Year'])
    earliest_fy_sales_available = min(water_deliveries_and_sales['Fiscal Year'])
    
    # because we need one extra historic year of actuals, grab it 
    prelim_year = min(fiscal_years_to_keep) - 1
    assert (earliest_fy_actuals_available <= prelim_year), \
        "Must start at later FY: actuals not available."
    current_fy_index = [tf for tf in (annual_budget['Fiscal Year'] == prelim_year)]
    annual_actuals.loc[annual_actuals['Fiscal Year'] == prelim_year,:] = [v for v in annual_budget.iloc[current_fy_index,:].values]
        
    # Nov 2021: for FY20, overwrite actual reserve fund levels as necessary
    # with CIP Report data from Maribel
    annual_actuals['R&R Fund (Total)'].loc[annual_actuals['Fiscal Year'] == (first_modeled_fy-1)] = \
        reserve_balances['FY ' + str(first_modeled_fy)].loc[reserve_balances['Fund Name'] == 'Renewal and Replacement Fund']
    annual_actuals['CIP Fund (Total)'].loc[annual_actuals['Fiscal Year'] == (first_modeled_fy-1)] = \
        reserve_balances['FY ' + str(first_modeled_fy)].loc[reserve_balances['Fund Name'] == 'Capital Improvement Fund']
    annual_actuals['Energy Savings Fund (Total)'].loc[annual_actuals['Fiscal Year'] == (first_modeled_fy-1)] = \
        reserve_balances['FY ' + str(first_modeled_fy)].loc[reserve_balances['Fund Name'] == 'Energy Fund']
        
    # Jan 2022: extend CIP plan schedule of reserve fund deposits out to 2040
    #   and make small corrections to the dataset for clarity and re-order it
    #   Only do this for future simulation for now
    reserve_deposits_to_use = reserve_deposits.copy()
    if min(fiscal_years_to_keep) >= first_modeled_fy-1:
        n_cip_plan_years = 11
        n_copy_years = len(annual_actuals['Fiscal Year'])-2 - n_cip_plan_years
        deposit_years_to_copy = ['FY ' + str(FY) for FY in range(first_modeled_fy, first_modeled_fy + n_copy_years)]
        deposit_years = ['FY ' + str(FY) for FY in range(first_modeled_fy, first_modeled_fy + n_cip_plan_years)]
        future_deposit_years_to_fill = ['FY ' + str(FY) for FY in range(first_modeled_fy + n_cip_plan_years, max(fiscal_years_to_keep)+1)]
        reserve_deposits_to_use['FY 2021'] = reserve_deposits['FY 2021'] + reserve_deposits['Remaining FY 2021']
        
        full_model_period_reserve_deposits = pd.DataFrame(columns = ['Fund Name'] + ['FY ' + str(FY) for FY in fiscal_years_to_keep[1:]])
        full_model_period_reserve_deposits['Fund Name'] = reserve_deposits_to_use['Fund Name'].values
        full_model_period_reserve_deposits[deposit_years] = reserve_deposits_to_use[deposit_years].values
        full_model_period_reserve_deposits[future_deposit_years_to_fill] = reserve_deposits_to_use[deposit_years_to_copy].values

    # loop across every year modeling will occur, and needed historical years,
    # to collect data into proper datasets for use in realization loop
    for fy in fiscal_years_to_keep:
        # set up budgets dataset, there are historic budgets through FY 2021
        # for historical simulation, must start at FY2015 or later, because
        # I only have budgets back to FY2014 and need one previous-FY budget
        # in the dataset for calculations
        assert (np.max([earliest_fy_budget_available,
                        earliest_fy_actuals_available,
                        earliest_fy_sales_available]) <= fy), \
                "Must start at later FY: full historic records not available."
        
        if fy <= first_modeled_fy+int(keep_extra_fy_of_approved_budget_data):
            current_fy_index = [tf for tf in (budget_projections['Fiscal Year'] == fy)]
            annual_budgets.loc[annual_budgets['Fiscal Year'] == fy,:] = [v for v in budget_projections.iloc[current_fy_index,:].values]
        
        # set up water deliveries
        # this will be tricky because need to re-arrange columns from historic
        # record as well as add in any records from modeling
        # HARD-CODED ASSUMPTION HERE (AND ABOVE WHERE MODELING DATA IS READ)
        # IS THAT MODELING BEGINS WITH JAN 1, 2021
        if fy < first_modeled_fy:
            # fill from historic data
            current_fy_index = [tf for tf in (water_deliveries_and_sales['Fiscal Year'] == fy)]
            water_delivery_sales.loc[water_delivery_sales.iloc[:,0] == fy,2:] = water_deliveries_and_sales.iloc[current_fy_index,1:-3].values
            
            # repeat for actuals from historic record (go through FY 2020 now that observed data fills out the record)
            current_fy_index = [tf for tf in (annual_budget['Fiscal Year'] == fy)]
            annual_actuals.loc[annual_actuals.iloc[:,0] == fy,:] = [v for v in annual_budget.iloc[current_fy_index,:].values]
        elif fy == first_modeled_fy:
            # special case with 3 months of observed data in Oct-Dec 2020 for start of FY2021
            # followed by 9 months of model data - for this year, use FY21 accepted budget to calculate revenues
            current_fy_index = [tf for tf in (water_deliveries_and_sales['Fiscal Year'] == fy)]
            water_delivery_sales.loc[(water_delivery_sales['Fiscal Year'] == fy) & (water_delivery_sales['Month'] > last_fy_month),2:] = water_deliveries_and_sales.iloc[current_fy_index,1:-3].values
            
            # get slack-factored monthly water deliveries for the rest of calendar year 2021 until end of FY21
            model_index = [(int(Month[d]) <= last_fy_month and int(Year[d]) == fy) for d in range(0,len(AMPL_cleaned_data))]
            model_months = pd.Series(Month).iloc[model_index]
            uniform_rate_member_deliveries, month_TBC_raw_deliveries = \
                calculate_TrueDeliveriesWithSlack(m_index = model_index, 
                                                  m_month = model_months, 
                                                  AMPL_data = AMPL_cleaned_data, 
                                                  TBC_data = TBC_raw_sales_to_CoT)
            
            # plug remaining FY21 data into dataset
            water_delivery_sales.loc[(water_delivery_sales['Fiscal Year'] == fy) & (water_delivery_sales['Month'] <= last_fy_month),2:(uniform_rate_member_deliveries.shape[1]+2)] = uniform_rate_member_deliveries.values
            water_delivery_sales['TBC Delivery - City of Tampa'].loc[(water_delivery_sales['Fiscal Year'] == fy) & (water_delivery_sales['Month'] <= last_fy_month)] = month_TBC_raw_deliveries.values
        else:
            # modeled data from here on out, just collect deliveries 
            # for any future years that will be modeled
            # get slack-factored monthly water deliveries
            # this logic statement: any month from current FY up to Sept
            #   (because model data is in terms of calendar years)
            #   along with previous year's Oct-Dec
            model_index = [(int(Month[d]) <= last_fy_month and int(Year[d]) == fy) or (int(Month[d]) > last_fy_month and int(Year[d]) == (fy-1)) for d in range(0,len(AMPL_cleaned_data))]
            model_months = pd.Series(Month).iloc[model_index]
            uniform_rate_member_deliveries, month_TBC_raw_deliveries = \
                calculate_TrueDeliveriesWithSlack(m_index = model_index, 
                                                  m_month = model_months, 
                                                  AMPL_data = AMPL_cleaned_data, 
                                                  TBC_data = TBC_raw_sales_to_CoT)
            
            # plug into dataset
            water_delivery_sales.loc[(water_delivery_sales.iloc[:,0] == fy),2:(uniform_rate_member_deliveries.shape[1]+2)] = uniform_rate_member_deliveries.values
            water_delivery_sales['TBC Delivery - City of Tampa'].loc[(water_delivery_sales.iloc[:,0] == fy)] = month_TBC_raw_deliveries.values

    # if this is just a historical simulation test, print copies of datasets now
    # while they contain observed, real actuals for ease of comparison later
    # (assumes this is being done for one simulation, one realization)
    if max(fiscal_years_to_keep) < first_modeled_fy:
        # also, because if end_fiscal_year = 2021, then the last fiscal_year_to_keep value
        # will be 2020, so when doing historic simulation make sure one extra budget FY
        # is included
        last_fy_to_add = int(max(fiscal_years_to_keep)) + 1
        current_fy_index = [tf for tf in (budget_projections['Fiscal Year'] == last_fy_to_add)]
        annual_budgets.loc[annual_budgets.iloc[:,0] == last_fy_to_add,:] = [v for v in budget_projections.iloc[current_fy_index,:].values]
        
        annual_actuals.to_csv(outpath + '/historic_actuals.csv')
        annual_budgets.to_csv(outpath + '/historic_budgets.csv')
        water_delivery_sales.to_csv(outpath + '/historic_sales.csv')

    return annual_actuals, annual_budgets, water_delivery_sales, full_model_period_reserve_deposits


def pull_ModeledData(additional_scripts_path, orop_output_path, oms_output_path, realization_id, 
                     fiscal_years_to_keep, end_fiscal_year, first_modeled_fy, PRE_CLEANED = True):
    # get modeled water delivery data
    import os
    AMPL_cleaned_data = [np.nan]; TBC_raw_sales_to_CoT = [np.nan]; Year = [np.nan]; Month = [np.nan]
    one_thousand_added_to_read_files = 1000; n_days_in_year = 365
    if end_fiscal_year > first_modeled_fy: # meaning the last FY modeled financially is 2020
        os.chdir(additional_scripts_path); from analysis_functions import read_AMPL_csv, read_AMPL_out
        if PRE_CLEANED:
            AMPL_cleaned_data = pd.read_csv(orop_output_path + '/ampl_0' + str(one_thousand_added_to_read_files + realization_id)[1:] + '.csv')
        else:
            AMPL_cleaned_data = read_AMPL_csv(orop_output_path + '/ampl_0' + str(one_thousand_added_to_read_files + realization_id)[1:] + '.csv', export = False)
        ndays_of_realization = len(AMPL_cleaned_data.iloc[:,0])
        
        # until water supply model is changed to include infrastructure adjustment
        # check for the variable in the set and put in a placeholder if it isn't there
        if 'Trigger Variable' not in AMPL_cleaned_data.columns:
            AMPL_cleaned_data['Trigger Variable'] = -1
            
        # get additional water supply modeling data from OMS results
        TBC_raw_sales_to_CoT = get_HarneyAugmentationFromOMS(oms_output_path + '/sim_0' + str(one_thousand_added_to_read_files + realization_id)[1:] + '.mat', ndays_of_realization, realization_id)
    
        # necessary to use the exact matching dates also because model
        # records are daily
        # can use same file each time
        AMPL_outfile = read_AMPL_out(orop_output_path + '/ampl_0001.out')
        Year  = [str(float(str(x)[:4]))[:4] for x in AMPL_outfile['Date']]
        Month = [str(x)[4:6] for x in AMPL_outfile['Date']]
        
        # do test of modeled data length - enough years of data?
        assert (int(ndays_of_realization/n_days_in_year) >= (len(fiscal_years_to_keep)-1)), 'End fiscal year is too late - not enough model data to cover.'
        
    return AMPL_cleaned_data, TBC_raw_sales_to_CoT, Year, Month


def calculate_WaterSalesForFY(FY, water_delivery_sales, 
                              annual_budgets, annual_actuals,
                              dv_list, 
                              rdm_factor_list,
                              annual_demand_growth_rate):
    # set parameters
    KEEP_UNIFORM_RATE_STABLE = bool(np.round(dv_list[2])) # if range is [0,1], will round to either bound for T/F value
    managed_uniform_rate_increase_rate = dv_list[3]
    managed_uniform_rate_decrease_rate = dv_list[4]
#    TAMPA_SALES_THRESHOLD_FRACTION = rdm_factor_list[15]
    
    # set other variables
    deliveries_column_index_range = range(2,9)
    deliveries_column_index_range_no_total = range(2,8)
    convert_kgal_to_MG = 1000; n_months_in_year = 12; n_days_in_year = 365
    fixed_column_index_range = [9,10,11,12,13,14]
    variable_column_index_range = [15,16,17,18,19,20]
    
    # set range for previous fiscal year's deliveries data
    previous_FY = FY - 1
    past_FY_year_data = water_delivery_sales[water_delivery_sales['Fiscal Year'] == previous_FY]
    
    # for years before FY2021 where revenue calculations and actuals already exist
    # we will overwrite them (in the case where we may be comparing vs. historical outcomes, for example)
    # collect water sales data for current FY
    uniform_rate_member_deliveries = \
        water_delivery_sales[water_delivery_sales['Fiscal Year'] == FY].iloc[:,deliveries_column_index_range]
    month_TBC_raw_deliveries = \
        water_delivery_sales['TBC Delivery - City of Tampa'].loc[water_delivery_sales['Fiscal Year'] == FY]
        
    # get financial parameters
    current_year_variable_rate = annual_budgets['Variable Uniform Rate'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    current_FY_budgeted_annual_estimate = annual_budgets['Annual Estimate'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    last_FY_member_delivery_fractions = \
        past_FY_year_data.iloc[:,deliveries_column_index_range_no_total].sum() / \
        past_FY_year_data.iloc[:,deliveries_column_index_range_no_total].sum().sum()
        
    # check that fixed costs approximately match the uniform rate
    # this step is done before actuals are calculated, so the "uniform rate"
    # here vs. what the annual estimate in the budget is for the FY
    # may not be compatible
    current_FY_budgeted_uniform_rate = \
        annual_budgets['Uniform Rate'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    current_FY_rate_stabilization_fund_balance = \
        annual_actuals['Rate Stabilization Fund (Total)'].loc[annual_actuals['Fiscal Year'] == previous_FY].values[0]
    current_FY_budgeted_rate_stabilization_transfer_in = \
        annual_budgets['Rate Stabilization Fund Transfers In'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    
    # get demand estimate for this FY
    # adjust if there were significant sales to Tampa, which can throw off
    # overall demand estimate when they are very large
    delivery_shift = 0
#    CoT_sales_fraction = \
#        past_FY_year_data['Water Delivery - City of Tampa (Uniform)'].sum() / \
#        past_FY_year_data['Water Delivery - Uniform Sales Total'].sum()
#    if CoT_sales_fraction > TAMPA_SALES_THRESHOLD_FRACTION:
#        delivery_shift = \
#            past_FY_year_data['Water Delivery - City of Tampa (Uniform)'].sum() - \
#            past_FY_year_data['Water Delivery - Uniform Sales Total'].sum() * TAMPA_SALES_THRESHOLD_FRACTION
        
    current_FY_demand_estimate_mgd = \
        (past_FY_year_data['Water Delivery - Uniform Sales Total'].sum() - delivery_shift)/n_days_in_year * \
        (1 + annual_demand_growth_rate)

    
    # do a preliminary calculation to determine if the current FY 
    # annual estimate is too large to fit the determined uniform rate
    # if that is the case, adjust the rate stabilization transfer in 
    # needed to balance it
    # note: when checking the "actual" revenues against what the AE requires,
    # the AE as calculated above does not account for additional deposits/transfers
    # so we need to include them here to isolate a comparison against
    # water sales revenues only
    current_FY_budgeted_annual_estimate_adjusted = \
        current_FY_budgeted_annual_estimate - \
        current_FY_budgeted_rate_stabilization_transfer_in
    adjusted_uniform_rate, current_FY_budgeted_annual_estimate, \
    adjusted_rate_stabilization_transfer_in = \
        estimate_UniformRate(annual_estimate = current_FY_budgeted_annual_estimate_adjusted, 
                             demand_estimate = current_FY_demand_estimate_mgd, 
                             current_uniform_rate = current_FY_budgeted_uniform_rate,
                             rs_transfer_in = current_FY_budgeted_rate_stabilization_transfer_in,
                             rs_fund_total = current_FY_rate_stabilization_fund_balance,
                             high_rate_bound = managed_uniform_rate_increase_rate,
                             low_rate_bound = managed_uniform_rate_decrease_rate,
                             MANAGE_RATE = KEEP_UNIFORM_RATE_STABLE,
                             DEBUGGING = False)

#    print(str(FY) + ' adjusted RS transfer in is ' + str(adjusted_rate_stabilization_transfer_in))
#    print(str(FY) + ' original RS transfer in is ' + str(current_FY_budgeted_rate_stabilization_transfer_in))
    current_year_projected_fixed_costs_to_recover = \
        current_FY_budgeted_annual_estimate - \
        annual_budgets['Variable Operating Expenses'].loc[annual_budgets['Fiscal Year'] == FY].values[0] - \
        (adjusted_rate_stabilization_transfer_in - current_FY_budgeted_rate_stabilization_transfer_in)
        
    # calculate revenues
    monthly_uniform_variable_sales_by_member = \
        pd.DataFrame(uniform_rate_member_deliveries.iloc[:,:-1].values * \
                     current_year_variable_rate * convert_kgal_to_MG)
    monthly_uniform_fixed_sales_by_member = \
        pd.DataFrame(np.array([[poc for poc in (last_FY_member_delivery_fractions.values * \
                                current_year_projected_fixed_costs_to_recover / \
                                n_months_in_year)] for v in range(0,len(month_TBC_raw_deliveries))]))
    monthly_tbc_sales = \
        month_TBC_raw_deliveries.values * \
        annual_budgets['TBC Rate'].loc[annual_budgets['Fiscal Year'] == FY].values * \
        convert_kgal_to_MG
        
    # append to deliveries and sales data           
    water_delivery_sales['TBC Sales - City of Tampa'].loc[water_delivery_sales['Fiscal Year'] == FY] = monthly_tbc_sales
    water_delivery_sales.loc[water_delivery_sales['Fiscal Year'] == FY, water_delivery_sales.columns[fixed_column_index_range]] = \
        monthly_uniform_fixed_sales_by_member.values
    water_delivery_sales.loc[water_delivery_sales['Fiscal Year'] == FY, water_delivery_sales.columns[variable_column_index_range]] = \
        monthly_uniform_variable_sales_by_member.values
    
    return water_delivery_sales, past_FY_year_data
    

def calculate_FYActuals(FY, current_FY_data, past_FY_year_data, 
                        annual_budgets, annual_actuals, financial_metrics, 
                        dv_list, rdm_factor_list,
                        ACTIVE_DEBUGGING,
                        actual_major_cip_expenditures_by_source_by_year,
                        actual_other_cip_expenditures_by_source_by_year,
                        reserve_balances,
                        reserve_deposits,
                        FOLLOW_CIP_SCHEDULE = True,
                        FLEXIBLE_CIP_SPENDING = True):
    # for debugging
    # dv_list = dvs; rdm_factor_list = dufs; FOLLOW_CIP_SCHEDULE = True; FLEXIBLE_CIP_SPENDING = True
    
    
    # list constants and unroll RDM factors and DVs
    rate_covenant_failure_counter = 0
    debt_covenant_failure_counter = 0
    reserve_fund_balance_failure_counter = 0
    rr_fund_balance_failure_counter = 0
    COVENANT_FAILURE = 1
    current_FY_needed_reserve_deposit = 0
    final_budget_failure_counter = 0
    FINAL_BUDGET_FAILURE = 1
#    first_debt_service_override_year = 2022
    
    # decision variables
    covenant_threshold_net_revenue_plus_fund_balance = dv_list[0]
    debt_covenant_required_ratio = dv_list[1]
    previous_FY_unaccounted_fraction_of_total_enterprise_fund = dv_list[5]
    rr_fund_floor_fraction_of_gross_revenues = dv_list[7]
    cip_fund_floor_fraction_of_gross_revenues = dv_list[8]
    energy_fund_floor_fraction_of_gross_revenues = dv_list[9]
    reserve_fund_floor_fraction_of_gross_revenues = dv_list[10]
    
    # deeply uncertain factors
    budgeted_unencumbered_fraction = rdm_factor_list[3] # historically, 2%
    fixed_op_ex_factor = rdm_factor_list[7]
    variable_op_ex_factor = rdm_factor_list[8] # fyi, budgets seem very hard to balance unless these are below 0.9
    non_sales_rev_factor = rdm_factor_list[9]
    rate_stab_transfer_factor = rdm_factor_list[10]
    rr_transfer_factor = rdm_factor_list[11]
#    other_transfer_factor = rdm_factor_list[12]
    required_cip_factor = rdm_factor_list[13]
    energy_transfer_factor = rdm_factor_list[16]
    utility_reserve_fund_deficit_reduction_fraction = rdm_factor_list[17]
    rate_stabilization_fund_deficit_reduction_fraction = 1 - utility_reserve_fund_deficit_reduction_fraction
    rate_stabilization_transfer_in_cap_fraction_of_gross_revenues = 0.03
    
    # give number of variables tracked in outputs
    fixed_column_index_range = [9,10,11,12,13,14]
    variable_column_index_range = [15,16,17,18,19,20]
    tbc_column_index_range = [22]
    water_sales_revenue_columns = [9,10,11,12,13,14,15,16,17,18,19,20,22]
    
    # get previous FY actuals for use in calculations below
    previous_FY_total_sales_revenues = \
        past_FY_year_data.iloc[:,water_sales_revenue_columns].sum().sum()
        
    previous_FY_rate_stabilization_transfer_in = \
        annual_actuals['Rate Stabilization Fund (Transfer In)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    previous_FY_rate_stabilization_deposit = \
        annual_actuals['Rate Stabilization Fund (Deposit)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    previous_FY_rate_stabilization_fund_balance = \
        annual_actuals['Rate Stabilization Fund (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    
    previous_FY_interest_income = \
        annual_actuals['Interest Income'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    previous_FY_insurance_litigation_income = \
        annual_actuals['Insurance-Litigation-Arbitrage Income'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    previous_FY_misc_income = \
        annual_actuals['Misc. Income'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    previous_FY_non_sales_revenue = \
        previous_FY_interest_income + \
        previous_FY_insurance_litigation_income + \
        previous_FY_misc_income
    
    # note about unencumbered funds - the actual unencumbered funds to be
    # counted as revenues in fiscal year X are the final funds marked 
    # as unencumbered in fiscal year X-1, so to get revenue stream for FY X-1,
    # need to grab FY X-2 actual value
    previous_FY_unencumbered_funds = \
        annual_actuals['Unencumbered Funds'].loc[annual_actuals['Fiscal Year'] == (FY-2)].values[0]
        
    previous_FY_cip_transfer_in = \
        annual_actuals['CIP Fund (Transfer In)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    previous_FY_cip_fund_balance = \
        annual_actuals['CIP Fund (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
        
    previous_FY_rr_transfer_in = \
        annual_actuals['R&R Fund (Transfer In)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    previous_FY_rr_fund_balance = \
        annual_actuals['R&R Fund (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    
    previous_FY_energy_fund_balance = \
        annual_actuals['Energy Savings Fund (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    previous_FY_energy_transfer_in = \
        annual_actuals['Energy Savings Fund (Transfer In)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    
    # collect previous year final reserve fund balances to estimate
    # enterprise fund size, if they aren't already pulled above
    previous_FY_utility_reserve_fund_balance = \
        annual_actuals['Utility Reserve Fund Balance (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    previous_FY_debt_service = \
        annual_actuals['Debt Service'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
        
    # to estimate the full enterprise fund, need to account for three remaining
    # funds that we don't explicitly model here: operations, operating reserve,
    # and interest/principal sinking fund account
    # in FY22, those balances were initially about $15M, $4.3M, and $53M resp.
    #   as a fraction of the enterprise fund, these amounts sum to 
    #   (15 + 4.3 + 53)/268 = 0.27 --> 27% of enterprise fund
    # this is set as a static decision variable, can be adjusted later
    previous_FY_enterprise_fund_total = \
        (previous_FY_rr_fund_balance + \
         previous_FY_cip_fund_balance + \
         previous_FY_energy_fund_balance + \
         previous_FY_rate_stabilization_fund_balance + \
         previous_FY_utility_reserve_fund_balance + \
         previous_FY_debt_service) / \
         (1 - previous_FY_unaccounted_fraction_of_total_enterprise_fund)
    
    # July 2020: gross revenues are calculated two different ways:
    # (1) "raw" where all income including transfers in are summed
    #       and no deposits or "netting" is done, which is used 
    #       for determining deposits into funds if they are too small
    # (2) "netted" where some costs and fund deposits are considered
    #       which is gross revenue used to calculate covenants
    previous_FY_raw_gross_revenue = \
        previous_FY_total_sales_revenues + \
        previous_FY_non_sales_revenue + \
        previous_FY_rate_stabilization_transfer_in + \
        previous_FY_unencumbered_funds + \
        previous_FY_cip_transfer_in + \
        previous_FY_rr_transfer_in + \
        previous_FY_energy_transfer_in
    
    # revenues from water supply OROP/OMS modeling for current year
    current_FY_fixed_sales_revenues = \
        current_FY_data.iloc[:,fixed_column_index_range].sum().sum()
    current_FY_variable_sales_revenues = \
        current_FY_data.iloc[:,variable_column_index_range].sum().sum()
    current_FY_tbc_sales_revenues = \
        current_FY_data.iloc[:,tbc_column_index_range].sum().sum()
    current_FY_total_sales_revenues = \
        current_FY_fixed_sales_revenues + \
        current_FY_variable_sales_revenues + \
        current_FY_tbc_sales_revenues
        
    if ACTIVE_DEBUGGING:
        print(str(FY) + ': Current Sales Revenues are ' + str(current_FY_total_sales_revenues))
        print(str(FY) + ': Past Raw Gross Revenues are ' + str(previous_FY_raw_gross_revenue))
    
    # debt service, acquisition credits,
    # assumed as equal to approved budget without perturbation
    # NOTE: recent approved budgets seem to consistently budget
    #   for rate stabilization funds to be used as revenue
    #   but no deposits are made (as expenditures in budget)
    # NOTE: these values don't change between budgeted and actuals
    #   and unencumbered carry-forward is about 2% of budget for
    #   upcoming year
    # Nov 2021: if CIP spending schedule is accounted for, 
    #   use the revenue bond CIP schedule after FY22
    #   before that, rely on planned debt service spending from
    #   approved budgets for consistency before "future" debt service
    #   begins being added in FY23. This is determined during the
    #   budget-setting process later on
    current_FY_debt_service = \
        annual_budgets['Debt Service'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
            
    current_FY_acquisition_credits = \
        annual_budgets['Acquisition Credits'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    current_FY_unencumbered_funds = \
        annual_budgets['Unencumbered Carryover Funds'].loc[annual_budgets['Fiscal Year'] == (FY)].values[0]
        
    # operational expenses and non-sales revenue assumed to be 
    # similar to approved budget with potential perturbation factor
    # rate stabilization transfer in as revenue can also vary from
    # budgeted levels, apparently widely based on expected change
    # to any budgeted operational costs
    # fixed operating expenses in this spreadsheet include
    # water quality credits ($48k/year) and R&R projects budgeted
    current_FY_fixed_operational_expenses = \
        annual_budgets['Fixed Operating Expenses'].loc[annual_budgets['Fiscal Year'] == FY].values[0] * \
        fixed_op_ex_factor
    current_FY_variable_operational_expenses = \
        annual_budgets['Variable Operating Expenses'].loc[annual_budgets['Fiscal Year'] == FY].values[0] * \
        variable_op_ex_factor
        
    # July 2020: non-sales revenues split into sub-categories of 
    # interest income, insurance-litigation, misc.
    # only interest income is budgeted, other non-sales rev will
    # be randomly generated within ranges
    current_FY_interest_income = \
        annual_budgets['Interest Income'].loc[annual_budgets['Fiscal Year'] == FY].values[0] * \
        non_sales_rev_factor
    
    # Dec 2021: interest income is an aggregate from all different sources,
    #   including different reserve funds. So, the aggregate value here is
    #   needed for higher-level budget calculations, but we can divide up that
    #   income and include it as deposits into reserve funds. Based on FY22,
    #   we can roughly break out how much of the interest include goes to
    #   each reserve fund by comparing their relative sizes. 
    #   Reserve funds to include are: 
    #       R&R, CIP, Energy, RS, Utility Reserve
    #       and the rest can be left as general interest for funds we
    #       dont account for here
    current_FY_rr_interest_income = \
        current_FY_interest_income * \
        (annual_actuals['R&R Fund (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0] / \
                        previous_FY_enterprise_fund_total)
    current_FY_cip_interest_income = \
        current_FY_interest_income * \
        (annual_actuals['CIP Fund (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0] / \
                        previous_FY_enterprise_fund_total)
    current_FY_energy_interest_income = \
        current_FY_interest_income * \
        (annual_actuals['Energy Savings Fund (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0] / \
                        previous_FY_enterprise_fund_total)
    current_FY_rs_interest_income = \
        current_FY_interest_income * \
        (annual_actuals['Rate Stabilization Fund (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0] / \
                        previous_FY_enterprise_fund_total)
    current_FY_reserve_interest_income = \
        current_FY_interest_income * \
        (annual_actuals['Utility Reserve Fund Balance (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0] / \
                        previous_FY_enterprise_fund_total)
    current_FY_remaining_unallocated_interest = \
        current_FY_interest_income * previous_FY_unaccounted_fraction_of_total_enterprise_fund
        
    # insurance income is usually less than 0.7% of previous FY gross revenues
    # misc income has a higher floor but also very small fraction
    current_FY_insurance_litigation_income = \
        previous_FY_raw_gross_revenue * \
        np.random.uniform(low = 0.0001, high = 0.007)
    current_FY_misc_income = \
        previous_FY_raw_gross_revenue * \
        np.random.uniform(low = 0.001, high = 0.01) 
    
    # sum the non-sales revenues for output    
    current_FY_non_sales_revenue = \
        current_FY_interest_income + \
        current_FY_insurance_litigation_income + \
        current_FY_misc_income
    
    # transfers in are equal to budgeted amounts (with an adjustment factor)
    # unless they need to be changed to account for differences
    # in costs and revenues (done later)
    # R&R and CIP funding may change with actuals depending on what
    # smaller projects are selected for that year, so this should
    # still have some uncertainty between budgeted and actual 
    # attached
    # NOTE: SO MAYBE DON'T HAVE DEEPLY UNCERTAIN MULTIPLIERS HERE??
    # it may be that the budgeted RS fund transfer in needs to be changed
    current_FY_budgeted_rate_stabilization_transfer_in = \
        annual_budgets['Rate Stabilization Fund Transfers In'].loc[annual_budgets['Fiscal Year'] == FY].values[0] * \
        rate_stab_transfer_factor
    current_FY_budgeted_rate_stabilization_fund_deposit = 0 # never a budgeted deposit to stabilization fund
    current_FY_rate_stabilization_final_transfer_in = \
        current_FY_budgeted_rate_stabilization_transfer_in 
        
    if FOLLOW_CIP_SCHEDULE == False:
        # follow this protocol if the model should be run without explicit
        # CIP program consideration
        current_FY_budgeted_rr_transfer_in = \
            annual_budgets['R&R Fund Transfers In'].loc[annual_budgets['Fiscal Year'] == FY].values[0] * \
            rr_transfer_factor
        current_FY_budgeted_rr_deposit = \
            annual_budgets['R&R Fund Deposit'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
        
        # never a budgeted transfer in to cip fund in the operating budget
        current_FY_budgeted_cip_transfer_in = \
            annual_budgets['CIP Fund Transfer In'].loc[annual_budgets['Fiscal Year'] == FY].values[0] 
        current_FY_budgeted_cip_deposit = \
            annual_budgets['CIP Fund Deposit'].loc[annual_budgets['Fiscal Year'] == FY].values[0]

        # there is never a budgeted energy fund transfer/deposit, so it may be adjusted below
        current_FY_budgeted_energy_transfer_in = \
            annual_budgets['Energy Savings Fund Transfer In'].loc[annual_budgets['Fiscal Year'] == FY].values[0] * \
            energy_transfer_factor
        current_FY_budgeted_energy_deposit = \
            annual_budgets['Energy Savings Fund Deposit'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
            
    else:
        # Jan 2021: account for CIP spending withdrawals from reserve funds
        # as well as the deposits into each fund and accumulated interest
        # to estimate the initial planned balances of reserves, where below
        # they are checked to make sure they are not overdrawn, etc.
        current_FY_budgeted_energy_deposit = \
            reserve_deposits['FY ' + str(FY)].loc[reserve_deposits['Fund Name'] == 'Energy Fund'].values[0]
        current_FY_budgeted_rr_deposit = \
            reserve_deposits['FY ' + str(FY)].loc[reserve_deposits['Fund Name'] == 'Renewal and Replacement Fund'].values[0]
        current_FY_budgeted_cip_deposit = \
            reserve_deposits['FY ' + str(FY)].loc[reserve_deposits['Fund Name'] == 'Capital Improvement Fund'].values[0]
    
        # for transfers in, these are likely not from the operating budget 
        # data I've pulled in, but should still be accounted for to balance
        # the individual fund sizes
        current_FY_budgeted_energy_transfer_in = \
            actual_other_cip_expenditures_by_source_by_year['Energy Fund'].loc[actual_other_cip_expenditures_by_source_by_year['Fiscal Year'] == FY].values[0]
        current_FY_budgeted_rr_transfer_in = \
            actual_other_cip_expenditures_by_source_by_year['Renewal and Replacement Fund'].loc[actual_other_cip_expenditures_by_source_by_year['Fiscal Year'] == FY].values[0]
        current_FY_budgeted_cip_transfer_in = \
            actual_other_cip_expenditures_by_source_by_year['Capital Improvement Fund'].loc[actual_other_cip_expenditures_by_source_by_year['Fiscal Year'] == FY].values[0]            
            
    ###  additional reserve requirements must be met --------------
    # (a) R&R fund must be at least 5% of previous FY gross rev
    #       Jan 2022: THIS IS NOW A DECISION VARIABLE THAT CAN 
    #       BE CHANGED IF WE WANT TO
    # (b) Reserve Fund (Fund Balance) must be >10% gross rev
    #       AND Fund Balance + Net Revenue (gross rev - op ex)
    #       MUST BE >125% of required debt service
    # (c) Net Revenues must cover 100% of the sum of debt service,
    #       required R&R deposits, and required Reserve deposits
    
    if ACTIVE_DEBUGGING:
        print(str(FY) + ': GR: Budgeted R&R Deposit (Check 1) is ' + str(current_FY_budgeted_rr_deposit))
  
    # check condition (a)
    # R&R fund budgeted transfer in from fund always covers 100% of planned
    # projects. There is also a budgeted deposit - if the net change in fund
    # size violates the fund size rule, reduce the transfer in
    current_FY_rr_net_deposit = \
        current_FY_budgeted_rr_deposit - current_FY_budgeted_rr_transfer_in + current_FY_rr_interest_income
    if ((previous_FY_raw_gross_revenue * rr_fund_floor_fraction_of_gross_revenues) > previous_FY_rr_fund_balance + current_FY_rr_net_deposit) and (current_FY_rr_net_deposit > 0):
        # reduce budgeted transfer in if it would deplete the fund
        # so that the transfer in and deposit are equal (no net fund change)
        # but prevent it from going negative
        current_FY_budgeted_rr_transfer_in = \
            np.max([current_FY_budgeted_rr_transfer_in - current_FY_rr_net_deposit, 0.0])
                
        # if there is remaining need, increase the deposit
        current_FY_rr_net_deposit = \
            current_FY_budgeted_rr_deposit - current_FY_budgeted_rr_transfer_in
        if (previous_FY_raw_gross_revenue * rr_fund_floor_fraction_of_gross_revenues) > previous_FY_rr_fund_balance + current_FY_rr_net_deposit:
            current_FY_budgeted_rr_deposit += current_FY_rr_net_deposit
            
    
    if ACTIVE_DEBUGGING:
        print(str(FY) + ': GR: Budgeted R&R Deposit (Check 2) is ' + str(current_FY_budgeted_rr_deposit))
    
    current_FY_rr_transfer_in = current_FY_budgeted_rr_transfer_in
    if ((previous_FY_raw_gross_revenue * rr_fund_floor_fraction_of_gross_revenues) > previous_FY_rr_fund_balance):
        # if the current fund level is already in violation, cancel transfer in
        # and ensure that planned deposit is at least large enough to compensate
        # only count a "failure" if reducing the budgeted transfer in
        # from the fund cannot satisfy this condition
        current_FY_rr_transfer_in = 0
        rr_fund_balance_failure_counter += COVENANT_FAILURE
        
        # figure out what the necessary deposit is, and ensure the budgeted 
        # deposit is at least that large
        current_FY_budgeted_rr_deposit = \
            previous_FY_raw_gross_revenue * rr_fund_floor_fraction_of_gross_revenues - previous_FY_rr_fund_balance
    elif ((previous_FY_raw_gross_revenue * rr_fund_floor_fraction_of_gross_revenues) > previous_FY_rr_fund_balance + current_FY_rr_net_deposit):
        # if there is already a net transfer out of the fund (net deposit is negative)
        # and this violates the rule, reduce the transfer in 
        # (add the negative difference)
        current_FY_rr_transfer_in += current_FY_rr_net_deposit

    if ACTIVE_DEBUGGING:
        print(str(FY) + ': GR: Unencumbered is ' + str(current_FY_unencumbered_funds))
        print(str(FY) + ': GR: RS Transfer In (Check 1) is ' + str(current_FY_rate_stabilization_final_transfer_in))
        print(str(FY) + ': GR: R&R Transfer In is ' + str(current_FY_rr_transfer_in))
        print(str(FY) + ': GR: Non-Sales Rev is ' + str(current_FY_non_sales_revenue))
        print(str(FY) + ': GR: RS Deposit is ' + str(current_FY_budgeted_rate_stabilization_fund_deposit))
        print(str(FY) + ': GR: Budgeted R&R Deposit (Check 3) is ' + str(current_FY_budgeted_rr_deposit))
        
    # check conditions under (b) 
    # there is never a budgeted deposit to the reserve fund, so don't need to
    # repeat all the trouble above like with the R&R Fund
    if previous_FY_utility_reserve_fund_balance < (previous_FY_raw_gross_revenue * reserve_fund_floor_fraction_of_gross_revenues):
        reserve_fund_balance_failure_counter += COVENANT_FAILURE
        current_FY_needed_reserve_deposit = \
            previous_FY_raw_gross_revenue * reserve_fund_floor_fraction_of_gross_revenues - previous_FY_utility_reserve_fund_balance
            
    # Dec 2021: if we are following the CIP schedule of reserve fund usage
    # then grab the budgeted values above. Do this for CIP, Energy funds.
    if FOLLOW_CIP_SCHEDULE:
        current_FY_cip_deposit = \
            current_FY_budgeted_cip_deposit
        current_FY_cip_transfer_in = \
            current_FY_budgeted_cip_transfer_in
        
        current_FY_energy_transfer_in = \
            current_FY_budgeted_energy_transfer_in
            
    else:
        # there doesn't seem to be a codified mechanism to decide
        # about required deposits for CIP Fund except to meet next
        # FY's budgeted project costs, so will generate random 
        # value here within bounds seen in past budgets
        # From FY 2013-2019, CIP required deposits were between
        #   1-3% of actual previous fy raw gross revenues
        #   use the 2-3% range because that seems to match better 
        #   with last 6 FYs (lowest value was FY 2013 outlier)
        # also include a deeply uncertain factor to be used if wanted
        current_FY_cip_deposit = \
            np.random.uniform(low = 0.02, high = 0.03) * \
            required_cip_factor * previous_FY_raw_gross_revenue
    
        # similarly, apply a random factor to set CIP fund transfer in
        # based on past FY actuals, transfer in is between 0.2-2%
        # of past fy raw gross revenues
        current_FY_cip_transfer_in = \
            np.random.uniform(low = 0.002, high = 0.02) * \
            required_cip_factor * previous_FY_raw_gross_revenue
            
        # repeat for energy fund - it has existed since 2014, and
        # based on past FY actuals, transfer in is between 0-0.15%
        # of past fy raw gross revenues
        current_FY_energy_transfer_in = \
            np.random.uniform(low = 0, high = 0.0015) * \
            energy_transfer_factor * previous_FY_raw_gross_revenue
        
    # check condition (c)
    # here, I assume that any failure to meet the above covenants
    # or fund requirements will try to be addressed through 
    # pulling from the rate stabilization fund
    # calculate "netted" gross revenues for below calculations
    # netted is only sales + non-sales + unencumbered + RS fund transfer in - RS fund deposit
    current_FY_netted_gross_revenue = \
        current_FY_total_sales_revenues + \
        current_FY_unencumbered_funds + \
        current_FY_rate_stabilization_final_transfer_in + \
        current_FY_non_sales_revenue - \
        current_FY_acquisition_credits - \
        current_FY_budgeted_rate_stabilization_fund_deposit
    current_FY_netted_net_revenue = \
        current_FY_netted_gross_revenue - \
        current_FY_fixed_operational_expenses - \
        current_FY_variable_operational_expenses 
    
    if calculate_DebtCoverageRatio(current_FY_netted_net_revenue,
                                   current_FY_debt_service,
                                   current_FY_cip_deposit + current_FY_budgeted_rr_deposit) < \
            debt_covenant_required_ratio:
        debt_covenant_failure_counter += COVENANT_FAILURE
        current_FY_rate_stabilization_final_transfer_in += \
            current_FY_debt_service + \
            current_FY_cip_deposit + \
            current_FY_budgeted_rr_deposit - \
            current_FY_netted_net_revenue
 
    if ACTIVE_DEBUGGING:
        print(str(FY) + ': GR: RS Transfer In (Check 2) is ' + str(current_FY_rate_stabilization_final_transfer_in))           
            
    # this is not the "true" debt coverage test (done below) but 
    # "calibrates" whether required transfers in from different 
    # funds is necessary/different than budgeted. we can track
    # when required transfers are made/how much they are and
    # what the final "leftover" must be covered from other sources
    if calculate_RateCoverageRatio(current_FY_netted_net_revenue,
                                   current_FY_debt_service,
                                   previous_FY_utility_reserve_fund_balance) < \
            covenant_threshold_net_revenue_plus_fund_balance:
        rate_covenant_failure_counter += COVENANT_FAILURE
        adjustment = \
            (covenant_threshold_net_revenue_plus_fund_balance * \
             (current_FY_debt_service + current_FY_cip_deposit + current_FY_budgeted_rr_deposit)) - \
            current_FY_netted_net_revenue - previous_FY_utility_reserve_fund_balance
        current_FY_needed_reserve_deposit = \
            np.max([current_FY_needed_reserve_deposit, adjustment])
        current_FY_rate_stabilization_final_transfer_in = \
            np.max([current_FY_rate_stabilization_final_transfer_in,
                    adjustment])
    
    if ACTIVE_DEBUGGING:
        print(str(FY) + ': GR: RS Transfer In (Check 3) is ' + str(current_FY_rate_stabilization_final_transfer_in))         
    
    # annual transfer in from rate stabilization account is capped
    # at the smallest of either:
    # (a) 3% of budgeted revenue for previous FY
    # (b) unencumberance carried forward from previous FY
    # (c) amount deposited in stabilization fund in previous FY
    previous_FY_budgeted_raw_gross_revenue = \
        annual_budgets['Gross Revenues'].loc[annual_budgets['Fiscal Year'] == (FY-1)].values[0]
    current_FY_rate_stabilization_transfer_cap = \
        np.min([previous_FY_budgeted_raw_gross_revenue * rate_stabilization_transfer_in_cap_fraction_of_gross_revenues, # (a)
                current_FY_unencumbered_funds, # (b)
                previous_FY_rate_stabilization_deposit, # (c)
                previous_FY_rate_stabilization_fund_balance]) # can't make fund go negative
    
    # if it occurs that the maximum transfer in from the rate 
    # stabilization fund cannot balance the budget, assume other 
    # funds can be drawn from to meet the difference
    potential_other_funds_transferred_in = 0
    if current_FY_rate_stabilization_final_transfer_in > \
            current_FY_rate_stabilization_transfer_cap:
        potential_other_funds_transferred_in += \
            current_FY_rate_stabilization_final_transfer_in - \
            current_FY_rate_stabilization_transfer_cap
        current_FY_rate_stabilization_final_transfer_in = \
            current_FY_rate_stabilization_transfer_cap
            
    if ACTIVE_DEBUGGING:
        print(str(FY) + ': GR: RS Transfer In (Check 4) is ' + str(current_FY_rate_stabilization_final_transfer_in))    
        print(str(FY) + ': Additional Transfer In Potential is ' + str(potential_other_funds_transferred_in))
               
    ### take record of current FY performance ---------------------
    # first, re-calculate "actual" current gross revenues and
    # net revenues, total costs including required deposits,
    # to get remaining actual budget surplus or deficit
    current_FY_netted_gross_revenue = \
        current_FY_total_sales_revenues + \
        current_FY_unencumbered_funds + \
        current_FY_rate_stabilization_final_transfer_in + \
        current_FY_non_sales_revenue - \
        current_FY_acquisition_credits - \
        current_FY_budgeted_rate_stabilization_fund_deposit + \
        current_FY_cip_transfer_in + \
        current_FY_rr_transfer_in + \
        current_FY_energy_transfer_in
    current_FY_netted_net_revenue = \
        current_FY_netted_gross_revenue - \
        current_FY_fixed_operational_expenses - \
        current_FY_variable_operational_expenses 
    current_FY_expenses_before_optional_deposits = \
        current_FY_debt_service + \
        current_FY_cip_deposit + \
        current_FY_budgeted_rr_deposit + \
        current_FY_budgeted_energy_deposit
        
    if ACTIVE_DEBUGGING:   
        print(str(FY) + ': Expenses before deposits is ' + str(current_FY_expenses_before_optional_deposits))
        print(str(FY) + ': Net gross revenue is ' + str(current_FY_netted_gross_revenue))
        print(str(FY) + ': Netted net revenue is ' + str(current_FY_netted_net_revenue))

    # next, determine how remaining unencumbered funds 
    # are split among reserve funds or preserved as unencumbered
    current_FY_budget_surplus = \
        current_FY_netted_net_revenue - \
        current_FY_expenses_before_optional_deposits
    
    # if there is a deficit, take the money that was meant to be transferred in
    # from rate stabilization but capped and mark any of it that must be
    # used to balance the budget as "required"    
    required_other_funds_transferred_in = 0
    if current_FY_budget_surplus < 0:
        required_other_funds_transferred_in = \
            np.min([potential_other_funds_transferred_in, -current_FY_budget_surplus])
    
    if ACTIVE_DEBUGGING:   
        print(str(FY) + ': Additional Transfer In Required is ' + str(required_other_funds_transferred_in))
    
    # if there is a budget deficit, pull from reserve fund
    # also check rate stabilization fund flows and take percentage
    # of surplus to be unencumbered funds (based on FY 18,19 
    # actuals, about 16-17% of surplus budget before any 
    # non-required deposits) - budgeted as 2.5% of prior year
    # water revenues
    # Jan 2022: add unallocated interest to utility reserve fund
    current_FY_final_unencumbered_funds = 0
    current_FY_final_reserve_fund_balance = \
        previous_FY_utility_reserve_fund_balance + current_FY_reserve_interest_income + \
        current_FY_remaining_unallocated_interest 
    current_FY_rate_stabilization_fund_deposit = \
        current_FY_budgeted_rate_stabilization_fund_deposit    
        
    if ACTIVE_DEBUGGING:
        print(str(FY) + ': Initial Budget Surplus is ' + str(current_FY_budget_surplus))
        
    # July 2020: any required transfers from 'other' funds
    # to cover budget shortfalls above will be pulled from 
    # reserve fund balance, however this can zero out the reserve fund
    # and cause it to go negative, so if there is a budget surplus
    # afterward, it can be pushed into the reserve fund to replenish
    # if there is a deficit in the budget, use the rate stabilization and 
    # utility reserve funds as primary sources by which to address the deficit
    if current_FY_budget_surplus < 0:
        # determine how much to pull from utility reserve to handle deficit
        # if fund is already emptied, account for this (the min-max statement)
        reserve_fund_adjustment = np.min([-current_FY_budget_surplus * utility_reserve_fund_deficit_reduction_fraction, 
                                          np.max([0.0, current_FY_final_reserve_fund_balance])])    
        current_FY_final_reserve_fund_balance -= reserve_fund_adjustment
        current_FY_budget_surplus += reserve_fund_adjustment
        
        # because the rate stabilization fund has budgeted transfers and deposits,
        # first reduce the planned withdrawals from the fund for the operating
        # budget (can't reduce deposit because planned deposits are always zero)
        rs_fund_adjustment = np.min([-current_FY_budget_surplus * rate_stabilization_fund_deficit_reduction_fraction, 
                                     np.max([0.0, previous_FY_rate_stabilization_fund_balance])])        
        current_FY_rate_stabilization_final_transfer_in -= np.min([current_FY_rate_stabilization_final_transfer_in, 
                                                                   rs_fund_adjustment])
        current_FY_budget_surplus += np.min([current_FY_rate_stabilization_final_transfer_in, 
                                             rs_fund_adjustment])
        
        # if there is still deficit left, pull from R&R fund,
        # increase transfer in (increase operating revenues for this FY)
        # and then reduce fund balance in the final budget calculations below
        if current_FY_budget_surplus < 0:
            # check that there is an ability to reduce the R&R fund beyond
            # currently-planned transfers into the operating budget
            # if not possible while balancing the fund, move on to next fund
            potential_rr_transfer_in_increase_margin = \
                previous_FY_rr_fund_balance - current_FY_netted_gross_revenue * rr_fund_floor_fraction_of_gross_revenues
            if potential_rr_transfer_in_increase_margin >= 0:
                current_FY_rr_transfer_in += np.min([-current_FY_budget_surplus, potential_rr_transfer_in_increase_margin])
                current_FY_budget_surplus += np.min([-current_FY_budget_surplus, potential_rr_transfer_in_increase_margin])
                
        # ...then from CIP fund   
        if current_FY_budget_surplus < 0:
            # check that there is an ability to reduce the CIP fund beyond
            # currently-planned transfers into the operating budget
            potential_cip_transfer_in_increase_margin = \
                previous_FY_cip_fund_balance - current_FY_netted_gross_revenue * cip_fund_floor_fraction_of_gross_revenues
            if potential_cip_transfer_in_increase_margin >= 0:
                current_FY_cip_transfer_in += np.min([-current_FY_budget_surplus, potential_cip_transfer_in_increase_margin])
                current_FY_budget_surplus  += np.min([-current_FY_budget_surplus, potential_cip_transfer_in_increase_margin])
           
        # if there isn't any budget margin left, can't push leftovers into the
        # reserve fund, so zero out this quantity
        current_FY_needed_reserve_deposit_realized = 0
    else:
        # if surplus is large enough, increase fund balance
        # if not, increase it as much as possible
        if current_FY_budget_surplus > current_FY_needed_reserve_deposit:
            current_FY_final_reserve_fund_balance += current_FY_needed_reserve_deposit
            current_FY_budget_surplus -= current_FY_needed_reserve_deposit
            current_FY_needed_reserve_deposit_realized = current_FY_needed_reserve_deposit
        else:
            current_FY_final_reserve_fund_balance += current_FY_budget_surplus
            current_FY_budget_surplus = 0
            current_FY_needed_reserve_deposit_realized = current_FY_budget_surplus
        
        # mark some funds unencumbered
        # THIS IS GOING NEGATIVE, WHY? BECAUSE UNIFORM RATE 
        # BECOMES NEGATIVE WHEN ANNUAL ESTIMATE GOES NEGATIVE
        # BECAUSE RATE STABILIZATION FUND HAS GROWN TOO LARGE...
        current_FY_final_unencumbered_funds = \
            np.min([current_FY_total_sales_revenues * \
                        budgeted_unencumbered_fraction, 
                    current_FY_budget_surplus])
        current_FY_budget_surplus -= \
            current_FY_final_unencumbered_funds
            
        # any remaining funds go into rate stabilization
        # and reserve fund, priority to restore the reserve fund
        # if it was earlier depleted
        if current_FY_final_reserve_fund_balance < (previous_FY_raw_gross_revenue * reserve_fund_floor_fraction_of_gross_revenues):
            adjustment = \
                np.min([current_FY_budget_surplus, 
                        (previous_FY_raw_gross_revenue * reserve_fund_floor_fraction_of_gross_revenues) - current_FY_final_reserve_fund_balance])
            current_FY_final_reserve_fund_balance += adjustment
            current_FY_budget_surplus -= adjustment
            
        # if the reserve fund is still low, move from rate stabilization
        if current_FY_final_reserve_fund_balance < (previous_FY_raw_gross_revenue * reserve_fund_floor_fraction_of_gross_revenues):
            adjustment = \
                np.min([-current_FY_rate_stabilization_final_transfer_in + \
                        previous_FY_rate_stabilization_fund_balance, 
                        (previous_FY_raw_gross_revenue * reserve_fund_floor_fraction_of_gross_revenues) - current_FY_final_reserve_fund_balance])
            current_FY_final_reserve_fund_balance += adjustment
            previous_FY_rate_stabilization_fund_balance -= adjustment
        
        # remaining surplus going to rate stabilization
        current_FY_rate_stabilization_fund_deposit += \
            current_FY_budget_surplus
            
    if ACTIVE_DEBUGGING:        
        print(str(FY) + ': Final Budget Surplus is ' + str(current_FY_budget_surplus))
        print(str(FY) + ': Final Unencumbered is ' + str(current_FY_final_unencumbered_funds))
        print(str(FY) + ': Surplus Deposit in Rate Stabilization is ' + str(current_FY_rate_stabilization_fund_deposit))
    
#    print(str(FY) + ': Initial Budget Surplus is ' + str(current_FY_budget_surplus))
#    print(str(FY) + ': Surplus Deposit in Rate Stabilization is ' + str(current_FY_rate_stabilization_fund_deposit))
    
    # Jan 2022: if CIP planning is flexible, the required additional transfers
    #   can instead be diverted from CIP funding sources before the reserve 
    #   fund is tapped
    print(str(FY) + ': GR: Budgeted R&R Deposit (Check FIRST) is ' + str(current_FY_budgeted_rr_deposit))
    
    current_FY_rr_deposit = current_FY_budgeted_rr_deposit
    current_FY_energy_deposit = current_FY_budgeted_energy_deposit
    if FLEXIBLE_CIP_SPENDING:
        # without any other assumptions, assume the other funds that need to
        # be covered should be proportionally covered by reducing deposits into
        # CIP, R&R, and Energy Funds. Cap the reductions at the amount of planned
        # deposits into funds from operating budget
        #print("Spending from Energy, R&R, and CIP funds is being adjusted as necessary")
        
        # DIVIDE BY ALL BUDGETED OR ALL ACTUALS
        current_FY_cip_deposit -= np.max([required_other_funds_transferred_in * \
            (current_FY_budgeted_cip_deposit / \
             (current_FY_budgeted_cip_deposit + current_FY_budgeted_rr_deposit + current_FY_budgeted_energy_deposit)),
             current_FY_cip_deposit])
        current_FY_rr_deposit -= np.max([required_other_funds_transferred_in * \
            (current_FY_budgeted_rr_deposit / \
             (current_FY_budgeted_cip_deposit + current_FY_budgeted_rr_deposit + current_FY_budgeted_energy_deposit)),
             current_FY_rr_deposit])
        current_FY_energy_deposit -= np.max([required_other_funds_transferred_in * \
            (current_FY_budgeted_energy_deposit / \
             (current_FY_budgeted_cip_deposit + current_FY_budgeted_rr_deposit + current_FY_budgeted_energy_deposit)),
             current_FY_energy_deposit])
            
        required_other_funds_transferred_in -= np.max([(current_FY_budgeted_cip_deposit + current_FY_budgeted_rr_deposit + current_FY_budgeted_energy_deposit),
                                                       required_other_funds_transferred_in])

    current_FY_final_reserve_fund_balance -= required_other_funds_transferred_in
    print(str(FY) + ': GR: Budgeted R&R Deposit (Check MIDDLE) is ' + str(current_FY_rr_deposit))
    
    # Jan 2022: re-balance CIP/R&R/Energy funds to ensure they don't drop low
    #   if too much CIP investment is planned and not large enough deposits are
    #   made to balance the funds. If this is happening, increase deposits to 
    #   those funds with either rate stabilization or utility reserve funds
    cip_deficit = 0; rr_deficit = 0; energy_deficit = 0
    
    # check CIP fund flows first
    current_FY_cip_fund_balance = \
        previous_FY_cip_fund_balance - \
        current_FY_cip_transfer_in + \
        current_FY_cip_deposit + \
        current_FY_cip_interest_income
    if current_FY_cip_fund_balance < np.max([0.0, current_FY_netted_gross_revenue * cip_fund_floor_fraction_of_gross_revenues]):
        print('Must rebalance CIP Fund in FY' + str(FY))
        cip_deficit = np.max([0.0, current_FY_netted_gross_revenue * cip_fund_floor_fraction_of_gross_revenues]) - current_FY_cip_fund_balance
        current_FY_cip_deposit += cip_deficit
    
    # check R&R fund flows next
    current_FY_rr_fund_balance = \
        previous_FY_rr_fund_balance - \
        current_FY_rr_transfer_in + \
        current_FY_rr_deposit + \
        current_FY_rr_interest_income
    if current_FY_rr_fund_balance < np.max([0.0, current_FY_netted_gross_revenue * rr_fund_floor_fraction_of_gross_revenues]):
        print('Must rebalance R&R Fund in FY' + str(FY))
        rr_deficit = np.max([0.0, current_FY_netted_gross_revenue * rr_fund_floor_fraction_of_gross_revenues]) - current_FY_rr_fund_balance
        current_FY_rr_deposit += rr_deficit
    
    # check Energy fund flows last
    current_FY_energy_fund_balance = \
        previous_FY_energy_fund_balance - \
        current_FY_energy_transfer_in + \
        current_FY_energy_deposit + \
        current_FY_energy_interest_income
    if current_FY_energy_fund_balance < np.max([0.0, current_FY_netted_gross_revenue * energy_fund_floor_fraction_of_gross_revenues]):
        print('Must rebalance Energy Fund in FY' + str(FY))
        energy_deficit = np.max([0.0, current_FY_netted_gross_revenue * energy_fund_floor_fraction_of_gross_revenues]) - current_FY_energy_fund_balance
        current_FY_energy_deposit += energy_deficit
        
    # handle the deficits by rebalancing with rate stabilization or reserve
    total_deficit = cip_deficit + rr_deficit + energy_deficit
    if total_deficit > 0:
        # start with rate stabilization fund, increase transfer in or decrease deposit
        deficit_reduction_step1 = np.min([total_deficit, 
                                          previous_FY_rate_stabilization_fund_balance,
                                          current_FY_rate_stabilization_transfer_cap - current_FY_rate_stabilization_final_transfer_in])
        deficit_reduction_step1 = np.max([deficit_reduction_step1, 0.0]) # negativity constraint     
        current_FY_rate_stabilization_final_transfer_in += deficit_reduction_step1
        total_deficit -= deficit_reduction_step1
        
        deficit_reduction_step2 = np.min([total_deficit, 
                                          current_FY_rate_stabilization_fund_deposit])
        deficit_reduction_step2 = np.max([deficit_reduction_step2, 0.0]) # negativity constraint
        current_FY_rate_stabilization_fund_deposit -= deficit_reduction_step2
        total_deficit -= deficit_reduction_step2
        
        # repeat for utility reserve
        deficit_reduction_step3 = np.min([total_deficit, 
                                          current_FY_final_reserve_fund_balance,
                                          current_FY_final_reserve_fund_balance - current_FY_final_reserve_fund_balance * reserve_fund_floor_fraction_of_gross_revenues])
        deficit_reduction_step3 = np.max([deficit_reduction_step3, 0.0]) # negativity constraint        
        current_FY_final_reserve_fund_balance -= deficit_reduction_step3
        total_deficit -= deficit_reduction_step3
          
    # after all these checks, rate stabilization and reserve funds can end up
    # negative. in those circumstances, update the total deficit to include
    # the negative balances and zero the funds out.
    # set rate stabilization balance
    # unencumbered funds deposited here at end of FY
    current_FY_rate_stabilization_fund_balance = \
        -current_FY_rate_stabilization_final_transfer_in + \
        current_FY_rate_stabilization_fund_deposit + \
        previous_FY_rate_stabilization_fund_balance + \
        current_FY_final_unencumbered_funds - \
        current_FY_unencumbered_funds + \
        current_FY_rs_interest_income
    if current_FY_rate_stabilization_fund_balance < 0:
        print(str(FY) + ': Failure of the Rate Stabilization Fund')
        total_deficit -= current_FY_rate_stabilization_fund_balance
        current_FY_rate_stabilization_fund_balance = 0
        
    if current_FY_final_reserve_fund_balance < 0:
        print(str(FY) + ': Failure of the Utility Reserve Fund')
        total_deficit -= current_FY_final_reserve_fund_balance
        current_FY_final_reserve_fund_balance = 0

    # if the deficit remains, mark a failure here and record how much remains
    if total_deficit > 0:
        final_budget_failure_counter += FINAL_BUDGET_FAILURE
        
    if ACTIVE_DEBUGGING:
        print(str(FY) + ': GR: R&R Deposit (Check 4) is ' + str(current_FY_rr_deposit))
    
    ### -----------------------------------------------------------------------
    # finally, take the final budget calculations of gross/net revenues
    # "raw" values and "netted" values
    current_FY_final_netted_gross_revenue = \
        current_FY_total_sales_revenues + \
        current_FY_unencumbered_funds + \
        current_FY_rate_stabilization_final_transfer_in + \
        current_FY_non_sales_revenue - \
        current_FY_acquisition_credits - \
        current_FY_rate_stabilization_fund_deposit - \
        current_FY_needed_reserve_deposit_realized
    current_FY_final_netted_net_revenue = \
        current_FY_final_netted_gross_revenue - \
        current_FY_fixed_operational_expenses - \
        current_FY_variable_operational_expenses

    current_FY_final_raw_gross_revenue = \
        current_FY_total_sales_revenues + \
        current_FY_non_sales_revenue + \
        current_FY_rate_stabilization_final_transfer_in + \
        current_FY_unencumbered_funds + \
        current_FY_cip_transfer_in + \
        current_FY_rr_transfer_in
    
    # check R&R fund flows
    current_FY_final_rr_fund_balance = \
        previous_FY_rr_fund_balance - \
        current_FY_rr_transfer_in + \
        current_FY_rr_deposit + \
        current_FY_rr_interest_income
    
    # check CIP fund flows
    current_FY_final_cip_fund_balance = \
        previous_FY_cip_fund_balance - \
        current_FY_cip_transfer_in + \
        current_FY_cip_deposit + \
        current_FY_cip_interest_income
        
    # check Energy fund flows
    current_FY_final_energy_fund_balance = \
        previous_FY_energy_fund_balance - \
        current_FY_energy_transfer_in + \
        current_FY_energy_deposit + \
        current_FY_energy_interest_income
        
    # finally, record outcomes
    financial_metrics.loc[financial_metrics['Fiscal Year'] == FY] = \
        pd.DataFrame([FY,
                        calculate_DebtCoverageRatio(
                                current_FY_final_netted_net_revenue, 
                                current_FY_debt_service, 
                                current_FY_cip_deposit + current_FY_budgeted_rr_deposit),  
                        calculate_RateCoverageRatio(
                                current_FY_final_netted_net_revenue, 
                                current_FY_debt_service,
                                previous_FY_utility_reserve_fund_balance),
                        debt_covenant_failure_counter, 
                        rate_covenant_failure_counter,
                        reserve_fund_balance_failure_counter,
                        rr_fund_balance_failure_counter,
                        current_FY_rate_stabilization_transfer_cap,
                        current_FY_rate_stabilization_final_transfer_in,
                        current_FY_budgeted_rr_deposit,
                        current_FY_needed_reserve_deposit,
                        required_other_funds_transferred_in, 
                        current_FY_final_netted_net_revenue,
                        current_FY_fixed_sales_revenues,
                        current_FY_variable_sales_revenues,
                        final_budget_failure_counter,
                        total_deficit]).transpose().values

    # record "actuals" of completed FY in historical record
    # to match columns of annual_budget
    # reminder, net rate stabilization transfer includes 
    #   unencumbered funds
    current_FY_uniform_rate = annual_budgets['Uniform Rate'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    current_FY_variable_rate = annual_budgets['Variable Uniform Rate'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    current_FY_tbc_rate = annual_budgets['TBC Rate'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    annual_actuals.loc[annual_actuals['Fiscal Year'] == FY] = \
        pd.DataFrame([FY,
                      current_FY_uniform_rate,
                      current_FY_variable_rate,
                      current_FY_tbc_rate,
                      current_FY_interest_income,
                      current_FY_final_raw_gross_revenue,
                      current_FY_debt_service,
                      current_FY_acquisition_credits,
                      current_FY_fixed_operational_expenses,
                      current_FY_variable_operational_expenses,
                      current_FY_final_reserve_fund_balance,
                      current_FY_final_rr_fund_balance,
                      current_FY_rr_deposit,
                      current_FY_rr_transfer_in,
                      current_FY_rate_stabilization_fund_deposit,
                      current_FY_rate_stabilization_fund_balance,
                      current_FY_rate_stabilization_final_transfer_in,
                      current_FY_final_unencumbered_funds,
                      current_FY_final_cip_fund_balance,
                      current_FY_cip_deposit,
                      current_FY_cip_transfer_in,
                      current_FY_misc_income,
                      current_FY_insurance_litigation_income,
                      current_FY_total_sales_revenues,
                      current_FY_final_energy_fund_balance,
                      current_FY_energy_deposit,
                      current_FY_energy_transfer_in]).transpose().values
                    
    print(str(FY) + ': GR: Budgeted R&R Deposit (Check FINAL) is ' + str(current_FY_rr_deposit))

    return annual_actuals, annual_budgets, financial_metrics
    

def calculate_NextFYBudget(FY, first_modeled_fy, current_FY_data, past_FY_year_data, 
                            annual_budgets, annual_actuals, financial_metrics, 
                            existing_issued_debt, new_projects_to_finance, potential_projects, existing_debt_targets,
                            accumulated_new_operational_fixed_costs_from_infra,
                            accumulated_new_operational_variable_costs_from_infra,
                            dv_list, 
                            rdm_factor_list,
                            ACTIVE_DEBUGGING,
                            actual_major_cip_expenditures_by_source_by_year,
                            actual_other_cip_expenditures_by_source_by_year,
                            reserve_balances,
                            reserve_deposits,
                            FOLLOW_CIP_SCHEDULE = True,
                            FLEXIBLE_CIP_SPENDING = True):
    # for debugging: dv_list = dvs; rdm_factor_list = dufs; FOLLOW_CIP_SCHEDULE = True; FLEXIBLE_CIP_SPENDING = True
    
    # set constants and variables as necessary
    convert_kgal_to_MG = 1000
    n_days_in_year = 365
    
    # decision variables
    KEEP_UNIFORM_RATE_STABLE = bool(np.round(dv_list[2])) # if range is [0,1], will round to either bound for T/F value
    managed_uniform_rate_increase_rate = dv_list[3]
    managed_uniform_rate_decrease_rate = dv_list[4]
    debt_service_cap_fraction_of_gross_revenues = dv_list[6]
    reserve_fund_floor_fraction_of_gross_revenues = dv_list[10]
    
    # deeply uncertain factors
    rate_stabilization_minimum_ratio = rdm_factor_list[0]
#    rate_stabilization_maximum_ratio = rdm_factor_list[1]
    fraction_variable_operational_cost = rdm_factor_list[2]
    budgeted_unencumbered_fraction = rdm_factor_list[3]
    annual_budget_fixed_operating_cost_inflation_rate = rdm_factor_list[4]
    annual_demand_growth_rate = rdm_factor_list[5]
    next_FY_budgeted_tampa_tbc_delivery = rdm_factor_list[6] # volume in MG/fiscal year
    annual_budget_variable_operating_cost_inflation_rate = rdm_factor_list[14]
#    TAMPA_SALES_THRESHOLD_FRACTION = rdm_factor_list[15]
    
    current_FY_final_reserve_fund_balance = \
        annual_actuals['Utility Reserve Fund Balance (Total)'].loc[annual_actuals['Fiscal Year'] == FY].values[0]
        
    # check if debt for a new project has been issued
    # add to existing debt based on supply model triggered projects
    # Jan 2022: override this with CIP schedule if desired
    existing_issued_debt = add_NewDebt(FY,
                                       existing_issued_debt, 
                                       potential_projects,
                                       new_projects_to_finance,
                                       FOLLOW_CIP_SCHEDULE)
    
    # set debt service target (for now, predetermined cap?)
    # and adjust existing debt based on payments on new debt
    # only do this if simulating future, otherwise no need
    if FY >= first_modeled_fy:
        current_FY_final_net_revenue = financial_metrics['Final Net Revenues'].loc[financial_metrics['Fiscal Year'] == FY].values[0]
        next_FY_budgeted_debt_service, existing_issued_debt = \
            set_BudgetedDebtService(existing_issued_debt, 
                                    current_FY_final_net_revenue, 
                                    existing_debt_targets, 
                                    actual_major_cip_expenditures_by_source_by_year,
                                    actual_other_cip_expenditures_by_source_by_year,
                                    FY+1, first_modeled_fy-1,
                                    FOLLOW_CIP_SCHEDULE_MAJOR_PROJECTS = FOLLOW_CIP_SCHEDULE)
    else:
        next_FY_budgeted_debt_service = \
            annual_budgets['Debt Service'].loc[annual_budgets['Fiscal Year'] == (FY+1)].values[0]
    
    # Jan 2022: new DV is a cap on what annual debt service can be w.r.t. gross revenues
    # if too high, defer debt to next year tracked with a deferral variable
    # begin the calculation by including the rollover debt service deferred
    # from the previous FY
    next_FY_deferred_debt_service = 0
    next_FY_budgeted_debt_service += annual_budgets['Debt Service Deferred'].loc[annual_budgets['Fiscal Year'] == (FY)].values[0]
    current_FY_gross_revenues = annual_actuals['Gross Revenues'].loc[annual_actuals['Fiscal Year'] == FY].values[0]
    if next_FY_budgeted_debt_service > debt_service_cap_fraction_of_gross_revenues * current_FY_gross_revenues:
        print('Debt service deferred in FY' + str(FY))
        next_FY_deferred_debt_service = \
            next_FY_budgeted_debt_service - debt_service_cap_fraction_of_gross_revenues * current_FY_gross_revenues
        next_FY_budgeted_debt_service -= next_FY_deferred_debt_service
    
    # if a new water supply project is added, bond issue will cover capital costs
    # but also adjust annual operating costs to account for the change
    # (what fraction of added operating cost is budgeted as "variable cost"?)
    new_fixed, new_variable = add_NewOperationalCosts(
            potential_projects, 
            new_projects_to_finance, 
            fraction_variable_operational_cost)
    accumulated_new_operational_fixed_costs_from_infra += new_fixed
    accumulated_new_operational_variable_costs_from_infra += new_variable
    
    # check if acquisition credits are still being issued
    # should end after FY 2029
    next_FY_budgeted_acquisition_credit = \
        annual_actuals['Acquisition Credits'].loc[annual_actuals['Fiscal Year'] == FY].values[0]
    if FY > 2029:
        next_FY_budgeted_acquisition_credit = 0
    
    # calculate next FY Annual Estimate projection
    #   sum of total anticipated costs, including debt service
    #   assume some rate of inflation in costs from current FY?
    #   if past year had a deficit, assume required deposits into
    #   various funds to make up for it
    # fixed and variable operating costs of existing system expected
    # to increase at inflation rate of 3.3% annually
    # NOTE: IN FUTURE, MAY CONSIDER RANGE OF INFLATION 3.3-5.5%
    # unencumbered budgeted funds are estimated to be 2.5% of
    # prior FY water revenue (see FY20 Operating Budget, p.42)
    # NOTE: ON P.32 OF SAME REPORT, SAYS 2.25% FOR PREVIOUS FYs
    # on the budget spreadsheet in the TBW reports, R&R budget is
    # split out from fixed costs, in this calculation they aren't
    next_FY_budgeted_fixed_operating_costs = \
        (annual_budgets['Fixed Operating Expenses'].loc[annual_budgets['Fiscal Year'] == FY].values[0] + \
         accumulated_new_operational_fixed_costs_from_infra) * \
        (1 + annual_budget_fixed_operating_cost_inflation_rate)
        
    # July 2020: this isn't best practice, but there is a drop in budgeted
    # variable costs between FY14 and 16 by a lot, but slowly steadily rise after that
    # so it makes sense to forecast an inflation rate similar to the fixed costs
    # but the revenues/budgets won't match historically well unless we
    # add a one-off adjustment after FY15 to lower the budgeted estimate
    # (I justify this with the argument that the model is meant to be
    #  forcasting, not copying the historical record, and TBW budgets
    #  themselves expect these costs to increase)
    if FY == 2015: # reduce budgeted estimate by 14% for next FY
        annual_budget_variable_operating_cost_inflation_rate = -0.14
    next_FY_budgeted_variable_operating_costs = \
        (annual_budgets['Variable Operating Expenses'].loc[annual_budgets['Fiscal Year'] == FY].values[0] + \
         accumulated_new_operational_variable_costs_from_infra) * \
        (1 + annual_budget_variable_operating_cost_inflation_rate)
        
    next_FY_budgeted_total_expenditures_before_fund_adjustment = \
        next_FY_budgeted_fixed_operating_costs + \
        next_FY_budgeted_variable_operating_costs + \
        next_FY_budgeted_debt_service + \
        next_FY_budgeted_acquisition_credit
    
    # unencumbered budget seems to ignore potential for previous
    # year to have budget issues?
    water_sales_revenue_columns = [9,10,11,12,13,14,15,16,17,18,19,20,22]
    next_FY_budgeted_unencumbered_funds = \
        current_FY_data.iloc[:,water_sales_revenue_columns].sum().sum() * \
        budgeted_unencumbered_fraction
        
    # estimate next year TBC rate and anticipated revenue from it
    # was $0.173/kgal until FY 2020, then became $0.195
    # future budgets imply this won't change? So, assume it stays
    # equal to current rate. At this rate, the FY21-25 budget
    # projections in FY20 Approved Budget p.42 imply that about 
    # 2 BG of water will be bought by Tampa via TBC
    # actually is 9.5 MGD budgeted plus fixed costs, see report,
    # need to correct this later but not a large issue
    # won't change the final values here but should be consistent
    next_FY_budgeted_tbc_rate = annual_actuals['TBC Sales Rate'].loc[annual_actuals['Fiscal Year'] == FY].values[0]
    next_FY_budgeted_tbc_revenue = \
        next_FY_budgeted_tampa_tbc_delivery * \
        next_FY_budgeted_tbc_rate * convert_kgal_to_MG
        
    # -------------------------------------------------------------------------
    # Jan 2022: update here to replace budgeted transfers and deposits with 
    #   CIP scheduled amounts from each reserve fund, if desired
        
    # estimate any transfers in from funds
    # budgets note that >=$1.5M is expected to be transferred in
    # from rate stabilization annually, with a minimum balance of
    # 8.5% maintained (don't know what this percentage is for)
    # assume a floor of $1.5M transfer in, can be randomly greater
    # in increments of $100k up to 4% of current year sales revenue
    # historically, can get as low as $0
    next_FY_budgeted_rate_stabilization_transfer_in = \
        np.round(np.random.uniform(
                low = 0, 
                high = current_FY_data.iloc[:,water_sales_revenue_columns].sum().sum() * 0.04 / 1000000),
                 decimals = 1) * 1000000
        
    # estimate transfers in for CIP from CIP Fund
    # (aka capital improvement not covered by uniform rate, R&R fund, or debt)
    # from historical budgets, this is always zero
    next_FY_budgeted_cip_fund_transfer_in = 0
    
    # estimate CIP Fund deposit - in the past are
    # 0.001-1% of last FY raw gross revenue
    past_FY_raw_gross_revenue = \
        annual_budgets['Gross Revenues'].loc[annual_budgets['Fiscal Year'] == (FY-1)].values[0]
    next_FY_budgeted_cip_fund_deposit = \
        np.random.uniform(low = past_FY_raw_gross_revenue * 0.001, 
                          high = past_FY_raw_gross_revenue * 0.01)
    
    if FOLLOW_CIP_SCHEDULE:
        next_FY_budgeted_cip_fund_transfer_in = \
            actual_other_cip_expenditures_by_source_by_year['Capital Improvement Fund'].loc[actual_other_cip_expenditures_by_source_by_year['Fiscal Year'] == FY].values[0]
        next_FY_budgeted_cip_fund_deposit = \
            reserve_deposits['FY ' + str(FY)].loc[reserve_deposits['Fund Name'] == 'Capital Improvement Fund'].values[0]
            
    # SECONDARY NOTE: IF THE RATE STABILIZATION FUND BECOMES VERY
    # LARGE, OR MANAGEMENT WISHES TO REDUCE THE UNIFORM RATE, 
    # MORE CAN BE TRANSFERRED IN. FOR NOW, WE ASSUME THAT THE 
    # STABILIZATION FUND IS DESIRED TO BE AT LEAST 8.5% OF 
    # SOME QUANTITY (ASSUME GROSS REVENUE) AND ALSO SHOULD NOT BE 
    # GREATER THAN 30% OF GROSS REVENUE, OTHERWISE FUNDS SHOULD
    # BE TRANSFERRED INTO THE UPCOMING BUDGET TO REDUCE THE RATE
    current_FY_final_rate_stabilization_fund_balance = \
        annual_actuals['Rate Stabilization Fund (Total)'].loc[annual_actuals['Fiscal Year'] == FY].values[0]
    current_FY_final_gross_revenue = \
        annual_actuals['Gross Revenues'].loc[annual_actuals['Fiscal Year'] == FY].values[0]
    if ACTIVE_DEBUGGING:
        print(str(FY) + ': Initial Budgeted Transfer from Rate Stabilization is ' + str(next_FY_budgeted_rate_stabilization_transfer_in))
        print(str(FY) + ': Rate Stabilization Balance is ' + str(current_FY_final_rate_stabilization_fund_balance))
        print(str(FY) + ': Rate Stabilization Balance LOW TARGET is ' + str(current_FY_final_gross_revenue * rate_stabilization_minimum_ratio))
    
    if (current_FY_final_rate_stabilization_fund_balance - \
            next_FY_budgeted_rate_stabilization_transfer_in) / \
            current_FY_final_gross_revenue \
        < rate_stabilization_minimum_ratio:
        next_FY_budgeted_rate_stabilization_transfer_in = np.max([\
            current_FY_final_rate_stabilization_fund_balance - \
            rate_stabilization_minimum_ratio * \
            current_FY_final_gross_revenue, 0])
       
     # DO NOT APPLY A CAP TO REDUCE FUND BALANCE FOR NOW,
     # EVENTUALLY IT CAUSES HUGE TRANSFERS INTO THE BUDGET TO OCCUR
     # IF ANNUAL FINAL SURPLUSES ARE LARGE AND THAT CAN 
     # CAUSE THE UNIFORM RATE TO DROP TO ZERO OR NEGATIVE
#                print(year + ': Secondary Budgeted Transfer from Rate Stabilization is ' + str(next_FY_budgeted_rate_stabilization_transfer_in))
#                print(year + ': Rate Stabilization Balance HIGH TARGET is ' + str(current_FY_final_gross_revenue * rate_stabilization_maximum_ratio))                       
#                if (current_FY_final_rate_stabilization_fund_balance - \
#                        next_FY_budgeted_rate_stabilization_transfer_in) / \
#                        current_FY_final_gross_revenue \
#                    > rate_stabilization_maximum_ratio:
#                    next_FY_budgeted_rate_stabilization_transfer_in = \
#                        current_FY_final_rate_stabilization_fund_balance - \
#                        rate_stabilization_maximum_ratio * \
#                        current_FY_final_gross_revenue
     
    if ACTIVE_DEBUGGING:        
        print(str(FY) + ': Budgeted Transfer from Rate Stabilization is ' + str(next_FY_budgeted_rate_stabilization_transfer_in))
        print(str(FY) + ': Budgeted Total Expenditures (before Fund Adjustments) is ' + str(next_FY_budgeted_total_expenditures_before_fund_adjustment))
        print(str(FY) + ': Budgeted Debt Service is ' + str(next_FY_budgeted_debt_service))
            
    # estimate transfers in to cover R&R expenses
    # bounded based on ratio of projected FY 21-25
    # R&R transfers to budgeted expenses before transfers
    # (ranging from 1.8-6% of budgeted expenses)
    # July 2020: adjusted this range based on more recent
    # FY observations
    # also estimate deposit into R&R fund and year's end
    # is either $4.5M or $5M in 6 years of future budget
    # projections, so have it be either one randomly?
    # come off this assumption to better match historical record,
    # let it range $2.5-5M observed over past
    next_FY_budgeted_rr_transfer_in = \
        np.random.uniform(
                low = next_FY_budgeted_total_expenditures_before_fund_adjustment * 0.01, 
                high = next_FY_budgeted_total_expenditures_before_fund_adjustment * 0.06)
    next_FY_budgeted_rr_deposit = \
        np.round(np.random.uniform(low = 2.5, high = 5),
                 decimals = 1) * 1000000
                 
    if FOLLOW_CIP_SCHEDULE:
        next_FY_budgeted_rr_transfer_in = \
            actual_other_cip_expenditures_by_source_by_year['Renewal and Replacement Fund'].loc[actual_other_cip_expenditures_by_source_by_year['Fiscal Year'] == FY].values[0]
        next_FY_budgeted_rr_deposit = \
            reserve_deposits['FY ' + str(FY)].loc[reserve_deposits['Fund Name'] == 'Renewal and Replacement Fund'].values[0]

    # double-check R&R fund balance, adjust transfers if it is
    # being drawn down too much by reducing transfer in
    current_FY_final_rr_fund_balance = \
        annual_actuals['R&R Fund (Total)'].loc[annual_actuals['Fiscal Year'] == FY].values[0]
    if current_FY_final_rr_fund_balance - \
            next_FY_budgeted_rr_transfer_in + \
            next_FY_budgeted_rr_deposit \
        < current_FY_final_gross_revenue * 0.05:
        next_FY_budgeted_rr_transfer_in = \
            (current_FY_final_rr_fund_balance + \
             next_FY_budgeted_rr_deposit) - \
            current_FY_final_gross_revenue * 0.05
    
    # estimate income from investment interest
    # it seems that all accounts of the enterprise fund (all funds)
    # make in aggregate about 0.5% interest annually
    # don't have all funds accounted for here, but can approximate
    sinking_fund_size_approximator = next_FY_budgeted_debt_service * 1.6
    cip_and_operating_fund_size_approximator = next_FY_budgeted_variable_operating_costs
    approximate_enterprise_fund_balance = \
        current_FY_final_rate_stabilization_fund_balance + \
        current_FY_final_reserve_fund_balance + \
        current_FY_final_rr_fund_balance + \
        next_FY_budgeted_variable_operating_costs + \
        sinking_fund_size_approximator + \
        cip_and_operating_fund_size_approximator
    next_FY_budgeted_interest_income = approximate_enterprise_fund_balance * \
        np.random.uniform(low = 0.002, high = 0.008)
        
    # estimate any remaining deposits to other funds
    # (includes operating reserve)
    # after FY2022, this hovers around $250k a year, before that
    # could be up to $2.2M. Will make it a uniform random value
    # between $200k and $2M
    # historically, it has often been $0 or less than $2M, so do that range
    # Jan 2022: account for energy fund, replacing "other" funds
    next_FY_budgeted_energy_deposit = np.random.uniform(
                low = 0, high = 2000000)
    next_FY_budgeted_energy_transfer_in = 0
    
    if FOLLOW_CIP_SCHEDULE:
        next_FY_budgeted_energy_transfer_in = \
            actual_other_cip_expenditures_by_source_by_year['Energy Fund'].loc[actual_other_cip_expenditures_by_source_by_year['Fiscal Year'] == FY].values[0]
        next_FY_budgeted_energy_deposit = \
            reserve_deposits['FY ' + str(FY)].loc[reserve_deposits['Fund Name'] == 'Energy Fund'].values[0]

    
    # not an actual step in any documents, but if there is a deficit
    # or loss of reserve funding in previous FY and fund balance
    # must be replenished, include a budgeted deposit to the 
    # utility reserve fund
    next_FY_budgeted_reserve_fund_deposit = 0
    if current_FY_final_reserve_fund_balance < \
            current_FY_final_gross_revenue * reserve_fund_floor_fraction_of_gross_revenues:
        next_FY_budgeted_reserve_fund_deposit += \
            current_FY_final_gross_revenue * reserve_fund_floor_fraction_of_gross_revenues - \
            current_FY_final_reserve_fund_balance
    
    # finalize Annual Estimate
    # to be consistent with numbers pulled from budget reports, the AE
    # is all costs before deposits into reserve funds
    next_FY_annual_estimate = \
        next_FY_budgeted_total_expenditures_before_fund_adjustment + \
        next_FY_budgeted_rate_stabilization_transfer_in
#        next_FY_budgeted_rr_deposit - \
#        next_FY_budgeted_other_deposits + \
#        next_FY_budgeted_reserve_fund_deposit + \
#        next_FY_budgeted_cip_fund_deposit
    
    # estimate water demand for upcoming FY
    # future budget projections based on water demand of 180.8 MGD
    # on average for FY 2020 and growing at a rate between 
    # 1-1.5% per year. For now, will set growth rate steady
    # based on what previous year's water demand was        
    next_FY_demand_estimate_mgd = \
        current_FY_data['Water Delivery - Uniform Sales Total'].sum()/n_days_in_year * \
        (1 + annual_demand_growth_rate)
    
    # given cost breakdowns, estimate water rates
    # also based on projection of total water demand
    #   from monthly data (or budgetary factor?)
    # reminder, rates in $/kgal
    # note: when checking the "actual" revenues against what the AE requires,
    # the AE as calculated above does not account for additional deposits/transfers
    # so we need to include them here to isolate a comparison against
    # water sales revenues only
    # Jan 2022: if it is FY2022 or earlier, rely on existing approved budgets
    #   rather than re-calculating the uniform rate and other costs
    if FY >= first_modeled_fy:
        next_FY_uniform_rate, next_FY_annual_estimate, \
        next_FY_budgeted_rate_stabilization_transfer_in = \
            estimate_UniformRate(annual_estimate = next_FY_annual_estimate, 
                                 demand_estimate = next_FY_demand_estimate_mgd, 
                                 current_uniform_rate = annual_budgets['Uniform Rate'].loc[annual_budgets['Fiscal Year'] == FY].values[0],
                                 rs_transfer_in = next_FY_budgeted_rate_stabilization_transfer_in,
                                 rs_fund_total = current_FY_final_rate_stabilization_fund_balance,
                                 high_rate_bound = managed_uniform_rate_increase_rate,
                                 low_rate_bound = managed_uniform_rate_decrease_rate,
                                 MANAGE_RATE = KEEP_UNIFORM_RATE_STABLE)
                
        next_FY_variable_uniform_rate = \
            estimate_VariableRate(next_FY_annual_estimate - next_FY_budgeted_rr_transfer_in,
                                  next_FY_budgeted_variable_operating_costs, 
                                  next_FY_uniform_rate)
        
    else:
        next_FY_uniform_rate = \
            annual_budgets['Uniform Rate'].loc[annual_budgets['Fiscal Year'] == (FY+1)].values[0]
        next_FY_variable_uniform_rate = \
            annual_budgets['Variable Uniform Rate'].loc[annual_budgets['Fiscal Year'] == (FY+1)].values[0]
        next_FY_annual_estimate = \
            annual_budgets['Annual Estimate'].loc[annual_budgets['Fiscal Year'] == (FY+1)].values[0]
        next_FY_budgeted_rate_stabilization_transfer_in = \
            annual_budgets['Rate Stabilization Fund Transfers In'].loc[annual_budgets['Fiscal Year'] == (FY+1)].values[0]
    
    # collect all elements of new FY budget projection
    # to match rows of budget_projections
    # first, fill in other variables that haven't explicitly been 
    # calculated yet.
    # in gross revenue calculation, not including litigation/
    # insurance recovery or arbitrage (ranges from $0-1.1M)
    next_FY_budgeted_uniform_sales_fixed_revenue = \
        next_FY_annual_estimate - \
        next_FY_budgeted_variable_operating_costs - \
        next_FY_budgeted_acquisition_credit
    next_FY_budgeted_uniform_sales_variable_revenue = \
        next_FY_demand_estimate_mgd * next_FY_variable_uniform_rate * \
        convert_kgal_to_MG * n_days_in_year
    
    next_FY_budgeted_water_sales_revenue = \
        next_FY_budgeted_uniform_sales_fixed_revenue + \
        next_FY_budgeted_uniform_sales_variable_revenue + \
        next_FY_budgeted_tbc_revenue
    
    next_FY_budgeted_raw_gross_revenues = \
        next_FY_budgeted_water_sales_revenue + \
        next_FY_budgeted_interest_income + \
        next_FY_budgeted_unencumbered_funds + \
        next_FY_budgeted_rr_transfer_in
        
#    print(str(FY) + ": next FY budgeted RS transfer in is " + str(next_FY_budgeted_rate_stabilization_transfer_in))
        
    next_FY_budgeted_raw_net_revenue = \
        next_FY_budgeted_raw_gross_revenues - \
        next_FY_budgeted_fixed_operating_costs - \
        next_FY_budgeted_variable_operating_costs
    
    next_FY_budgeted_other_transfer_in = 0
    next_FY_budgeted_other_deposit = 0
    next_FY_budgeted_rate_stabilization_deposit = 0
    annual_budgets.loc[annual_budgets['Fiscal Year'] == (FY+1)] = \
                    pd.DataFrame([FY+1, 
                                  next_FY_annual_estimate, 
                                  next_FY_budgeted_raw_gross_revenues,
                                  next_FY_budgeted_water_sales_revenue, 
                                  next_FY_budgeted_fixed_operating_costs, 
                                  next_FY_budgeted_variable_operating_costs, 
                                  next_FY_budgeted_raw_net_revenue, 
                                  next_FY_budgeted_debt_service, 
                                  next_FY_budgeted_acquisition_credit, 
                                  next_FY_budgeted_unencumbered_funds, 
                                  next_FY_budgeted_rr_deposit, 
                                  next_FY_budgeted_rate_stabilization_deposit, 
                                  next_FY_budgeted_other_deposit, 
                                  next_FY_uniform_rate, 
                                  next_FY_variable_uniform_rate, 
                                  next_FY_budgeted_tbc_rate, 
                                  next_FY_budgeted_rate_stabilization_transfer_in, 
                                  next_FY_budgeted_rr_transfer_in, 
                                  next_FY_budgeted_other_transfer_in, # never any other funds budgeted transferred in?
                                  next_FY_budgeted_interest_income, 
                                  next_FY_budgeted_cip_fund_transfer_in,
                                  next_FY_budgeted_cip_fund_deposit,
                                  next_FY_budgeted_energy_transfer_in,
                                  next_FY_budgeted_energy_deposit,
                                  next_FY_deferred_debt_service]).transpose().values 

    
    return annual_budgets, existing_issued_debt, potential_projects, \
            accumulated_new_operational_fixed_costs_from_infra, \
            accumulated_new_operational_variable_costs_from_infra


### ----------------------------------------------------------------------- ###
### BUILD MONTHLY FINANCIAL MODEL SIMULATION (WRAPPER) FUNCTION
### assume model will run as a post-processing step
### because it will not impact daily water supply operations
### ----------------------------------------------------------------------- ###

def run_FinancialModelForSingleRealization(start_fiscal_year, end_fiscal_year,
                                           simulation_id,
                                           decision_variables, 
                                           rdm_factors,
                                           annual_budget,
                                           budget_projections,
                                           water_deliveries_and_sales,
                                           existing_issued_debt,
                                           existing_debt_targets,
                                           potential_projects,
                                           CIP_plan,
                                           fraction_cip_spending_for_major_projects_by_year_by_source,
                                           generic_CIP_plan,
                                           generic_fraction_cip_spending_for_major_projects_by_year_by_source,
                                           reserve_balances,
                                           reserve_deposits,
                                           realization_id = 1,
                                           additional_scripts_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Code/Visualization',
                                           orop_output_path = 'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/cleaned', 
                                           oms_output_path = 'F:/MonteCarlo_Project/FNAII/IM to Tirusew/Integrated Models/SWERP_V1/AMPL_Results_run_125',
                                           outpath = 'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/output',
                                           formulation_id = 125,
                                           PRE_CLEANED = True,
                                           ACTIVE_DEBUGGING = False,
                                           FOLLOW_CIP_MAJOR_SCHEDULE = True,
                                           FLEXIBLE_OTHER_CIP_SCHEDULE = True):
    # get necessary packages
    import pandas as pd; import numpy as np
    
    ### -----------------------------------------------------------------------
    # constants (some assigned elsewhere...)
    last_fy_month = 9; first_modeled_fy = 2021
    n_months_in_year = 12
    accumulated_new_operational_fixed_costs_from_infra = 0
    accumulated_new_operational_variable_costs_from_infra = 0
    
    # deeply uncertain factors ACTIVE IN THIS LAYER OF MODEL (rest elsewhere)
    annual_demand_growth_rate = rdm_factors[5]
    
    # decision variables ACTIVE HERE
    # none

    # give number of variables tracked in outputs
    n_financial_metric_outcomes = 17
    n_actual_budget_outcomes = 27
    n_proposed_budget_outcomes = 25
    n_deliveries_sales_variables = 23
                
    ### -----------------------------------------------------------------------
    # step 0: create partially empty final tables based on range of dates
    #           assume that modeling operates on scale of fiscal years
    #   based on the starting fiscal year, will also need the preceeding FY
    #   for some calculations.
    assert (start_fiscal_year < end_fiscal_year), 'End year must be greater than start year.'
    assert (start_fiscal_year <= first_modeled_fy), 'Start FY must be <= first modeled FY (2021)'
    fiscal_years_to_keep = [int(y) for y in range(start_fiscal_year-1,end_fiscal_year)]
    
    financial_metrics = np.empty((len(fiscal_years_to_keep)-1,n_financial_metric_outcomes))
    financial_metrics[:] = np.nan; financial_metrics[:,0] = fiscal_years_to_keep[1:]
    
    annual_actuals = np.empty((len(fiscal_years_to_keep)+1,n_actual_budget_outcomes)) # keep 2 extra years
    annual_actuals[:] = np.nan; annual_actuals[:,0] = [min(fiscal_years_to_keep)-1] + fiscal_years_to_keep
    
    annual_budgets = np.empty((len(fiscal_years_to_keep)+1,n_proposed_budget_outcomes))
    annual_budgets[:] = np.nan; annual_budgets[:,0] = fiscal_years_to_keep + [end_fiscal_year]
    
    water_delivery_sales = np.empty((len(fiscal_years_to_keep)*n_months_in_year,n_deliveries_sales_variables))
    water_delivery_sales[:] = np.nan; 
    water_delivery_sales[:,0] = [y for y in fiscal_years_to_keep for m in range(0,n_months_in_year)] # FY
    water_delivery_sales[:,1] = [m for y in fiscal_years_to_keep for m in [10,11,12,1,2,3,4,5,6,7,8,9]] # FY order of CALENDAR months
        
    # set column names and convert format...
    financial_metrics = pd.DataFrame(financial_metrics)
    financial_metrics.columns = ['Fiscal Year',
                                    'Debt Covenant Ratio', 
                                    'Rate Covenant Ratio',
                                    'Partial Debt Covenant Failure',
                                    'Partial Rate Covenant Failure',
                                    'Reserve Fund Balance Initial Failure',
                                    'R&R Fund Balance Initial Failure',
                                    'Cap on Rate Stabilization Fund Transfers In',
                                    'Rate Stabilization Funds Transferred In',
                                    'Required R&R Fund Deposit',
                                    'Required Reserve Fund Deposit',
                                    'Necessary Use of Other Funds (Rate Stabilization Supplement)', 
                                    'Final Net Revenues', 
                                    'Fixed Sales Revenue', 
                                    'Variable Sales Revenue',
                                    'Reserve Fund Balancing Failure',
                                    'Remaining Unallocated Deficit']
    
    annual_budgets = pd.DataFrame(annual_budgets)
    annual_budgets.columns = budget_projections.columns
    
    annual_actuals = pd.DataFrame(annual_actuals)
    annual_actuals.columns = annual_budget.columns
    
    water_delivery_sales = pd.DataFrame(water_delivery_sales)
    water_delivery_sales.columns = [water_deliveries_and_sales.columns[-1], water_deliveries_and_sales.columns[-2]] + [v for v in water_deliveries_and_sales.columns[1:-3]]
    
    ### -----------------------------------------------------------------------
    # step 1: read in realization data from water supply modeling
    #           should include risk metric/trigger levels for infrastructure
    #           and ID/timing of any infrastructure project built
    #   NOTE: THIS IS THE MOST TIME-CONSUMING STEP
    #   IF DOING HISTORICAL TEST, NO NEED TO READ DATA
    AMPL_cleaned_data, TBC_raw_sales_to_CoT, Year, Month = \
        pull_ModeledData(additional_scripts_path, orop_output_path, oms_output_path, realization_id, 
                         fiscal_years_to_keep, end_fiscal_year, first_modeled_fy, PRE_CLEANED)
    
    ### -----------------------------------------------------------------------
    # step 1b: collect existing data in future output files 
    #           along with modeled data of future years
    annual_actuals, annual_budgets, water_delivery_sales, reserve_deposits = \
        collect_ExistingRecords(annual_actuals, annual_budgets, water_delivery_sales,
                                annual_budget, budget_projections, water_deliveries_and_sales, 
                                CIP_plan, reserve_balances, reserve_deposits,
                                AMPL_cleaned_data, TBC_raw_sales_to_CoT, Month, Year,
                                fiscal_years_to_keep, first_modeled_fy, n_months_in_year, 
                                annual_demand_growth_rate, last_fy_month, 
                                outpath)
        
    ### -----------------------------------------------------------------------
    # step 1c: organize CIP spending by major water supply projects and 
    #           all other capital expenses. Assume major projects are either
    #           future debt financed via bonds or co-funded with SWFWMD 
    #           (unless overridden for customized funding split designated 
    #           by decision variables) and all other projects are split 
    #           according to trends observed in the FY2022-2031 CIP Report,
    #           generally allocated annually such that:
    #
    #               MAJOR PROJECT 10-YEAR SCHEDULE (about $850M over 10 years)
    #               (as fraction of total investment paid per year)
    #               (and split between bond/co-funding)
    #               Y0: 5%      (99/1)
    #               Y1: 5.7%    (93/7)
    #               Y2: 6.2%    (96/4)
    #               Y3: 6.2%    (96/4)
    #               Y4: 20.6%   (64/36)
    #               Y5: 31.6%   (58/42)
    #               Y6: 11.4%   (71/29)
    #               Y7: 10.9%   (72/28)
    #               Y8: 2.3%    (50/50)
    #               Y9: NA
    #               Y+: NA
    #
    #               OTHER PROJECT 10-YEAR SCHEDULE (<$75M CAPITAL COST PER PROJ.)
    #               (about $380M over 10-year period)
    #               (as fraction of total investment paid per year)
    #               (and split between CIF, Energy Fund, Member Contribution,
    #                R&R Fund, Past Bonds 1, Past Bonds 2, Future Bonds,
    #                State Grant, SWFWMD, Uniform Rate)
    #               Y0: 9.6%    (0.27 0.03 0.08 0.33    0 0.04 0.11 0.00 0.04  0.10)
    #               Y1: 15.1%   (0.29 0.02 0.05 0.29    0 0.04 0.20 0.01 0.03  0.06)
    #               Y2: 18.2%   (0.28 0.01 0.04 0.17    0 0.03 0.40 0.00 0.05  0.02)
    #               Y3: 14%     (0.20   NA 0.05 0.16   NA 0.00 0.54   NA 0.05  0.01)
    #               Y4: 15%     (0.07   NA 0.20 0.04   NA 0.00 0.48   NA 0.20  0.00)
    #               Y5: 11.1%   (0.03   NA 0.43 0.04   NA   NA 0.08   NA 0.43  0.00)
    #               Y6: 11%     (0.03   NA 0.43 0.10   NA   NA 0.00   NA 0.43  0.00)
    #               Y7: 5%      (0.06   NA 0.36 0.23   NA   NA 0.00   NA 0.36  0.00)
    #               Y8: 1%      (0.33   NA   NA 0.67   NA   NA 0.00   NA   NA  0.00)
    #               Y9: NA
    #               Y+: NA
    #
    #   NOTE: the payment schedules commented here are "normalized" from the CIP Report,
    #       meaning that, within the classes of projects (major/other), 
    #       individual projects were standardized to a generic start date of repayment
    #       to isolate general repayment practices for different classes of project.
    #       After the next decade of CIP, the model WILL ASSUME A MORE UNIFORM ANNUAL
    #       DIVISION OF CAPTIAL EXPENDITURES until the end of planning period (2040).
    #       But for 2021-2031: MODEL WILL FOLLOW SCHEDULED (NOT NORMALIZED) CIP REPORT.
    planned_major_cip_expenditures_by_source_full_model_period, planned_other_cip_expenditures_by_source_full_model_period = \
        allocate_InitialAnnualCIPSpending(start_fiscal_year, end_fiscal_year, first_modeled_fy,
                                          CIP_plan, 
                                          fraction_cip_spending_for_major_projects_by_year_by_source,
                                          generic_CIP_plan,
                                          generic_fraction_cip_spending_for_major_projects_by_year_by_source,
                                          outpath, PRINT_INITIAL_ALLOCATIONS = False)
        
    # initialize "actual" CIP spending datasets to compare to planned spending at end of simulation
    actual_other_cip_expenditures_by_source_by_year = planned_other_cip_expenditures_by_source_full_model_period.copy()
    actual_major_cip_expenditures_by_source_by_year = planned_major_cip_expenditures_by_source_full_model_period.copy()
    
    ### -----------------------------------------------------------------------
    # step 2: take an annual step loop over water supply outcomes for future
    #           collect summed water deliveries to each member government
    #           through uniform rate sales and TBC sales
    #           and check if any infrastructure was triggered/built
    #           also record monthly values for exporting output
    for FY in range(start_fiscal_year, end_fiscal_year):
        # for debugging: FY = start_fiscal_year
        ### -------------------------------------------------------------------
        # step 2a: calculate revenues from water sales, collect within dataset
        water_delivery_sales, past_FY_year_data = \
            calculate_WaterSalesForFY(FY, water_delivery_sales, 
                                      annual_budgets, annual_actuals,
                                      dv_list = decision_variables, 
                                      rdm_factor_list = rdm_factors,
                                      annual_demand_growth_rate = annual_demand_growth_rate)
            
        ### -------------------------------------------------------------------
        # step 2b: identify planned capital expenditures for major water supply
        #       projects over model period. THERE ARE TWO OPTIONS FOR DOING SO:
        #           1. based on SWRE runs, trigger individual projects
        #               and their specialized financing plans at manually-
        #               selected future fiscal years (original model design)
        #           2. follow CIP plan for major projects financing, which is
        #               based on generic placeholders and TBW assumptions about
        #               future debt financing and other spending sources
        actual_major_cip_expenditures_by_source_by_year, new_projects_to_finance, AMPL_cleaned_data = \
            update_MajorSupplyInfrastructureInvestment(FOLLOW_CIP_MAJOR_SCHEDULE,
                                                       FY, first_modeled_fy, last_fy_month, Month, Year, formulation_id,
                                                       AMPL_cleaned_data,
                                                       actual_major_cip_expenditures_by_source_by_year)
        
        ### -------------------------------------------------------------------
        # step 3: perform annual end-of-FY calculations
        #               (1) next year uniform rate estimate (fixed and variable)
        #               (2) next year TBC rate estimate
        #               (3) full budget estimate and handle annual costs like debt
        #               (4) bond covenants

        # collect model output from just-completed FY
        current_FY_data = water_delivery_sales.loc[water_delivery_sales['Fiscal Year'] == FY]
        
        ### (1) calculate "actual" budget for completed FY ------------
        # using modeled water demands, budgeted debt service, and
        # operational costs (which can be perturbed from accepted
        # budget levels to approximate actual variability/growth)
        # assume debt service doesn't vary from approved budget level
        # FYs 18,19: actual variable op costs were 17% and 24% lower than
        # approved budgeted costs. actual fixed op costs were 8% and 16%
        # lower than approved.
        annual_actuals, annual_budgets, financial_metrics = \
            calculate_FYActuals(FY, current_FY_data, past_FY_year_data, 
                                annual_budgets, annual_actuals, financial_metrics,
                                decision_variables, 
                                rdm_factors,
                                ACTIVE_DEBUGGING,
                                actual_major_cip_expenditures_by_source_by_year,
                                actual_other_cip_expenditures_by_source_by_year,
                                reserve_balances,
                                reserve_deposits,
                                FOLLOW_CIP_SCHEDULE = FOLLOW_CIP_MAJOR_SCHEDULE,
                                FLEXIBLE_CIP_SPENDING = FLEXIBLE_OTHER_CIP_SCHEDULE)

        ### begin "budget development" for next FY --------------------
        # (a) estimate debt service and split among bond issues
        # (b) set Annual Estimate
        # (c) extimate demand and set Uniform Rates (full and variable)
        # UPDATE, Jan 2022: begin forecasting the budget one FY after modeling
        #   of actuals begins, because in FY2021 when modeling begins, the
        #   FY22 budget has already been approved.
        next_modeled_fy_budget_already_approved = int(True)
        annual_budgets, existing_issued_debt, potential_projects, \
                accumulated_new_operational_fixed_costs_from_infra, \
                accumulated_new_operational_variable_costs_from_infra = \
            calculate_NextFYBudget(FY, first_modeled_fy+next_modeled_fy_budget_already_approved, 
                                    current_FY_data, past_FY_year_data, 
                                    annual_budgets, annual_actuals, financial_metrics, 
                                    existing_issued_debt, new_projects_to_finance, potential_projects, existing_debt_targets,
                                    accumulated_new_operational_fixed_costs_from_infra,
                                    accumulated_new_operational_variable_costs_from_infra,
                                    decision_variables, 
                                    rdm_factors,
                                    ACTIVE_DEBUGGING,
                                    actual_major_cip_expenditures_by_source_by_year,
                                    actual_other_cip_expenditures_by_source_by_year,
                                    reserve_balances,
                                    reserve_deposits,
                                    FOLLOW_CIP_SCHEDULE = FOLLOW_CIP_MAJOR_SCHEDULE,
                                    FLEXIBLE_CIP_SPENDING = FLEXIBLE_OTHER_CIP_SCHEDULE)
    
    # step 4: end loop and export results, including objectives
    # Nov 2020: adjust paths to also show current model formulation (infrastructure pathway)
    
    annual_budgets.to_csv(outpath + '/budget_projections_f' + str(formulation_id) + '_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    annual_actuals.to_csv(outpath + '/budget_actuals_f' + str(formulation_id) + '_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    financial_metrics.to_csv(outpath + '/financial_metrics_f' + str(formulation_id) + '_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    existing_issued_debt.to_csv(outpath + '/final_debt_balance_f' + str(formulation_id) + '_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    water_delivery_sales.to_csv(outpath + '/water_deliveries_revenues_f' + str(formulation_id) + '_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    
    return annual_budgets, annual_actuals, financial_metrics, water_delivery_sales, existing_issued_debt
    


### ----------------------------------------------------------------------- ###
### RUN ACROSS DIFFERENT MONTE CARLO SETS OF DVS
### ----------------------------------------------------------------------- ###
import numpy as np; import pandas as pd
# set data paths, differentiating local vs common path components
# see past commits or vgrid_version branch for paths to run on TBW system
local_base_path = 'F:/MonteCarlo_Project/Cornell_UNC'
local_data_sub_path = '/financial_model_input_data'
local_code_sub_path = ''
local_MonteCarlo_data_base_path = 'F:/MonteCarlo_Project/Cornell_UNC/cleaned_AMPL_files'

# read in decision variables from spreadsheet
dv_path = local_base_path + local_code_sub_path + '/TampaBayWater/FinancialModeling'
DVs = pd.read_csv(dv_path + '/financial_model_DVs.csv', header = None)

# read in deeply uncertain factors
DUFs = pd.read_csv(dv_path + '/financial_model_DUfactors.csv', header = None)

### ---------------------------------------------------------------------------
# read in historic records
historical_data_path = local_base_path + local_data_sub_path + '/model_input_data'

monthly_water_deliveries_and_sales = pd.read_csv(historical_data_path + '/water_sales_and_deliveries_all_2020.csv')
historical_annual_budget_projections = pd.read_csv(historical_data_path + '/historical_budgets.csv')
annual_budget_data = pd.read_csv(historical_data_path + '/historical_actuals.csv')
existing_debt = pd.read_csv(historical_data_path + '/existing_debt.csv')
infrastructure_options = pd.read_csv(historical_data_path + '/potential_projects.csv')
current_debt_targets = pd.read_excel(historical_data_path + '/Current_Future_BondIssues.xlsx', sheet_name = 'FutureDSTotals')
projected_10year_CIP_spending = pd.read_csv(historical_data_path + '/original_CIP_spending_all_projects.csv')
projected_10year_CIP_spending_major_project_fraction = pd.read_csv(historical_data_path + '/original_CIP_spending_major_projects_fraction.csv')
normalized_CIP_spending = pd.read_csv(historical_data_path + '/normalized_CIP_spending_all_projects.csv')
normalized_CIP_spending_major_project_fraction = pd.read_csv(historical_data_path + '/normalized_CIP_spending_major_projects_fraction.csv')
projected_first_year_reserve_fund_balances = pd.read_csv(historical_data_path + '/projected_FY21_reserve_fund_starting_balances.csv')
projected_10year_reserve_fund_deposits = pd.read_csv(historical_data_path + '/projected_reserve_fund_deposits.csv')

# for simplicity? organize all input data into data dictionary to make
# passing to functions easier THIS TBD
#ALL_INPUT_DATA = {'Data Name': '',
#                  'Data Structure': monthly_water_deliveries_and_sales}

### =========================================================================== ###
### RUN FINANCIAL MODEL OVER RANGE OF INFRASTRUCTURE SCENARIOS/FORMULATIONS
### =========================================================================== ###
for run_id in [125]: # NOTE: DAVID'S LOCAL CP ONLY HAS 125 RUN OUTPUT FOR TESTING
    # run for testing: run_id = 125; sim = 0; r_id = 1
    
    ### ---------------------------------------------------------------------------
    # set additional required paths
    scripts_path = local_base_path + local_code_sub_path + '/TampaBayWater/data_management'
    ampl_output_path = local_MonteCarlo_data_base_path + '/run0' + str(run_id)
    oms_path = 'F:/MonteCarlo_Project/FNAII/IM to Tirusew/Integrated Models/SWERP_V1/AMPL_Results_run_' + str(run_id)
    output_path = local_base_path + '/updated_financial_model_output'
    
    ### ---------------------------------------------------------------------------
    # run loop across DV sets
    sim_objectives = [0,0,0,0] # sim id + three objectives
    start_fy = 2021; end_fy = 2040; n_reals_tested = 10 # NOTE: DAVID'S LOCAL CP ONLY HAS RUN 125 MC REALIZATION FILES 0-200 FOR TESTING
    #for sim in range(0,len(DVs)): # sim = 0 for testing
    #for sim in range(0,1): # FOR RUNNING HISTORICALLY ONLY
    for sim in range(0,9): # FOR RUNNING MULTIPLE SIMULATIONS
        ### ----------------------------------------------------------------------- ###
        ### RUN REALIZATION FINANCIAL MODEL ACROSS SET OF REALIZATIONS
        ### ----------------------------------------------------------------------- ###  
        dvs = [x for x in DVs.iloc[sim,:]]
        dufs = [x for x in DUFs.iloc[sim,:]]
        
        FLEXIBLE_CIP_SCHEDULE_TOGGLE = bool(dufs[18])
        FOLLOW_CIP_SCHEDULE_TOGGLE = bool(dufs[19])
        
        debt_covenant_years = [int(x) for x in range(start_fy,end_fy)]
        rate_covenant_years = [int(x) for x in range(start_fy,end_fy)]
        full_rate_years = [int(x) for x in range(start_fy-2,end_fy)]
        variable_rate_years = [int(x) for x in range(start_fy-2,end_fy)]
        total_deliveries_months = [int(x) for x in range(1,(end_fy - start_fy + 1)*12+1)]
        for r_id in range(1,n_reals_tested+1):
            print(r_id)
            # seems to be an issue with run 95 .mat file, skip this realization
            if r_id == 95:
                continue
            
    #    for r_id in range(1,2): # r_id = 1 for testing
            # run this line for testing: 
            # start_fiscal_year = start_fy; end_fiscal_year = end_fy;simulation_id = sim;decision_variables = dvs;rdm_factors = dufs;annual_budget = annual_budget_data;budget_projections = historical_annual_budget_projections;water_deliveries_and_sales = monthly_water_deliveries_and_sales;existing_issued_debt = existing_debt;existing_debt_targets = current_debt_targets;potential_projects = infrastructure_options;CIP_plan = projected_10year_CIP_spending;reserve_balances = projected_first_year_reserve_fund_balances;reserve_deposits = projected_10year_reserve_fund_deposits;realization_id = r_id; additional_scripts_path = scripts_path;orop_output_path = ampl_output_path;oms_output_path = oms_path; outpath = output_path; formulation_id = run_id; PRE_CLEANED = True; ACTIVE_DEBUGGING = False; fraction_cip_spending_for_major_projects_by_year_by_source = projected_10year_CIP_spending_major_project_fraction; generic_CIP_plan = normalized_CIP_spending; generic_fraction_cip_spending_for_major_projects_by_year_by_source = normalized_CIP_spending_major_project_fraction; FOLLOW_CIP_MAJOR_SCHEDULE = True; FLEXIBLE_OTHER_CIP_SCHEDULE = True   
                        
            budget_projection, actuals, outcomes, water_vars, final_debt = \
                run_FinancialModelForSingleRealization(
                        start_fiscal_year = start_fy, end_fiscal_year = end_fy,
                        simulation_id = sim,
                        decision_variables = dvs, 
                        rdm_factors = dufs,
                        annual_budget = annual_budget_data,
                        budget_projections = historical_annual_budget_projections,
                        water_deliveries_and_sales = monthly_water_deliveries_and_sales,
                        existing_issued_debt = existing_debt,
                        existing_debt_targets = current_debt_targets,
                        potential_projects = infrastructure_options,
                        CIP_plan = projected_10year_CIP_spending,
                        fraction_cip_spending_for_major_projects_by_year_by_source = projected_10year_CIP_spending_major_project_fraction,
                        generic_CIP_plan = normalized_CIP_spending,
                        generic_fraction_cip_spending_for_major_projects_by_year_by_source = normalized_CIP_spending_major_project_fraction,
                        reserve_balances = projected_first_year_reserve_fund_balances,
                        reserve_deposits = projected_10year_reserve_fund_deposits,
                        realization_id = r_id, 
                        additional_scripts_path = scripts_path,
                        orop_output_path = ampl_output_path,
                        oms_output_path = oms_path,
                        outpath = output_path, formulation_id = run_id,
                        PRE_CLEANED = True, ACTIVE_DEBUGGING = False,
                        FOLLOW_CIP_MAJOR_SCHEDULE = FOLLOW_CIP_SCHEDULE_TOGGLE,
                        FLEXIBLE_OTHER_CIP_SCHEDULE = FLEXIBLE_CIP_SCHEDULE_TOGGLE)
            
            ### -----------------------------------------------------------------------
            # collect data of some results across all realizations
            debt_covenant_years = np.vstack((debt_covenant_years, [x for x in outcomes['Debt Covenant Ratio']]))
            rate_covenant_years = np.vstack((rate_covenant_years, [x for x in outcomes['Rate Covenant Ratio']]))
            full_rate_years = np.vstack((full_rate_years, [x for x in actuals['Uniform Rate (Full)']]))
            variable_rate_years = np.vstack((variable_rate_years, [x for x in actuals['Uniform Rate (Variable Portion)']]))
            total_deliveries_months = np.vstack((total_deliveries_months, [x for x in water_vars['Water Delivery - Uniform Sales Total']]))
               
        ### ---------------------------------------------------------------------------
        # reorganize data
        DC = pd.DataFrame(debt_covenant_years[1:,:]); DC.columns = [int(x) for x in debt_covenant_years[0,:]]
        RC = pd.DataFrame(rate_covenant_years[1:,:]); RC.columns = [int(x) for x in rate_covenant_years[0,:]]
        UR = pd.DataFrame(full_rate_years[1:,:]); UR.columns = [int(x) for x in full_rate_years[0,:]]
        VR = pd.DataFrame(variable_rate_years[1:,:]); VR.columns = [int(x) for x in variable_rate_years[0,:]]
        WD = pd.DataFrame(total_deliveries_months[1:,:]); WD.columns = [int(x) for x in total_deliveries_months[0,:]]
        
        ### ---------------------------------------------------------------------------
        # calculate financial objectives
        # 1: debt covenant (fraction of realizations with covenant violation in year with most violations)
        DC_Violations = (DC < 1).sum()
        Objective_DC_Violations = max(DC_Violations)/len(DC)
        
        # 2: rate covenant (fraction of realizations with covenant violation in year with most violations)
        RC_Violations = (RC < 1.25).sum()
        Objective_RC_Violations = max(RC_Violations)/len(RC)
        
        # 3: uniform date (average of greatest annual rate across realizations)
        Objective_UR_Highs = UR.max(axis = 1).mean()
        
        # write objectives to outfile
        sim_objectives = np.vstack((sim_objectives, 
                                    [sim,
                                     Objective_DC_Violations, 
                                     Objective_RC_Violations, 
                                     Objective_UR_Highs]))
        
        ### ---------------------------------------------------------------------------
        # plot Debt Covenant, Rate Covenant, Uniform Rate, Variable Rate, Water Deliveries
        #DC.transpose().plot(legend = False).get_figure().savefig(output_path + '/DC_f' + str(run_id) + '_s' + str(sim) + '.png', format = 'png')
        #RC.transpose().plot(legend = False).get_figure().savefig(output_path + '/RC_f' + str(run_id) + '_s' + str(sim) + '.png', format = 'png')
        #UR.transpose().plot(legend = False).get_figure().savefig(output_path + '/UR_f' + str(run_id) + '_s' + str(sim) + '.png', format = 'png')
        #VR.transpose().plot(legend = False).get_figure().savefig(output_path + '/VR_f' + str(run_id) + '_s' + str(sim) + '.png', format = 'png')
        #WD.transpose().plot(legend = False).get_figure().savefig(output_path + '/WD_f' + str(run_id) + '_s' + str(sim) + '.png', format = 'png')
        
        # export the objective sets for quantile plotting
        DC.to_csv(output_path + '/DC_f' + str(run_id) + '_s' + str(sim) + '.csv')
        RC.to_csv(output_path + '/RC_f' + str(run_id) + '_s' + str(sim) + '.csv')
        UR.to_csv(output_path + '/UR_f' + str(run_id) + '_s' + str(sim) + '.csv')
       
    ### ---------------------------------------------------------------------------
    # write output file for all objectives
    Objectives = pd.DataFrame(sim_objectives[1:,:])
    Objectives.columns = ['Simulation ID',
                          'Debt Covenant Violation Frequency', 
                          'Rate Covenant Violation Frequency', 
                          'Peak Uniform Rate']
    Objectives.to_csv(output_path + '/Objectives_f' + str(run_id) + '.csv')
    
    
