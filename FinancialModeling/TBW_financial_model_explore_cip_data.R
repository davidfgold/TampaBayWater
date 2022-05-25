# TBW Financial Model - Explore CIP Forecast
# D Gorelick (Aug 2021)
# ------------------------------------------

rm(list=ls())
hist_financial_path = 'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/financials'

# read in CIP 10-year model forecast
CIP_Forecast = read.csv(paste(hist_financial_path, '/FinancialModelForecast10yrmultiplesourcesTBW.csv', sep = ''))

# summarize the data for trend plotting
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
CIPF_melt_sub$variable = plyr::revalue(CIPF_melt_sub$variable, c('Remaining.FY.2021'='2021', 'FY.2022'='2022',
                                        'FY.2023'='2023', 'FY.2024'='2024', 'FY.2025'='2025',
                                        'FY.2026'='2026', 'FY.2027'='2027', 'FY.2028'='2028',
                                        'FY.2029'='2029', 'FY.2030'='2030', 'FY.2031'='2031', 'Future'='2032'))
P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.integer(as.character(variable)), y = Dollars, fill = Current.Funding.Source), 
                                        color = NA, stat = 'identity') + 
  facet_wrap(Project.Name ~ ., nrow = 12, scales = "free") + scale_y_continuous(labels = comma) +
  scale_x_continuous(labels = as.character(c(seq(2021,2031), "2032+")), breaks = seq(2021,2032), name = "Fiscal Year") +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.8, hjust = 0.7, size = 10), legend.position = "none",
        axis.text.y = element_text(size = 10, face = "bold"))
#ggsave('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/otherfigures/check_CIP.png',
#       dpi = 800, units = 'in', height = 20, width = 30)

CIPF_melt_sub = CIPF_melt_sub[which(CIPF_melt_sub$Project.Name != "Totals"),]
P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.integer(as.character(variable)), y = Dollars, 
                                                fill = Current.Funding.Source), 
                                            color = NA, stat = 'identity') + 
  scale_y_continuous(labels = comma, name = "Million USD") + scale_x_continuous(labels = as.character(c(seq(2021,2031), "2032+")), 
                                                          breaks = seq(2021,2032), name = "Fiscal Year") +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.8, hjust = 0.7, size = 14), legend.position = "none",
        axis.text.y = element_text(size = 14, face = "bold"))
ggsave('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/otherfigures/check_CIP_basic.png',
       dpi = 1200, units = 'in', height = 3.5, width = 5)

# break down funding for small vs medium vs large projects
CIPF_melt = melt(CIP_Forecast, id = c('Project.No.', 'Project.Name', 'Current.Funding.Source', 'Total.Funds.Needed'))
CIPF_melt$Dollars = gsub(CIPF_melt$value, pattern = '\\$', replacement = '')
CIPF_melt$Dollars = gsub(CIPF_melt$Dollars, pattern = ',', replacement = '')
CIPF_melt$Dollars = as.numeric(as.character(CIPF_melt$Dollars))
CIPF_melt$TotalDollars = gsub(CIPF_melt$Total.Funds.Needed, pattern = '\\$', replacement = '')
CIPF_melt$TotalDollars = gsub(CIPF_melt$TotalDollars, pattern = ',', replacement = '')
CIPF_melt$TotalDollars = as.numeric(as.character(CIPF_melt$TotalDollars))

CIPF_melt$`Total Capital Needed` = "Large Projects (>$75m)"
CIPF_melt$`Total Capital Needed`[which(CIPF_melt$TotalDollars <= 75000000)] = "Medium Projects (>$10m, <$75m)"
CIPF_melt$`Total Capital Needed`[which(CIPF_melt$TotalDollars <= 10000000)] = "Small Projects (<$10m)"

CIPF_melt_sub = CIPF_melt[which(CIPF_melt$variable %in% unique(CIPF_melt$variable)[c(3,4:14)]),]
CIPF_melt_sub$variable = plyr::revalue(CIPF_melt_sub$variable, c('Remaining.FY.2021'='2021', 'FY.2022'='2022',
                                                                 'FY.2023'='2023', 'FY.2024'='2024', 'FY.2025'='2025',
                                                                 'FY.2026'='2026', 'FY.2027'='2027', 'FY.2028'='2028',
                                                                 'FY.2029'='2029', 'FY.2030'='2030', 'FY.2031'='2031', 'Future'='2032'))
CIPF_melt_sub = CIPF_melt_sub[which(CIPF_melt_sub$Project.Name != "Totals"),]
P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.numeric(as.character(variable)), y = Dollars/1000000, 
                                                fill = Current.Funding.Source), 
                                            color = NA, stat = 'identity') +
  facet_wrap(`Total Capital Needed` ~ ., ncol = 3, scales = "free_y") + 
  scale_x_continuous(labels = as.character(c(seq(2021,2031), "2032+")), 
                       breaks = seq(2021,2032), name = "Fiscal Year") +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.8, hjust = 0.7, size = 10), legend.position = "none",
        axis.text.y = element_text(size = 10),
        strip.text.x = element_text(size = 15, face = "bold")) +
  xlab("Fiscal Year\n(2032 includes all future funding TBA)") + scale_y_continuous(labels = comma, name = "Million USD")
ggsave('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/otherfigures/check_CIP_bysize.png',
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
P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.numeric(as.character(variable)), y = Dollars/1000000, 
                                                fill = Current.Funding.Source), 
                                            color = NA, stat = 'identity') +
  facet_wrap(`Total Capital Needed` ~ ., ncol = 3, scales = "free_y") + 
  scale_x_continuous(labels = as.character(c(seq(2021,2031), "2032+")), 
                     breaks = seq(2021,2032), name = "Fiscal Year") +
  theme(axis.text.x = element_text(angle = 45, vjust = 0.8, hjust = 0.7, size = 10), legend.position = "right",
        axis.text.y = element_text(size = 10),
        strip.text.x = element_text(size = 15, face = "bold")) +
  xlab("Fiscal Year\n(2032 includes all future funding TBA)") + scale_y_continuous(labels = comma, name = "Million USD")
ggsave('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/otherfigures/check_CIP_bysize_simple_categories_legend.png',
       dpi = 1000, units = 'in', height = 4, width = 12)

P = ggplot(data = CIPF_melt_sub) + geom_bar(aes(x = as.numeric(as.character(variable)), y = Dollars, fill = Current.Funding.Source), 
                                            color = NA, stat = 'identity') +
  facet_grid(Current.Funding.Source ~ `Total Capital Needed`, scales = "free_y") + 
  xlab("Fiscal Year\n(2032 includes all future funding TBA)") + scale_y_continuous(labels = comma)
ggsave('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/otherfigures/check_CIP_bysize_type.png',
       dpi = 600, units = 'in', height = 18, width = 15)

# check out normalized repayment schedules... beginning from planned repayment start year,
# how are each funding source doled out?
rm(P); CIPF_normalizedbyyear = c()
print(paste("Total CIP Projects (FY21 to FY31+): ", length(unique(CIPF_melt_sub$Project.Name)), sep = ""))
for (project in unique(CIPF_melt_sub$Project.Name)) {
  # isolate each project, select just years where it is funded, re-index them 0-X rather than 2021-2031
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
CIP_raw_schedule[1,2] = 7691664

write.table(CIP_raw_schedule, sep = ",", row.names = FALSE,
            'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/model_input_data/original_CIP_spending_all_projects.csv')

CIP_remaining_schedule = CIPF_melt_sub[which(CIPF_melt_sub$`Total Capital Needed` != "Large Projects (>$75m)"),] %>% 
  group_by(Current.Funding.Source, `variable`, `Total Capital Needed`) %>% 
  summarize(total = sum(Dollars))
CIP_remaining_schedule = CIP_remaining_schedule %>% 
  group_by(`variable`, Current.Funding.Source) %>% summarize(Total = sum(total))
CIP_remaining_schedule = reshape2::dcast(CIP_remaining_schedule, 
                                   `Current.Funding.Source` ~ `variable`)
CIP_remaining_schedule[1,2] = 7691664

fraction_major_project_spending = 
  round(1 - CIP_remaining_schedule[,2:ncol(CIP_remaining_schedule)]/CIP_raw_schedule[,2:ncol(CIP_raw_schedule)],2)
fraction_major_project_spending[is.na(fraction_major_project_spending)] = 0
rownames(fraction_major_project_spending) = CIP_remaining_schedule$Current.Funding.Source
write.table(fraction_major_project_spending, sep = ",", col.names = NA,
            'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/model_input_data/original_CIP_spending_major_projects_fraction.csv')


sum_repayment_per_year_schedule = CIPF_normalizedbyyear %>% 
  group_by(Current.Funding.Source, `Normalized Year Index`, `Total Capital Needed`) %>% 
  summarize(total = sum(Dollars))
all_project_schedule = sum_repayment_per_year_schedule %>% 
  group_by(`Normalized Year Index`, Current.Funding.Source) %>% summarize(Total = sum(total))
all_project_schedule = reshape2::dcast(all_project_schedule, 
                                      `Current.Funding.Source` ~ `Normalized Year Index`)
write.table(all_project_schedule, sep = ",", row.names = FALSE,
            'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/model_input_data/normalized_CIP_spending_all_projects.csv')

major_project_schedule = 
  sum_repayment_per_year_schedule[which(sum_repayment_per_year_schedule$`Total Capital Needed` == "Large Projects (>$75m)"),] %>%
  group_by(`Normalized Year Index`, Current.Funding.Source) %>% summarize(Total = sum(total)) 
major_project_schedule = reshape2::dcast(major_project_schedule, 
                                         `Current.Funding.Source` ~ `Normalized Year Index`)
major_project_fractional_splits_over_time = colSums(major_project_schedule[,2:ncol(major_project_schedule)]) / 
  sum(major_project_schedule[,2:ncol(major_project_schedule)])

major_project_fractional_splits_over_source = t(t(major_project_schedule[,2:ncol(major_project_schedule)]) / 
                                                  colSums(major_project_schedule[,2:ncol(major_project_schedule)]))
remaining_project_schedule = 
  sum_repayment_per_year_schedule[which(sum_repayment_per_year_schedule$`Total Capital Needed` != "Large Projects (>$75m)"),] %>%
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

remaining_project_schedule[is.na(remaining_project_schedule)] = 0
all_project_schedule[is.na(all_project_schedule)] = 0
fraction_cip_spending_for_other_projects_by_source = round(
  remaining_project_schedule[,2:ncol(remaining_project_schedule)] / 
  all_project_schedule[,2:ncol(all_project_schedule)], 2)

fraction_cip_spending_for_major_projects_by_source = 1 - fraction_cip_spending_for_other_projects_by_source
rownames(fraction_cip_spending_for_major_projects_by_source) = all_project_schedule$Current.Funding.Source

fraction_cip_spending_for_major_projects_by_source[is.na(fraction_cip_spending_for_major_projects_by_source)] = 0
write.table(fraction_cip_spending_for_major_projects_by_source, sep = ",", col.names = NA,
           'C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/model_input_data/normalized_CIP_spending_major_projects_fraction.csv')

# plot results
P = ggplot(data = CIPF_normalizedbyyear) + geom_bar(aes(x = `Normalized Year Index`, y = Dollars, fill = Current.Funding.Source), 
                                                    color = NA, stat = 'identity') +
  xlab("Years after First Year a Project is Funded") + scale_y_continuous(labels = comma)
ggsave('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/otherfigures/check_CIP_normalizedstartyear_all.png',
       dpi = 600, units = 'in', height = 5, width = 8)

P = ggplot(data = CIPF_normalizedbyyear) + geom_bar(aes(x = `Normalized Year Index`, y = Dollars, fill = Current.Funding.Source), 
                                            color = NA, stat = 'identity') +
  facet_wrap(`Total Capital Needed`~., scales = "free_y", ncol = 3) + 
  xlab("Years after First Year a Project is Funded") + scale_y_continuous(labels = comma)
ggsave('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/otherfigures/check_CIP_normalizedstartyear.png',
       dpi = 600, units = 'in', height = 6, width = 12)

P = ggplot(data = CIPF_normalizedbyyear) + geom_bar(aes(x = `Normalized Year Index`, fill = Current.Funding.Source, y = Dollars), 
                                                    color = NA, stat = 'identity', position = 'fill') +
  facet_wrap(`Total Capital Needed`~., ncol = 3) + 
  xlab("Years after First Year a Project is Funded")
ggsave('C:/Users/dgorelic/OneDrive - University of North Carolina at Chapel Hill/UNC/Research/TBW/Data/otherfigures/check_CIP_normalizedstartyear_relatives.png',
       dpi = 600, units = 'in', height = 6, width = 12)

