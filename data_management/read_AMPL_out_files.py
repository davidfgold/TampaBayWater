import pandas as pd
from glob import glob
import os
import re
import numpy as np

# READS AMPL .OUT FILES AND WRITES TO NEW CSV
# D Gorelick (Feb 2019)

# set parent directory
os.chdir('C:/Users/David/Desktop/TBWData/AMPL_output')

# create a list of all realization file names in this working directory
files = glob("ampl_*.OUT")

# read .out files and write new csv for each file with copy of information
for f in files:
    # read each realization, just columns I want
    # because of errors parsing into columns, I will read data in by row (single string)
    # and extract each column of interest that way
    ampl_out = pd.read_csv(f, sep = ',', skiprows = [0,1,2])
        
    # exclude rows where data file has copies of header
    bad_rows = ampl_out.index.isin(list(range(50,ampl_out.shape[0],51)))
    ampl_out = ampl_out[~bad_rows]
    
    # collect data after parsing each row (remove parentheses)
    ampl_data = np.zeros([len(ampl_out), 30])
    for r in range(0,len(ampl_out)):
        # elements of row, after delimiting for " " and parentheses
        # only keep non-empty list elements
        ampl_data[r,:]  = [elem for elem in re.split(' |\(|\)', [x for x in ampl_out.iloc[r,:]][0]) if elem != '']

    # attach column headers properly to the data, rewrite ampl_out correctly
    tempnames = [elem for elem in re.split(' |\(|\)', [x for x in ampl_out.columns][0]) if elem not in ['','No']]
    tempnames[6] = 'A1'; tempnames[8] = 'A2'; tempnames[10] = 'A3' # different headers for Avail columns
    ampl_out = pd.DataFrame(ampl_data); ampl_out.columns = tempnames
    
    # output this data for file
    ampl_out.to_csv(f[0:9] + '_outfile.csv')