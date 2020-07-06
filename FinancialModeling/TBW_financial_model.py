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
                triggered_project_ids):
    # check if new debt should be issued for triggered projects 
    # maturity date, year principal payments start, interest rate, 
    import numpy as np; import pandas as pd
    debt_colnames = existing_debt.columns
    for infra_id in np.unique(triggered_project_ids):
        if infra_id != -1:
            new_debt_issue = [current_year + 3, # year principal payment starts, default to current year + 3 (repayment starts after infrastructure comes online?)
                              current_year + 30, # maturity year, assume 30-year amortization schedule
                              4, # min or actual interest rate, assume flat 4% rate for future stuff
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
    # NOTE: ASSUMES IDS OF POTENTIAL PROJECTS ARE ALL > -1
    import numpy as np
    new_project_id = -1 # default value, nothing built this month
    if len(np.unique(daily_ampl_tracking_variable)) > 1: # should have -1 as only unique value unless new project is triggered
        new_project_id = np.unique(daily_ampl_tracking_variable)[1:] # get next value(s)

    return [x for x in [new_project_id]]

def calculate_DebtCoverageRatio(net_revenues, 
                                debt_service, 
                                required_deposits):
    # if ratio < 1, covenant failure
    return net_revenues / (debt_service + required_deposits)

def calculate_RateCoverageRatio(net_revenues, 
                                debt_service, 
                                required_deposits, 
                                fund_balance):
    # if ratio < 1.25, covenant failure
    return (net_revenues + fund_balance) / (debt_service + required_deposits)

def set_BudgetedDebtService(existing_debt, last_year_net_revenue, 
                            finance_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/financials', 
                            year = '2020', start_year = 2020):
    # read in approximate "caps" on annual debt service out to 2038
    # based on existing debt only - will need to add debt
    # as new projects come online
    import pandas as pd; import numpy as np
    existing_debt_targets = pd.read_excel(
            finance_path + '/Current_Future_BondIssues.xlsx', 
            sheet_name = 'FutureDSTotals')
    
    total_budgeted_debt_service = \
        existing_debt_targets['Total'].iloc[int(year) - start_year]
    
    # check for new debt/projects and adjust targets
    # existing debt in 2019 has ID nan, any debt issued
    # during modeling has a real ID
    for bond in range(0,len(existing_debt['ID'])):
        if ~np.isnan(existing_debt['ID'].iloc[bond]):
            # how much should even annual payments mean to
            # add to this year?
            remaining_principal_owed = existing_debt['Outstanding Principal'].iloc[bond]
            remaining_repayment_years = existing_debt['Maturity'].iloc[bond] - int(year)
            interest_rate = existing_debt['Interest Rate (actual or min)'].iloc[bond]
            
            # calculate even annual payments, including interest
            # TO ADD: CAP IF TOTAL DEBT SERVICE RISES TOO HIGH
            level_debt_service_payment = \
                remaining_principal_owed * \
                (interest_rate/10 * (1 + interest_rate/10)**remaining_repayment_years) / \
                ((1 + interest_rate/10)**(remaining_repayment_years-1))
            total_budgeted_debt_service += \
                level_debt_service_payment
            existing_debt['Outstanding Principal'].iloc[bond] -= \
                level_debt_service_payment - \
                interest_rate/100*remaining_principal_owed
        
    return total_budgeted_debt_service, existing_debt

def add_NewOperationalCosts(possible_projs, 
                            new_projs_this_FY, 
                            fraction_fixed_cost = 0.85):
    # if a new bond is issued to cover an infrastructure project
    # add that project's O&M costs to budget
    new_fixed_costs = 0; new_variable_costs = 0
    for proj in range(0,len(possible_projs['Project ID'])):
        if proj in new_projs_this_FY:
            new_fixed_costs += \
                possible_projs['Annual O&M Cost'].iloc[proj] * \
                fraction_fixed_cost
            new_variable_costs += \
                possible_projs['Annual O&M Cost'].iloc[proj] * \
                (1-fraction_fixed_cost)
    
    return new_fixed_costs, new_variable_costs

def estimate_UniformRate(annual_estimate, 
                         demand_estimate,
                         current_uniform_rate,
                         rs_transfer_in,
                         rs_fund_total,
                         increase_rate_cap = 0.01,
                         MANAGE_RATE = False):
    import numpy as np
    n_days_in_year = 365; convert_kgal_to_MG = 1000
    
    if MANAGE_RATE:
        # in this scenario, will need to pull from rate stabilization
        # fund to balance budget - increase transfer in if 
        # rate would naturally be greater than desired
        if current_uniform_rate * (1 + increase_rate_cap) > \
                annual_estimate / (demand_estimate * n_days_in_year) / convert_kgal_to_MG:
            # increase rate stabilization transfer in by as much as necessary,
            # capped if transfer depletes fund
            rs_transfer_in_shift = \
                np.min([\
                ((annual_estimate / (demand_estimate * n_days_in_year) / convert_kgal_to_MG) - \
                 (current_uniform_rate * (1 + increase_rate_cap))) * \
                (demand_estimate * n_days_in_year) * convert_kgal_to_MG, 
                rs_fund_total - \
                rs_transfer_in])
                
            # need to re-calculate annual estimate accordingly
            # before doing final calculation
            updated_annual_estimate = \
                annual_estimate - rs_transfer_in_shift
                
            uniform_rate = updated_annual_estimate / \
                (demand_estimate * n_days_in_year) / convert_kgal_to_MG
                
            rs_transfer_in += rs_transfer_in_shift
    else:
        uniform_rate = annual_estimate / \
            (demand_estimate * n_days_in_year) / convert_kgal_to_MG
        updated_annual_estimate = annual_estimate
    
    return uniform_rate, updated_annual_estimate, rs_transfer_in

### ----------------------------------------------------------------------- ###
### BUILD MONTHLY FINANCIAL MODEL SIMULATION (WRAPPER) FUNCTION
### assume model will run as a post-processing step
### because it will not impact daily water supply operations
### ----------------------------------------------------------------------- ###

def run_FinancialModelForSingleRealization(simulation_id,
                                           decision_variables, 
                                           rdm_factors,
                                           annual_budget,
                                           budget_projections,
                                           water_deliveries_and_sales,
                                           existing_issued_debt,
                                           potential_projects,
                                           realization_id = 1,
                                           additional_scripts_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Code/Visualization',
                                           orop_oms_output_path = 'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/cleaned', 
                                           financial_results_output_path = 'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125', 
                                           historical_financial_data_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/financials',
                                           PRE_CLEANED = True,
                                           ACTIVE_DEBUGGING = False):
    # get necessary packages
    import os; import pandas as pd; import numpy as np
    
    ### -----------------------------------------------------------------------
    # constants
    one_thousand_added_to_read_files = 1000
    start_year = 2020; convert_kgal_to_MG = 1000; n_months_in_year = 12; n_days_in_year = 365
    n_days_per_month = [31,28,31,30,31,30,31,31,30,31,30,31]
    new_projects_to_finance = []
    accumulated_new_operational_fixed_costs_from_infra = 0
    accumulated_new_operational_variable_costs_from_infra = 0
    current_FY_required_rr_deposit = 0
    current_FY_required_cip_deposit = 0
    current_FY_needed_reserve_deposit = 0
    required_other_funds_transferred_in = 0
    current_FY_final_unencumbered_funds = 0
    rate_covenant_failure_counter = 0
    debt_covenant_failure_counter = 0
    reserve_fund_balance_failure_counter = 0
    rr_fund_balance_failure_counter = 0
    COVENANT_FAILURE = 1
    
    # decision variables
    covenant_threshold_net_revenue_plus_fund_balance = decision_variables[0]
    debt_covenant_required_ratio = decision_variables[1]
    KEEP_UNIFORM_RATE_STABLE = bool(np.round(decision_variables[2])) # if range is [0,1], will round to either bound for T/F value
    managed_uniform_rate_increase_rate = decision_variables[3]
    
    # deeply uncertain factors
    rate_stabilization_minimum_ratio = rdm_factors[0]
    rate_stabilization_maximum_ratio = rdm_factors[1]
    fraction_fixed_operational_cost = rdm_factors[2]
    budgeted_unencumbered_fraction = rdm_factors[3]
    annual_budget_operating_cost_inflation_rate = rdm_factors[4]
    annual_demand_growth_rate = rdm_factors[5]
    next_FY_budgeted_tampa_tbc_delivery = rdm_factors[6] # volume in MG/fiscal year
    fixed_op_ex_factor = rdm_factors[7]
    variable_op_ex_factor = rdm_factors[8] # fyi, budgets seem very hard to balance unless these are below 0.9
    non_sales_rev_factor = rdm_factors[9]
    rate_stab_transfer_factor = rdm_factors[10]
    rr_transfer_factor = rdm_factors[11]
    other_transfer_factor = rdm_factors[12]
    required_cip_factor = rdm_factors[13]

    # outcomes to track in modeling
    financial_metrics = pd.DataFrame(['Debt Covenant Ratio', 
                                     'Rate Covenant Ratio',
                                     'Partial Debt Covenant Failure',
                                     'Partial Rate Covenant Failure',
                                     'Reserve Fund Balance Initial Failure',
                                     'R&R Fund Balance Initial Failure',
                                     'Cap on Rate Stabilization Fund Transfers In',
                                     'Rate Stabilization Funds Transferred In',
                                     'Required R&R Fund Deposit',
                                     'Required Reserve Fund Deposit',
                                     'Necessary Use of Other Funds (Rate Stabilization Supplement)']).transpose()
    
    ### -----------------------------------------------------------------------
    # step 1: read in realization data from water supply modeling
    #           should include risk metric/trigger levels for infrastructure
    #           and ID/timing of any infrastructure project built
    #   NOTE: THIS IS THE MOST TIME-CONSUMING STEP
    os.chdir(additional_scripts_path); from analysis_functions import read_AMPL_csv, read_AMPL_out
    if PRE_CLEANED:
        AMPL_cleaned_data = pd.read_csv(orop_oms_output_path + '/ampl_0' + str(one_thousand_added_to_read_files + realization_id)[1:] + '.csv')
    else:
        AMPL_cleaned_data = read_AMPL_csv(orop_oms_output_path + '/ampl_0' + str(one_thousand_added_to_read_files + realization_id)[1:] + '.csv', export = False)
    ndays_of_realization = len(AMPL_cleaned_data.iloc[:,0])
    
    # until water supply model is changed to include infrastructure adjustment
    # check for the variable in the set and put in a placeholder if it isn't there
    if 'Trigger Variable' not in AMPL_cleaned_data.columns:
        AMPL_cleaned_data['Trigger Variable'] = -1
    
    # get index for days, months, years
    # can use same file each time
    AMPL_outfile = read_AMPL_out(orop_oms_output_path + '/ampl_0001.out')
    Year  = [str(float(str(x)[:4])-1)[:4] for x in AMPL_outfile['Date']] # corrected to 2020-2039 rather than 2021-2040...
    Month = [str(x)[4:6] for x in AMPL_outfile['Date']]
    
    # get additional water supply modeling data from OMS results
    TBC_raw_sales_to_CoT = get_HarneyAugmentationFromOMS(orop_oms_output_path + '/sim_0' + str(one_thousand_added_to_read_files + realization_id)[1:] + '.mat', ndays_of_realization, realization_id)
    
    # set remaining constants, etc. based on read-in data
    deliveries_sales_colnames = water_deliveries_and_sales.columns
    annual_budget_colnames = annual_budget.columns
    budget_projections_colnames = budget_projections.columns
    past_FY_year_data = water_deliveries_and_sales.iloc[-15:-3,:] # FY 2019 (Oct 2018 - Sept 2019)
    

    ### -----------------------------------------------------------------------
    # step 2: take a monthly step loop over water supply outcomes for future
    # NOTE: record outputs EVERY month, including end-of-FY months
    #           collect summed water deliveries to each member government
    #           through uniform rate sales and TBC sales
    #           and check if any infrastructure was triggered/built
    #           also record monthly values for exporting output
    # NOTE: because model starts Jan 2021, but FY starts Oct 2021,
    #   use FY 2020 real values for initial conditions within model
#    for year in ['2020']: # FOR TESTING ONLY
#        for month in ['01','02','03','04','05','06','07','08','09']: # FOR TESTING ONLY
    for year in np.unique(Year):
        for month in np.unique(Month):
            # collect water sales data for current month
            current_month_indices = \
                [(Month[d] == month and Year[d] == year) for d in range(0,ndays_of_realization)]
            uniform_rate_member_deliveries = \
                get_MemberDeliveries(AMPL_cleaned_data.iloc[current_month_indices,:])
            delivery_slack = \
                get_DailySupplySlack(AMPL_cleaned_data.iloc[current_month_indices,:])
            month_TBC_raw_deliveries = \
                pd.Series(TBC_raw_sales_to_CoT).iloc[current_month_indices]
                
            # distribute slack, remove it from deliveries
            # slack distributed based on fraction of total delivery to 
            # each member government
            # NOTE: in future, slack could be adjusted for at a daily level
            #  but that would mean distributing moving-average slack variables
            #  from weekly to daily level first. for now, do monthly total
            slack_by_member = delivery_slack.sum().sum() * \
                uniform_rate_member_deliveries.iloc[:,:-1].sum() / \
                uniform_rate_member_deliveries.iloc[:,:-1].sum().sum()
                
            # calculate revenues from water sales
            # FY 2020 is row 3 (row index 2) of dataset
            current_year_variable_rate = \
                budget_projections['Variable Uniform Rate'].iloc[-1] 
            last_FY_member_delivery_fractions = \
                past_FY_year_data.iloc[:,1:7].sum() / \
                past_FY_year_data.iloc[:,1:7].sum().sum()
            current_year_projected_fixed_costs_to_recover = \
                budget_projections['Annual Estimate'].iloc[-1] - \
                budget_projections['Variable Operating Expenses'].iloc[-1]
    
            month_uniform_variable_sales_by_member = \
                (uniform_rate_member_deliveries.iloc[:,:-1].sum() - slack_by_member) * \
                current_year_variable_rate * convert_kgal_to_MG
            month_uniform_fixed_sales_by_member = \
                last_FY_member_delivery_fractions * \
                current_year_projected_fixed_costs_to_recover / \
                n_months_in_year
            month_tbc_sales = month_TBC_raw_deliveries.sum() * \
                budget_projections['TBC Rate'].iloc[-1] * \
                convert_kgal_to_MG
            
            # append to deliveries and sales data           
            this_month_delivery_sales_data = \
                [pd.datetime(int(year),int(month),n_days_per_month[int(month)-1]).timestamp()] + \
                [x for x in (uniform_rate_member_deliveries.iloc[:,:-1].sum() - slack_by_member)] + \
                [(uniform_rate_member_deliveries.iloc[:,-1].sum() - slack_by_member.sum())] + \
                [x for x in month_uniform_fixed_sales_by_member] + \
                [x for x in month_uniform_variable_sales_by_member] + \
                [month_TBC_raw_deliveries.sum(), month_tbc_sales]
            water_deliveries_and_sales = \
                pd.DataFrame(np.vstack((water_deliveries_and_sales,
                                        this_month_delivery_sales_data)))
            water_deliveries_and_sales.columns = \
                deliveries_sales_colnames # clean up axis titles
            water_deliveries_and_sales['Date'].iloc[-1] = \
                pd.to_datetime(pd.datetime(int(year),
                                           int(month),
                                           n_days_per_month[int(month)-1])) # clean date
            
            # track if new infrastructure is triggered in the current month
            triggered_project_ids = \
                check_ForTriggeredProjects(
                        AMPL_cleaned_data['Trigger Variable'].iloc[current_month_indices])
            for p_id in triggered_project_ids:
                new_projects_to_finance.append(p_id) # multiple projects can be triggered in same FY???
            
            # step 3 (within monthly loop): perform annual end-of-FY calculations
            #           after September calculations are done, calculate 
            #               (1) next year uniform rate estimate (fixed and variable)
            #               (2) next year TBC rate estimate
            #               (3) full budget estimate and handle annual costs like debt
            #               (4) bond covenants
            if (month == '09'): # if it is the end of the fiscal year, september 
                # collect model output from just-completed FY
                current_FY_data = water_deliveries_and_sales.iloc[-n_months_in_year:,:]
                
                ### (1) calculate "actual" budget for completed FY ------------
                # using modeled water demands, budgeted debt service, and
                # operational costs (which can be perturbed from accepted
                # budget levels to approximate actual variability/growth)
                # assume debt service doesn't vary from approved budget level
                # FYs 18,19: actual variable op costs were 17% and 24% lower than
                # approved budgeted costs. actual fixed op costs were 8% and 16%
                # lower than approved.
                
                # revenues from water supply OROP/OMS modeling
                current_FY_total_sales_revenues = \
                    current_FY_data.iloc[:,[8,9,10,11,12,13,14,15,16,17,18,19,21]].sum().sum()
                
                if ACTIVE_DEBUGGING:
                    print(year + ': Current Sales Revenues are ' + str(current_FY_total_sales_revenues))
                
                # debt service, acquisition credits, funds carried forward
                # assumed as equal to approved budget without perturbation
                # NOTE: recent approved budgets seem to consistently budget
                #   for rate stabilization funds to be used as revenue
                #   but no deposits are made (as expenditures in budget) 
                #   so I will treat 'net' budgeted rate stabilization fund
                #   transfers as just revenues, if that makes sense
                # NOTE: these values don't change between budgeted and actuals
                #   and unencumbered carry-forward is about 2% of budget for
                #   upcoming year - Sandro says this is an exact percentage
                #   but not sure how it is set/calculated
                current_FY_debt_service = \
                    budget_projections['Debt Service'].iloc[-1]
                current_FY_acquisition_credits = \
                    budget_projections['Acquisition Credits'].iloc[-1]   
                current_FY_unencumbered_funds_carried_forward = \
                    budget_projections['Unencumbered Carryover Funds'].iloc[-1]
                current_FY_budgeted_gross_revenue = \
                    budget_projections['Gross Revenues'].iloc[-1]
                    
                # operational expenses and non-sales revenue assumed to be 
                # similar to approved budget with potential perturbation factor
                # rate stabilization transfer in as revenue can also vary from
                # budgeted levels, apparently widely based on expected change
                # to any budgeted operational costs
                # fixed operating expenses in this spreadsheet include
                # water quality credits ($48k/year) and R&R projects budgeted
                current_FY_fixed_operational_expenses = \
                    budget_projections['Fixed Operating Expenses'].iloc[-1] * \
                    fixed_op_ex_factor
                current_FY_variable_operational_expenses = \
                    budget_projections['Variable Operating Expenses'].iloc[-1] * \
                    variable_op_ex_factor
                current_FY_non_sales_revenues = \
                    budget_projections['Non-Sales Revenues'].iloc[-1] * \
                    non_sales_rev_factor
                
                # transfers in are equal to budgeted amounts (with an adjustment factor)
                # unless they need to be changed to account for differences
                # in costs and revenues (done later)
                # R&R and CIP funding may change with actuals depending on what
                # smaller projects are selected for that year, so this should
                # still have some uncertainty between budgeted and actual 
                # attached
                # NOTE: SO MAYBE DON'T HAVE DEEPLY UNCERTAIN MULTIPLIERS HERE??
                current_FY_rate_stabilization_funds_transferred_in = \
                    budget_projections['Rate Stabilization Fund Transfers In'].iloc[-1] * \
                    rate_stab_transfer_factor
                current_FY_rr_funds_transferred_in = \
                    budget_projections['R&R Fund Transfers In'].iloc[-1] * \
                    rr_transfer_factor
                current_FY_other_funds_transferred_in = \
                    budget_projections['Other Funds Transfers In'].iloc[-1] * \
                    other_transfer_factor
                current_FY_rate_stabilization_fund_deposit = 0 # never a budgeted deposit to stabilization fund?
                
                
                ###  additional reserve requirements must be met --------------
                # (a) R&R fund must be at least 5% of previous FY gross rev
                # (b) Reserve Fund (Fund Balance) must be >10% gross rev
                #       AND Fund Balance + Net Revenue (gross rev - op ex)
                #       MUST BE >125% of required debt service
                # (c) Net Revenues must cover 100% of the sum of debt service,
                #       required R&R deposits, and required Reserve deposits
                previous_FY_total_sales_revenues = \
                    past_FY_year_data.iloc[:,[8,9,10,11,12,13,14,15,16,17,18,19,21]].sum().sum()
                previous_FY_acquisition_credits = \
                    annual_budget['Acquisition Credits'].iloc[-1]
                    
                # positive here means the year had a net deposit into the fund, so should be negated in gross revenue calculation
                # net transfer from stabilization fund in gross revenue calculation
                # implicitly includes unencumbered funds as deposit to fund
                # so this value is (-transfer out to be used as revenue + planned deposit to fund + unencumbered monies from previous FY)
                previous_FY_rate_stabilization_net_transfer = \
                    annual_budget['Rate Stabilization Fund (Net Change)'].iloc[-1]
                previous_FY_non_sales_revenue = \
                    annual_budget['Non-Sales Revenues'].iloc[-1]
                previous_FY_rate_stabilization_fund_balance = \
                    annual_budget['Rate Stabilization Fund (Total)'].iloc[-1]
                previous_FY_rate_stabilization_deposit = \
                    annual_budget['Rate Stabilization Fund (Deposit)'].iloc[-1] # DOES NOT INCLUDE UNENCUMBERED FUNDS
                
                previous_FY_gross_revenue = \
                    previous_FY_non_sales_revenue + \
                    previous_FY_total_sales_revenues - \
                    previous_FY_rate_stabilization_net_transfer - \
                    previous_FY_acquisition_credits
                    
                # check condition (a)
                if annual_budget['R&R Fund (Total)'].iloc[-1] < previous_FY_gross_revenue * 0.05:
                    rr_fund_balance_failure_counter += COVENANT_FAILURE
                    current_FY_required_rr_deposit = \
                        previous_FY_gross_revenue * 0.05 - \
                        annual_budget['R&R Fund (Total)'].iloc[-1]
                    
                # check conditions under (b) 
                current_FY_gross_revenue = current_FY_total_sales_revenues + \
                    current_FY_unencumbered_funds_carried_forward + \
                    current_FY_rate_stabilization_funds_transferred_in + \
                    current_FY_rr_funds_transferred_in + \
                    current_FY_other_funds_transferred_in + \
                    current_FY_non_sales_revenues - \
                    current_FY_acquisition_credits - \
                    current_FY_rate_stabilization_fund_deposit
                current_FY_net_revenue = \
                    current_FY_gross_revenue - \
                    current_FY_fixed_operational_expenses - \
                    current_FY_variable_operational_expenses 
                    
                if annual_budget['Utility Reserve Fund Balance (Total)'].iloc[-1] < \
                        current_FY_gross_revenue * 0.1:
                    reserve_fund_balance_failure_counter += COVENANT_FAILURE
                    current_FY_needed_reserve_deposit = \
                        current_FY_gross_revenue * 0.1 - \
                        annual_budget['Utility Reserve Fund Balance (Total)'].iloc[-1]
                        
                # there doesn't seem to be a codified mechanism to decide
                # about required deposits for CIP Fund except to meet next
                # FY's budgeted project costs, so will generate random 
                # value here within bounds seen in past budgets
                # From FY 2011-2017, CIP required deposits were between
                #   0.6-4% of actual gross revenues
                # also include a deeply uncertain factor to be used if wanted
                current_FY_required_cip_deposit = \
                    np.random.uniform(low = 0.006, high = 0.04) * \
                    required_cip_factor * current_FY_gross_revenue
                   
                # this is not the "true" debt coverage test (done below) but 
                # "calibrates" whether required transfers in from different 
                # funds is necessary/different than budgeted. we can track
                # when required transfers are made/how much they are and
                # what the final "leftover" must be covered from other sources
                if calculate_RateCoverageRatio(current_FY_net_revenue, 
                                               current_FY_debt_service,
                                               current_FY_required_cip_deposit + current_FY_required_rr_deposit,
                                               annual_budget['Utility Reserve Fund Balance (Total)'].iloc[-1]) < \
                        covenant_threshold_net_revenue_plus_fund_balance:
                    rate_covenant_failure_counter += COVENANT_FAILURE
                    adjustment = \
                        (covenant_threshold_net_revenue_plus_fund_balance * \
                         current_FY_debt_service) - \
                        current_FY_net_revenue - \
                        annual_budget['Utility Reserve Fund Balance (Total)'].iloc[-1]
                    current_FY_needed_reserve_deposit = \
                        np.max([current_FY_needed_reserve_deposit, adjustment])
                    
                # check condition (c)
                # here, I assume that any failure to meet the above covenants
                # or fund requirements will try to be addressed through 
                # pulling from the rate stabilization fund
                if calculate_DebtCoverageRatio(current_FY_net_revenue,
                                               current_FY_debt_service,
                                               current_FY_required_cip_deposit + current_FY_required_rr_deposit) < \
                        debt_covenant_required_ratio:
                    debt_covenant_failure_counter += COVENANT_FAILURE
                    current_FY_rate_stabilization_funds_transferred_in += \
                        current_FY_debt_service + \
                        current_FY_required_cip_deposit + \
                        current_FY_required_rr_deposit - \
                        current_FY_net_revenue
                
                # annual transfer in from rate stabilization account is capped
                # at the smallest of either:
                # (a) 3% of budgeted revenue for previous FY
                # (b) unencumberance carried forward from previous FY
                # (c) amount deposited in stabilization fund in previous FY
                current_FY_rate_stabilization_transfer_cap = \
                    np.min([current_FY_budgeted_gross_revenue * 0.03, # (a)
                            current_FY_unencumbered_funds_carried_forward, # (b)
                            previous_FY_rate_stabilization_deposit, # (c)
                            previous_FY_rate_stabilization_fund_balance]) # can't make fund go negative
                    
                # if it occurs that the maximum transfer in from the rate 
                # stabilization fund cannot balance the budget, assume other 
                # funds can be drawn from to meet the difference
                if current_FY_rate_stabilization_funds_transferred_in > \
                        current_FY_rate_stabilization_transfer_cap:
                    required_other_funds_transferred_in += \
                        current_FY_rate_stabilization_funds_transferred_in - \
                        current_FY_rate_stabilization_transfer_cap
                    current_FY_rate_stabilization_funds_transferred_in = \
                        current_FY_rate_stabilization_transfer_cap
                
                ### take record of current FY performance ---------------------
                # first, re-calculate "actual" current gross revenues and
                # net revenues, total costs including required deposits,
                # to get remaining actual budget surplus or deficit
                current_FY_final_gross_revenue = \
                    current_FY_total_sales_revenues + \
                    current_FY_unencumbered_funds_carried_forward + \
                    current_FY_rate_stabilization_funds_transferred_in + \
                    current_FY_rr_funds_transferred_in + \
                    current_FY_other_funds_transferred_in + \
                    current_FY_non_sales_revenues - \
                    current_FY_acquisition_credits - \
                    current_FY_rate_stabilization_fund_deposit
                current_FY_final_net_revenue = \
                    current_FY_gross_revenue - \
                    current_FY_fixed_operational_expenses - \
                    current_FY_variable_operational_expenses 
                current_FY_final_expenses_before_optional_deposits = \
                    current_FY_debt_service + \
                    current_FY_required_cip_deposit + \
                    current_FY_required_rr_deposit

                        
                # next, determine how remaining unencumbered funds 
                # are split among reserve funds or preserved as unencumbered
                current_FY_final_budget_surplus = \
                    current_FY_final_net_revenue - \
                    current_FY_final_expenses_before_optional_deposits
                
                # if there is a budget deficit, pull from reserve fund
                # and ignore "needed" deposits into it because they are not
                # actually part of the budget above
                # also check rate stabilization fund flows and take percentage
                # of surplus to be unencumbered funds (based on FY 18,19 
                # actuals, about 16-17% of surplus budget before any 
                # non-required deposits) - budgeted as 2.5% of prior year
                # water revenues
                if ACTIVE_DEBUGGING:
                    print(year + ': Initial Budget Surplus is ' + str(current_FY_final_budget_surplus))
                    
                if current_FY_final_budget_surplus < 0:
                    current_FY_final_reserve_fund_balance = \
                        annual_budget['Utility Reserve Fund Balance (Total)'].iloc[-1] + \
                        current_FY_final_budget_surplus 
                    current_FY_rate_stabilization_fund_deposit = 0
                else:
                    # if surplus is large enough, increase fund balance
                    # if not, increase it as much as possible
                    if current_FY_final_budget_surplus > \
                            current_FY_needed_reserve_deposit:
                        current_FY_final_reserve_fund_balance = \
                            annual_budget['Utility Reserve Fund Balance (Total)'].iloc[-1] + \
                            current_FY_needed_reserve_deposit
                        current_FY_final_budget_surplus -= current_FY_needed_reserve_deposit
                    else:
                        current_FY_final_reserve_fund_balance = \
                            annual_budget['Utility Reserve Fund Balance (Total)'].iloc[-1] + \
                            current_FY_final_budget_surplus
                        current_FY_final_budget_surplus = 0
                    
                    # mark some funds unencumbered
                    # THIS IS GOING NEGATIVE, WHY? BECAUSE UNIFORM RATE 
                    # BECOMES NEGATIVE WHEN ANNUAL ESTIMATE GOES NEGATIVE
                    # BECAUSE RATE STABILIZATION FUND HAS GROWN TOO LARGE...
                    current_FY_final_unencumbered_funds = \
                        np.min([current_FY_total_sales_revenues * \
                                    budgeted_unencumbered_fraction, 
                                current_FY_final_budget_surplus])
                    current_FY_final_budget_surplus -= \
                        current_FY_final_unencumbered_funds
                        
                    # any remaining funds go into rate stabilization
                    # this deposit gets very large, why?
                    current_FY_rate_stabilization_fund_deposit = \
                        current_FY_final_budget_surplus
                        
                if ACTIVE_DEBUGGING:        
                    print(year + ': Final Budget Surplus is ' + str(current_FY_final_budget_surplus))
                    print(year + ': Final Unencumbered is ' + str(current_FY_final_unencumbered_funds))
                    print(year + ': Surplus Deposit in Rate Stabilization is ' + str(current_FY_rate_stabilization_fund_deposit))
                
                # check R&R fund flows
                # positive value is money deposited to fund
                current_FY_final_rr_net_transfer = \
                    -current_FY_rr_funds_transferred_in + \
                    current_FY_required_rr_deposit 
                current_FY_final_rr_fund_balance = \
                    current_FY_final_rr_net_transfer + \
                    annual_budget['R&R Fund (Total)'].iloc[-1]
                
                # set rate stabilization balance
                # unencumbered funds deposited here at end of FY
                current_FY_final_rate_stabilization_fund_balance = \
                    -current_FY_rate_stabilization_funds_transferred_in + \
                    current_FY_rate_stabilization_fund_deposit + \
                    previous_FY_rate_stabilization_fund_balance + \
                    current_FY_final_unencumbered_funds
                    
            
                # finally, record outcomes
                FY_financial_metrics = pd.DataFrame([
                                        calculate_DebtCoverageRatio(
                                                current_FY_net_revenue, 
                                                current_FY_debt_service, 
                                                current_FY_required_cip_deposit + current_FY_required_rr_deposit),  
                                        calculate_RateCoverageRatio(
                                                current_FY_net_revenue, 
                                                current_FY_debt_service, 
                                                current_FY_required_cip_deposit + current_FY_required_rr_deposit, 
                                                annual_budget['Utility Reserve Fund Balance (Total)'].iloc[-1]),
                                        debt_covenant_failure_counter, 
                                        rate_covenant_failure_counter,
                                        reserve_fund_balance_failure_counter,
                                        rr_fund_balance_failure_counter,
                                        current_FY_rate_stabilization_transfer_cap,
                                        current_FY_rate_stabilization_funds_transferred_in,
                                        current_FY_required_rr_deposit,
                                        current_FY_needed_reserve_deposit,
                                        required_other_funds_transferred_in]).transpose()
                financial_metrics = pd.DataFrame(np.vstack((financial_metrics, 
                                                            FY_financial_metrics)))
                
                # record "actuals" of completed FY in historical record
                # to match columns of annual_budget
                # reminder, net rate stabilization transfer includes 
                #   unencumbered funds
                current_FY_uniform_rate = budget_projections['Uniform Rate'].iloc[-1]
                current_FY_variable_rate = budget_projections['Variable Uniform Rate'].iloc[-1]
                current_FY_tbc_rate = budget_projections['TBC Rate'].iloc[-1]
                current_FY_final_rate_stabilization_net_transfer = \
                    current_FY_rate_stabilization_fund_deposit - \
                    current_FY_rate_stabilization_funds_transferred_in + \
                    current_FY_final_unencumbered_funds
                
                FY_actuals = [int(year), 
                              current_FY_uniform_rate, 
                              current_FY_variable_rate, 
                              current_FY_tbc_rate, 
                              current_FY_non_sales_revenues, 
                              current_FY_final_gross_revenue, 
                              current_FY_debt_service, 
                              current_FY_acquisition_credits, 
                              current_FY_fixed_operational_expenses, 
                              current_FY_variable_operational_expenses, 
                              current_FY_final_reserve_fund_balance, 
                              current_FY_final_rr_fund_balance, 
                              current_FY_final_rr_net_transfer, 
                              current_FY_rate_stabilization_fund_deposit, 
                              current_FY_final_rate_stabilization_fund_balance, 
                              current_FY_final_rate_stabilization_net_transfer]
                annual_budget = pd.DataFrame(np.vstack((annual_budget, 
                                                             FY_actuals)))
                annual_budget.columns = annual_budget_colnames
                
                ### begin "budget development" for next FY --------------------
                # (a) estimate debt service and split among bond issues
                # (b) set Annual Estimate
                # (c) extimate demand and set Uniform Rates (full and variable)
                
                # check if debt for a new project has been issued
                # add to existing debt based on supply model triggered projects
                existing_issued_debt = add_NewDebt(int(year),
                                                   existing_issued_debt, 
                                                   potential_projects,
                                                   new_projects_to_finance)
                
                # set debt service target (for now, predetermined cap?)
                # and adjust existing debt based on payments on new debt
                next_FY_budgeted_debt_service, existing_issued_debt = \
                    set_BudgetedDebtService(existing_issued_debt, 
                                            current_FY_final_net_revenue, 
                                            historical_financial_data_path, 
                                            str(int(year)+1), start_year)
                
                # if a new water supply project is added, bond issue will cover capital costs
                # but also adjust annual operating costs to account for the change
                # (what fraction of added operating cost is budgeted as "variable cost"?)
                new_fixed, new_variable = add_NewOperationalCosts(
                        potential_projects, 
                        new_projects_to_finance, 
                        fraction_fixed_operational_cost)
                accumulated_new_operational_fixed_costs_from_infra += new_fixed
                accumulated_new_operational_variable_costs_from_infra += new_variable
                
                # check if acquisition credits are still being issued
                # should end after FY 2029
                next_FY_budgeted_acquisition_credit = \
                    current_FY_acquisition_credits
                if int(year) > 2029:
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
                    (budget_projections['Fixed Operating Expenses'].iloc[-1] + \
                     accumulated_new_operational_fixed_costs_from_infra) * \
                    (1 + annual_budget_operating_cost_inflation_rate)
                next_FY_budgeted_variable_operating_costs = \
                    (budget_projections['Variable Operating Expenses'].iloc[-1] + \
                     accumulated_new_operational_variable_costs_from_infra) * \
                    (1 + annual_budget_operating_cost_inflation_rate)
                    
                next_FY_budgeted_total_expenditures_before_fund_adjustment = \
                    next_FY_budgeted_fixed_operating_costs + \
                    next_FY_budgeted_variable_operating_costs + \
                    next_FY_budgeted_debt_service + \
                    next_FY_budgeted_acquisition_credit
                
                # unencumbered budget seems to ignore potential for previous
                # year to have budget issues?
                next_FY_budgeted_unencumbered_funds = \
                    current_FY_total_sales_revenues * \
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
                next_FY_budgeted_tbc_rate = current_FY_tbc_rate
                next_FY_budgeted_tbc_revenue = \
                    next_FY_budgeted_tampa_tbc_delivery * \
                    next_FY_budgeted_tbc_rate * convert_kgal_to_MG
                    
                # estimate any transfers in from funds
                # budgets note that >=$1.5M is expected to be transferred in
                # from rate stabilization annually, with a minimum balance of
                # 8.5% maintained (don't know what this percentage is for)
                # assume a floor of $1.5M transfer in, can be randomly greater
                # in increments of $100k up to 4% of current year sales revenue
                next_FY_budgeted_rate_stabilization_transfer_in = \
                    np.round(np.random.uniform(
                            low = 1.5, 
                            high = current_FY_total_sales_revenues * 0.04 / 1000000),
                             decimals = 1) * 1000000
                    
                # SECONDARY NOTE: IF THE RATE STABILIZATION FUND BECOMES VERY
                # LARGE, OR MANAGEMENT WISHES TO REDUCE THE UNIFORM RATE, 
                # MORE CAN BE TRANSFERRED IN. FOR NOW, WE ASSUME THAT THE 
                # STABILIZATION FUND IS DESIRED TO BE AT LEAST 8.5% OF 
                # SOME QUANTITY (ASSUME GROSS REVENUE) AND ALSO SHOULD NOT BE 
                # GREATER THAN 30% OF GROSS REVENUE, OTHERWISE FUNDS SHOULD
                # BE TRANSFERRED INTO THE UPCOMING BUDGET TO REDUCE THE RATE
                if ACTIVE_DEBUGGING:
                    print(year + ': Initial Budgeted Transfer from Rate Stabilization is ' + str(next_FY_budgeted_rate_stabilization_transfer_in))
                    print(year + ': Rate Stabilization Balance is ' + str(current_FY_final_rate_stabilization_fund_balance))
                    print(year + ': Rate Stabilization Balance LOW TARGET is ' + str(current_FY_final_gross_revenue * rate_stabilization_minimum_ratio))
                
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
                    print(year + ': Budgeted Transfer from Rate Stabilization is ' + str(next_FY_budgeted_rate_stabilization_transfer_in))
                        
                # estimate transfers in to cover R&R expenses
                # bounded based on ratio of projected FY 21-25
                # R&R transfers to budgeted expenses before transfers
                # (ranging from 1.8-6% of budgeted expenses)
                # also estimate deposit into R&R fund and year's end
                # is either $4.5M or $5M in 6 years of future budget
                # projections, so have it be either one randomly?
                next_FY_budgeted_rr_transfer_in = \
                    np.random.uniform(
                            low = next_FY_budgeted_total_expenditures_before_fund_adjustment * 0.018, 
                            high = next_FY_budgeted_total_expenditures_before_fund_adjustment * 0.06)
                next_FY_budgeted_rr_deposit = \
                    np.random.choice([4500000,5000000])
                    
                # double-check R&R fund balance, adjust transfers if it is
                # being drawn down too much by reducing transfer in
                if current_FY_final_rr_fund_balance - \
                        next_FY_budgeted_rr_transfer_in + \
                        next_FY_budgeted_rr_deposit \
                    < current_FY_final_gross_revenue * 0.05:
                    next_FY_budgeted_rr_transfer_in = \
                        (current_FY_final_rr_fund_balance + \
                         next_FY_budgeted_rr_deposit) - \
                        current_FY_final_gross_revenue * 0.05
                
                # estimate income from investment interest
                # seems to range from $1.5-2M annually
                # NOTE: in future, could have this tied to sum of all fund
                # balances, but unclear which are more liquid, if there is
                # an actual investment account, I'm not currently tracking that
                next_FY_budgeted_interest_income = np.random.uniform(
                            low = 1500000, high = 2000000)
                    
                # estimate any remaining deposits to other funds
                # (includes CIP and operating reserve)
                # after FY2022, this hovers around $250k a year, before that
                # could be up to $2.2M. Will make it a uniform random value
                # between $200k and $2M
                next_FY_budgeted_other_deposits = np.random.uniform(
                            low = 200000, high = 2000000)
                
                # not an actual step in any documents, but if there is a deficit
                # or loss of reserve funding in previous FY and fund balance
                # must be replenished, include a budgeted deposit to the 
                # utility reserve fund
                next_FY_budgeted_reserve_fund_deposit = 0
                if current_FY_final_reserve_fund_balance < \
                        current_FY_final_gross_revenue * 0.1:
                    next_FY_budgeted_reserve_fund_deposit += \
                        current_FY_final_gross_revenue * 0.1 - \
                        current_FY_final_reserve_fund_balance
                
                # finalize Annual Estimate estimation
                next_FY_annual_estimate = \
                    next_FY_budgeted_total_expenditures_before_fund_adjustment + \
                    next_FY_budgeted_rr_deposit + \
                    next_FY_budgeted_other_deposits - \
                    next_FY_budgeted_interest_income - \
                    next_FY_budgeted_rate_stabilization_transfer_in - \
                    next_FY_budgeted_rr_transfer_in - \
                    next_FY_budgeted_unencumbered_funds - \
                    next_FY_budgeted_tbc_revenue + \
                    next_FY_budgeted_reserve_fund_deposit
                
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
                # NOTE: MAY WANT TO TEST EFFECT OF MAINTAINING SAME RATE
                # OR ENSURING SLOWER INCREASE OF IT YEAR-TO-YEAR
                next_FY_uniform_rate, next_FY_annual_estimate, \
                next_FY_budgeted_rate_stabilization_transfer_in = \
                    estimate_UniformRate(annual_estimate = next_FY_annual_estimate, 
                                         demand_estimate = next_FY_demand_estimate_mgd, 
                                         current_uniform_rate = current_FY_uniform_rate,
                                         rs_transfer_in = next_FY_budgeted_rate_stabilization_transfer_in,
                                         rs_fund_total = current_FY_final_rate_stabilization_fund_balance,
                                         increase_rate_cap = managed_uniform_rate_increase_rate,
                                         MANAGE_RATE = KEEP_UNIFORM_RATE_STABLE)
                        
                next_FY_variable_uniform_rate = \
                    estimate_VariableRate(next_FY_annual_estimate,
                                          next_FY_budgeted_variable_operating_costs, 
                                          next_FY_uniform_rate)
                
                # collect all elements of new FY budget projection
                # to match rows of budget_projections
                # first, fill in other variables that haven't explicitly been 
                # calculated yet. 
                # in gross revenue calculation, not including litigation/
                # insurance recovery or arbitrage (ranges from $0-1.1M)
                next_FY_budgeted_uniform_sales_revenue = \
                    next_FY_demand_estimate_mgd * next_FY_uniform_rate * \
                    convert_kgal_to_MG * n_days_in_year
                
                next_FY_budgeted_water_sales_revenue = \
                    next_FY_budgeted_uniform_sales_revenue + \
                    next_FY_budgeted_tbc_revenue
                
                next_FY_budgeted_gross_revenues = \
                    next_FY_budgeted_water_sales_revenue + \
                    next_FY_budgeted_rate_stabilization_transfer_in - \
                    next_FY_budgeted_acquisition_credit + \
                    next_FY_budgeted_interest_income
                    
                next_FY_budgeted_net_revenue = \
                    next_FY_budgeted_gross_revenues - \
                    next_FY_budgeted_fixed_operating_costs - \
                    next_FY_budgeted_variable_operating_costs
                    
                # positive value here means fund is net larger than before
                next_FY_budgeted_rr_net_transfer = \
                    next_FY_budgeted_rr_deposit - \
                    next_FY_budgeted_rr_transfer_in
                
                next_FY_budget_projections = [int(year)+1, 
                                              next_FY_annual_estimate, 
                                              next_FY_budgeted_gross_revenues,
                                              next_FY_budgeted_water_sales_revenue, 
                                              next_FY_budgeted_fixed_operating_costs, 
                                              next_FY_budgeted_variable_operating_costs, 
                                              next_FY_budgeted_net_revenue, 
                                              next_FY_budgeted_debt_service, 
                                              next_FY_budgeted_acquisition_credit, 
                                              next_FY_budgeted_unencumbered_funds, 
                                              next_FY_budgeted_rr_net_transfer, 
                                              -next_FY_budgeted_rate_stabilization_transfer_in, 
                                              next_FY_budgeted_other_deposits, 
                                              next_FY_uniform_rate, 
                                              next_FY_variable_uniform_rate, 
                                              next_FY_budgeted_tbc_rate, 
                                              next_FY_budgeted_rate_stabilization_transfer_in, 
                                              next_FY_budgeted_rr_transfer_in, 
                                              0, # never any other funds budgeted transferred in?
                                              next_FY_budgeted_interest_income] # basically saying interest is only non-sales revenue...
                budget_projections = \
                    pd.DataFrame(
                            np.vstack((budget_projections, 
                                       next_FY_budget_projections)))
                budget_projections.columns = \
                    budget_projections_colnames
                
                # update most recent FY to be the current one
                past_FY_year_data = current_FY_data 
                
                # when new FY starts, reset checkers and other variables
                new_projects_to_finance = [] 
                current_FY_required_rr_deposit = 0
                current_FY_required_cip_deposit = 0
                current_FY_needed_reserve_deposit = 0
                required_other_funds_transferred_in = 0
                current_FY_final_unencumbered_funds = 0
                rate_covenant_failure_counter = 0
                debt_covenant_failure_counter = 0
                reserve_fund_balance_failure_counter = 0
                rr_fund_balance_failure_counter = 0
    
    # step 4: end loop and export results, including objectives
    metrics_colnames = [x for x in financial_metrics.iloc[0,:]]
    financial_metrics_final = pd.DataFrame(financial_metrics.iloc[1:,:])
    financial_metrics_final.columns = metrics_colnames
    
    budget_projections.to_csv(financial_results_output_path + '/output/budget_projections_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    annual_budget.to_csv(financial_results_output_path + '/output/budget_actuals_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    financial_metrics_final.to_csv(financial_results_output_path + '/output/financial_metrics_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    existing_issued_debt.to_csv(financial_results_output_path + '/output/final_debt_balance_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    water_deliveries_and_sales.to_csv(financial_results_output_path + '/output/water_deliveries_revenues_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    
    return budget_projections, annual_budget, financial_metrics_final, water_deliveries_and_sales, existing_issued_debt
    


### ----------------------------------------------------------------------- ###
### RUN ACROSS DIFFERENT MONTE CARLO SETS OF DVS
### ----------------------------------------------------------------------- ###
import numpy as np; import pandas as pd
# read in decision variables from spreadsheet
dv_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Code/TampaBayWater/FinancialModeling'
DVs = pd.read_csv(dv_path + '/financial_model_DVs.csv', header = None)

# read in deeply uncertain factors
DUFs = pd.read_csv(dv_path + '/financial_model_DUfactors.csv', header = None)

### ---------------------------------------------------------------------------
# read in historic records
historical_data_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/model_input_data'
monthly_water_deliveries_and_sales = pd.read_csv(historical_data_path + '/water_sales_and_deliveries_all_2020.csv')
historical_annual_budget_projections = pd.read_csv(historical_data_path + '/historical_budgets.csv')
annual_budget_data = pd.read_csv(historical_data_path + '/historical_actuals.csv')
existing_debt = pd.read_csv(historical_data_path + '/existing_debt.csv')
infrastructure_options = pd.read_csv(historical_data_path + '/potential_projects.csv')

### ---------------------------------------------------------------------------
# set additional required paths
hist_financial_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/financials'
scripts_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Code/Visualization'
ampl_output_path = 'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/cleaned'
financial_output_path = 'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125'

### ---------------------------------------------------------------------------
# run loop across DV sets
sim_objectives = [0,0,0,0] # sim id + three objectives
for sim in range(0,len(DVs)):
    ### ----------------------------------------------------------------------- ###
    ### RUN REALIZATION FINANCIAL MODEL ACROSS SET OF REALIZATIONS
    ### ----------------------------------------------------------------------- ###  
    dvs = [x for x in DVs.iloc[sim,:]]
    dufs = [x for x in DUFs.iloc[sim,:]]
    
    debt_covenant_years = [int(x) for x in range(2020,2040)]
    rate_covenant_years = [int(x) for x in range(2020,2040)]
    full_rate_years = [int(x) for x in range(2010,2040)]
    variable_rate_years = [int(x) for x in range(2010,2040)]
    total_deliveries_months = [int(x) for x in range(1,364)]
    for r_id in range(1,3):
        budget_projection, actuals, outcomes, water_vars, final_debt = \
            run_FinancialModelForSingleRealization(
                    simulation_id = sim,
                    decision_variables = dvs, 
                    rdm_factors = dufs,
                    annual_budget = annual_budget_data,
                    budget_projections = historical_annual_budget_projections,
                    water_deliveries_and_sales = monthly_water_deliveries_and_sales,
                    existing_issued_debt = existing_debt,
                    potential_projects = infrastructure_options,
                    realization_id = r_id, 
                    additional_scripts_path = scripts_path,
                    orop_oms_output_path = ampl_output_path, 
                    financial_results_output_path = financial_output_path, 
                    historical_financial_data_path = hist_financial_path)
        
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
    DC.transpose().plot().get_figure().savefig('C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/output/DC.png', format = 'png')
    RC.transpose().plot().get_figure().savefig('C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/output/RC.png', format = 'png')
    UR.transpose().plot().get_figure().savefig('C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/output/UR.png', format = 'png')
    VR.transpose().plot().get_figure().savefig('C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/output/VR.png', format = 'png')
    WD.transpose().plot().get_figure().savefig('C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/output/WD.png', format = 'png')
    
### ---------------------------------------------------------------------------
# write output file for all objectives
Objectives = pd.DataFrame(sim_objectives[1:,:])
Objectives.columns = ['Simulation ID',
                      'Debt Covenant Violation Frequency', 
                      'Rate Covenant Violation Frequency', 
                      'Peak Uniform Rate']
Objectives.to_csv('C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/output/Objectives.csv')
    
    