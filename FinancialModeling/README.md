# Financial Model

1. Run_FinancialModelForSingleRealization\*
- pull_ModeledData
	-get_HarneyAugmentationFromOMS
- collect_ExistingRecords
	- calculate_TrueDeliveriesWithSlack
		1.	get_MemberDeliveries
		2.	get_DailySupplySlack
- allocate_InitialAnnualCIPSpending
- Calculate_WaterSalesforFY
	-Estimate_UniformRate
- Update_MajorSupplyInfrastructureInvestment\*
	- Check_forTriggeredProjects
- Calculate_FYActuals\*
	- Calculate_DebtCoverageRatio
	- Calculate_RateCoverageRatio
- Calculate_NextFYBudget\*
	- Add_NewDebt
	- Set_BudgetedDebtService
	- Add_NewOperationalCosts
	- Estimate_UniformRate
	- Estimate_VariableRate

\*Makes a difference if the CIP schedule is toggled on (True)




## Summary of functions

1. estimate_VariableRate
2. get_DailySupplySlack
3. get_MemberDeliveries
4. get_MemberDemands (Never used?)
5. get_HarneyAugmentationFromOMS
6. add_NewDebt
7. check_ForTriggeredProjects
8. calculate_DebtCoverageRatio
9. calculate_RateCoverageRatio
10. set_BudgetedDebtService
11. add_NewOperationalCosts
12. allocate_InitialAnnualCIPSpending
13. pdate_MajorSupplyInfrastructureInvestment
14. estimate_UniformRate
15. calculate_TrueDeliveriesWithSlack
16. collect_ExistingRecords
- Arguments:
	- annual_actuals
		- output: 'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/output': this output path eventually goes to the model output – just not sure where those other csvs go and what they are used for? (this is all overwritten with a new output file pathway)
	- annual_budgets
	- water_delivery_sales
	- annual_budget
	- budget_projection
		C:\Users\cmpet\OneDrive\Documents\UNCTBW\Financialoutputs\historical_budgets.csv (this is created from the build_historic_records model)
	- water_delivery_sales
	- CIP_plan
	- reserve_balances
	- reserve_deposits
	- AMPL_cleaned_data
	- TBC_raw_sales_to_CoT
	- Month
	- Year
	- fiscal_years_to_keep
	- first_modeled_fy
	- n_months_in_year
	- annual_demand_growth_rate
	- last_fy_month
	- outpath
- Outputs:
	- annual_actuals
		goes to the output file pathway: historic_actuals.csv
	- annual_budgets
		goes to the output file pathway: historic_budgets.csv
	- water_delivery_sales
		goes to ouput file pathway: historic_sales.csv
	- full_model_period_reserve_deposits
- Utilized:
	- run_FinancialModelForSingleRealization
- Summary:
	Pulls the oldest year from the historical budgets csv (budget projections argument), historical actuals csv (annual budget argument), water deliveries and sales 2020 csv (water deliveries and sales argument). 
	The preliminary year should be two years before the inputed Fiscal start year. To confirm that the accurate number of historic records are available the preliminary year is comparted to the earliest fiscal year actuals available.

	Begin to create the annual actuals (becomes budget actuals csv with the simulation run ids) using data from the reserve balances input (projected FY21 reserve fund starting balances csv). This is where the amounts for the R&R fund, the CIP fund, and the Energy Savings Fund (Totals) comes from.
	[[If the minimum fiscal year to keep (start fiscal year – 1) >= the first modeled year – 1 (**I can’t think of a situation where these two would not be equal to one another**) 
	Set the number of CIP planning years
	The number of (copy years?) is equal to two less than the number of fiscal years in the budget actuals and the number of set CIP planning years
	This section creates the output -> full_model)period_reserve_deposits]]
	Fiscal year to keep = 2020 - 2040


17.	pull_ModeledData
a.	Arguments:
	i.	additional_scripts_path
		'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Code/Visualization'
	ii.	orop_output_path
		'C:/Users/dgorelic/Desktop/TBWruns/rrv_0125/cleaned'
	iii.	oms_output_path
		'F:/MonteCarlo_Project/FNAII/IM to Tirusew/Integrated Models/SWERP_V1/AMPL_Results_run_125'
	iv.	realization_id
		1 (defined differences between realization id, simulation id, and ) When to change the realization id?
	v.	fiscal_years_to_keep
		Defined variable in step 0 of the run_FinancialModelForSingleRealization function
	vi.	end_fiscal_year
		end_year (just can’t remember where this is defined)
	vii.	first_modeled_fy
		defined in constants of run_FinancialModelForSingleRealization function
	viii.	PRE_CLEANED = True
b.	Outputs:
	i.	AMPL_cleaned_data:
		This is a dataframe – it cleans the data from the ampl csv files
	ii.	TBC_raw_sales_to_CoT
		This is the Tampa Bay Canal sales to City of Tampa this is calculated using the get_HarneyAugmentationFromOMS
	iii.	Year
		Pulls the year from the ampl out file 
	iv.	Month
		Pulls the month from the ampl out file
c.	Utilized: 
	i.	run_FinancialModelForSingleRealization
d.	Summary:
e.	Questions:
	i.	How do I determine if the data is pre-cleaned?
	ii.	If the directory for additional scripts path is pointing to David’s folder what is it pointing towards? Same with the OROP one?
	iii.	Os.chdir – what is this and where does the analysis_functions variable come from?
	iv.	How to read an OUT file?
18.	calculate_WaterSalesForFY
19.	calculate_FYActuals
20.	calculate_NextFYBudget
21.	run_FinancialModelForSingleRealization **(big function)**
