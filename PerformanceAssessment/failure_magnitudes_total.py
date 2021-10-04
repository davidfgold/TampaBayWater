import numpy as np
import matplotlib
import matplotlib.cm as cm 
from matplotlib import pyplot as plt
import seaborn as sns
sns.set()

non_sch_sources = ['Alafia', 'TBC',  'CWUP', 'BUD',]
sch_sources = ['SCH', 'SCH3']
non_sch_source_names = ['Alafia \nRiver',  
           'Tampa Bypass Canal',  'Consolidated Well Use', 'BUD',]

sch_source_names = ['SCH wells', 'SCH demand']

scenario = 142
years = np.arange(2021, 2041)

non_sch_mo_ave = np.zeros([len(years), 100])

# Sum non-sch
for i in range(0, 3):
    source = non_sch_sources[i]
    current_ave = np.loadtxt('Magnitude/' + source + '_mov30_' + str(scenario) +'.csv', delimiter=',')
    non_sch_mo_ave =+ current_ave

fig = plt.figure(figsize=(10,4))
ax1 = fig.add_subplot(121)
ax1.plot(years, non_sch_mo_ave[:,85], color='darkred')


# Sum sch
sch_wells = np.loadtxt('Magnitude/' + sch_sources[0] + '_mov30_' + str(scenario) +'.csv', delimiter=',')
sch_demand = np.loadtxt('Magnitude/' + sch_sources[1] + '_mov30_' + str(scenario) +'.csv', delimiter=',')
sch_mov_ave = sch_wells+sch_demand


ax2 = fig.add_subplot(122)
ax2.plot(years, sch_mov_ave[:,85], color='darkred')


'''
scenario = 143
years = np.arange(2021, 2041)

non_sch_mo_ave = np.zeros([len(years), 100])

# Sum non-sch
for i in range(0, 3):
    source = non_sch_sources[i]
    current_ave = np.loadtxt('Magnitude/' + source + '_mov30_' + str(scenario) +'.csv', delimiter=',')
    non_sch_mo_ave =+ current_ave

ax1.plot(years, non_sch_mo_ave[:,85], color='royalblue', linestyle='--')

'''
ax1.set_xlim([2020,2040])
ax1.set_xticks([2020, 2025, 2030,2035, 2040])
ax1.set_xticklabels(range(2020,2045, 5), fontsize=12)
ax1.set_ylim([0,12])


'''
# Sum sch
sch_wells = np.loadtxt('Magnitude/' + sch_sources[0] + '_mov30_' + str(scenario) +'.csv', delimiter=',')
sch_demand = np.loadtxt('Magnitude/' + sch_sources[1] + '_mov30_' + str(scenario) +'.csv', delimiter=',')
sch_mov_ave = sch_wells+sch_demand

ax2.plot(years, sch_mov_ave[:,85], color='royalblue', linestyle='--')
'''
ax2.set_xlim([2020,2040])
ax2.set_xticks([2020, 2025, 2030,2035, 2040])
ax2.set_ylim([0,12])
ax2.set_yticklabels([])


plt.savefig('Figures/mags_142.png')


