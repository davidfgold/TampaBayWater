# PRE-PROCESS AMPL CSV OUTPUTS FOR FURTHER ANALYSIS
# D Gorelick (Oct 2020)

import os

# read in files from analysis_functions.py
os.chdir('f:\MonteCarlo_Project\Cornell_UNC\TampaBayWater\data_management')
from analysis_functions import read_AMPL_csv

# process AMPL files
for run in [125, 126, 128]:
    # first create folder for dumping output
    os.chdir('f:\MonteCarlo_Project\Cornell_UNC\cleaned_AMPL_files')
    os.mkdir('run0' + str(run))

    # run calculations
    for r in range(1,1001):
        data_csv = read_AMPL_csv('f:\SystemReliability_old\Output\\rrv_' + str(10000 + run)[1:] + '\\',
                                 'f:\MonteCarlo_Project\Cornell_UNC\cleaned_AMPL_files\\run' + str(10000 + run)[1:] + '\\',
                                 'ampl_' + str(10000 + r)[1:] + '.csv')

