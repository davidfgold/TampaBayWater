import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import seaborn as sns
sns.set_theme(style="whitegrid")

# load data
obj_names = ['REL_W', 'RF_W', 'INF_NPC_W', 'PFC_W', 'WCC_W', \
        'REL_D', 'RF_D', 'INF_NPC_D', 'PFC_D', 'WCC_D', \
        'REL_F', 'RF_F', 'INF_NPC_F', 'PFC_F', 'WCC_F', \
        'REL_R', 'RF_R', 'INF_NPC_R', 'PFC_R', 'WCC_R']

dv_names = ['RT_W', 'RT_D', 'RT_F', 'TT_D', 'TT_F', 'LMA_W', 'LMA_D', 'LMA_F',\
            'RC_W', 'RC_D', 'RC_F', 'IT_W', 'IT_D', 'IT_F', 'IP_W', 'IP_D', \
            'IP_F', 'INF_W', 'INF_D', 'INF_F']

utilities = ['Watertown', 'Dryville', 'Fallsland', 'Regional']
utils_indv = ['Watertown', 'Dryville', 'Fallsland']
comp = ['Fallback\nbargaining', 'Least\nsquares', 'Power\nindex']

dir_robustness = '/home/fs02/pmr82_0001/lbl59/Implementation_Uncertainty/post_processing_du/DU_reeval_output_Apr2022/'
dir_dvs = '/home/fs02/pmr82_0001/lbl59/Implementation_Uncertainty/WaterPaths_duReeval/IU_Samples/'

filename_robustness_FB = 'FB171/robustness_perturbed_og_FB171.csv'
filename_robustness_PW = 'PW113/robustness_perturbed_og_PW113.csv'
filename_robustness_LS = 'LS98/robustness_perturbed_og_LS98.csv'

worst_robustness = [543, 433, 250]
best_robustness = [564, 589, 4]

# load robustness for all utilities across all RDMs for each of the 1000 perturbed instances
data_FB = pd.read_csv(dir_robustness + filename_robustness_FB, sep=',', names=utilities, index_col=False)
data_PW = pd.read_csv(dir_robustness + filename_robustness_PW, sep=',', names=utilities, index_col=False)
data_LS = pd.read_csv(dir_robustness + filename_robustness_LS, sep=',', names=utilities, index_col=False)

data_FB = pd.DataFrame(data_FB)
data_PW = pd.DataFrame(data_PW)
data_LS = pd.DataFrame(data_LS)

# Color will be minimum robustness across utilities
# scale by .7 to make colorbar readable
regional_FB = data_FB[utilities].min(axis=1)
regional_PW = data_PW[utilities].min(axis=1)
regional_LS = data_LS[utilities].min(axis=1)

data_FB['regional_scaled'] = regional_FB
data_PW['regional_scaled'] = regional_PW
data_LS['regional_scaled'] = regional_LS

data_FB = data_FB.sort_values('regional_scaled')
data_PW = data_PW.sort_values('regional_scaled')
data_LS = data_LS.sort_values('regional_scaled')

regional_plot_FB = data_FB['regional_scaled'].values
regional_plot_PW = data_PW['regional_scaled'].values
regional_plot_LS = data_LS['regional_scaled'].values

robustness_FB = data_FB[utils_indv].values
robustness_PW = data_PW[utils_indv].values
robustness_LS = data_LS[utils_indv].values

# collect robustnes by compromise solution for each utility
robustness_W = pd.DataFrame(data_FB['Watertown'])
robustness_W['Power\nindex'] = data_PW['Watertown']
robustness_W['Least\nsquares'] = data_LS['Watertown']

robustness_D = pd.DataFrame(data_FB['Dryville'])
robustness_D['Power\nindex'] = data_PW['Dryville']
robustness_D['Least\nsquares'] = data_LS['Dryville']

robustness_F = pd.DataFrame(data_FB['Fallsland'])
robustness_F['Power\nindex'] = data_PW['Fallsland']
robustness_F['Least\nsquares'] = data_LS['Fallsland']

robustness_R = pd.DataFrame(data_FB['Regional'])
robustness_R['Power\nindex'] = data_PW['Regional']
robustness_R['Least\nsquares'] = data_LS['Regional']

# set colormap
colormaps = ['YlOrBr', 'Greens', 'Purples']
cmap_LS = matplotlib.cm.get_cmap("Purples")
cmap_PW = matplotlib.cm.get_cmap("Greens")
cmap_FB = matplotlib.cm.get_cmap("YlOrBr")

'''
Plot all robustness across each compromise solution for all utilities
'''

'''
fig, axs = plt.subplots(4,1,figsize=(7,11), constrained_layout=True)
robustness_dict = {}
robustness_dict['W'] = robustness_W
robustness_dict['D'] = robustness_D
robustness_dict['F'] = robustness_F
robustness_dict['R'] = robustness_R
utils = ['W', 'D', 'F', 'R']
color = ['darkorange', 'darkgreen', 'purple']

for c in range(len(utils)):
    robustness_df = robustness_dict[utils[c]]
    robustness = robustness_df.to_numpy()
    #col = color[c]
    for i in range(len(robustness[:,0])):
        ys = (robustness[i,:])
        xs = range(len(ys))
        axs[c].plot(xs, ys, c='lightgrey', alpha=.6, linewidth=4)

    axs[c].plot(xs, robustness[1000,:], c='k', alpha=1.0, linewidth=2, label='Compromise\nsolution')
    axs[c].set_ylabel("% Robustness \n $\longrightarrow$", fontsize= 10)
    axs[c].set_ylim([0,1])
    axs[c].set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    axs[c].set_yticklabels(['0%', '25%', '50%', '75%', '100%'], fontsize= 8)
    axs[c].spines['top'].set_visible(False)
    axs[c].spines['bottom'].set_visible(False)
    if c == 3:
        axs[c].set_xticks([0,1,2])
        axs[c].set_xticklabels(comp, fontsize=10)
    else:
        axs[c].set_xticks([0,1,2])
        axs[c].set_xticklabels(['', '', ''])
    
    axs[c].set_xlim([0,2])

    axs[c].set_title(utilities[c], fontsize=10)
    axs[c].legend(loc='upper right', prop={'size': 8})    

plt.savefig('Figures/parallel_plots/robustness_allComp_compSol.pdf')
plt.show()
'''
'''
Plot all robustness across each utility for all compromise solutions
'''

fig, axs = plt.subplots(3,1,figsize=(7,11), constrained_layout=True)


# Plot all solutions
robustness_dict = {}
robustness_dict['FB'] = robustness_FB
robustness_dict['PW'] = robustness_PW
robustness_dict['LS'] = robustness_LS

regplots = {}
regplots['FB'] = regional_plot_FB
regplots['PW'] = regional_plot_PW
regplots['LS'] = regional_plot_LS

cmap_dict = {}
cmap_dict['FB'] = cmap_FB
cmap_dict['PW'] = cmap_PW
cmap_dict['LS'] = cmap_LS

compromise = ['FB', 'LS', 'PW']

for c in range(len(compromise)):
    reg_plot = regplots[compromise[c]]
    robustness = robustness_dict[compromise[c]]
    cmap = cmap_dict[compromise[c]]
    for i in range(len(robustness[:,0])):
        ys = (robustness[i,:])
        xs = range(len(ys))
        axs[c].plot(xs, ys, c=cmap(reg_plot[i]*0.9), alpha=.6, linewidth=4)

    axs[c].plot(xs, robustness[1000,:], c='k', alpha=1.0, linewidth=2, label=comp[c])
    axs[c].plot(xs, robustness[worst_robustness[c],:], c='k', alpha=1.0, linewidth=2,\
                label='Worst regional\nrobustness', linestyle=':')
    axs[c].plot(xs, robustness[best_robustness[c],:], c='k', alpha=1.0, linewidth=2,\
                label='Best regional\nrobustness', linestyle='--')
    axs[c].set_ylabel("% Robustness \n $\longrightarrow$", fontsize= 10)
    axs[c].set_ylim([0,1])
    axs[c].set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    axs[c].set_yticklabels(['0%', '25%', '50%', '75%', '100%'], fontsize= 8)
    if c == 2:
        axs[c].set_xticks([0,1,2])
        axs[c].set_xticklabels(utils_indv, fontsize=10)
    else:
        axs[c].set_xticks([0,1,2])
        axs[c].set_xticklabels(['', '', ''])
    
    axs[c].set_xlim([0,2])
    if c == 0:
        axs[c].set_title('Fallback bargaining', fontsize=12)
    if c == 1:
        axs[c].set_title('Least-squares', fontsize=12)
    if c == 2:
        axs[c].set_title('Power index', fontsize=12)
    axs[c].legend(loc='upper right', prop={'size': 8})
    

plt.savefig('Figures/parallel_plots/robustness_allComp_utils_gradient.pdf')
plt.show()



