import pandas as pd
from glob import glob
import os

# READS AMPL OUTPUT .LOG FILES AS FIXED WIDTH FILES
# DOES NOT WORK FOR ALL FILES, SOME SHIFT IN WIDTH PARTWAY THROUGH...
# D Gorelick (Mar 2019)

# set parent directory
os.chdir('C:/Users/David/Desktop/TBWData/AMPL_output')

# create a list of all realization file names in this working directory
files = glob("ampl_*.log")

# read in ampl log files to get weekly objective metrics
for f in files:
    # read each realization, skip first 1,336 rows that hold information
    # about day 1 optimization variable values
    # in some .log files, these widths shift partway through the file when
    # one of the columns gets too wide. Dave Gold has a fix for this?
    ampl_out = pd.read_fwf(f, widths = list([6,13,10,8,10,10,6,8,8]),
                           skiprows = range(0,1336), skipfooter = 2, 
                           skip_blank_lines = True)

    # exclude rows where data file has copies of header
    bad_rows = ampl_out.index.isin(list(range(50,ampl_out.shape[0],52)) + list(range(51,ampl_out.shape[0],52)))
    ampl_out = ampl_out[~bad_rows]

    # write as wide csv files
    ampl_out.to_csv('wide_' + f[0:9] + '.csv')