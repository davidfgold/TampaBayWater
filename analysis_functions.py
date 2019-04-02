import numpy as np
import pandas as pd
import re

# FUNCTIONS TO DO BASIC DATA READING AND MANIPULATION OPERATIONS FOR TBW DATA
# D GORELICK (APR 2019)

def read_AMPL_csv(filename):
    # read in file
    csv_out = pd.read_csv(filename, sep = ',') # about a year is 50,000 rows
    
    # collect the file data and organize such that each column is a unique variable timeseries
    uniquevars = csv_out[['VariableName','VariableIndex']].drop_duplicates()
    numrows = len(np.unique(csv_out['DayNumber']))
    csvdata = np.empty((numrows,len(uniquevars))); csvdata[:] = np.nan
    for v,j in zip(uniquevars.values,range(0,len(uniquevars.values))):
        vday  = csv_out['DayNumber'][(csv_out['VariableIndex'] == v[1]) & (csv_out['VariableName'] == v[0])]
        vdata = csv_out['Value'][(csv_out['VariableIndex'] == v[1]) & (csv_out['VariableName'] == v[0])]
        csvdata[vday.values-1,j] = vdata.values
    
    # format data
    uniquecols = uniquevars.values[:,0] + '__' + uniquevars.values[:,1]
    ampl_out = pd.DataFrame(csvdata)
    ampl_out.columns = uniquecols
    
    return ampl_out



def read_AMPL_out(filename):
    ampl_out = pd.read_csv(filename, sep = ',', skiprows = [0,1,2])
        
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
    
    return ampl_out



def read_AMPL_log(filename):
    # read input file
    f = open(filename, 'r')
    
    # collect column names and initialize matrix to hold data
    header = ['DateNo', 'Obj-Function', 'sw_term', 'wf_term', 
              'orop_term', 'tg_offset', 'oprc', 'overage', 'penalty']
    ampl_out = np.empty((0,len(header)))
    
    # read line by line (skip first 1336 lines)
    for _ in range(1336):
        next(f)
        
    for line in f:
        if line[0] != 'D' and line[0] != 'T' and len(line) > 1:
            formatted_line = line.split()
            
            # catch when first two columns are connected via a dash
            if len(formatted_line[0]) > 4:
                date = formatted_line[0][0:4]
                obj = formatted_line[0][4:]
                formatted_line = [date, obj] + formatted_line[1:]
              
            # when second and third columns are combined
            # this checks if the number continues beyond the scientific format
            # ending (i.e. "e+00") further than it should
            if len(formatted_line[1]) > formatted_line[1].find('e')+4:
                obj = formatted_line[1][:(formatted_line[1].find('e')+4)]
                sw = formatted_line[1][(formatted_line[1].find('e')+4):]
                formatted_line = [formatted_line[0], obj, sw] + formatted_line[2:]
            
            if len(formatted_line[3]) > 4:
                if len(formatted_line[2])> 12:
                    obj = formatted_line[2][:12]
                    sw = formatted_line[2][12:]
                    wf_term = formatted_line[3][0:3]
                    orop_term = formatted_line[3][4:]
                    
                    new_list = [formatted_line[0], obj, sw, \
                                wf_term, orop_term, formatted_line[4], \
                                formatted_line[5], formatted_line[6]]
                    
                else:
                    wf_term = formatted_line[3][0:3]
                    orop_term = formatted_line[3][4:]
                    new_list = [formatted_line[0], formatted_line[1],\
        						           formatted_line[2], wf_term, orop_term, \
        						           formatted_line[4], formatted_line[5], \
        						           formatted_line[6], formatted_line[7]]
                    
            elif len(formatted_line[2])> 12:
                obj = formatted_line[2][:12]
                sw = formatted_line[2][12:]
                wf_term = formatted_line[3][0:3]
                orop_term = formatted_line[3][4:]
                new_list = [formatted_line[0], obj, sw, \
    					              formatted_line[3], formatted_line[4], \
    					              formatted_line[5], formatted_line[6], \
    					              formatted_line[7]]
                
            else:
                new_list = formatted_line
                        
            ampl_out = np.vstack((ampl_out, [float(x) for x in new_list]))

    f.close()
    
    ampl_out = pd.DataFrame(ampl_out); ampl_out.columns = header
    return ampl_out
    
