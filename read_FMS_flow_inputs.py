import os
import csv
import scipy.io as sio
import numpy as np

# SCRIPT TO READ TBW FMS2 INPUT FLOW FILES TO OMS1
# AND WRITE MONTHLY AND DAILY DATA TO CSV
# D GORELICK AND D GOLD (Mar 2019)
# -----------------------------------------------------------------------------

# Each python script in this repository for reading and writing TBW model
# output data follows the same general format and utilizes the same reading
# and writing code for consistency

# this file loops across all inflow realization files (1,000) files
# and writes the accumulated data to separate csv files
# each row of the resultant files is a single realization
# realizations can be of monthly or daily data
# monthly data is for 300 years (total realization length) per realization
# daily data is for 40 years (limited by computation time)
# -----------------------------------------------------------------------------

# Step 0: Set working directory 
os.chdir('C:/Users/David/Desktop/TBWData/1000_flow_realization') # DG1b personal cp

# Step 1: Loop through inflow files
sims = list(range(1,1001)) # 1,000 realizations to be read 
dailyrecordlength = 15000 # limit on number of days
monthlyrecordlength = 3600 # full 300-year record of monthly data

# names of sites to be read in - not all sites have both monthly and daily records
monthlysites = ['CYC', 'STL', 'PC', 'MB', 'TBC', 'ALA', 'Cyp', 'Trt', 'ZH', 'HRUnmeas']
dailysites = ['LPUnmeas', 'MPUnmeas', 'MB', 'TBC', 'ALA', 'Cyp', 'Trt', 'ZH', 'HRUnmeas']

# Step 2: Read in each site and collect flow values
for site in np.unique(monthlysites + dailysites):
    
    # initialize collectors to hold data
    dailycollector = np.array([])
    monthlycollector = np.array([])
    
    # monthly data is easily aggregated to yearly levels, but daily data
    # requires an index of month and year to make manipulation better later
    # get initial year and month values for daily data
    if site in dailysites:
        RawData = sio.loadmat('000' + str(1) + '_SimRain_NPMonthlyNoise_NPDailyNoise_Nov2011.mat')
        InflowData = RawData[list(RawData)[3]] # gets ndarray of actual data
        DailyInflowRecords = InflowData['daily'] # gets daily records of flow for all inflow sites
        
        # ONLY KEEP 15000 DAILY RECORDS, about 40 years
        # first two rows of collected data is the year and month of simulation
        dailycollector = np.concatenate((dailycollector, DailyInflowRecords.item(0)['dv'][0,0][0:dailyrecordlength,0]), axis=0)
        dailycollector = np.concatenate((dailycollector, DailyInflowRecords.item(0)['dv'][0,0][0:dailyrecordlength,1]), axis=0)
    
    # loop through all sites for actual flow data
    for sim in sims:
        
        # this is an ugly statement but captures the correct file
        # read the data
        if sim < 10:
            RawData = sio.loadmat('1000_flow_realization/sim_' + '000' + str(sim) + '_SimRain_NPMonthlyNoise_NPDailyNoise_Nov2011.mat')
        elif sim < 100:
            RawData = sio.loadmat('1000_flow_realization/sim_' + '00' + str(sim) + '_SimRain_NPMonthlyNoise_NPDailyNoise_Nov2011.mat')
        elif sim < 1000:
            RawData = sio.loadmat('1000_flow_realization/sim_' + '0' + str(sim) + '_SimRain_NPMonthlyNoise_NPDailyNoise_Nov2011.mat')
        else:
            RawData = sio.loadmat('1000_flow_realization/sim_' + str(sim) + '_SimRain_NPMonthlyNoise_NPDailyNoise_Nov2011.mat')
        
        # get in necessary form
        InflowData = RawData[list(RawData)[3]] # gets ndarray of actual data
        MonthlyInflowRecords = InflowData['mandy'] # gets monthly records of flow for all inflow sites
        DailyInflowRecords = InflowData['daily'] # gets daily records of flow for all inflow sites
        
        # collect in one row
        if site in monthlysites:
            monthlycollector = np.concatenate((monthlycollector, MonthlyInflowRecords.item(0)[site][0,0][:,0]), axis=0)
        if site in dailysites:
            dailycollector = np.concatenate((dailycollector, DailyInflowRecords.item(0)[site][0,0][0:dailyrecordlength,0]), axis=0)

    # Step 3: Write data for each site to csv
    # as this code is set up, it is saved to a file within a subfolder
    # named with the site name - this may require another line of code 
    # to create the folder. there may also be errors if the file already exists
    # when you try to write a new one. just delete the old copy
    if site in dailysites:
        collector_aranged = np.reshape(dailycollector,[int(dailycollector.size/dailyrecordlength),dailyrecordlength], order = 'C')     
        myFile = open(site + '/dailyflowrealizations.csv', 'w')  
        with myFile:
            writer = csv.writer(myFile, lineterminator = '\n')
            writer.writerows(collector_aranged)

    if site in monthlysites:
        collector_aranged = np.reshape(monthlycollector,[int(monthlycollector.size/monthlyrecordlength),monthlyrecordlength], order = 'C')     
        myFile = open(site + '/monthlyflowrealizations.csv', 'w')  
        with myFile:
            writer = csv.writer(myFile, lineterminator = '\n')
            writer.writerows(collector_aranged)