# TBW Financial Model - Explore Historic CIP Forecast
# D Gorelick (Aug 2021)

#(2022 this is same script as TBW_financial_model_explore_cip_data it just processes the CIP forecast 
#from 2019 [first section] and 2018 [second section])
# ------------------------------------------

rm(list=ls())
hist_financial_path = 'C:/Users/cmpet/OneDrive/Documents/UNCTBW'

# read in CIP 10-year model forecast years 2019-2030
CIP_Forecast = read.csv(paste(hist_financial_path, '/FY2020-2029_CashFlowAnalysis_Version7.csv', sep = ''))


### summarize the data for trend plotting ----------
library(tidyverse); library(reshape2)
CIP_Forecast = CIP_Forecast[,c(2:ncol(CIP_Forecast))]
CIPF_melt = melt(CIP_Forecast, id = c('Project.No.', 'Project.Name', 'Current.Funding.Source'))
CIPF_melt$Dollars = gsub(CIPF_melt$value, pattern = '\\$', replacement = '')
CIPF_melt$Dollars = gsub(CIPF_melt$Dollars, pattern = ',', replacement = '')
CIPF_melt$Dollars = as.numeric(as.character(CIPF_melt$Dollars))


# plot some stuff to find basics
require(scales)

# without total needed, ignoring spending pre-FY21
# then smooth out labels for plotting
CIPF_melt_sub = CIPF_melt[which(CIPF_melt$variable %in% unique(CIPF_melt$variable)[c(3,4:14)]),]
CIPF_melt_sub$variable = plyr::revalue(CIPF_melt_sub$variable, c('Remaining.FY.2019'='2019',
                                                                 'FY.2020'='2020', 'FY.2021'='2021', 'FY.2022'='2022',
                                                                 'FY.2023'='2023', 'FY.2024'='2024', 'FY.2025'='2025',
                                                                 'FY.2026'='2026', 'FY.2027'='2027', 'FY.2028'='2028', 'FY.2029'='2029', 
                                                                 'Future'='2030'))
P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.integer(as.character(variable)), y = Dollars, fill = Current.Funding.Source), 
                                            color = NA, stat = 'identity') + 
  facet_wrap(Project.Name ~ ., nrow = 12, scales = "free") + scale_y_continuous(labels = comma) +
  scale_x_continuous(labels = as.character(c(seq(2019,2029), "2030+")), breaks = seq(2019,2030), name = "Fiscal Year") +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.8, hjust = 0.7, size = 10), legend.position = "none",
        axis.text.y = element_text(size = 10, face = "bold"))
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIPFY19.png',
       dpi = 800, units = 'in', height = 20, width = 30)

CIPF_melt_sub = CIPF_melt_sub[which(CIPF_melt_sub$Project.Name != "Totals"),]
P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.integer(as.character(variable)), y = Dollars, 
                                                fill = Current.Funding.Source), 
                                            color = NA, stat = 'identity') + 
  scale_y_continuous(labels = comma, name = "Million USD") + scale_x_continuous(labels = as.character(c(seq(2019,2029), "2030+")), 
                                                                                breaks = seq(2019,2030), name = "Fiscal Year") +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.8, hjust = 0.7, size = 14), legend.position = "none",
        axis.text.y = element_text(size = 14, face = "bold"))
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_basicFY19.png',
       dpi = 1200, units = 'in', height = 3.5, width = 5)

### break down funding for small vs medium vs large projects-----
CIPF_melt = melt(CIP_Forecast, id = c('Project.No.', 'Project.Name', 'Current.Funding.Source', 'Total.Funds.Needed'))
CIPF_melt$Dollars = gsub(CIPF_melt$value, pattern = '\\$', replacement = '')
CIPF_melt$Dollars = gsub(CIPF_melt$Dollars, pattern = ',', replacement = '')
CIPF_melt$Dollars = as.numeric(as.character(CIPF_melt$Dollars))
CIPF_melt$TotalDollars = gsub(CIPF_melt$Total.Funds.Needed, pattern = '\\$', replacement = '')
CIPF_melt$TotalDollars = gsub(CIPF_melt$TotalDollars, pattern = ',', replacement = '')
CIPF_melt$TotalDollars = as.numeric(as.character(CIPF_melt$TotalDollars))

CIPF_melt$`Total Capital Needed` = "Large Projects (>$10m)"
CIPF_melt$`Total Capital Needed`[which(CIPF_melt$TotalDollars <= 10000000)] = "Medium Projects (>$1m, <$10m)"
CIPF_melt$`Total Capital Needed`[which(CIPF_melt$TotalDollars <= 1000000)] = "Small Projects (<$1m)"

CIPF_melt_sub = CIPF_melt[which(CIPF_melt$variable %in% unique(CIPF_melt$variable)[c(3,4:14)]),]
CIPF_melt_sub$variable = plyr::revalue(CIPF_melt_sub$variable, c('Remaining.FY.2019'='2019',
                                                                 'FY.2020'='2020', 'FY.2021'='2021', 'FY.2022'='2022',
                                                                 'FY.2023'='2023', 'FY.2024'='2024', 'FY.2025'='2025',
                                                                 'FY.2026'='2026', 'FY.2027'='2027', 'FY.2028'='2028', 'FY.2029'='2029',
                                                                 'Future'='2030'))
CIPF_melt_sub = CIPF_melt_sub[which(CIPF_melt_sub$Project.Name != "Totals"),]
P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.numeric(as.character(variable)), y = Dollars/1000000,
                                                fill = Current.Funding.Source),
                                            color = NA, stat = 'identity') +
  facet_wrap(`Total Capital Needed` ~ ., ncol = 3, scales = "free_y") +
  scale_x_continuous(labels = as.character(c(seq(2019,2029), "2030+")),
                     breaks = seq(2019,2030), name = "Fiscal Year") +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.8, hjust = 0.7, size = 10), legend.position = "none",
        axis.text.y = element_text(size = 10),
        strip.text.x = element_text(size = 15, face = "bold")) +
  xlab("Fiscal Year\n(2032 includes all future funding TBA)") + scale_y_continuous(labels = comma, name = "Million USD")
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_bysizeFY19.png',
       dpi = 1000, units = 'in', height = 4, width = 12)

# CIPF_melt_sub$Current.Funding.Source[which(CIPF_melt_sub$Current.Funding.Source %in% c("Renewal and Replacement Fund",
#                                                                                        "Capital Improvement Fund",
#                                                                                        "Energy Fund"))] = "Reserve Funds"
# CIPF_melt_sub$Current.Funding.Source[which(CIPF_melt_sub$Current.Funding.Source %in% c("Revenue Bonds (Future)",
#                                                                                        "Revenue Bonds (320)",
#                                                                                        "Revenue Bonds (350)"))] = "Debt Issuance"
# CIPF_melt_sub$Current.Funding.Source[which(CIPF_melt_sub$Current.Funding.Source %in% c("SWFWMD Co-Funding",
#                                                                                        "Member Goverment Contribution-JPA",
#                                                                                        "State Grant"))] = "State and Local Grants"
# P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.numeric(as.character(variable)), y = Dollars/1000000,
#                                                 fill = Current.Funding.Source),
#                                             color = NA, stat = 'identity') +
#   facet_wrap(`Total Capital Needed` ~ ., ncol = 3, scales = "free_y") +
#   scale_x_continuous(labels = as.character(c(seq(2021,2032), "2033+")),
#                      breaks = seq(2021,2033), name = "Fiscal Year") +
#   theme(axis.text.x = element_text(angle = 45, vjust = 0.8, hjust = 0.7, size = 10), legend.position = "right",
#         axis.text.y = element_text(size = 10),
#         strip.text.x = element_text(size = 15, face = "bold")) +
#   xlab("Fiscal Year\n(2032 includes all future funding TBA)") + scale_y_continuous(labels = comma, name = "Million USD")
# ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_bysize_simple_categories_legendFY22.png',
#        dpi = 1000, units = 'in', height = 4, width = 12)
#
P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.numeric(as.character(variable)), y = Dollars, fill = Current.Funding.Source),
                                            color = NA, stat = 'identity') +
  facet_grid(Current.Funding.Source ~ `Total Capital Needed`, scales = "free_y") +
  xlab("Fiscal Year\n(2030 includes all future funding TBA)") + scale_y_continuous(labels = comma)
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_bysize_typeFY19.png',
       dpi = 600, units = 'in', height = 18, width = 15)

# check out normalized repayment schedules... beginning from planned repayment start year,
# how are each funding source doled out?
rm(P); CIPF_normalizedbyyear = c()
print(paste("Total CIP Projects (FY19 to FY30+): ", length(unique(CIPF_melt_sub$Project.Name)), sep = ""))
for (project in unique(CIPF_melt_sub$Project.Name)) {
  # isolate each project, select just years where it is funded, re-index them 0-X rather than 2019-2029
  project_data = CIPF_melt_sub[which(CIPF_melt_sub$Project.Name == project),]
  first_year_funded = min(as.numeric(as.character(project_data$variable[which(project_data$Dollars != 0)])))
  last_year_funded = max(as.numeric(as.character(project_data$variable[which(project_data$Dollars != 0)])))
  
  reordered_data = project_data[which(as.numeric(as.character(project_data$variable)) >= first_year_funded & 
                                        as.numeric(as.character(project_data$variable)) <= last_year_funded), 
                                c("Project.Name", "Current.Funding.Source", 
                                  "TotalDollars", "Dollars", "variable", "Total Capital Needed")]
  reordered_data$Year = as.numeric(as.character(reordered_data$variable))
  reordered_data$`Normalized Year Index` = reordered_data$Year - min(reordered_data$Year)
  
  # print some statistics
  print(paste("Project Name: ", project_data$Project.Name, sep = ""))
  print(paste("Project Total Cost: ", project_data$Total.Funds.Needed, sep = ""))
  print(paste("Years of funding needed: ", last_year_funded - first_year_funded + 1, sep = ""))
  print(paste("Number of funding sources: ", length(unique(reordered_data$Current.Funding.Source)), sep = ""))
  
  # combine into new dataset for plotting
  CIPF_normalizedbyyear = rbind(CIPF_normalizedbyyear, reordered_data)
}

# grab summary statistics for project repayment schedules
CIP_raw_schedule = CIPF_melt_sub %>% 
  group_by(Current.Funding.Source, `variable`, `Total Capital Needed`) %>% 
  summarize(total = sum(Dollars))
CIP_raw_schedule = CIP_raw_schedule %>% 
  group_by(`variable`, Current.Funding.Source) %>% summarize(Total = sum(total))
CIP_raw_schedule = reshape2::dcast(CIP_raw_schedule, 
                                   `Current.Funding.Source` ~ `variable`)
#CIP_raw_schedule[1,2] = 7691664

write.table(CIP_raw_schedule, sep = ",", row.names = FALSE,
            'C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/original_CIP_spending_all_projectsFY19.csv')

CIP_remaining_schedule = CIPF_melt_sub[which(CIPF_melt_sub$`Total Capital Needed` != "Large Projects (>$10m)"),] %>% 
  group_by(Current.Funding.Source, `variable`, `Total Capital Needed`) %>% 
  summarize(total = sum(Dollars))
CIP_remaining_schedule = CIP_remaining_schedule %>% 
  group_by(`variable`, Current.Funding.Source) %>% summarize(Total = sum(total))
CIP_remaining_schedule = reshape2::dcast(CIP_remaining_schedule, 
                                         `Current.Funding.Source` ~ `variable`)
#CIP_remaining_schedule[1,2] = 7691664

fraction_major_project_spending = 
  round(1 - CIP_remaining_schedule[,2:ncol(CIP_remaining_schedule)]/CIP_raw_schedule[,2:ncol(CIP_raw_schedule)],2)
fraction_major_project_spending[is.na(fraction_major_project_spending)] = 0
rownames(fraction_major_project_spending) = CIP_remaining_schedule$Current.Funding.Source
write.table(fraction_major_project_spending, sep = ",", col.names = NA,
            'C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/original_CIP_spending_major_projects_fractionFY19.csv')


sum_repayment_per_year_schedule = CIPF_normalizedbyyear %>% 
  group_by(Current.Funding.Source, `Normalized Year Index`, `Total Capital Needed`) %>% 
  summarize(total = sum(Dollars))
all_project_schedule = sum_repayment_per_year_schedule %>% 
  group_by(`Normalized Year Index`, Current.Funding.Source) %>% summarize(Total = sum(total))
all_project_schedule = reshape2::dcast(all_project_schedule, 
                                       `Current.Funding.Source` ~ `Normalized Year Index`)
remaining_project_schedule[is.na(remaining_project_schedule)] = 0
all_project_schedule[is.na(all_project_schedule)] = 0
fraction_cip_spending_for_other_projects_by_source = round(
  remaining_project_schedule[,2:ncol(remaining_project_schedule)] / 
    all_project_schedule[,2:ncol(all_project_schedule)], 2)
write.table(all_project_schedule, sep = ",", row.names = FALSE,
            'C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/normalized_CIP_spending_all_projectsFY19.csv')

major_project_schedule = 
  sum_repayment_per_year_schedule[which(sum_repayment_per_year_schedule$`Total Capital Needed` == "Large Projects (>$10m)"),] %>%
  group_by(`Normalized Year Index`, Current.Funding.Source) %>% summarize(Total = sum(total)) 
major_project_schedule = reshape2::dcast(major_project_schedule, 
                                         `Current.Funding.Source` ~ `Normalized Year Index`)
major_project_fractional_splits_over_time = colSums(major_project_schedule[,2:ncol(major_project_schedule)]) / 
  sum(major_project_schedule[,2:ncol(major_project_schedule)])

major_project_fractional_splits_over_source = t(t(major_project_schedule[,2:ncol(major_project_schedule)]) / 
                                                  colSums(major_project_schedule[,2:ncol(major_project_schedule)]))
remaining_project_schedule = 
  sum_repayment_per_year_schedule[which(sum_repayment_per_year_schedule$`Total Capital Needed` != "Large Projects (>$10m)"),] %>%
  group_by(`Normalized Year Index`, Current.Funding.Source) %>% summarize(Total = sum(total))
remaining_project_schedule = reshape2::dcast(remaining_project_schedule, 
                                             `Current.Funding.Source` ~ `Normalized Year Index`)
remaining_project_fractional_splits_over_time = colSums(remaining_project_schedule[,2:ncol(remaining_project_schedule)], na.rm = TRUE) / 
  sum(remaining_project_schedule[,2:ncol(remaining_project_schedule)], na.rm = TRUE)

remaining_project_fractional_splits_over_source = t(t(remaining_project_schedule[,2:ncol(remaining_project_schedule)]) / 
                                                      colSums(remaining_project_schedule[,2:ncol(remaining_project_schedule)], na.rm = TRUE))


# calculate some summary stats for input to financial model as default splits
fraction_cip_spending_for_other_projects = sum(remaining_project_schedule[,2:ncol(remaining_project_schedule)], na.rm = TRUE)/
  (sum(remaining_project_schedule[,2:ncol(remaining_project_schedule)], na.rm = TRUE) + 
     sum(major_project_schedule[,2:ncol(major_project_schedule)]))

fraction_cip_spending_for_major_projects_by_source = 1 - fraction_cip_spending_for_other_projects_by_source
rownames(fraction_cip_spending_for_major_projects_by_source) = all_project_schedule$Current.Funding.Source

fraction_cip_spending_for_major_projects_by_source[is.na(fraction_cip_spending_for_major_projects_by_source)] = 0
write.table(fraction_cip_spending_for_major_projects_by_source, sep = ",", col.names = NA,
            'C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/normalized_CIP_spending_major_projects_fractionFY19.csv')

### plot results-----
P = ggplot(data = CIPF_normalizedbyyear) + geom_bar(aes(x = `Normalized Year Index`, y = Dollars, fill = Current.Funding.Source), 
                                                    color = NA, stat = 'identity') +
  xlab("Years after First Year a Project is Funded") + scale_y_continuous(labels = comma)
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_normalizedstartyear_allFY19.png',
       dpi = 600, units = 'in', height = 5, width = 8)

P = ggplot(data = CIPF_normalizedbyyear) + geom_bar(aes(x = `Normalized Year Index`, y = Dollars, fill = Current.Funding.Source), 
                                                    color = NA, stat = 'identity') +
  facet_wrap(`Total Capital Needed`~., scales = "free_y", ncol = 3) + 
  xlab("Years after First Year a Project is Funded") + scale_y_continuous(labels = comma)
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_normalizedstartyearFY19.png',
       dpi = 600, units = 'in', height = 6, width = 12)

P = ggplot(data = CIPF_normalizedbyyear) + geom_bar(aes(x = `Normalized Year Index`, fill = Current.Funding.Source, y = Dollars), 
                                                    color = NA, stat = 'identity', position = 'fill') +
  facet_wrap(`Total Capital Needed`~., ncol = 3) + 
  xlab("Years after First Year a Project is Funded")
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_normalizedstartyear_relativesFY19.png',
       dpi = 600, units = 'in', height = 6, width = 12)

####################################################################################
##Next Historic CIP forecast (2018 - 2029)##
####################################################################################
# read in CIP 10-year model forecast years 2019-2030
CIP_Forecast2018 = read.csv(paste(hist_financial_path, '/FY2018_CIP_forcast.csv', sep = ''))


### summarize the data for trend plotting ----------
library(tidyverse); library(reshape2)
CIP_Forecast2018 = CIP_Forecast2018[,c(2:ncol(CIP_Forecast2018))]
CIPF_melt2018 = melt(CIP_Forecast2018, id = c('Project.No.', 'Project.Name', 'Current.Funding.Source'))
CIPF_melt2018$Dollars = gsub(CIPF_melt2018$value, pattern = '\\$', replacement = '')
CIPF_melt2018$Dollars = gsub(CIPF_melt2018$Dollars, pattern = ',', replacement = '')
CIPF_melt2018$Dollars = as.numeric(as.character(CIPF_melt2018$Dollars))


# plot some stuff to find basics
require(scales)

# without total needed, ignoring spending pre-FY21
# then smooth out labels for plotting
CIPF_melt_sub2018 = CIPF_melt2018[which(CIPF_melt2018$variable %in% unique(CIPF_melt2018$variable)[c(3,4:13)]),]
CIPF_melt_sub2018$variable = plyr::revalue(CIPF_melt_sub2018$variable, c('FY.2018'='2018',
                                                                 'FY.2019'='2019', 'FY.2020'='2020', 'FY.2021'='2021',
                                                                 'FY.2022'='2022', 'FY.2023'='2023', 'FY.2024'='2024',
                                                                 'FY.2025'='2025', 'FY.2026'='2026', 'FY.2027'='2027', 'FY.2028'='2028'))
P = ggplot(data = CIPF_melt_sub2018) + geom_bar(aes(x = as.integer(as.character(variable)), y = Dollars, fill = Current.Funding.Source), 
                                            color = NA, stat = 'identity') + 
  facet_wrap(Project.Name ~ ., nrow = 12, scales = "free") + scale_y_continuous(labels = comma) +
  scale_x_continuous(labels = as.character(c(seq(2018,2028))), breaks = seq(2018,2028), name = "Fiscal Year") +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.8, hjust = 0.7, size = 10), legend.position = "none",
        axis.text.y = element_text(size = 10, face = "bold"))
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIPFY18.png',
       dpi = 800, units = 'in', height = 20, width = 30)

CIPF_melt_sub2018 = CIPF_melt_sub2018[which(CIPF_melt_sub2018$Project.Name != "Totals"),]
P = ggplot(data = CIPF_melt_sub2018) + geom_bar(aes(x = as.integer(as.character(variable)), y = Dollars, 
                                                fill = Current.Funding.Source), 
                                            color = NA, stat = 'identity') + 
  scale_y_continuous(labels = comma, name = "Million USD") + scale_x_continuous(labels = as.character(c(seq(2018,2028))), 
                                                                                breaks = seq(2018,2028), name = "Fiscal Year") +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.8, hjust = 0.7, size = 14), legend.position = "none",
        axis.text.y = element_text(size = 14, face = "bold"))
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_basicFY18.png',
       dpi = 1200, units = 'in', height = 3.5, width = 5)

### break down funding for small vs medium vs large projects-----
CIPF_melt2018 = melt(CIP_Forecast2018, id = c('Project.No.', 'Project.Name', 'Current.Funding.Source', 'Total.Funds.Needed'))
CIPF_melt2018$Dollars = gsub(CIPF_melt2018$value, pattern = '\\$', replacement = '')
CIPF_melt2018$Dollars = gsub(CIPF_melt2018$Dollars, pattern = ',', replacement = '')
CIPF_melt2018$Dollars = as.numeric(as.character(CIPF_melt2018$Dollars))
CIPF_melt2018$TotalDollars = gsub(CIPF_melt2018$Total.Funds.Needed, pattern = '\\$', replacement = '')
CIPF_melt2018$TotalDollars = gsub(CIPF_melt2018$TotalDollars, pattern = ',', replacement = '')
CIPF_melt2018$TotalDollars = as.numeric(as.character(CIPF_melt2018$TotalDollars))

CIPF_melt2018$`Total Capital Needed` = "Large Projects (>$10m)"
CIPF_melt2018$`Total Capital Needed`[which(CIPF_melt2018$TotalDollars <= 10000000)] = "Medium Projects (>$1m, <$10m)"
CIPF_melt2018$`Total Capital Needed`[which(CIPF_melt2018$TotalDollars <= 1000000)] = "Small Projects (<$1m)"

CIPF_melt_sub2018 = CIPF_melt2018[which(CIPF_melt2018$variable %in% unique(CIPF_melt2018$variable)[c(3,4:13)]),]
CIPF_melt_sub2018$variable = plyr::revalue(CIPF_melt_sub2018$variable, c('FY.2018'='2018',
                                                                 'FY.2019'='2019', 'FY.2020'='2020', 'FY.2021'='2021',
                                                                 'FY.2022'='2022', 'FY.2023'='2023', 'FY.2024'='2024',
                                                                 'FY.2025'='2025', 'FY.2026'='2026', 'FY.2027'='2027', 'FY.2028'='2028'))

CIPF_melt_sub2018 = CIPF_melt_sub2018[which(CIPF_melt_sub2018$Project.Name != "Totals"),]
P = ggplot(data = CIPF_melt_sub2018) + geom_bar(aes(x = as.numeric(as.character(variable)), y = Dollars/1000000,
                                                fill = Current.Funding.Source),
                                            color = NA, stat = 'identity') +
  facet_wrap(`Total Capital Needed` ~ ., ncol = 3, scales = "free_y") +
  scale_x_continuous(labels = as.character(c(seq(2018,2028))),
                     breaks = seq(2018,2028), name = "Fiscal Year") +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.8, hjust = 0.7, size = 10), legend.position = "none",
        axis.text.y = element_text(size = 10),
        strip.text.x = element_text(size = 15, face = "bold")) +
  xlab("Fiscal Year") + scale_y_continuous(labels = comma, name = "Million USD")
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_bysizeFY18.png',
       dpi = 1000, units = 'in', height = 4, width = 12)

# CIPF_melt_sub$Current.Funding.Source[which(CIPF_melt_sub$Current.Funding.Source %in% c("Renewal and Replacement Fund",
#                                                                                        "Capital Improvement Fund",
#                                                                                        "Energy Fund"))] = "Reserve Funds"
# CIPF_melt_sub$Current.Funding.Source[which(CIPF_melt_sub$Current.Funding.Source %in% c("Revenue Bonds (Future)",
#                                                                                        "Revenue Bonds (320)",
#                                                                                        "Revenue Bonds (350)"))] = "Debt Issuance"
# CIPF_melt_sub$Current.Funding.Source[which(CIPF_melt_sub$Current.Funding.Source %in% c("SWFWMD Co-Funding",
#                                                                                        "Member Goverment Contribution-JPA",
#                                                                                        "State Grant"))] = "State and Local Grants"
# P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.numeric(as.character(variable)), y = Dollars/1000000,
#                                                 fill = Current.Funding.Source),
#                                             color = NA, stat = 'identity') +
#   facet_wrap(`Total Capital Needed` ~ ., ncol = 3, scales = "free_y") +
#   scale_x_continuous(labels = as.character(c(seq(2021,2032), "2033+")),
#                      breaks = seq(2021,2033), name = "Fiscal Year") +
#   theme(axis.text.x = element_text(angle = 45, vjust = 0.8, hjust = 0.7, size = 10), legend.position = "right",
#         axis.text.y = element_text(size = 10),
#         strip.text.x = element_text(size = 15, face = "bold")) +
#   xlab("Fiscal Year\n(2032 includes all future funding TBA)") + scale_y_continuous(labels = comma, name = "Million USD")
# ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_bysize_simple_categories_legendFY22.png',
#        dpi = 1000, units = 'in', height = 4, width = 12)
#
P = ggplot(data = CIPF_melt_sub2018) + geom_bar(aes(x = as.numeric(as.character(variable)), y = Dollars, fill = Current.Funding.Source),
                                            color = NA, stat = 'identity') +
  facet_grid(Current.Funding.Source ~ `Total Capital Needed`, scales = "free_y") +
  xlab("Fiscal Year") + scale_y_continuous(labels = comma)
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_bysize_typeFY18.png',
       dpi = 600, units = 'in', height = 18, width = 15)

# check out normalized repayment schedules... beginning from planned repayment start year,
# how are each funding source doled out?
rm(P); CIPF_normalizedbyyear2018 = c()
print(paste("Total CIP Projects (FY18 to FY28): ", length(unique(CIPF_melt_sub2018$Project.Name)), sep = ""))
for (project in unique(CIPF_melt_sub2018$Project.Name)) {
  # isolate each project, select just years where it is funded, re-index them 0-X rather than 2018-2028
  project_data2018 = CIPF_melt_sub2018[which(CIPF_melt_sub2018$Project.Name == project),]
  first_year_funded2018 = min(as.numeric(as.character(project_data2018$variable[which(project_data2018$Dollars != 0)])))
  last_year_funded2018 = max(as.numeric(as.character(project_data2018$variable[which(project_data2018$Dollars != 0)])))
  
  reordered_data2018 = project_data2018[which(as.numeric(as.character(project_data2018$variable)) >= first_year_funded2018 & 
                                        as.numeric(as.character(project_data2018$variable)) <= last_year_funded2018), 
                                c("Project.Name", "Current.Funding.Source", 
                                  "TotalDollars", "Dollars", "variable", "Total Capital Needed")]
  reordered_data2018$Year = as.numeric(as.character(reordered_data2018$variable))
  reordered_data2018$`Normalized Year Index` = reordered_data2018$Year - min(reordered_data2018$Year)
  
  # print some statistics
  print(paste("Project Name: ", project_data2018$Project.Name, sep = ""))
  print(paste("Project Total Cost: ", project_data2018$Total.Funds.Needed, sep = ""))
  print(paste("Years of funding needed: ", last_year_funded2018 - first_year_funded2018 + 1, sep = ""))
  print(paste("Number of funding sources: ", length(unique(reordered_data2018$Current.Funding.Source)), sep = ""))
  
  # combine into new dataset for plotting
  CIPF_normalizedbyyear2018 = rbind(CIPF_normalizedbyyear2018, reordered_data2018)
}

# grab summary statistics for project repayment schedules
CIP_raw_schedule2018 = CIPF_melt_sub2018 %>% 
  group_by(Current.Funding.Source, `variable`, `Total Capital Needed`) %>% 
  summarize(total = sum(Dollars))
CIP_raw_schedule2018 = CIP_raw_schedule2018 %>% 
  group_by(`variable`, Current.Funding.Source) %>% summarize(Total = sum(total))
CIP_raw_schedule2018 = reshape2::dcast(CIP_raw_schedule2018, 
                                   `Current.Funding.Source` ~ `variable`)
#CIP_raw_schedule[1,2] = 7691664

write.table(CIP_raw_schedule2018, sep = ",", row.names = FALSE,
            'C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/original_CIP_spending_all_projectsFY18.csv')

CIP_remaining_schedule2018 = CIPF_melt_sub2018[which(CIPF_melt_sub2018$`Total Capital Needed` != "Large Projects (>$10m)"),] %>% 
  group_by(Current.Funding.Source, `variable`, `Total Capital Needed`) %>% 
  summarize(total = sum(Dollars))
CIP_remaining_schedule2018 = CIP_remaining_schedule2018 %>% 
  group_by(`variable`, Current.Funding.Source) %>% summarize(Total = sum(total))
CIP_remaining_schedule2018 = reshape2::dcast(CIP_remaining_schedule2018, 
                                         `Current.Funding.Source` ~ `variable`)
#CIP_remaining_schedule[1,2] = 7691664

fraction_major_project_spending2018 = 
  round(1 - CIP_remaining_schedule2018[,2:ncol(CIP_remaining_schedule2018)]/CIP_raw_schedule2018[,2:ncol(CIP_raw_schedule2018)],2)
fraction_major_project_spending2018[is.na(fraction_major_project_spending2018)] = 0
rownames(fraction_major_project_spending2018) = CIP_remaining_schedule2018$Current.Funding.Source
write.table(fraction_major_project_spending2018, sep = ",", col.names = NA,
            'C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/original_CIP_spending_major_projects_fractionFY18.csv')


sum_repayment_per_year_schedule2018 = CIPF_normalizedbyyear2018 %>% 
  group_by(Current.Funding.Source, `Normalized Year Index`, `Total Capital Needed`) %>% 
  summarize(total = sum(Dollars))
all_project_schedule2018 = sum_repayment_per_year_schedule2018 %>% 
  group_by(`Normalized Year Index`, Current.Funding.Source) %>% summarize(Total = sum(total))
all_project_schedule2018 = reshape2::dcast(all_project_schedule2018, 
                                       `Current.Funding.Source` ~ `Normalized Year Index`)
all_project_schedule2018[is.na(all_project_schedule2018)] = 0

write.table(all_project_schedule2018, sep = ",", row.names = FALSE,
            'C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/normalized_CIP_spending_all_projectsFY18.csv')

major_project_schedule2018 = 
  sum_repayment_per_year_schedule2018[which(sum_repayment_per_year_schedule2018$`Total Capital Needed` == "Large Projects (>$10m)"),] %>%
  group_by(`Normalized Year Index`, Current.Funding.Source) %>% summarize(Total = sum(total)) 
major_project_schedule2018 = reshape2::dcast(major_project_schedule2018, 
                                         `Current.Funding.Source` ~ `Normalized Year Index`)
major_project_fractional_splits_over_time2018 = colSums(major_project_schedule2018[,2:ncol(major_project_schedule2018)]) / 
  sum(major_project_schedule2018[,2:ncol(major_project_schedule2018)])

major_project_fractional_splits_over_source2018 = t(t(major_project_schedule2018[,2:ncol(major_project_schedule2018)]) / 
                                                  colSums(major_project_schedule2018[,2:ncol(major_project_schedule2018)]))
remaining_project_schedule2018 = 
  sum_repayment_per_year_schedule2018[which(sum_repayment_per_year_schedule2018$`Total Capital Needed` != "Large Projects (>$10m)"),] %>%
  group_by(`Normalized Year Index`, Current.Funding.Source) %>% summarize(Total = sum(total))
remaining_project_schedule2018 = reshape2::dcast(remaining_project_schedule2018, 
                                             `Current.Funding.Source` ~ `Normalized Year Index`)
remaining_project_fractional_splits_over_time2018 = colSums(remaining_project_schedule2018[,2:ncol(remaining_project_schedule2018)], na.rm = TRUE) / 
  sum(remaining_project_schedule2018[,2:ncol(remaining_project_schedule2018)], na.rm = TRUE)

remaining_project_fractional_splits_over_source2018 = t(t(remaining_project_schedule2018[,2:ncol(remaining_project_schedule2018)]) / 
                                                      colSums(remaining_project_schedule2018[,2:ncol(remaining_project_schedule2018)], na.rm = TRUE))
remaining_project_schedule2018[is.na(remaining_project_schedule2018)] = 0
fraction_cip_spending_for_other_projects_by_source2018 = round(
  remaining_project_schedule2018[,2:ncol(remaining_project_schedule2018)] / 
    all_project_schedule2018[,2:ncol(all_project_schedule2018)], 2)

# calculate some summary stats for input to financial model as default splits
fraction_cip_spending_for_other_projects2018 = sum(remaining_project_schedule2018[,2:ncol(remaining_project_schedule2018)], na.rm = TRUE)/
  (sum(remaining_project_schedule2018[,2:ncol(remaining_project_schedule2018)], na.rm = TRUE) + 
     sum(major_project_schedule2018[,2:ncol(major_project_schedule2018)]))

fraction_cip_spending_for_major_projects_by_source2018 = 1 - fraction_cip_spending_for_other_projects_by_source2018
rownames(fraction_cip_spending_for_major_projects_by_source2018) = all_project_schedule2018$Current.Funding.Source

fraction_cip_spending_for_major_projects_by_source2018[is.na(fraction_cip_spending_for_major_projects_by_source2018)] = 0
write.table(fraction_cip_spending_for_major_projects_by_source2018, sep = ",", col.names = NA,
            'C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/normalized_CIP_spending_major_projects_fractionFY18.csv')

### plot results-----
P = ggplot(data = CIPF_normalizedbyyear2018) + geom_bar(aes(x = `Normalized Year Index`, y = Dollars, fill = Current.Funding.Source), 
                                                    color = NA, stat = 'identity') +
  xlab("Years after First Year a Project is Funded") + scale_y_continuous(labels = comma)
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_normalizedstartyear_allFY18.png',
       dpi = 600, units = 'in', height = 5, width = 8)

P = ggplot(data = CIPF_normalizedbyyear2018) + geom_bar(aes(x = `Normalized Year Index`, y = Dollars, fill = Current.Funding.Source), 
                                                    color = NA, stat = 'identity') +
  facet_wrap(`Total Capital Needed`~., scales = "free_y", ncol = 3) + 
  xlab("Years after First Year a Project is Funded") + scale_y_continuous(labels = comma)
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_normalizedstartyearFY18.png',
       dpi = 600, units = 'in', height = 6, width = 12)

P = ggplot(data = CIPF_normalizedbyyear2018) + geom_bar(aes(x = `Normalized Year Index`, fill = Current.Funding.Source, y = Dollars), 
                                                    color = NA, stat = 'identity', position = 'fill') +
  facet_wrap(`Total Capital Needed`~., ncol = 3) + 
  xlab("Years after First Year a Project is Funded")
ggsave('C:/Users/cmpet/OneDrive/Documents/UNCTBW/Financialoutputs/check_CIP_normalizedstartyear_relativesFY18.png',
       dpi = 600, units = 'in', height = 6, width = 12)
