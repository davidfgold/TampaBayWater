import numpy as np
import pandas as pd
import re

# FUNCTIONS TO DO BASIC DATA READING AND MANIPULATION OPERATIONS FOR TBW DATA
# D GORELICK (APR 2019)

def read_AMPL_csv(in_path, out_path, filename, export = True):
    # read in file
    csv_out = pd.read_csv(in_path + filename, sep = ',') # about a year is 50,000 rows
    
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
    
    if export:
        pd.DataFrame.to_csv(ampl_out, out_path + filename)
        
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
    # Aug 2019: changed to be conditional on last line
    #for _ in range(1336):
    #    next(f)
    
    # skip to first line of data
    first_data_line_catch = False
    for line in f:
        # skip lines that are empty
        linelen = len(line)
        if linelen == 1: 
            continue
        
        # catch when data starts
        if line.split()[0] == 'DateNo':
            first_data_line_catch = True
        
        # skip lines until data starts
        if first_data_line_catch == False: 
            continue

        if line[0] != 'D' and line[0] != 'T' and len(line) > 1:
            formatted_line = line.split()
            
            # catch when first two columns are connected via a dash
            if len(formatted_line[0]) > 4:
                date = formatted_line[0][0:4]
                obj = formatted_line[0][4:]
                formatted_line = [date, obj] + formatted_line[1:]
                
            # catch if negative sign was included in first column at end
            # when it should be on second
            if formatted_line[0][-1:] == '-':
                formatted_line[0] = formatted_line[0][:-1]
                formatted_line[1] = '-' + formatted_line[1]
              
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
    


def read_AMPL_log_variable_constraints(filename):
    # read input file
    f = open(filename, 'r')
    
    # collect column names and initialize matrix to hold data
#    header = ['Variable', 'Slack', 'Lower Bound', 'Value', 
#              'Upper Bound', 'Status']
    header = ['Variable', 'Lower Bound', 'Upper Bound']
    ampl_out = np.empty((0,len(header)))
    
    # read line by line (skip first 186 lines)
    for _ in range(186):
        next(f)
        
    for line in f:
        # discard blank lines
        if len(line) > 1:
            formatted_line = line.split()
            
            # stop when reached the bottom of the constraints list
            if formatted_line[0] == 'DateNo':
                print(formatted_line)
                break
            
            # catch any headers to skip
            # CATCHES HERE THAT SHOULD BE INCLUDED, EXCEPTIONS ADDED
            if len(formatted_line) != 6:
                # catch any issues?
                if len(formatted_line) == 5:
                    print(formatted_line)
                    
                if formatted_line[0][0:12] == "BIDIR_NEG_UB" or formatted_line[2][0:9] == '-Infinity':  
                    f_l_2 = formatted_line[2][0:9]
                    f_l_3 = formatted_line[2][9:]
                    formatted_line = [formatted_line[0], formatted_line[1], 
                                      f_l_2, f_l_3, 
                                      formatted_line[3], formatted_line[4]]
                    print(formatted_line)
                else:
                    print(formatted_line)
                    continue
            
            # ignore header label halfway through variables
            if formatted_line[0] == 'Constraint':
                print(formatted_line)
                continue
            
            # assign values to keep
            var_or_constr_name = formatted_line[0]
            first_case_slack_value = formatted_line[1]
            lower_bound = formatted_line[2]
            first_case_value = formatted_line[3]
            upper_bound = formatted_line[4]
            
            # write keeper values
            new_list = [var_or_constr_name, lower_bound, upper_bound]
            ampl_out = np.vstack((ampl_out, [x for x in new_list]))

    f.close()
    
    ampl_out = pd.DataFrame(ampl_out); ampl_out.columns = header
    return ampl_out
