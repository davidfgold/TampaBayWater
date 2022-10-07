import numpy as np
import matplotlib
import matplotlib.cm as cm 
from matplotlib import pyplot as plt
import seaborn as sns
sns.set()

'''
Calculate the rate of change for failure and plot for 30 and 60 day failures
'''

# Load data on 30 day failure periods
failure_criteria_141 = np.loadtxt('Severity/failure_1mgd_duration_no_sch_141.csv',
 delimiter=',')
failure_criteria_143 = np.loadtxt('Severity/failure_1mgd_duration_no_sch_143.csv',
 delimiter=',')


years = np.arange(2021, 2041)

# Find what a year each percentile has more than 2 mos of failure
times_125_2mo = np.zeros([50])
times_128_2mo = np.zeros([50])
times_126_2mo = np.zeros([50])

for i, prob in enumerate(np.arange(50, 100)):
    try:
        times_125_2mo[i] = np.argwhere(failure_criteria_141[prob,:]>2)[0]
    except:
        times_125_2mo[i] = 30
    try:
        times_128_2mo[i] = np.argwhere(failure_criteria_143[prob,:]>2)[0]
    except:
        times_128_2mo[i] = 30

# Find what a year each percentile has more than 1 mo of failure
times_125_1mo = np.zeros([50])
times_128_1mo = np.zeros([50])

for i, prob in enumerate(np.arange(50, 100)):
    try:
        times_125_1mo[i] = np.argwhere(failure_criteria_141[prob,:]>1)[0]
    except:
        times_125_1mo[i] = 30
    try:
        times_128_1mo[i] = np.argwhere(failure_criteria_143[prob,:]>1)[0]
    except:
        times_128_1mo[i] = 30

# y-axis probabilities
failure_probability = 1-np.arange(50,100)/100

# make the figures
#fig, (ax1, ax2) = plt.subplots(1,2, figsize=(14,6))

fig = plt.figure(figsize=(8,6))
ax1 = fig.add_subplot(111)
plt.tick_params(axis='both', which='major', labelsize=14)

# plot one month failurse
ax1.step(2021+times_125_1mo, failure_probability*100, linestyle = '--',
            color = '#7570b3', linewidth=2)
ax1.step(2021+times_128_1mo, failure_probability*100, linestyle=':',
            color='#1b9e77', linewidth=2)

ax1.set_ylim([0, 50])
ax1.set_xticks(years)
ax1.set_xticklabels(years, rotation=90)
ax1.set_xlim([2021, 2040])
ax1.set_ylabel('Realizations with more \n than 1 month of supply failure (%)', fontsize=16)
ax1.legend(['SCH Pipeline',\
            'SCH Pipeline + SWTP Expansion'], fontsize=14)
'''
# plot 2 mo failures    
ax2.step(2021+times_125_2mo, failure_probability*100, linestyle = '--',
            color = '#7570b3', linewidth=2)
ax2.step(2021+times_128_2mo, failure_probability*100, linestyle=':',
            color='#1b9e77', linewidth=2)
ax2.set_xticks(years)
ax2.set_xticklabels(years, rotation=90)
ax2.set_ylim([0, 50])
#ax1.set_xticks(years, rotation='vertical', fontsize=14)
ax2.set_xlim([2021, 2040])

ax2.legend(['SCH Pipeline',\
            'SCH Pipeline + SWTP Expansion'], fontsize=14)

ax2.set_ylabel('Realizations with more \n than 2 months of supply failure (%)', fontsize=16)
'''
plt.tight_layout()    
plt.savefig('Figures/updated_cdf.png', bbox_inches='tight')
