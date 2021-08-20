# TBW Financial Model - Explore CIP Forecast
# D Gorelick (Aug 2021)
# ------------------------------------------

rm(list=ls())
hist_financial_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/financials'

# read in CIP 10-year model forecast
CIP_Forecast = read.csv(paste(hist_financial_path, '/FinancialModelForecast10yrmultiplesourcesTBW.csv', sep = ''))

# summarize the data for trend plotting
library(tidyverse)
CIP_Forecast = CIP_Forecast[,c(2:ncol(CIP_Forecast))]
CIPF_melt = melt(CIP_Forecast, id = c('Project.No.', 'Project.Name', 'Current.Funding.Source'))
CIPF_melt$Dollars = gsub(CIPF_melt$value, pattern = '\\$', replacement = '')
CIPF_melt$Dollars = gsub(CIPF_melt$Dollars, pattern = ',', replacement = '')
CIPF_melt$Dollars = as.numeric(as.character(CIPF_melt$Dollars))

# plot some stuff to find basics

# without total needed, ignoring spending pre-FY21
# then smooth out labels for plotting
CIPF_melt_sub = CIPF_melt[which(CIPF_melt$variable %in% unique(CIPF_melt$variable)[c(3,4:14)]),]
CIPF_melt_sub$variable = plyr::revalue(CIPF_melt_sub$variable, c('Remaining.FY.2021'='2021', 'FY.2022'='2022',
                                        'FY.2023'='2023', 'FY.2024'='2024', 'FY.2025'='2025',
                                        'FY.2026'='2026', 'FY.2027'='2027', 'FY.2028'='2028',
                                        'FY.2029'='2029', 'FY.2030'='2030', 'FY.2031'='2031', 'Future'='2032'))
P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.numeric(as.character(variable)), y = Dollars, fill = Current.Funding.Source), 
                                        color = NA, stat = 'identity') +
  facet_wrap(Project.Name ~ ., ncol = 8, scales = "free_y")
ggsave('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/otherfigures/check_CIP.png',
       dpi = 600, units = 'in', height = 14, width = 25)

# break down funding for small vs medium vs large projects
CIPF_melt = melt(CIP_Forecast, id = c('Project.No.', 'Project.Name', 'Current.Funding.Source', 'Total.Funds.Needed'))
CIPF_melt$Dollars = gsub(CIPF_melt$value, pattern = '\\$', replacement = '')
CIPF_melt$Dollars = gsub(CIPF_melt$Dollars, pattern = ',', replacement = '')
CIPF_melt$Dollars = as.numeric(as.character(CIPF_melt$Dollars))
CIPF_melt$TotalDollars = gsub(CIPF_melt$Total.Funds.Needed, pattern = '\\$', replacement = '')
CIPF_melt$TotalDollars = gsub(CIPF_melt$TotalDollars, pattern = ',', replacement = '')
CIPF_melt$TotalDollars = as.numeric(as.character(CIPF_melt$TotalDollars))

CIPF_melt$`Total Capital Needed` = "Large (>$100m)"
CIPF_melt$`Total Capital Needed`[which(CIPF_melt$TotalDollars <= 100000000)] = "Medium (>$10m, <$100m)"
CIPF_melt$`Total Capital Needed`[which(CIPF_melt$TotalDollars <= 10000000)] = "Small (<$10m)"

CIPF_melt_sub = CIPF_melt[which(CIPF_melt$variable %in% unique(CIPF_melt$variable)[c(3,4:14)]),]
CIPF_melt_sub$variable = plyr::revalue(CIPF_melt_sub$variable, c('Remaining.FY.2021'='2021', 'FY.2022'='2022',
                                                                 'FY.2023'='2023', 'FY.2024'='2024', 'FY.2025'='2025',
                                                                 'FY.2026'='2026', 'FY.2027'='2027', 'FY.2028'='2028',
                                                                 'FY.2029'='2029', 'FY.2030'='2030', 'FY.2031'='2031', 'Future'='2032'))
CIPF_melt_sub = CIPF_melt_sub[which(CIPF_melt_sub$Project.Name != "Totals"),]
P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.numeric(as.character(variable)), y = Dollars, fill = Current.Funding.Source), 
                                            color = NA, stat = 'identity') +
  facet_wrap(`Total Capital Needed` ~ ., ncol = 3, scales = "free_y") + xlab("Fiscal Year\n(2032 includes all future funding TBA)")
ggsave('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/otherfigures/check_CIP_bysize.png',
       dpi = 600, units = 'in', height = 6, width = 12)

P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.numeric(as.character(variable)), y = Dollars, fill = Current.Funding.Source), 
                                            color = NA, stat = 'identity') +
  facet_grid(Current.Funding.Source ~ `Total Capital Needed`, scales = "free_y") + xlab("Fiscal Year\n(2032 includes all future funding TBA)")
ggsave('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/otherfigures/check_CIP_bysize_type.png',
       dpi = 600, units = 'in', height = 18, width = 15)

# check out normalized repayment schedules... beginning from planned repayment start year,
# how are each funding source doled out?



