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

def estimate_UniformRate(annual_estimate, 
                         demand_estimate,
                         current_uniform_rate,
                         rs_transfer_in,
                         rs_fund_total,
                         increase_rate_cap = 0.01,
                         decrease_rate_cap = 0.01,
                         MANAGE_RATE = False):
    import numpy as np
    n_days_in_year = 365; convert_kgal_to_MG = 1000
    
    # if the rates of increase and decrease allowed are very close to zero,
    # assume the goal is to maintain the UR and skip all below calcs
    # no change to Annual Estimate because that is sum of expenditures,
    # which will not change if UR changes
    if (MANAGE_RATE) and (increase_rate_cap < 0.001) and (decrease_rate_cap < 0.001):
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
    else:
        # in this scenario, will need to pull from rate stabilization
        # fund to balance budget - increase transfer in if 
        # rate would naturally be greater than desired
        high_capped_next_FY_uniform_rate = current_uniform_rate * (1 + increase_rate_cap)
        low_capped_next_FY_uniform_rate = current_uniform_rate * (1 - decrease_rate_cap)
        uncapped_next_FY_uniform_rate = annual_estimate / (demand_estimate * n_days_in_year) / convert_kgal_to_MG
        if (MANAGE_RATE) and (high_capped_next_FY_uniform_rate < uncapped_next_FY_uniform_rate):
            # increase rate stabilization transfer in by as much as necessary,
            # capped if transfer depletes fund
            rs_transfer_in_shift = \
                np.min([\
                (uncapped_next_FY_uniform_rate - \
                 high_capped_next_FY_uniform_rate) * \
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
            
        # to maintain a flat rate, also add in ability to trap rate within bounds
        # so that it doesn't drop too far either
        elif (MANAGE_RATE) and (low_capped_next_FY_uniform_rate > uncapped_next_FY_uniform_rate):
            # decrease rate stabilization transfer in by as much as necessary,
            # capped if transfer zeroes out
            rs_transfer_in_shift = \
                np.min([\
                (low_capped_next_FY_uniform_rate - \
                 uncapped_next_FY_uniform_rate) * \
                (demand_estimate * n_days_in_year) * convert_kgal_to_MG, 
                rs_transfer_in])
                
            # need to re-calculate annual estimate accordingly
            # before doing final calculation
            updated_annual_estimate = \
                annual_estimate + rs_transfer_in_shift
                
            uniform_rate = updated_annual_estimate / \
                (demand_estimate * n_days_in_year) / convert_kgal_to_MG
                
            rs_transfer_in -= rs_transfer_in_shift
        else:
            uniform_rate = annual_estimate / \
                (demand_estimate * n_days_in_year) / convert_kgal_to_MG
            updated_annual_estimate = annual_estimate
    
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
                            AMPL_cleaned_data, TBC_raw_sales_to_CoT, Month, Year,
                            fiscal_years_to_keep, first_modeled_fy, n_months_in_year, 
                            annual_demand_growth_rate, last_fy_month,
                            financial_results_output_path, outpath):
    
    earliest_fy_budget_available = min(budget_projections['Fiscal Year'])
    earliest_fy_actuals_available = min(annual_budget['Fiscal Year'])
    earliest_fy_sales_available = min(water_deliveries_and_sales['Fiscal Year'])
    
    # because we need one extra historic year of actuals, grab it 
    prelim_year = min(fiscal_years_to_keep) - 1
    assert (earliest_fy_actuals_available <= prelim_year), \
        "Must start at later FY: actuals not available."
    current_fy_index = [tf for tf in (annual_budget['Fiscal Year'] == prelim_year)]
    annual_actuals.loc[annual_actuals.iloc[:,0] == prelim_year,:] = [v for v in annual_budget.iloc[current_fy_index,:].values]
        
    # loop across every year modeling will occur, and needed historical years,
    # to collect data into proper datasets for use in realization loop
    for fy in fiscal_years_to_keep:
        # set up budgets dataset, there are historic budgets through FY 2021
        # for historical simulation, must start at FY2017 or later, because
        # I only have budgets back to FY2016 and need one previous-FY budget
        # in the dataset for calculations
        assert (np.max([earliest_fy_budget_available,
                        earliest_fy_actuals_available,
                        earliest_fy_sales_available]) <= fy), \
                "Must start at later FY: full historic records not available."
        
        if fy <= first_modeled_fy+1:
            current_fy_index = [tf for tf in (budget_projections['Fiscal Year'] == fy)]
            annual_budgets.loc[annual_budgets.iloc[:,0] == fy,:] = [v for v in budget_projections.iloc[current_fy_index,:].values]
        
        # set up water deliveries
        # this will be tricky because need to re-arrange columns from historic
        # record as well as add in any records from modeling
        # HARD-CODED ASSUMPTION HERE (AND ABOVE WHERE MODELING DATA IS READ)
        # IS THAT MODELING BEGINS WITH JAN 1, 2021
        if fy < first_modeled_fy:
            # fill from historic data
            current_fy_index = [tf for tf in (water_deliveries_and_sales['Fiscal Year'] == fy)]
            water_delivery_sales.loc[water_delivery_sales.iloc[:,0] == fy,2:] = water_deliveries_and_sales.iloc[current_fy_index,1:-3].values
            
            # repeat for actuals from historic record (only go through FY2019)
            current_fy_index = [tf for tf in (annual_budget['Fiscal Year'] == fy)]
            annual_actuals.loc[annual_actuals.iloc[:,0] == fy,:] = [v for v in annual_budget.iloc[current_fy_index,:].values]
        elif fy == first_modeled_fy:
            # special case to fill-in data mid-year, half historic from current year half 2019 data with an increase multiplier
            # NOTE: should actually do explicit calculations as these multipliers might not perfectly translate
            #       for revenues like they do for deliveries, but it's only for 3 months right now
            # AS PROJECT CONTINUES IN REAL TIME, EVENTUALLY GET FULL 2020 DATA
            current_fy_index = [tf for tf in (water_deliveries_and_sales['Fiscal Year'] == fy)]
            last_fy_index = [tf for tf in (water_deliveries_and_sales['Fiscal Year'] == (fy-1))]
            historic_component = water_deliveries_and_sales.iloc[current_fy_index,1:-3].values
            modeled_component = water_deliveries_and_sales.iloc[last_fy_index,1:-3].values * (1+annual_demand_growth_rate)
            modeled_component = modeled_component[:(n_months_in_year-sum(current_fy_index)),:] # last X months of FY20 that we don't have observed data for
            all2020_component = np.vstack((historic_component,modeled_component))
            all2020_component[sum(current_fy_index):,7:13] = all2020_component[:(n_months_in_year-sum(current_fy_index)),7:13] # make fixed payments consistent
            water_delivery_sales.loc[(water_delivery_sales.iloc[:,0] == fy),2:] = all2020_component
        elif fy == first_modeled_fy+1:
            # another special case with 3 months of placeholder data to fill in Oct-Dec 2020
            # followed by 9 months of model data - for this year, use FY21 proposed budget to calculate revenues
            last_fy_index = [tf for tf in (water_deliveries_and_sales['Fiscal Year'] == (fy-1))]
            historic_component = water_deliveries_and_sales.iloc[last_fy_index,1:8].values
            historic_component = historic_component[:(n_months_in_year-sum(last_fy_index)),:] * (1+annual_demand_growth_rate)
            
            cot_historic_component = water_deliveries_and_sales.iloc[last_fy_index,-5].values
            cot_historic_component = cot_historic_component[:(n_months_in_year-sum(last_fy_index))] * (1+annual_demand_growth_rate)
            
            # get slack-factored monthly water deliveries
            model_index = [(int(Month[d]) <= last_fy_month and int(Year[d]) == fy) for d in range(0,len(AMPL_cleaned_data))]
            model_months = pd.Series(Month).iloc[model_index]
            uniform_rate_member_deliveries, month_TBC_raw_deliveries = \
                calculate_TrueDeliveriesWithSlack(m_index = model_index, 
                                                  m_month = model_months, 
                                                  AMPL_data = AMPL_cleaned_data, 
                                                  TBC_data = TBC_raw_sales_to_CoT)
            
            # collect full FY delivery data and plug into dataset
            all2021_component = np.vstack((historic_component,uniform_rate_member_deliveries))
            all2021_cot_tbc   = [v for v in cot_historic_component] + [v for v in month_TBC_raw_deliveries.values]
            water_delivery_sales.loc[(water_delivery_sales.iloc[:,0] == fy),2:(all2021_component.shape[1]+2)] = all2021_component
            water_delivery_sales['TBC Delivery - City of Tampa'].loc[(water_delivery_sales.iloc[:,0] == fy)] = all2021_cot_tbc
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
        # also, because if end_fiscal_year = 2020, then the last fiscal_year_to_keep value
        # will be 2019, so when doing historic simulation make sure one extra budget FY
        # is included
        last_fy_to_add = int(max(fiscal_years_to_keep)) + 1
        current_fy_index = [tf for tf in (budget_projections['Fiscal Year'] == last_fy_to_add)]
        annual_budgets.loc[annual_budgets.iloc[:,0] == last_fy_to_add,:] = [v for v in budget_projections.iloc[current_fy_index,:].values]
        
        annual_actuals.to_csv(outpath + '/historic_actuals.csv')
        annual_budgets.to_csv(outpath + '/historic_budgets.csv')
        water_delivery_sales.to_csv(outpath + '/historic_sales.csv')

    return annual_actuals, annual_budgets, water_delivery_sales

def pull_ModeledData(additional_scripts_path, orop_oms_output_path, realization_id, 
                     fiscal_years_to_keep, end_fiscal_year, first_modeled_fy, PRE_CLEANED = True):
    # get modeled water delivery data
    import os
    AMPL_cleaned_data = [np.nan]; TBC_raw_sales_to_CoT = [np.nan]; Year = [np.nan]; Month = [np.nan]
    one_thousand_added_to_read_files = 1000; n_days_in_year = 365
    if end_fiscal_year > first_modeled_fy: # meaning the last FY modeled financially is 2020
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
            
        # get additional water supply modeling data from OMS results
        TBC_raw_sales_to_CoT = get_HarneyAugmentationFromOMS(orop_oms_output_path + '/sim_0' + str(one_thousand_added_to_read_files + realization_id)[1:] + '.mat', ndays_of_realization, realization_id)
    
        # necessary to use the exact matching dates also because model
        # records are daily
        # can use same file each time
        AMPL_outfile = read_AMPL_out(orop_oms_output_path + '/ampl_0001.out')
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
    variable_op_ex_factor = rdm_factor_list[8]
    
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
    current_FY_demand_estimate_mgd = \
        past_FY_year_data['Water Delivery - Uniform Sales Total'].sum()/n_days_in_year * \
        (1 + annual_demand_growth_rate)
    current_FY_budgeted_uniform_rate = \
        annual_budgets['Uniform Rate'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    current_FY_rate_stabilization_fund_balance = \
        annual_actuals['Rate Stabilization Fund (Total)'].loc[annual_actuals['Fiscal Year'] == previous_FY].values[0]
    current_FY_budgeted_rate_stabilization_transfer_in = \
        annual_budgets['Rate Stabilization Fund Transfers In'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    
    # do a preliminary calculation to determine if the current FY 
    # annual estimate is too large to fit the determined uniform rate
    # if that is the case, adjust the rate stabilization transfer in 
    # needed to balance it
    adjusted_uniform_rate, current_FY_budgeted_annual_estimate, \
    adjusted_rate_stabilization_transfer_in = \
        estimate_UniformRate(annual_estimate = current_FY_budgeted_annual_estimate, 
                             demand_estimate = current_FY_demand_estimate_mgd, 
                             current_uniform_rate = current_FY_budgeted_uniform_rate,
                             rs_transfer_in = current_FY_budgeted_rate_stabilization_transfer_in,
                             rs_fund_total = current_FY_rate_stabilization_fund_balance,
                             increase_rate_cap = managed_uniform_rate_increase_rate,
                             decrease_rate_cap = managed_uniform_rate_decrease_rate,
                             MANAGE_RATE = KEEP_UNIFORM_RATE_STABLE)

#    print(str(FY) + ' adjusted RS transfer in is ' + str(adjusted_rate_stabilization_transfer_in))
#    print(str(FY) + ' original RS transfer in is ' + str(current_FY_budgeted_rate_stabilization_transfer_in))
    current_year_projected_fixed_costs_to_recover = \
        current_FY_budgeted_annual_estimate - \
        annual_budgets['Variable Operating Expenses'].loc[annual_budgets['Fiscal Year'] == FY].values[0] * variable_op_ex_factor - \
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
                        ACTIVE_DEBUGGING):
    # list constants and unroll RDM factors and DVs
    rate_covenant_failure_counter = 0
    debt_covenant_failure_counter = 0
    reserve_fund_balance_failure_counter = 0
    rr_fund_balance_failure_counter = 0
    COVENANT_FAILURE = 1
    current_FY_needed_reserve_deposit = 0
    
    # decision variables
    covenant_threshold_net_revenue_plus_fund_balance = dv_list[0]
    debt_covenant_required_ratio = dv_list[1]
    
    # deeply uncertain factors
    budgeted_unencumbered_fraction = rdm_factor_list[3]
    fixed_op_ex_factor = rdm_factor_list[7]
    variable_op_ex_factor = rdm_factor_list[8] # fyi, budgets seem very hard to balance unless these are below 0.9
    non_sales_rev_factor = rdm_factor_list[9]
    rate_stab_transfer_factor = rdm_factor_list[10]
    rr_transfer_factor = rdm_factor_list[11]
    other_transfer_factor = rdm_factor_list[12]
    required_cip_factor = rdm_factor_list[13]

    # give number of variables tracked in outputs
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
        
    previous_FY_rr_transfer_in = \
        annual_actuals['R&R Fund (Transfer In)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    previous_FY_rr_fund_balance = \
        annual_actuals['R&R Fund (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    
    # July 2020: gross revenues are calculated two different ways:
    # (1) "raw" where all income including transfers in are summed
    #       and no deposits or "netting" is done, which is used 
    #       for determining deposits into funds if they are too small
    # (2) "netted" where some costs and fund deposits are considered
    #       which is gross revenue used to calculate covenants
    # NOTE: energy fund transfers in not accounted for, relatively small
    previous_FY_raw_gross_revenue = \
        previous_FY_total_sales_revenues + \
        previous_FY_non_sales_revenue + \
        previous_FY_rate_stabilization_transfer_in + \
        previous_FY_unencumbered_funds + \
        previous_FY_cip_transfer_in + \
        previous_FY_rr_transfer_in
    
    # revenues from water supply OROP/OMS modeling for current year
    current_FY_total_sales_revenues = \
        current_FY_data.iloc[:,water_sales_revenue_columns].sum().sum()
    
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
    current_FY_debt_service = \
        annual_budgets['Debt Service'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    current_FY_acquisition_credits = \
        annual_budgets['Acquisition Credits'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    current_FY_unencumbered_funds = \
        annual_actuals['Unencumbered Funds'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
        
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
    # insurance income is usually less than 0.7% of previous FY gross revenues
    # misc income has a higher floor but also very small fraction
    current_FY_interest_income = \
        annual_budgets['Interest Income'].loc[annual_budgets['Fiscal Year'] == FY].values[0] * \
        non_sales_rev_factor
    current_FY_insurance_litigation_income = \
        previous_FY_raw_gross_revenue * \
        np.random.uniform(low = 0.0001, high = 0.007)
    current_FY_misc_income = \
        previous_FY_raw_gross_revenue * \
        np.random.uniform(low = 0.001, high = 0.02) 
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
    current_FY_budgeted_rate_stabilization_transfer_in = \
        annual_budgets['Rate Stabilization Fund Transfers In'].loc[annual_budgets['Fiscal Year'] == FY].values[0] * \
        rate_stab_transfer_factor
    current_FY_rr_funds_transfer_in = \
        annual_budgets['R&R Fund Transfers In'].loc[annual_budgets['Fiscal Year'] == FY].values[0] * \
        rr_transfer_factor
    current_FY_other_funds_transferred_in = \
        annual_budgets['Other Funds Transfers In'].loc[annual_budgets['Fiscal Year'] == FY].values[0] * \
        other_transfer_factor
    current_FY_rate_stabilization_fund_deposit = 0 # never a budgeted deposit to stabilization fund
    current_FY_cip_transfer_in = 0 # never a budgeted transfer in to cip fund
    current_FY_budgeted_rr_deposit = \
        annual_budgets['R&R Fund Deposit'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
        
    # it may be that the budgeted RS fund transfer in needs to be changed
    current_FY_rate_stabilization_final_transfer_in = \
        current_FY_budgeted_rate_stabilization_transfer_in
    
    ###  additional reserve requirements must be met --------------
    # (a) R&R fund must be at least 5% of previous FY gross rev
    # (b) Reserve Fund (Fund Balance) must be >10% gross rev
    #       AND Fund Balance + Net Revenue (gross rev - op ex)
    #       MUST BE >125% of required debt service
    # (c) Net Revenues must cover 100% of the sum of debt service,
    #       required R&R deposits, and required Reserve deposits
  
    # check condition (a)
    # R&R fund budgeted transfer in from fund always covers 100% of planned
    # projects. There is also a budgeted deposit - if the net change in fund
    # size violates the fund size rule, reduce the transfer in
    current_FY_rr_net_deposit = \
        current_FY_budgeted_rr_deposit - current_FY_rr_funds_transfer_in
    if ((previous_FY_raw_gross_revenue * 0.05) > previous_FY_rr_fund_balance + current_FY_rr_net_deposit) and (current_FY_rr_net_deposit > 0):
        # reduce budgeted transfer in if it would deplete the fund
        # so that the transfer in and deposit are equal (no net fund change)
        current_FY_rr_funds_transfer_in -= current_FY_rr_net_deposit
    
    if ((previous_FY_raw_gross_revenue * 0.05) > previous_FY_rr_fund_balance):
        # if the current fund level is already in violation, cancel transfer in
        # and ensure that planned deposit is at least large enough to compensate
        # only count a "failure" if reducing the budgeted transfer in
        # from the fund cannot satisfy this condition
        current_FY_rr_funds_transfer_in = 0
        rr_fund_balance_failure_counter += COVENANT_FAILURE
        
        # figure out what the necessary deposit is, and ensure the budgeted 
        # deposit is at least that large
        current_FY_budgeted_rr_deposit = \
            previous_FY_raw_gross_revenue * 0.05 - previous_FY_rr_fund_balance
    elif ((previous_FY_raw_gross_revenue * 0.05) > previous_FY_rr_fund_balance + current_FY_rr_net_deposit):
        # if there is already a net transfer out of the fund (net deposit is negative)
        # and this violates the rule, reduce the transfer in 
        # (add the negative difference)
        current_FY_rr_funds_transfer_in += current_FY_rr_net_deposit

    print(str(FY) + ': GR: Unencumbered is ' + str(current_FY_unencumbered_funds))
    print(str(FY) + ': GR: RS Transfer In is ' + str(current_FY_rate_stabilization_final_transfer_in))
    print(str(FY) + ': GR: R&R Transfer In is ' + str(current_FY_rr_funds_transfer_in))
    print(str(FY) + ': GR: Other Transfer In is ' + str(current_FY_other_funds_transferred_in))
    print(str(FY) + ': GR: Non-Sales Rev is ' + str(current_FY_non_sales_revenue))
    print(str(FY) + ': GR: RS Deposit is ' + str(current_FY_rate_stabilization_fund_deposit))
        
    # check conditions under (b) 
    # there is never a budgeted deposit to the reserve fund, so don't need to
    # repeat all the trouble above like with the R&R Fund
    previous_FY_reserve_fund_balance = \
        annual_actuals['Utility Reserve Fund Balance (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    if previous_FY_reserve_fund_balance < (previous_FY_raw_gross_revenue * 0.1):
        reserve_fund_balance_failure_counter += COVENANT_FAILURE
        current_FY_needed_reserve_deposit = \
            previous_FY_raw_gross_revenue * 0.1 - previous_FY_reserve_fund_balance
            
    # there doesn't seem to be a codified mechanism to decide
    # about required deposits for CIP Fund except to meet next
    # FY's budgeted project costs, so will generate random 
    # value here within bounds seen in past budgets
    # From FY 2013-2019, CIP required deposits were between
    #   1-3% of actual previous fy raw gross revenues
    # also include a deeply uncertain factor to be used if wanted
    current_FY_cip_deposit = \
        np.random.uniform(low = 0.01, high = 0.03) * \
        required_cip_factor * previous_FY_raw_gross_revenue
        
    # similarly, apply a random factor to set CIP fund transfer in
    # based on past FY actuals, transfer in is between 0.2-2%
    # of past fy raw gross revenues
    current_FY_cip_deposit = \
        np.random.uniform(low = 0.002, high = 0.02) * \
        required_cip_factor * previous_FY_raw_gross_revenue
        
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
        current_FY_rate_stabilization_fund_deposit
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
            
    # this is not the "true" debt coverage test (done below) but 
    # "calibrates" whether required transfers in from different 
    # funds is necessary/different than budgeted. we can track
    # when required transfers are made/how much they are and
    # what the final "leftover" must be covered from other sources
    if calculate_RateCoverageRatio(current_FY_netted_net_revenue,
                                   current_FY_debt_service,
                                   current_FY_cip_deposit + current_FY_budgeted_rr_deposit,
                                   previous_FY_reserve_fund_balance) < \
            covenant_threshold_net_revenue_plus_fund_balance:
        rate_covenant_failure_counter += COVENANT_FAILURE
        adjustment = \
            (covenant_threshold_net_revenue_plus_fund_balance * \
             (current_FY_debt_service + current_FY_cip_deposit + current_FY_budgeted_rr_deposit)) - \
            current_FY_netted_net_revenue - previous_FY_reserve_fund_balance
        current_FY_needed_reserve_deposit = \
            np.max([current_FY_needed_reserve_deposit, adjustment])
        current_FY_rate_stabilization_final_transfer_in = \
            np.max([current_FY_rate_stabilization_final_transfer_in,
                    adjustment])
    
    # annual transfer in from rate stabilization account is capped
    # at the smallest of either:
    # (a) 3% of budgeted revenue for previous FY
    # (b) unencumberance carried forward from previous FY
    # (c) amount deposited in stabilization fund in previous FY
    previous_FY_budgeted_raw_gross_revenue = \
        annual_budgets['Gross Revenues'].loc[annual_budgets['Fiscal Year'] == (FY-1)].values[0]
    current_FY_rate_stabilization_transfer_cap = \
        np.min([previous_FY_budgeted_raw_gross_revenue * 0.03, # (a)
                current_FY_unencumbered_funds, # (b)
                previous_FY_rate_stabilization_deposit, # (c)
                previous_FY_rate_stabilization_fund_balance]) # can't make fund go negative
    
    # if it occurs that the maximum transfer in from the rate 
    # stabilization fund cannot balance the budget, assume other 
    # funds can be drawn from to meet the difference
    required_other_funds_transferred_in = 0
    if current_FY_rate_stabilization_final_transfer_in > \
            current_FY_rate_stabilization_transfer_cap:
        required_other_funds_transferred_in += \
            current_FY_rate_stabilization_final_transfer_in - \
            current_FY_rate_stabilization_transfer_cap
        current_FY_rate_stabilization_final_transfer_in = \
            current_FY_rate_stabilization_transfer_cap
            
            
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
        current_FY_rate_stabilization_fund_deposit
    current_FY_netted_net_revenue = \
        current_FY_netted_gross_revenue - \
        current_FY_fixed_operational_expenses - \
        current_FY_variable_operational_expenses 
    current_FY_expenses_before_optional_deposits = \
        current_FY_debt_service + \
        current_FY_cip_deposit + \
        current_FY_budgeted_rr_deposit

    # next, determine how remaining unencumbered funds 
    # are split among reserve funds or preserved as unencumbered
    current_FY_budget_surplus = \
        current_FY_netted_net_revenue - \
        current_FY_expenses_before_optional_deposits
    
    # if there is a budget deficit, pull from reserve fund
    # and ignore "needed" deposits into it because they are not
    # actually part of the budget above
    # also check rate stabilization fund flows and take percentage
    # of surplus to be unencumbered funds (based on FY 18,19 
    # actuals, about 16-17% of surplus budget before any 
    # non-required deposits) - budgeted as 2.5% of prior year
    # water revenues
    if ACTIVE_DEBUGGING:
        print(str(FY) + ': Initial Budget Surplus is ' + str(current_FY_budget_surplus))
    
    # July 2020: any required transfers from 'other' funds
    # to cover budget shortfalls above will be pulled from 
    # reserve fund balance
    current_FY_final_reserve_fund_balance = \
        annual_actuals['Utility Reserve Fund Balance (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0]
    if current_FY_budget_surplus < 0:
        current_FY_final_reserve_fund_balance += current_FY_budget_surplus
        current_FY_rate_stabilization_fund_deposit = 0
    else:
        # if surplus is large enough, increase fund balance
        # if not, increase it as much as possible
        if current_FY_budget_surplus > current_FY_needed_reserve_deposit:
            current_FY_final_reserve_fund_balance += current_FY_needed_reserve_deposit
            current_FY_budget_surplus -= current_FY_needed_reserve_deposit
        else:
            current_FY_final_reserve_fund_balance += current_FY_budget_surplus
            current_FY_budget_surplus = 0
        
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
        # and reserve fund - split remaining balance 50/50
        current_FY_rate_stabilization_fund_deposit += \
            current_FY_budget_surplus * 0.5
        current_FY_final_reserve_fund_balance += \
            current_FY_budget_surplus * 0.5
            
    if ACTIVE_DEBUGGING:        
        print(str(FY) + ': Final Budget Surplus is ' + str(current_FY_budget_surplus))
        print(str(FY) + ': Final Unencumbered is ' + str(current_FY_final_unencumbered_funds))
        print(str(FY) + ': Surplus Deposit in Rate Stabilization is ' + str(current_FY_rate_stabilization_fund_deposit))
    
    # finally, take the final budget calculations of gross/net revenues
    # "raw" values and "netted" values
    current_FY_final_netted_gross_revenue = \
        current_FY_total_sales_revenues + \
        current_FY_unencumbered_funds + \
        current_FY_rate_stabilization_final_transfer_in + \
        current_FY_non_sales_revenue - \
        current_FY_acquisition_credits - \
        current_FY_rate_stabilization_fund_deposit
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
        current_FY_rr_funds_transfer_in
#    current_FY_final_raw_net_revenue = \
#        current_FY_final_raw_gross_revenue - \
#        current_FY_fixed_operational_expenses - \
#        current_FY_variable_operational_expenses - \
#        current_FY_acquisition_credits
    
    # check R&R fund flows
    # positive value is money deposited to fund
    current_FY_final_rr_net_transfer = \
        -current_FY_rr_funds_transfer_in + \
        current_FY_budgeted_rr_deposit 
    current_FY_final_rr_fund_balance = \
        current_FY_final_rr_net_transfer + \
        previous_FY_rr_fund_balance
    
    # set rate stabilization balance
    # unencumbered funds deposited here at end of FY
    current_FY_final_rate_stabilization_fund_balance = \
        -current_FY_rate_stabilization_final_transfer_in + \
        current_FY_rate_stabilization_fund_deposit + \
        previous_FY_rate_stabilization_fund_balance + \
        current_FY_final_unencumbered_funds
        
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
                                current_FY_cip_deposit + current_FY_budgeted_rr_deposit, 
                                previous_FY_reserve_fund_balance),
                        debt_covenant_failure_counter, 
                        rate_covenant_failure_counter,
                        reserve_fund_balance_failure_counter,
                        rr_fund_balance_failure_counter,
                        current_FY_rate_stabilization_transfer_cap,
                        current_FY_rate_stabilization_final_transfer_in,
                        current_FY_budgeted_rr_deposit,
                        current_FY_needed_reserve_deposit,
                        required_other_funds_transferred_in, 
                        current_FY_final_netted_net_revenue]).transpose().values

    # record "actuals" of completed FY in historical record
    # to match columns of annual_budget
    # reminder, net rate stabilization transfer includes 
    #   unencumbered funds
    current_FY_uniform_rate = annual_budgets['Uniform Rate'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    current_FY_variable_rate = annual_budgets['Variable Uniform Rate'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    current_FY_tbc_rate = annual_budgets['TBC Rate'].loc[annual_budgets['Fiscal Year'] == FY].values[0]
    current_FY_final_cip_fund_balance = \
        annual_actuals['CIP Fund (Total)'].loc[annual_actuals['Fiscal Year'] == (FY-1)].values[0] + \
        current_FY_cip_deposit - current_FY_cip_transfer_in

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
                      current_FY_budgeted_rr_deposit,
                      current_FY_rr_funds_transfer_in,
                      current_FY_rate_stabilization_fund_deposit,
                      current_FY_final_rate_stabilization_fund_balance,
                      current_FY_rate_stabilization_final_transfer_in,
                      current_FY_unencumbered_funds,
                      current_FY_final_cip_fund_balance,
                      current_FY_cip_deposit,
                      current_FY_cip_transfer_in,
                      current_FY_misc_income,
                      current_FY_insurance_litigation_income]).transpose().values

    return annual_actuals, annual_budgets, financial_metrics
    
def calculate_NextFYBudget(FY, current_FY_data, past_FY_year_data, 
                            annual_budgets, annual_actuals, financial_metrics, 
                            existing_issued_debt, new_projects_to_finance, potential_projects,
                            accumulated_new_operational_fixed_costs_from_infra,
                            accumulated_new_operational_variable_costs_from_infra,
                            historical_financial_data_path,
                            dv_list, 
                            rdm_factor_list,
                            ACTIVE_DEBUGGING):
    # set constants and variables as necessary
    first_modeled_fy = 2020
    convert_kgal_to_MG = 1000
    n_days_in_year = 365
    
    # decision variables
    KEEP_UNIFORM_RATE_STABLE = bool(np.round(dv_list[2])) # if range is [0,1], will round to either bound for T/F value
    managed_uniform_rate_increase_rate = dv_list[3]
    managed_uniform_rate_decrease_rate = dv_list[4]
    
    # deeply uncertain factors
    rate_stabilization_minimum_ratio = rdm_factor_list[0]
#    rate_stabilization_maximum_ratio = rdm_factor_list[1]
    fraction_variable_operational_cost = rdm_factor_list[2]
    budgeted_unencumbered_fraction = rdm_factor_list[3]
    annual_budget_fixed_operating_cost_inflation_rate = rdm_factor_list[4]
    annual_demand_growth_rate = rdm_factor_list[5]
    next_FY_budgeted_tampa_tbc_delivery = rdm_factor_list[6] # volume in MG/fiscal year
    annual_budget_variable_operating_cost_inflation_rate = rdm_factor_list[14]
    
    current_FY_final_reserve_fund_balance = \
        annual_actuals['Utility Reserve Fund Balance (Total)'].loc[annual_actuals['Fiscal Year'] == FY].values[0]
        
    # check if debt for a new project has been issued
    # add to existing debt based on supply model triggered projects
    existing_issued_debt = add_NewDebt(FY,
                                       existing_issued_debt, 
                                       potential_projects,
                                       new_projects_to_finance)
    
    # set debt service target (for now, predetermined cap?)
    # and adjust existing debt based on payments on new debt
    # only do this if simulating future, otherwise no need
    if FY >= first_modeled_fy:
        current_FY_final_net_revenue = financial_metrics['Final Net Revenues'].loc[financial_metrics['Fiscal Year'] == FY].values[0]
        next_FY_budgeted_debt_service, existing_issued_debt = \
            set_BudgetedDebtService(existing_issued_debt, 
                                    current_FY_final_net_revenue, 
                                    historical_financial_data_path, 
                                    str(FY+1), first_modeled_fy)
    else:
        next_FY_budgeted_debt_service = annual_budgets['Debt Service'].loc[annual_budgets['Fiscal Year'] == (FY+1)].values[0]
    
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
        
    # estimate any transfers in from funds
    # budgets note that >=$1.5M is expected to be transferred in
    # from rate stabilization annually, with a minimum balance of
    # 8.5% maintained (don't know what this percentage is for)
    # assume a floor of $1.5M transfer in, can be randomly greater
    # in increments of $100k up to 4% of current year sales revenue
    next_FY_budgeted_rate_stabilization_transfer_in = \
        np.round(np.random.uniform(
                low = 1.5, 
                high = current_FY_data.iloc[:,water_sales_revenue_columns].sum().sum() * 0.04 / 1000000),
                 decimals = 1) * 1000000
        
    # estimate transfers in for CIP from CIP Fund
    # (aka capital improvement not covered by uniform rate, R&R fund, or debt)
    # from historical budgets, this is always zero
    next_FY_budgeted_cip_fund_transfer_in = 0
        
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
    # also estimate deposit into R&R fund and year's end
    # is either $4.5M or $5M in 6 years of future budget
    # projections, so have it be either one randomly?
    # come off this assumption to better match historical record,
    # let it range $2.5-5M observed over past
    next_FY_budgeted_rr_transfer_in = \
        np.random.uniform(
                low = next_FY_budgeted_total_expenditures_before_fund_adjustment * 0.018, 
                high = next_FY_budgeted_total_expenditures_before_fund_adjustment * 0.06)
    next_FY_budgeted_rr_deposit = \
        np.round(np.random.uniform(low = 2.5, high = 5),
                 decimals = 1) * 1000000
        
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
    sinking_fund_size_approximator = next_FY_budgeted_debt_service* 1.6
    cip_and_operating_fund_size_approximator = next_FY_budgeted_variable_operating_costs
    approximate_enterprise_fund_balance = \
        current_FY_final_rate_stabilization_fund_balance + \
        current_FY_final_reserve_fund_balance + \
        current_FY_final_rr_fund_balance + \
        next_FY_budgeted_variable_operating_costs + \
        sinking_fund_size_approximator + \
        cip_and_operating_fund_size_approximator
    next_FY_budgeted_interest_income = approximate_enterprise_fund_balance * \
        np.random.uniform(low = 0.003, high = 0.007)
        
    # estimate any remaining deposits to other funds
    # (includes operating reserve)
    # after FY2022, this hovers around $250k a year, before that
    # could be up to $2.2M. Will make it a uniform random value
    # between $200k and $2M
    next_FY_budgeted_other_deposits = np.random.uniform(
                low = 200000, high = 2000000)
    
    # estimate CIP Fund deposit - in the past are
    # 0.001-1% of last FY raw gross revenue
    past_FY_raw_gross_revenue = \
        annual_budgets['Gross Revenues'].loc[annual_budgets['Fiscal Year'] == (FY-1)].values[0]
    next_FY_budgeted_cip_fund_deposit = \
        np.random.uniform(low = past_FY_raw_gross_revenue * 0.001, 
                          high = past_FY_raw_gross_revenue * 0.01)
    
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
        next_FY_budgeted_other_deposits + \
        next_FY_budgeted_reserve_fund_deposit + \
        next_FY_budgeted_cip_fund_deposit
    
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
                             current_uniform_rate = annual_budgets['Uniform Rate'].loc[annual_budgets['Fiscal Year'] == FY].values[0],
                             rs_transfer_in = next_FY_budgeted_rate_stabilization_transfer_in,
                             rs_fund_total = current_FY_final_rate_stabilization_fund_balance,
                             increase_rate_cap = managed_uniform_rate_increase_rate,
                             decrease_rate_cap = managed_uniform_rate_decrease_rate,
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
    
    next_FY_budgeted_raw_gross_revenues = \
        next_FY_budgeted_water_sales_revenue + \
        next_FY_budgeted_rate_stabilization_transfer_in + \
        next_FY_budgeted_interest_income + \
        next_FY_budgeted_unencumbered_funds + \
        next_FY_budgeted_rr_transfer_in
        
    next_FY_budgeted_raw_net_revenue = \
        next_FY_budgeted_raw_gross_revenues - \
        next_FY_budgeted_fixed_operating_costs - \
        next_FY_budgeted_variable_operating_costs
    
    next_FY_budgeted_other_transfer_in = 0
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
                                  next_FY_budgeted_other_deposits, 
                                  next_FY_uniform_rate, 
                                  next_FY_variable_uniform_rate, 
                                  next_FY_budgeted_tbc_rate, 
                                  next_FY_budgeted_rate_stabilization_transfer_in, 
                                  next_FY_budgeted_rr_transfer_in, 
                                  next_FY_budgeted_other_transfer_in, # never any other funds budgeted transferred in?
                                  next_FY_budgeted_interest_income, 
                                  next_FY_budgeted_cip_fund_transfer_in,
                                  next_FY_budgeted_cip_fund_deposit]).transpose().values # basically saying interest is only non-sales revenue... 

    
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
                                           potential_projects,
                                           realization_id = 1,
                                           additional_scripts_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Code/Visualization',
                                           orop_oms_output_path = 'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/cleaned', 
                                           financial_results_output_path = 'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125', 
                                           historical_financial_data_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/financials',
                                           outpath = 'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/output',
                                           PRE_CLEANED = True,
                                           ACTIVE_DEBUGGING = False):
    # get necessary packages
    import pandas as pd; import numpy as np
    
    ### -----------------------------------------------------------------------
    # constants (some assigned elsewhere...)
    last_fy_month = 9; first_modeled_fy = 2020
    n_months_in_year = 12
    accumulated_new_operational_fixed_costs_from_infra = 0
    accumulated_new_operational_variable_costs_from_infra = 0
    
    # deeply uncertain factors ACTIVE IN THIS LAYER OF MODEL (rest elsewhere)
    annual_demand_growth_rate = rdm_factors[5]

    # give number of variables tracked in outputs
    n_financial_metric_outcomes = 13
    n_actual_budget_outcomes = 23
    n_proposed_budget_outcomes = 22
    n_deliveries_sales_variables = 23
                
    ### -----------------------------------------------------------------------
    # step 0: create partially empty final tables based on range of dates
    #           assume that modeling operates on scale of fiscal years
    #   based on the starting fiscal year, will also need the preceeding FY
    #   for some calculations.
    assert (start_fiscal_year < end_fiscal_year), 'End year must be greater than start year.'
    assert (start_fiscal_year <= first_modeled_fy), 'Start FY must be <= first modeled FY (2020)'
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
                                    'Final Net Revenues']
    
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
        pull_ModeledData(additional_scripts_path, orop_oms_output_path, realization_id, 
                         fiscal_years_to_keep, end_fiscal_year, first_modeled_fy, PRE_CLEANED)
    
    ### -----------------------------------------------------------------------
    # step 1b: collect existing data in future output files 
    #           along with modeled data of future years
    annual_actuals, annual_budgets, water_delivery_sales = \
        collect_ExistingRecords(annual_actuals, annual_budgets, water_delivery_sales,
                                annual_budget, budget_projections, water_deliveries_and_sales, 
                                AMPL_cleaned_data, TBC_raw_sales_to_CoT, Month, Year,
                                fiscal_years_to_keep, first_modeled_fy, n_months_in_year, 
                                annual_demand_growth_rate, last_fy_month, 
                                financial_results_output_path, outpath)

    ### -----------------------------------------------------------------------
    # step 2: take an annual step loop over water supply outcomes for future
    #           collect summed water deliveries to each member government
    #           through uniform rate sales and TBC sales
    #           and check if any infrastructure was triggered/built
    #           also record monthly values for exporting output
    for FY in range(start_fiscal_year, end_fiscal_year):
        # when new FY starts, reset checkers and other variables
        new_projects_to_finance = []
        
        # calculate revenues from water sales, collect within dataset
        water_delivery_sales, past_FY_year_data = \
            calculate_WaterSalesForFY(FY, water_delivery_sales, 
                                      annual_budgets, annual_actuals,
                                      dv_list = decision_variables, 
                                      rdm_factor_list = rdm_factors,
                                      annual_demand_growth_rate = annual_demand_growth_rate)
        
        # track if new infrastructure is triggered in the current FY
        if ((len(AMPL_cleaned_data) > 1) and (FY > first_modeled_fy)): # if using model data
            model_index = [(int(Month[d]) <= last_fy_month and int(Year[d]) == FY) or (int(Month[d]) > last_fy_month and int(Year[d]) == (FY-1)) for d in range(0,len(AMPL_cleaned_data))]
            triggered_project_ids = \
                check_ForTriggeredProjects(
                        AMPL_cleaned_data['Trigger Variable'].loc[model_index])
            for p_id in triggered_project_ids:
                new_projects_to_finance.append(p_id) # multiple projects can be triggered in same FY???
            
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
                                dv_list = decision_variables, 
                                rdm_factor_list = rdm_factors,
                                ACTIVE_DEBUGGING = ACTIVE_DEBUGGING)


        ### begin "budget development" for next FY --------------------
        # (a) estimate debt service and split among bond issues
        # (b) set Annual Estimate
        # (c) extimate demand and set Uniform Rates (full and variable)
        annual_budgets, existing_issued_debt, potential_projects, \
                accumulated_new_operational_fixed_costs_from_infra, \
                accumulated_new_operational_variable_costs_from_infra = \
            calculate_NextFYBudget(FY, current_FY_data, past_FY_year_data, 
                                        annual_budgets, annual_actuals, financial_metrics, 
                                        existing_issued_debt, new_projects_to_finance, potential_projects,
                                        accumulated_new_operational_fixed_costs_from_infra,
                                        accumulated_new_operational_variable_costs_from_infra,
                                        historical_financial_data_path,
                                        dv_list = decision_variables, 
                                        rdm_factor_list = rdm_factors,
                                        ACTIVE_DEBUGGING = ACTIVE_DEBUGGING)
    
    # step 4: end loop and export results, including objectives    
    annual_budgets.to_csv(outpath + '/budget_projections_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    annual_actuals.to_csv(outpath + '/budget_actuals_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    financial_metrics.to_csv(outpath + '/financial_metrics_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    existing_issued_debt.to_csv(outpath + '/final_debt_balance_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    water_delivery_sales.to_csv(outpath + '/water_deliveries_revenues_s' + str(simulation_id) + '_r' + str(realization_id) + '.csv')
    
    return annual_budgets, annual_actuals, financial_metrics, water_delivery_sales, existing_issued_debt
    


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
output_path = 'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/output'

### ---------------------------------------------------------------------------
# run loop across DV sets
sim_objectives = [0,0,0,0] # sim id + three objectives
start_fy = 2015; end_fy = 2020; n_reals_tested = 12
#for sim in range(0,len(DVs)): # sim = 0 for testing
for sim in range(1,2): # FOR RUNNING HISTORICALLY ONLY
    ### ----------------------------------------------------------------------- ###
    ### RUN REALIZATION FINANCIAL MODEL ACROSS SET OF REALIZATIONS
    ### ----------------------------------------------------------------------- ###  
    dvs = [x for x in DVs.iloc[sim,:]]
    dufs = [x for x in DUFs.iloc[sim,:]]
    
    debt_covenant_years = [int(x) for x in range(start_fy,end_fy)]
    rate_covenant_years = [int(x) for x in range(start_fy,end_fy)]
    full_rate_years = [int(x) for x in range(start_fy-2,end_fy)]
    variable_rate_years = [int(x) for x in range(start_fy-2,end_fy)]
    total_deliveries_months = [int(x) for x in range(1,(end_fy - start_fy + 1)*12+1)]
#    for r_id in range(1,n_reals_tested):
    for r_id in range(1,2): # r_id = 1 for testing
        # run this line for testing : ACTIVE_DEBUGGING = True; PRE_CLEANED = True; start_fiscal_year = 2015;end_fiscal_year = 2020;simulation_id = sim;decision_variables = dvs;rdm_factors = dufs;annual_budget = annual_budget_data;budget_projections = historical_annual_budget_projections;water_deliveries_and_sales = monthly_water_deliveries_and_sales;existing_issued_debt = existing_debt;potential_projects = infrastructure_options;realization_id = r_id;additional_scripts_path = scripts_path;orop_oms_output_path = ampl_output_path;financial_results_output_path = financial_output_path;historical_financial_data_path = hist_financial_path
        
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
                    potential_projects = infrastructure_options,
                    realization_id = r_id, 
                    additional_scripts_path = scripts_path,
                    orop_oms_output_path = ampl_output_path, 
                    financial_results_output_path = financial_output_path, 
                    historical_financial_data_path = hist_financial_path,
                    outpath = output_path,
                    PRE_CLEANED = True, ACTIVE_DEBUGGING = False)
        
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
    DC.transpose().plot(legend = False).get_figure().savefig(output_path + '/DC_s' + str(sim) + '.png', format = 'png')
    RC.transpose().plot(legend = False).get_figure().savefig(output_path + '/RC_s' + str(sim) + '.png', format = 'png')
    UR.transpose().plot(legend = False).get_figure().savefig(output_path + '/UR_s' + str(sim) + '.png', format = 'png')
    VR.transpose().plot(legend = False).get_figure().savefig(output_path + '/VR_s' + str(sim) + '.png', format = 'png')
    WD.transpose().plot(legend = False).get_figure().savefig(output_path + '/WD_s' + str(sim) + '.png', format = 'png')
   
### ---------------------------------------------------------------------------
# write output file for all objectives
Objectives = pd.DataFrame(sim_objectives[1:,:])
Objectives.columns = ['Simulation ID',
                      'Debt Covenant Violation Frequency', 
                      'Rate Covenant Violation Frequency', 
                      'Peak Uniform Rate']
Objectives.to_csv(output_path + '/Objectives.csv')
    
    