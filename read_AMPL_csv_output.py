import numpy as np
import pandas as pd
from glob import glob
import os
import csv
import time

# READS AMPL .CSV OUTPUT AND WRITES TO WIDE CSV
# D Gorelick (Mar 2019)

# set parent directory
os.chdir('C:/Users/David/Desktop/TBWData/AMPL_output')

# create a list of all realization file names in this working directory
csvfiles = glob("ampl_*.csv")

# read and write each file
# timing is included as this process takes about 4 min per file
for cf in csvfiles:
    # read in ampl csv files, reshape data to get all necessary info
    # into timeseries format, some data not reported daily FYI
    # use unique combinations of VariableIndex and VariableName fields
    print('reading ' + cf); start = time.time()
    csv_out = pd.read_csv(cf, sep = ',') # about a year is 50,000 rows
    end = time.time(); print('reading file complete after ' + str(end-start) + ' seconds')
    
    # collect the file data and organize such that each column is a unique variable timeseries
    print('accumulating column values'); start = time.time()
    uniquevars = csv_out[['VariableName','VariableIndex']].drop_duplicates()
    numrows = len(np.unique(csv_out['DayNumber']))
    csvdata = np.empty((numrows,len(uniquevars))); csvdata[:] = np.nan
    for v,j in zip(uniquevars.values,range(0,len(uniquevars.values))):
        vday  = csv_out['DayNumber'][(csv_out['VariableIndex'] == v[1]) & (csv_out['VariableName'] == v[0])]
        vdata = csv_out['Value'][(csv_out['VariableIndex'] == v[1]) & (csv_out['VariableName'] == v[0])]
        csvdata[vday.values-1,j] = vdata.values
    end = time.time(); print('building wide data complete after ' + str(end-start) + ' seconds')
    
    # write as wide files
    # first two rows give the (1) column variable time and (2) variable name
    print('writing ' + cf); start = time.time()
    myFile = open('wide_' + cf, 'w')  
    with myFile:
        writer = csv.writer(myFile, lineterminator = '\n')
        writer.writerow(list(uniquevars.values[:,0]))
        writer.writerow(list(uniquevars.values[:,1]))
        writer.writerows(csvdata)
    end = time.time(); print('writing complete after ' + str(end-start) + ' seconds')