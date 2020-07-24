# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 23:09:49 2020
TAMPA BAY WATER AUTHORITY FINANCIAL MODEL - BUILD HISTORICAL FINANCIAL RECORDS
all code used to collect and clean historic financial data is now here
and will be used to generate the final-stage input data for the 
simulation model

@author: dgorelic
"""

def build_HistoricalMonthlyWaterDeliveriesAndSalesData(historical_financial_data_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/financials'):
    # also need separate tracked data for water deliveries (to calculate sales revenue) to each member for true-up - WaterSalesByMember_cleaned
    #   (can I get this by month?)
    import os; import pandas as pd; import numpy as np
    os.chdir(historical_financial_data_path)
    convert_kgal_to_MG = 1000
    
    MonthlyWaterSales = ['Date',
                         'Water Delivery - City of St. Petersburg',
                         'Water Delivery - Pinellas County', 
                         'Water Delivery - City of Tampa (Uniform)', 
                         'Water Delivery - Hillsborough County',  
                         'Water Delivery - Pasco County', 
                         'Water Delivery - City of New Port Richey', 
                         'Water Delivery - Uniform Sales Total']
    
    # read in Water sales revenue tables to get monthly deliveries
    monthly_water_sales_by_member = pd.DataFrame(np.array(MonthlyWaterSales)).transpose()
    for year in range(2010,2020):
        if os.path.exists('Water Sales Revenue ' + str(year) + '-WS.xlsx'):
            sales_data = pd.read_excel('Water Sales Revenue ' + str(year) + '-WS.xlsx', 
                                       skiprows = 3)
            monthly_water_sales_by_member = pd.DataFrame(np.vstack((monthly_water_sales_by_member, sales_data.iloc[1:13,0:8])))
        elif os.path.exists('Water Sales Revenue ' + str(year) + ' WS.xlsx'):
            sales_data = pd.read_excel('Water Sales Revenue ' + str(year) + ' WS.xlsx', 
                                       skiprows = 3)
            monthly_water_sales_by_member = pd.DataFrame(np.vstack((monthly_water_sales_by_member, sales_data.iloc[1:13,0:8])))
        elif os.path.exists('Water Sales Revenue ' + str(year) + ' WS.xls'):
            sales_data = pd.read_excel('Water Sales Revenue ' + str(year) + ' WS.xls', 
                                       skiprows = 3)
            monthly_water_sales_by_member = pd.DataFrame(np.vstack((monthly_water_sales_by_member, sales_data.iloc[1:13,0:8])))
        elif os.path.exists('Water Sales Revenue ' + str(year) + ' WS-FINAL.xls'):
            sales_data = pd.read_excel('Water Sales Revenue ' + str(year) + ' WS-FINAL.xls', 
                                       skiprows = 3)
            monthly_water_sales_by_member = pd.DataFrame(np.vstack((monthly_water_sales_by_member, sales_data.iloc[1:13,0:8])))
            
    # clean and fill in missing data in 2015
    monthly_water_sales_by_member.columns = MonthlyWaterSales
    monthly_water_sales_by_member = monthly_water_sales_by_member.iloc[1:,:]
    monthly_water_sales_by_member.iloc[70,1:] = [880.93,1432.20,0,1445.67,665.73,89.13,4513.66] # aug 2015
    monthly_water_sales_by_member.iloc[71,1:] = [842.7,1316.33,0,1508.09,680.08,89.82,4437.02]# sept 2015
    monthly_water_sales_by_member = monthly_water_sales_by_member.replace(np.nan,0)
    
    # use same spreadsheets to collect monthly billing for fixed and variable uniform sales
    MonthlyWaterSalesFixed = ['Fixed Water Sales - City of St. Petersburg',
                              'Fixed Water Sales - Pinellas County', 
                              'Fixed Water Sales - City of Tampa (Uniform)', 
                              'Fixed Water Sales - Hillsborough County',  
                              'Fixed Water Sales - Pasco County', 
                              'Fixed Water Sales - City of New Port Richey']
    MonthlyWaterSalesVariable = ['Variable Water Sales - City of St. Petersburg',
                                 'Variable Water Sales - Pinellas County', 
                                 'Variable Water Sales - City of Tampa (Uniform)', 
                                 'Variable Water Sales - Hillsborough County',  
                                 'Variable Water Sales - Pasco County', 
                                 'Variable Water Sales - City of New Port Richey',
                                 'TBC Delivery - City of Tampa', 
                                 'TBC Sales - City of Tampa']
    
    # as well as TBC sales for tampa
    tabs = ['StPete','Pin','Tpa','Hills','Pas','NPR']; p = 0
    monthly_water_sales_by_member_variable = pd.DataFrame(np.empty(shape = (120,len(MonthlyWaterSalesVariable))))
    monthly_water_sales_by_member_variable[:] = np.nan
    monthly_water_sales_by_member_fixed = pd.DataFrame(np.empty(shape = (120,len(MonthlyWaterSales[1:-1]))))
    monthly_water_sales_by_member_fixed[:] = np.nan
    monthly_water_sales_by_member_fixed.columns = MonthlyWaterSalesFixed
    monthly_water_sales_by_member_variable.columns = MonthlyWaterSalesVariable
    for poc in tabs:
        for year in range(2010,2020):
            # read file
            if os.path.exists('Water Sales Revenue ' + str(year) + '-WS.xlsx'):
                sales_data = pd.read_excel('Water Sales Revenue ' + str(year) + '-WS.xlsx', 
                                           sheet_name = poc, skiprows = 3)
            elif os.path.exists('Water Sales Revenue ' + str(year) + ' WS.xlsx'):
                sales_data = pd.read_excel('Water Sales Revenue ' + str(year) + ' WS.xlsx', sheet_name = poc,
                                           skiprows = 3)
            elif os.path.exists('Water Sales Revenue ' + str(year) + ' WS.xls'):
                sales_data = pd.read_excel('Water Sales Revenue ' + str(year) + ' WS.xls', sheet_name = poc,
                                           skiprows = 3)
            elif os.path.exists('Water Sales Revenue ' + str(year) + ' WS-FINAL.xls'):
                sales_data = pd.read_excel('Water Sales Revenue ' + str(year) + ' WS-FINAL.xls', sheet_name = poc,
                                           skiprows = 3)
              
            # extract specific columns
            if year < 2013:
                monthly_water_sales_by_member_variable.iloc[range(0+12*(year-2010),12+12*(year-2010)),p] = [x for x in sales_data.iloc[17,3:15]] # variable rate monthly charges
                monthly_water_sales_by_member_fixed.iloc[range(0+12*(year-2010),12+12*(year-2010)),p] = [x for x in sales_data.iloc[22,3:15]] # fixed rate monthly charges 
            else:
                monthly_water_sales_by_member_variable.iloc[range(0+12*(year-2010),12+12*(year-2010)),p] = [x for x in sales_data.iloc[19,3:15]] # variable rate monthly charges
                monthly_water_sales_by_member_fixed.iloc[range(0+12*(year-2010),12+12*(year-2010)),p] = [x for x in sales_data.iloc[24,3:15]] # fixed rate monthly charges 
    
            if poc == 'Tpa': # grab TBC monthly use and charge
                # 2010-2012, rows 30 and 31 are mg use and charge
                if year < 2013:
                    monthly_water_sales_by_member_variable.iloc[range(0+12*(year-2010),12+12*(year-2010)),6] = [x for x in sales_data.iloc[30,3:15]] # tbc delivery and sales
                    monthly_water_sales_by_member_variable.iloc[range(0+12*(year-2010),12+12*(year-2010)),7] = [x for x in sales_data.iloc[31,3:15]]    
                # 2013, rows 32 and 33
                elif year < 2014:
                    monthly_water_sales_by_member_variable.iloc[range(0+12*(year-2010),12+12*(year-2010)),6] = [x for x in sales_data.iloc[32,3:15]] # tbc delivery and sales
                    monthly_water_sales_by_member_variable.iloc[range(0+12*(year-2010),12+12*(year-2010)),7] = [x for x in sales_data.iloc[33,3:15]] 
                # 2014-2015 has nothing
                elif year < 2016:
                    print('')
                # 2016-2019, 28-29
                elif year < 2020:
                    monthly_water_sales_by_member_variable.iloc[range(0+12*(year-2010),12+12*(year-2010)),6] = [x for x in sales_data.iloc[28,3:15]] # tbc delivery and sales
                    monthly_water_sales_by_member_variable.iloc[range(0+12*(year-2010),12+12*(year-2010)),7] = [x for x in sales_data.iloc[29,3:15]] 
    
        p += 1
       
    # fill in missing variable rate data
    monthly_water_sales_by_member_variable.iloc[70,:-2] = [x*0.439*convert_kgal_to_MG for x in [880.93,1432.20,0,1445.67,665.73,89.13]] # aug 2015, multiply use by variable uniform rate (see spreadsheets for 2015 rate)
    monthly_water_sales_by_member_variable.iloc[71,:-2] = [x*0.439*convert_kgal_to_MG for x in [842.7,1316.33,0,1508.09,680.08,89.82]] # sept 2015
    monthly_water_sales_by_member_variable = monthly_water_sales_by_member_variable.replace(np.nan,0)
    
    # export for record/convenience
    all_monthly_data = pd.DataFrame(np.hstack((monthly_water_sales_by_member, 
                                               monthly_water_sales_by_member_fixed, 
                                               monthly_water_sales_by_member_variable)))
    all_monthly_data.columns = MonthlyWaterSales + MonthlyWaterSalesFixed + MonthlyWaterSalesVariable
    # all_monthly_data.to_csv('historical_monthly_water_deliveries_and_sales_by_member.csv')
    
    return all_monthly_data


def build_HistoricalAnnualData(n_fiscal_years = 10, most_recent_year = 2020,
        historical_financial_data_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/financials'):
    # names of financial streams/categories to track
    # that are NOT included already in historical_monthly_water_deliveries_and_sales_by_member.csv
    # other notes: 
    # from Sandro Svrdlin (May 2020): 
    #   The plan of the executive team has always been to keep the total 
    #   debt payments including acquisition credits around 80 Million which 
    #   in the past has been about 50% or less of our budget. That allows us to 
    #   keep our rates pretty steady and if there is an increase that it 
    #   would not be a big increase. The acquisition credits are 
    #   going away in FY2029 so there is a $10.2 million debt relief 
    #   we will get that at that time, and also we see a big reduction 
    #   in our debt in FY2032. So any new debt (not refunding) we like to schedule 
    #   the principal payments after we get some debt relief 
    #   either in FY2029 or FY2032. 
    AnnualStreamsForModeling = ['Uniform Rate (Full)', 
                                'Uniform Rate (Variable Portion)', 
                                'TBC Sales Rate',
                                'Interest Income',
                                'Gross Revenues', # SAME AS TABLE 12, ROW 16? assume so for now. how to calculate this and annual estimate from flows?
                                'Debt Service', # does not include acquisition credits, which are $10,231,557 annually
                                'Acquisition Credits', # will end after FY 2028
                                'Fixed Operational Expenses', # just expenses (excluding debt service, acquisition credits) minus variable exp
                                'Variable Operational Expenses', 
                                'Utility Reserve Fund Balance (Total)', # how to actually calculate this from financial flows?
                                'R&R Fund (Total)', # not sure that this and the next category are right to compare?
                                'R&R Fund (Deposit)',
                                'R&R Fund (Transfer In)',
                                'Rate Stabilization Fund (Deposit)', # will not include unencumbered funds
                                'Rate Stabilization Fund (Total)', # INCLUDES UNENCUMBERED FUNDS, JUST A QUIRK OF THIS ONE RECORD - not a perfect match with transfers in/out flows, but error is <$1M/yr usually
                                'Rate Stabilization Fund (Transfer In)', # not including unencumbered - they just transfer "through" RS Fund
                                'Unencumbered Funds',
                                'CIP Fund (Total)',
                                'CIP Fund (Deposit)',
                                'CIP Fund (Transfer In)',
                                'Misc. Income',
                                'Insurance-Litigation-Arbitrage Income',
                                'Uniform Sales Revenues']
    
    import pandas as pd; import numpy as np
    annual_streams = pd.DataFrame(np.empty(shape = (n_fiscal_years, len(AnnualStreamsForModeling)+1)))
    annual_streams[:] = np.nan; annual_streams.columns = ['Fiscal Year'] + AnnualStreamsForModeling
    
    # full and variable uniform rates of FY2010-2019, and TBC sales rate
    # manually pulled from reports and Water Sales Revenue
    import os; os.chdir(historical_financial_data_path)
    variable_rate = []; full_rate = []; tbc_rate = []; debt_service = []
    fund_balance = []; rate_stab_fund_net_change = []; rr_fund_net_change = []
    gross_revenue = []; non_sales_revenue = []
    for year in range(most_recent_year-n_fiscal_years,most_recent_year):
        if os.path.exists('Water Sales Revenue ' + str(year) + '-WS.xlsx'):
            variable_rate_data = pd.read_excel('Water Sales Revenue ' + str(year) + '-WS.xlsx', skiprows = 0, sheet_name = 'Tpa')
        elif os.path.exists('Water Sales Revenue ' + str(year) + ' WS.xlsx'):
            variable_rate_data = pd.read_excel('Water Sales Revenue ' + str(year) + ' WS.xlsx', skiprows = 0, sheet_name = 'Tpa')
        elif os.path.exists('Water Sales Revenue ' + str(year) + ' WS.xls'):
            variable_rate_data = pd.read_excel('Water Sales Revenue ' + str(year) + ' WS.xls', skiprows = 0, sheet_name = 'Tpa')
        elif os.path.exists('Water Sales Revenue ' + str(year) + ' WS-FINAL.xls'):
            variable_rate_data = pd.read_excel('Water Sales Revenue ' + str(year) + ' WS-FINAL.xls', skiprows = 0, sheet_name = 'Tpa')
          
        if year > 2015:
            hist_oper_data = pd.read_excel('Table 12 - Historical Operating Results by Fiscal Year - 2019-DONE.xlsx', skiprows = 2, usecols = (0,1,2,3,4,5))
        else:
            hist_oper_data = pd.read_excel('Table 11 - Historical Operating Results by Fiscal Year 2015-2011.xlsx', skiprows = 2, usecols = (0,1,2,3,4,5))
          
        # replace empty '-' cells with 0. Doesn't seem to remove negative signs from filled cells (good)    
        hist_oper_data = hist_oper_data.replace('-',0)  
            
        variable_rate.append(variable_rate_data.iloc[6,3])
        
        # value not always given explicitly, seems to be $0.157/kgal every year
        if np.isnan(variable_rate_data.iloc[4,3]):
            tbc_rate.append(0.157)
        else:
            tbc_rate.append(variable_rate_data.iloc[4,3])
        
        # missing 2010 from data, will manually fill
        if year < 2011:
            full_rate.append(2.3980) # from 2019 CAFR, p.124
            debt_service.append(74380770) # from 2016 Approved Operating Budget, p.104
            fund_balance.append(np.nan)
            rate_stab_fund_net_change.append(np.nan)
            rr_fund_net_change.append(np.nan) # $-250,000 from 2016 Approved Operating Budget, p.105 (leaving out, don't trust?)
            gross_revenue.append(np.nan)
            non_sales_revenue.append(np.nan)
        elif year < 2016:
            full_rate.append(hist_oper_data[year].iloc[3])
            debt_service.append(hist_oper_data[year].iloc[30]) # 2011 value is lower from this source than seen elsewhere?
            fund_balance.append(hist_oper_data[year].iloc[37])
            rate_stab_fund_net_change.append(-hist_oper_data[year].iloc[6])
            rr_fund_net_change.append(hist_oper_data[year].iloc[33])
            gross_revenue.append(hist_oper_data[year].iloc[12])
            non_sales_revenue.append(hist_oper_data[year].iloc[9] + hist_oper_data[year].iloc[10] + hist_oper_data[year].iloc[11])
        else:
            full_rate.append(hist_oper_data[year].iloc[3])
            debt_service.append(hist_oper_data[year].iloc[31])
            fund_balance.append(hist_oper_data[year].iloc[38])
            rate_stab_fund_net_change.append(-hist_oper_data[year].iloc[6])
            rr_fund_net_change.append(hist_oper_data[year].iloc[34])
            gross_revenue.append(hist_oper_data[year].iloc[12])
            non_sales_revenue.append(hist_oper_data[year].iloc[9] + hist_oper_data[year].iloc[10] + hist_oper_data[year].iloc[11])
    
    # r&r fund contributions manually entered for 2018 and 2019 (not in data yet)
    rr_fund_net_change[8] = 3325468 - 1438279 # 2020 Annual Budget Report, p. 31
    rr_fund_net_change[9] = 5509008 - 1013595 # from FY19 sources/uses spreadsheet
        
    acquisition_credits = [10231557, 10231557, 10231557, 10231557, 10231557, 10231557, 10231557, 10231557, 10231557, 10231557]
        
    # read in Operating Expenses (table 5) over time
    # NOTE: each row is different FY, row 0 is FY19, goes to FY10 in row 9
    OperatingExpenses = pd.read_excel('Table 5 Operating Department -Program Expenses - 2019-DONE.xlsx', 
                                      skiprows = 3, nrows = 10, 
                                      usecols = (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16))
    OperatingExpenses = OperatingExpenses.replace('-',0)
    
    # re-ordered from 2010 to 2019
    variable_operating_expenses = OperatingExpenses['Variable Cost Expenses'][::-1]
    fixed_operating_expenses = OperatingExpenses['Total Operating Expenses'][::-1] - OperatingExpenses['Variable Cost Expenses'][::-1]
    
    # read in Restricted Assets (table 2) over time
    # NOTE: each row is different FY, row 0 is FY19, goes to FY10 in row 9
    RestrictedAssets = pd.read_excel('Table 2 Restricted Assets - 2019-DONE.xlsx', 
                                     skiprows = 3, nrows = 10, 
                                     usecols = (0,1,2,3,4,5,6,7,8,9,10,11,12))
    RestrictedAssets = RestrictedAssets.replace('-',0)

    # re-ordered from 2010 to 2019
    rr_fund_total = RestrictedAssets['Renewal and Replacement Funds'].values[::-1]
    
    # collect reserve fund and rate stabilization fund balances
    # with end-of-FY amounts from FY2010 to FY2019
    RateStab = pd.read_excel(historical_financial_data_path + '/Rate Stabilization 2019 - FINAL.xls')
#    FundBalance = pd.read_excel(historical_financial_data_path + '/Utility Rsrv -2019 - FINAL.xlsx')
    
    rate_stab_fund_total = [x for x in RateStab.iloc[[182, 193, 209, 231, 250, 268, 285, 305, 334, 369],19]]
    rate_stab_fund_deposit = [x for x in RateStab.iloc[[179, 191, 208, 228, 246, 261, 283, 303, 333, 367],20]] # not including unencumbered carryover
        
#    fund_balance = [x for x in FundBalance.iloc[[142, 160, 178, 198, 221, 248, 291, 324, 358, 395],3]] # overwrite other record
    
    # collect unencumbered funds carried forward - manually added from actuals
    # found in FY approved budgets, usually p.31 or so
    # no actual result from FY19 yet
    unencumbered_funds = [np.nan, np.nan, 3004848, 2857706, 7292798, 
                          7162745, 5325000, 3072043, 3472702, 4772996]
    
    # because misc income is not totally insignificant, track it too
    # and also overwrite non-sales revenue while we are here
    # and split into sub-categories
    # non-sales rev = interest
    misc_income = [np.nan, np.nan, 486098, 4051526, 244769, 
                   177065, 660011, 1035635, 754619, 460656]
    interest_income = [np.nan, np.nan, 1235692, 899766, 640275, 
                       758519, 1019717, 1911132, 2440815, 3804846]
    insurance_litigation_arbitrage_income = [np.nan, np.nan, -19299350, -823286, 22, 
                                             979352, 1188148, 1084167, 18178, 6476]
    
    # collect gross revenues that are consistent in definition
    # the way gross revenues used to determine covenants are calculated is
    # different than the gross revenue calculation included in budget reports
    # so will overwrite the former with the latter here, pulled from reports
    # will use the "Total Sources" row of p.31/32 of budget reports
    # that does not remove acquisition credits or fund deposits from gross rev
    # so, GR = Water Sales + Non-Sales Rev + Unencumbered + RS Transfer In + R&R Transfer In + CIP Transfer In
    # (ignoring Energy Fund transfers in, they are very small if they exist)
    gross_revenue = [np.nan, np.nan, 179745762, 174582244, 174111351, 
                     173361220, 174546428, 178721034, 175914894, 183438752]
    
    # because of inconsistencies between spreadsheets (due to my lack of 
    # understanding mostly), also overwrite the RS Fund Transfers In
    # it is better this way to pull all numbers from same sources (reports)
    # rather than so many spreadsheets, and because we don't need all the
    # way back to FY2010
    # this does NOT include unencumbered funds
    rate_stab_fund_transfer_in = [np.nan, np.nan, 31075823, 7690580, 8129415, 
                                  4424673, 8509699, 9058018, 6479981, 7039535]
    
    # for similar reasons, repeat for RS Fund Deposit
    # THIS INCLUDES MONEY DESIGNATED AS UNENCUMBERED FOR NEXT FY
    rate_stab_fund_deposit = [np.nan, np.nan, 26150905, 16639716, 9572418, 
                              12759993, 12089243, 12790683, 12908523, 17086535]
    
    # repeat overwrite for R&R and CIP Fund flows
    # don't have R&R transfer in for FY19 yet, back it out with other actuals
    rr_fund_deposit = [np.nan, np.nan, 775437, 3533711, 6019372, 
                       2891688, 3155183, 3242539, 3325468, 5509008]
    rr_fund_transfer_in = [np.nan, np.nan, 300626, 1401864, 1522804, 
                           1318097, 2516508, 3139817, 1438279, rr_fund_deposit[-1] - (rr_fund_total[-1] - rr_fund_total[-2])]
    
    cip_fund_transfer_in = [np.nan, np.nan, 4825958, 2011207, 947670, 
                            3640572, 1553479, 1918031, 344247, 653919]
    cip_fund_deposit = [np.nan, np.nan, 976653, 1727032, 2583103, 
                        2986952, 4592553, 5158861, 4215354, 5356993]
    cip_fund_total = RestrictedAssets['Capital Improvement Funds'].values[::-1]
    
    # there is a debt service actuals discrepancy in 2015-16, so will overwrite
    # with numbers from budget reports as well
    debt_service = [np.nan, np.nan, 73084766, 75447974, 75337316, 
                    72668588, 71414576, 70129335, 70133614, 70122276]
    
    # collect actual sales revenues 
    # includes tbc sales
    total_sales_revenue = [np.nan, np.nan, 157523970+592097, 156134324+358558, 155291597+42000, 
                           154691290+33269, 153126957+46080+72526, 156135112+39555+570433, 160487626+36736+315441, 165973331+66855+146980]
        
    # collect data to output for table
    annual_streams.iloc[:,0] = [2010,2011,2012,2013,2014,2015,2016,2017,2018,2019]
    annual_streams.iloc[:,1] = full_rate
    annual_streams.iloc[:,2] = variable_rate      
    annual_streams.iloc[:,3] = tbc_rate
    annual_streams.iloc[:,4] = interest_income   
    annual_streams.iloc[:,5] = gross_revenue
    annual_streams.iloc[:,6] = debt_service   
    annual_streams.iloc[:,7] = acquisition_credits
    annual_streams.iloc[:,8] = fixed_operating_expenses   
    annual_streams.iloc[:,9] = variable_operating_expenses   
    annual_streams.iloc[:,10] = fund_balance
    annual_streams.iloc[:,11] = rr_fund_total   
    annual_streams.iloc[:,12] = rr_fund_deposit
    annual_streams.iloc[:,13] = rr_fund_transfer_in
    annual_streams.iloc[:,14] = rate_stab_fund_deposit
    annual_streams.iloc[:,15] = rate_stab_fund_total 
    annual_streams.iloc[:,16] = rate_stab_fund_transfer_in 
    annual_streams.iloc[:,17] = unencumbered_funds 
    annual_streams.iloc[:,18] = cip_fund_total   
    annual_streams.iloc[:,19] = cip_fund_deposit
    annual_streams.iloc[:,20] = cip_fund_transfer_in
    annual_streams.iloc[:,21] = misc_income
    annual_streams.iloc[:,22] = insurance_litigation_arbitrage_income
    annual_streams.iloc[:,23] = total_sales_revenue
    
    return annual_streams


def build_HistoricalProjectedAnnualBudgets(financial_path = 'C:\\Users\\dgorelic\\OneDrive - University of North Carolina at Chapel Hill\\UNC\\Research\\TBW\\Data\\financials'):
    # set working directory
    import os; import pandas as pd; import numpy as np
    os.chdir(financial_path)
    
    # which variables will we track for approved annual budgets?
    ApprovedBudgetVariables = ['Fiscal Year',
                               'Annual Estimate', # all costs/expenses that must be met, Subtotal in budget (not including deposits to funds?)
                               'Gross Revenues', # REPLACED WITH "Total Sources" BUDGET VALUE ON P.31/32 of annual reports to be consistent with actuals
                               'Water Sales Revenue', # sales + credits/surcharges + tbc sales + grants
                               'Fixed Operating Expenses', 
                               'Variable Operating Expenses', 
                               'Net Revenues', # gross revenue - all operational expenses
                               'Debt Service', 
                               'Acquisition Credits', 
                               'Unencumbered Carryover Funds', 
                               'R&R Fund Deposit', 
                               'Rate Stabilization Fund Deposit',
                               'Other Funds Deposit', 
                               'Uniform Rate', 
                               'Variable Uniform Rate', 
                               'TBC Rate',
                               'Rate Stabilization Fund Transfers In', 
                               'R&R Fund Transfers In', 
                               'Other Funds Transfers In', 
                               'Interest Income', # really all non-sales income - litigation/insurance recoveries + misc income always budgeted at zero
                               'CIP Fund Transfer In', 
                               'CIP Fund Deposit'] # includes interest
    
    # manually record values from FY21 Proposed Operating Budget Report, p.31
    # used in place of approved budget because 
    # 1. they dont vary too much between proposed and approved
    # 2. need FY21 budget estimate for last 3 months of 2020 in model
    #    so that simulation can start in Jan 2021
    FY21_proposed = [2021,
                     178053678, 
                     182829643, 
                     172518114+42000+392000+2432238, 
                     178053678-70093840-10231558-(12410244+13027527+500800), 
                     12410244+13027527+500800, 
                     182829643 - (178053678-70093840-10231558), 
                     70093840, 
                     10231558, 
                     4233325, 
                     3000000, 
                     0, 
                     0, 
                     2.559, 
                     0.3848,
                     0.195,
                     0,
                     0,
                     0, 
                     3211966, 
                     0,
                     1500000+275965]
    
    # manually record values from FY20 Approved Operating Budget Report, p.31
    FY20_approved = [2020,
                     175479563, 
                     184036207, 
                     169332978+42000+392000, 
                     175479563-70133315-10231558-(12606616+13548122+502800), 
                     12606616+13548122+502800, 
                     184036207 - (175479563-70133315-10231558), 
                     70133315, 
                     10231558, 
                     4168060, 
                     4500000, 
                     0, 
                     112872+1600000, 
                     2.559, 
                     0.4028,
                     0.195,
                     1600000,
                     6607280,
                     0, 
                     1893889, 
                     0,
                     2200000+143772]
    
    # read in FY 2019 CAFR summary table and clean
#    CAFR_FY19 = pd.read_excel(financial_path + '/FY19 Budget Sources & Uses-FINAL.xlsx')
#    CAFR_FY19_cleaned = CAFR_FY19[(~pd.isna(CAFR_FY19['Enterprise Funds'])) & (~pd.isna(CAFR_FY19['Approved']))]
#    FY19_approved = [2019,
#                     CAFR_FY19_cleaned['Approved'].iloc[31], # subtotal category
#                     np.sum(CAFR_FY19_cleaned['Approved'].iloc[0:3]) + CAFR_FY19_cleaned['Approved'].iloc[5] + (-CAFR_FY19_cleaned['Approved'].iloc[9] + CAFR_FY19_cleaned['Approved'].iloc[37]) + CAFR_FY19_cleaned['Approved'].iloc[10] + CAFR_FY19_cleaned['Approved'].iloc[3] - CAFR_FY19_cleaned['Approved'].iloc[24], 
#                     np.sum(CAFR_FY19_cleaned['Approved'].iloc[0:3]) + CAFR_FY19_cleaned['Approved'].iloc[5],
#                     CAFR_FY19_cleaned['Approved'].iloc[31] - np.sum(CAFR_FY19_cleaned['Approved'].iloc[27:31]) - np.sum(CAFR_FY19_cleaned['Approved'].iloc[23:25]),
#                     np.sum(CAFR_FY19_cleaned['Approved'].iloc[27:31]),
#                     np.sum(CAFR_FY19_cleaned['Approved'].iloc[0:3]) + CAFR_FY19_cleaned['Approved'].iloc[5] + (-CAFR_FY19_cleaned['Approved'].iloc[9] + CAFR_FY19_cleaned['Approved'].iloc[37]) + CAFR_FY19_cleaned['Approved'].iloc[10] + CAFR_FY19_cleaned['Approved'].iloc[3] - CAFR_FY19_cleaned['Approved'].iloc[24] - (CAFR_FY19_cleaned['Approved'].iloc[31] - np.sum(CAFR_FY19_cleaned['Approved'].iloc[23:25])), 
#                     CAFR_FY19_cleaned['Approved'].iloc[23],
#                     CAFR_FY19_cleaned['Approved'].iloc[24],
#                     CAFR_FY19_cleaned['Approved'].iloc[10],
#                     -CAFR_FY19_cleaned['Approved'].iloc[13] + CAFR_FY19_cleaned['Approved'].iloc[34],
#                     -CAFR_FY19_cleaned['Approved'].iloc[9] + CAFR_FY19_cleaned['Approved'].iloc[37],
#                     np.sum(CAFR_FY19_cleaned['Approved'].iloc[35:37]) + CAFR_FY19_cleaned['Approved'].iloc[38] + np.sum(CAFR_FY19_cleaned['Approved'].iloc[32:34]) - np.sum(CAFR_FY19_cleaned['Approved'].iloc[11:13]),
#                     2.559, # hard-coded numbers manually pulled from FY Operating Budget Report
#                     0.3988,
#                     0.157,
#                     CAFR_FY19_cleaned['Approved'].iloc[9],
#                     CAFR_FY19_cleaned['Approved'].iloc[13],
#                     np.sum(CAFR_FY19_cleaned['Approved'].iloc[11:13]), 
#                     np.sum(CAFR_FY19_cleaned['Approved'].iloc[3:5]), 
#                     0.0,
#                     2920690] # CIP transfer, p. 60 of report
    FY19_approved = [2019,
                     172497233, 
                     177878612, 
                     166722403+42000, 
                     172497233-70122276-10231558-(10801430+13666498+1512378), 
                     10801430+13666498+1512378, 
                     177878612 - (172497233-70122276-10231558), 
                     70122276, 
                     10231558, 
                     3618988, 
                     5000000, 
                     0, 
                     288898, 
                     2.559, 
                     0.3988,
                     0.157,
                     1153898,
                     5078843,
                     0, 
                     1262480, 
                     0,
                     92481]
    
    
    # read in FY 2018 CAFR summary table and clean
    # NOTE: also includes FY17 actuals
#    CAFR_FY18 = pd.read_excel(financial_path + '/FY18 Budget Sources & Uses.xlsx', sheet_name = 2)
#    CAFR_FY18_cleaned = CAFR_FY18[(~pd.isna(CAFR_FY18['Enterprise Funds'])) & ((~pd.isna(CAFR_FY18['Actual'])) | (CAFR_FY18['Enterprise Funds'] == 'CIP Additional O&M'))]
#    CAFR_FY18_cleaned = CAFR_FY18_cleaned.replace(np.nan, 0)
#    FY18_approved = [2018,
#                     CAFR_FY18_cleaned['Approved'].iloc[31], # subtotal category
#                     np.sum(CAFR_FY18_cleaned['Approved'].iloc[0:3]) + CAFR_FY18_cleaned['Approved'].iloc[5] + (-CAFR_FY18_cleaned['Approved'].iloc[9] + CAFR_FY18_cleaned['Approved'].iloc[37]) + CAFR_FY18_cleaned['Approved'].iloc[10] + CAFR_FY18_cleaned['Approved'].iloc[3] - CAFR_FY18_cleaned['Approved'].iloc[24], 
#                     np.sum(CAFR_FY18_cleaned['Approved'].iloc[0:3]) + CAFR_FY18_cleaned['Approved'].iloc[5],
#                     CAFR_FY18_cleaned['Approved'].iloc[31] - np.sum(CAFR_FY18_cleaned['Approved'].iloc[27:31]) - np.sum(CAFR_FY18_cleaned['Approved'].iloc[23:25]),
#                     np.sum(CAFR_FY18_cleaned['Approved'].iloc[27:31]),
#                     np.sum(CAFR_FY18_cleaned['Approved'].iloc[0:3]) + CAFR_FY18_cleaned['Approved'].iloc[5] + (-CAFR_FY18_cleaned['Approved'].iloc[9] + CAFR_FY18_cleaned['Approved'].iloc[37]) + CAFR_FY18_cleaned['Approved'].iloc[10] + CAFR_FY18_cleaned['Approved'].iloc[3] - CAFR_FY18_cleaned['Approved'].iloc[24] - (CAFR_FY18_cleaned['Approved'].iloc[31] - np.sum(CAFR_FY18_cleaned['Approved'].iloc[23:25])), 
#                     CAFR_FY18_cleaned['Approved'].iloc[23],
#                     CAFR_FY18_cleaned['Approved'].iloc[24],
#                     CAFR_FY18_cleaned['Approved'].iloc[10],
#                     -CAFR_FY18_cleaned['Approved'].iloc[13] + CAFR_FY18_cleaned['Approved'].iloc[34],
#                     -CAFR_FY18_cleaned['Approved'].iloc[9] + CAFR_FY18_cleaned['Approved'].iloc[37],
#                     np.sum(CAFR_FY18_cleaned['Approved'].iloc[35:37]) + CAFR_FY18_cleaned['Approved'].iloc[38] + np.sum(CAFR_FY18_cleaned['Approved'].iloc[32:34]) - np.sum(CAFR_FY18_cleaned['Approved'].iloc[11:13]),
#                     2.559, # hard-coded numbers manually pulled from FY Operating Budget Report
#                     0.3858,
#                     0.157,
#                     CAFR_FY18_cleaned['Approved'].iloc[9],
#                     CAFR_FY18_cleaned['Approved'].iloc[13],
#                     np.sum(CAFR_FY18_cleaned['Approved'].iloc[11:13]), 
#                     np.sum(CAFR_FY18_cleaned['Approved'].iloc[3:5]), 
#                     0.0,
#                     692442] # CIP expenditure from FY18 report, p.58
    
    FY18_approved = [2018,
                     163630279, 
                     167692256, 
                     160843917+42000, 
                     163630279-70133615-10231558-(9823439+12911100+1512378), 
                     9823439+12911100+1512378, 
                     167692256 - (163630279-70133615-10231558), 
                     70133615, 
                     10231558, 
                     3472702, 
                     3000000, 
                     0, 
                     0, 
                     2.559, 
                     0.3858,
                     0.157,
                     0,
                     2110867,
                     0, 
                     1222770, 
                     0,
                     1000000+61977]
    
    # manually enter FY 2017 approved budget from its report
    FY17_approved = [2017,
                     162049744, 
                     165083908, 
                     154117850+42000, 
                     162049744-70129336-10231558-(9441417+12407551+1508178), 
                     9441417+12407551+1508178, 
                     165083908 - (162049744-70129336-10231558), 
                     70129336, 
                     10231558, 
                     3072043, 
                     3000000, 
                     0, 
                     0, 
                     2.559, 
                     0.3878,
                     0.157,
                     2870000,
                     4074146,
                     0, 
                     907870, 
                     0,
                     34165]

    # manually enter FY 2016 approved budget from its report
    FY16_approved = [2016,
                     165020845, 
                     168047840, 
                     153602133+42000+0, 
                     165020845-72413958-10231558-(10665878+12003244+1544575), 
                     10665878+12003244+1544575, 
                     168047840 - (165020845-72413958-10231558), 
                     72413958, 
                     10231558, 
                     3200826, 
                     3000000, 
                     0, 
                     0, 
                     2.559, 
                     0.4034,
                     0.157,
                     5325000,
                     5018329,
                     0, 
                     859552, 
                     0,
                     26995]
    
    # manually enter FY 2015 approved budget from its report
    FY15_approved = [2015,
                     166501212, 
                     169320135, 
                     156541319+42000+581260, 
                     166501212-72876252-10231558-(11769355+13543263+1544575), 
                     11769355+13543263+1544575, 
                     169320135 - (166501212-72876252-10231558), 
                     72876252, 
                     10231558, 
                     3147745, 
                     2781000, 
                     0, 
                     0, 
                     2.559, 
                     0.4390,
                     0.157,
                     4015000,
                     4115387,
                     0, 
                     877424, 
                     0,
                     37923] # CIP costs, p.59
    
    # manually enter FY 2014 approved budget from its report
    FY14_approved = [2014,
                     165781147, 
                     168927297, 
                     157387253+42000+581260, 
                     165781147-72982799-10231558-(10965065+18287208+1512240), 
                     10965065+18287208+1512240, 
                     168927297 - (165781147-72982799-10231558), 
                     72982799, 
                     10231558, 
                     3160798, 
                     2700000, 
                     0, 
                     407382, 
                     2.559, 
                     0.5002,
                     0.157,
                     4132000,
                     2781000,
                     0, 
                     842986, 
                     0,
                     38768]
    
    # collect approved budget data for export
    approved_budgets = pd.DataFrame(np.vstack((FY14_approved, 
                                               FY15_approved, 
                                               FY16_approved, 
                                               FY17_approved, 
                                               FY18_approved, 
                                               FY19_approved, 
                                               FY20_approved, 
                                               FY21_proposed)))
    approved_budgets.columns = ApprovedBudgetVariables
    # approved_budgets.to_csv('historical_approved_annual_budgets.csv')
    
    return approved_budgets



def append_UpToJuly2020DeliveryAndSalesData(monthly_record, 
                                            FY2020_approved_budget, 
                                            daily_delivery_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/observed_deliveries'):
    # historic monthly record from finance data only goes through Sept 2019
    # but need to extend through end of calendar year 2020
    # this includes
    #   (1) getting observed deliveries at a monthly level from daily records
    #   (2) calculating TBC and variable sales revenue based on FY2020 rates from budget
    #   (3) calculating fixed sales revenues based on estimated FY2020 fixed costs to be recovered
    #       and FY2019 demands by each member relative to each other
    n_months_in_year = 12; convert_kgal_to_MG = 1000
    
    # (0) get approved budget variables in list format
    FY2020_approved_budget = [x for x in FY2020_approved_budget]
    
    # (1) get monthly deliveries by member
    import pandas as pd
    import numpy as np
    # read daily records starting at Oct 2019 -> June 2020
    additional_daily_water_deliveries = pd.read_excel(daily_delivery_path + '/DeliveryandHarneyAug_up_to_June_2020.xlsx', 
                                                      skiprows = 3652, sheet_name = 'Daily') 
    additional_daily_water_deliveries.columns = ['Year','Month','Day','CoT','CoT TBC','NPR','NW Hillsborough','Pasco','Pinellas','SC Hillsborough','St. Pete']
    additional_daily_water_deliveries['Date'] = pd.to_datetime(additional_daily_water_deliveries[['Year','Month','Day']])
    additional_daily_water_deliveries['Hillsborough'] = additional_daily_water_deliveries['NW Hillsborough'] + additional_daily_water_deliveries['SC Hillsborough']
    
    organized_additional_daily_water_deliveries = additional_daily_water_deliveries[['Date','St. Pete','Pinellas','CoT','Hillsborough','Pasco','NPR','CoT TBC']]
    additional_monthly_water_deliveries = organized_additional_daily_water_deliveries.groupby(organized_additional_daily_water_deliveries['Date'].dt.month).sum().reset_index()
    
    # put months back in order
    additional_monthly_water_deliveries = additional_monthly_water_deliveries.iloc[[6,7,8,0,1,2,3,4,5],:]
    
    # (2) calculate variable sales revenue for each month
    # NOTE: A LOT OF INDICES HERE ARE HARD CODED AND WILL BE WRONG IF
    # MORE OR LESS COLUMNS ARE ADDED TO INPUT DATASETS
    additional_monthly_variable_water_sales = additional_monthly_water_deliveries.iloc[:,1:-1] * FY2020_approved_budget[-6] * convert_kgal_to_MG
    additional_monthly_tbc_sales = additional_monthly_water_deliveries.iloc[:,-1] * FY2020_approved_budget[-5] * convert_kgal_to_MG
    
    # (3) calculate fixed sales
    fraction_FY_total_deliveries_by_member = monthly_record.iloc[-n_months_in_year:,1:7].sum() / monthly_record.iloc[-n_months_in_year:,1:7].sum().sum()
    fixed_costs_to_recover_in_FY20 = FY2020_approved_budget[1] - FY2020_approved_budget[5] # annual estimate - budgeted variable costs
    monthly_fixed_sales_by_member = np.vstack((fraction_FY_total_deliveries_by_member * fixed_costs_to_recover_in_FY20 / n_months_in_year,
                                               fraction_FY_total_deliveries_by_member * fixed_costs_to_recover_in_FY20 / n_months_in_year,
                                               fraction_FY_total_deliveries_by_member * fixed_costs_to_recover_in_FY20 / n_months_in_year,
                                               fraction_FY_total_deliveries_by_member * fixed_costs_to_recover_in_FY20 / n_months_in_year,
                                               fraction_FY_total_deliveries_by_member * fixed_costs_to_recover_in_FY20 / n_months_in_year,
                                               fraction_FY_total_deliveries_by_member * fixed_costs_to_recover_in_FY20 / n_months_in_year,
                                               fraction_FY_total_deliveries_by_member * fixed_costs_to_recover_in_FY20 / n_months_in_year,
                                               fraction_FY_total_deliveries_by_member * fixed_costs_to_recover_in_FY20 / n_months_in_year,
                                               fraction_FY_total_deliveries_by_member * fixed_costs_to_recover_in_FY20 / n_months_in_year))
    
    # (4) append to existing record and return
    # order of columns in monthly_record spreadsheet is:
    # Date, water delivery by member (x6), uniform water delivery total,
    # fixed water sales by member (x6), variable water sales by member (x6),
    # tbc delivery, tbc sales
    new_months_collected = pd.DataFrame(np.hstack((pd.DataFrame([pd.datetime(2019,10,31).timestamp(), 
                                                                 pd.datetime(2019,11,30).timestamp(), 
                                                                 pd.datetime(2019,12,31).timestamp(), 
                                                                 pd.datetime(2020,1,31).timestamp(),
                                                                 pd.datetime(2020,2,29).timestamp(),
                                                                 pd.datetime(2020,3,31).timestamp(),
                                                                 pd.datetime(2020,4,30).timestamp(),
                                                                 pd.datetime(2020,5,31).timestamp(),
                                                                 pd.datetime(2020,6,30).timestamp()]),
        additional_monthly_water_deliveries.iloc[:,1:-1],
        pd.DataFrame(additional_monthly_water_deliveries.iloc[:,1:-1].sum(1)),
        monthly_fixed_sales_by_member,
        additional_monthly_variable_water_sales,
        pd.DataFrame(additional_monthly_water_deliveries.iloc[:,-1].transpose()),
        pd.DataFrame(additional_monthly_tbc_sales.transpose()))))
    monthly_deliveries_and_sales = pd.DataFrame(np.vstack((monthly_record,
                                                           new_months_collected)))
    monthly_deliveries_and_sales.columns = [x for x in monthly_record.columns]
    monthly_deliveries_and_sales['Date'].iloc[-9] = pd.to_datetime(pd.datetime(2019,10,31))
    monthly_deliveries_and_sales['Date'].iloc[-8] = pd.to_datetime(pd.datetime(2019,11,30))
    monthly_deliveries_and_sales['Date'].iloc[-7] = pd.to_datetime(pd.datetime(2019,12,31))
    monthly_deliveries_and_sales['Date'].iloc[-6] = pd.to_datetime(pd.datetime(2020,1,31))
    monthly_deliveries_and_sales['Date'].iloc[-5] = pd.to_datetime(pd.datetime(2020,2,29))
    monthly_deliveries_and_sales['Date'].iloc[-4] = pd.to_datetime(pd.datetime(2020,3,31))
    monthly_deliveries_and_sales['Date'].iloc[-3] = pd.to_datetime(pd.datetime(2020,4,30))
    monthly_deliveries_and_sales['Date'].iloc[-2] = pd.to_datetime(pd.datetime(2020,5,31))
    monthly_deliveries_and_sales['Date'].iloc[-1] = pd.to_datetime(pd.datetime(2020,6,30))
    
    # fix 2009 date typo
    monthly_deliveries_and_sales['Date'].iloc[2] = pd.to_datetime(pd.datetime(2009,12,31))
    
    # Split out with Year, Fiscal Year, and Month Columns
    monthly_deliveries_and_sales['Year'] = pd.DatetimeIndex(monthly_deliveries_and_sales['Date']).year
    monthly_deliveries_and_sales['Month'] = pd.DatetimeIndex(monthly_deliveries_and_sales['Date']).month
    
    monthly_deliveries_and_sales['Fiscal Year'] = pd.DatetimeIndex(monthly_deliveries_and_sales['Date']).year
    i = 0
    for m in monthly_deliveries_and_sales['Month']:
        if m in [10,11,12]:
            monthly_deliveries_and_sales['Fiscal Year'].iloc[i] += 1
        i += 1
    
    # export fixed version
    # monthly_deliveries_and_sales.to_csv(daily_delivery_path + '/monthly_deliveries_and_sales_by_member_through2019.csv')
    
    return monthly_deliveries_and_sales
    
  
def get_ExistingDebt(data_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/financials'):
    # pull bond issue data, simplified to only include necessary info for modeling
    # as model progresses, this table will be adjusted to remove debt paid off
    import pandas as pd
    debt_data = pd.read_excel(data_path + '/Current_Future_BondIssues.xlsx', sheet_name = 'Existing Debt for Modeling')
    
    return debt_data

def get_PotentialInfrastructureProjects(data_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/financials'):
    # pull potential infrastructure projects to be financed, simplified to only include necessary info for modeling
    import pandas as pd
    debt_data = pd.read_excel(data_path + '/Current_Future_BondIssues.xlsx', sheet_name = 'Potential Projs for Modeling')
    
    return debt_data




### ---------------------------------------------------------------------------
### COLLECT AND CLEAN DATA BELOW
### ---------------------------------------------------------------------------

### -----------------------------------------------------------------------
# step 0a: read in historical financial info
#           in future, if this is run in a larger loop across realizations
#           consider reading in historical data outside function once
#           and passed here
hist_financial_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/financials'

monthly_water_deliveries_and_sales = build_HistoricalMonthlyWaterDeliveriesAndSalesData(hist_financial_path)
annual_budget_data = build_HistoricalAnnualData(historical_financial_data_path = hist_financial_path)
historical_annual_budget_projections = build_HistoricalProjectedAnnualBudgets(hist_financial_path)

# step 0b: data for actual budget results goes to end of FY 2019 (Sept 31, 2019)
#           but OROP/OMS water supply modeling begins "Jan 2021"
#           BUT WE WILL ASSUME WATER SUPPLY MODELING ACTUALLY BEGINS JAN 2020
#           AND OROP/OMS RESULTS REPRESENT 2020-2039 YEARS RATHER THAN 2021-2040
#           so for now we need to use the approved FY2020 budget/uniform rates
#           for calculation of revenue from observed water sales 
observed_delivery_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/observed_deliveries'
monthly_water_deliveries_and_sales = append_UpToJuly2020DeliveryAndSalesData(monthly_record = monthly_water_deliveries_and_sales, 
                                                                             FY2020_approved_budget = historical_annual_budget_projections.iloc[4,:], 
                                                                             daily_delivery_path = observed_delivery_path)

# step 0c: collect existing and future debt/infrastructure project costs
# get existing debt by issue
model_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/model_input_data'
existing_issued_debt = get_ExistingDebt(model_path)

# get potential projects and their specs
potential_projects = get_PotentialInfrastructureProjects(model_path)

### step 0d: export each dataset to be read by financial model
# (exporting steps removed from above functions to be done here at end)
existing_issued_debt.to_csv(model_path + '/existing_debt.csv', index = None)
potential_projects.to_csv(model_path + '/potential_projects.csv', index = None)
monthly_water_deliveries_and_sales.to_csv(model_path + '/water_sales_and_deliveries_all_2020.csv', index = None)
annual_budget_data.to_csv(model_path + '/historical_actuals.csv', index = None)
historical_annual_budget_projections.to_csv(model_path + '/historical_budgets.csv', index = None)


