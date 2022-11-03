# import all required libraries

from tkinter import *
import subprocess
import sys
import os
from tkinter import font
import pandas as pd
import numpy as np
from openpyxl import load_workbook
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import seaborn as sns
sns.set()


# create root widget 
root = Tk()
root.title("TBW Financial Model GUI")
root.iconbitmap('tbw_icon.ico')

root.geometry("1500x980")
root.resizable(False, False)

# data entry enabled here
#main_folder_location = Entry(root,text="Main Folder Location", width=10)

# Model setup frame
frame_setup_model = LabelFrame(root, text="1-Setup financial model", padx=8, pady=8, 
    bg='lightcyan', font=('HelvLight', 20), width=800, height=350)
frame_setup_model.grid(row=0,column=0,padx=10,pady=10, sticky="ew")
frame_setup_model.grid_propagate(False)

main_folder_loc = Label(frame_setup_model, text="Main folder location", justify=LEFT, bg='lightcyan').grid(sticky = W, row=1, column=0)
main_folder_loc_entry = Entry(frame_setup_model, width=50)
main_folder_loc_entry.grid(row=1, column=1, sticky=W)
main_folder_loc_entry.insert(0, "C:/Users/llau/Desktop/TampaBayWater-GUI/") 

run_num = Label(frame_setup_model, text="Run Number", anchor="w", justify=LEFT, bg='lightcyan').grid(sticky = W, row=2, column=0)
run_num_entry = Entry(frame_setup_model, width=10)
run_num_entry.grid(row=2, column=1, sticky = W)
run_num_entry.insert(0, "0") 

run_id = Label(frame_setup_model, text="Run ID", anchor="w", justify=LEFT, bg='lightcyan').grid(sticky = W, row=3, column=0)
run_id_entry = Entry(frame_setup_model, width=10)
run_id_entry.grid(row=3, column=1, sticky = W)
run_id_entry.insert(0, "125") 

start_fy = Label(frame_setup_model, text="Starting FY", anchor="w", justify=LEFT, bg='lightcyan').grid(sticky = W, row=4, column=0)
start_fy_entry = Entry(frame_setup_model, width=10)
start_fy_entry.grid(row=4, column=1, sticky = W)
start_fy_entry.insert(0, "2021")

end_fy = Label(frame_setup_model, text="Ending FY", anchor="w", justify=LEFT, bg='lightcyan').grid(sticky = W, row=5, column=0)
end_fy_entry = Entry(frame_setup_model, width=10)
end_fy_entry.grid(row=5, column=1, sticky = W)
end_fy_entry.insert(0, "2040")

num_reals = Label(frame_setup_model, text="Number of realizations", anchor="w", justify=LEFT, bg='lightcyan').grid(sticky = W, row=6, column=0)
num_reals_entry = Entry(frame_setup_model, width=10)
num_reals_entry.grid(row=6, column=1, sticky = W)
num_reals_entry.insert(0, "1")

num_sim = Label(frame_setup_model, text="Number of simulations", anchor="w", justify=LEFT, bg='lightcyan').grid(sticky = W, row=7, column=0)
num_sim_entry = Entry(frame_setup_model, width=10)
num_sim_entry.grid(row=7, column=1, sticky = W)
num_sim_entry.insert(0, "1")

empty = Label(frame_setup_model, text=" ", anchor="w", justify=LEFT, bg='lightcyan').grid(sticky = W, row=8, column=0)


# make csv file for entry into both model and plotting
def store_finmod_deets():
    df = pd.DataFrame([[main_folder_loc_entry.get(), int(run_num_entry.get()), int(run_id_entry.get()), int(start_fy_entry.get()), int(end_fy_entry.get()), 
                   int(num_reals_entry.get()), int(num_sim_entry.get())]], columns=['main_folder_loc', 'run_num', 'run_id', 'start_fy', 'end_fy', 'num_reals', 'num_sim'])
    df_filepath = main_folder_loc_entry.get() + 'Data/model_input_data/model_setup.xlsx'

    df.to_excel(df_filepath, index=False)
    myLabel = Label(frame_setup_model, 
                    text="Financial model initialized.\nDetails found in 'Data/model_input_data/model_setup.xlsx'", anchor='w', 
                    justify=LEFT, width=50, bg='lightcyan').grid(row=10, column=1, sticky=W)

init_button = Button(frame_setup_model, text="Initialize financial model", padx=10, pady=5, command=store_finmod_deets, 
                fg='darkslategrey', bg='lightblue', font=['HelvLight', 10, 'bold']).grid(row=10, column=0, sticky='we')

def install():    
    subprocess.check_call("pip install -r requirements.txt")
    myLabel = Label(frame_setup_model, text="Financial model software requirements installed.", anchor='w',
        justify=LEFT, width=50, bg='lightcyan').grid(row=13, column=1, sticky=W)

setup_button = Button(frame_setup_model, text="Setup Financial Model", padx=10, pady=5, command=install, 
                    fg='darkslategrey', bg='lightblue', font=['HelvLight', 10, 'bold']).grid(row=13, column=0, sticky='we')

# Generate scenarios frame
frame_gen_scenarios = LabelFrame(root, text="3-Generate scenarios", padx=8, pady=8,
    bg='moccasin', font=('HelvLight', 20), width=800, height=550)
frame_gen_scenarios.grid(row=1,column=0,padx=10,pady=10, sticky="ew")
frame_gen_scenarios.grid_propagate(False)

# file descriptions
yes_no_dropdown = ["Yes", "No"]
clicked_uniform_rate = StringVar()
clicked_uniform_rate.set( "Yes" )

clicked_cip_schedule = StringVar()
clicked_cip_schedule.set( "Yes" )

clicked_cip_spending = StringVar()
clicked_cip_spending.set( "No" )

param_bounds = Label(frame_gen_scenarios, text="Financial scenario parameter bounds", 
    bg='moccasin', font=['HelvLight', 10, 'bold'], justify=LEFT).grid(row=0, column=0, sticky=W)

param_bounds_low = Label(frame_gen_scenarios, text="Lower", 
    bg='moccasin', font=['HelvLight', 10, 'bold'], justify=LEFT).grid(row=0, column=1, sticky=W)

param_bounds_upper = Label(frame_gen_scenarios, text="Upper", 
    bg='moccasin', font=['HelvLight', 10, 'bold'], justify=LEFT).grid(row=0, column=2, sticky=W)

fin_bounds = Label(frame_gen_scenarios, text="Financial decision bounds", 
    bg='moccasin', font=['HelvLight', 10, 'bold'], justify=LEFT).grid(row=0, column=4, sticky=W)

fin_bounds_low = Label(frame_gen_scenarios, text="Lower", 
    bg='moccasin', font=['HelvLight', 10, 'bold'], justify=LEFT).grid(row=0, column=5, sticky=W)

fin_bounds_upper = Label(frame_gen_scenarios, text="Upper", 
    bg='moccasin', font=['HelvLight', 10, 'bold'], justify=LEFT).grid(row=0, column=6, sticky=W)

# DU Factors
rate_stable_min = Label(frame_gen_scenarios, text="Rate stabilization min ratio", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=1, column=0)
rate_stable_min_low = Entry(frame_gen_scenarios, width=10)
rate_stable_min_low.grid(row=1, column=1)
rate_stable_min_low.insert(0,0)
rate_stable_min_high = Entry(frame_gen_scenarios, width=10)
rate_stable_min_high.grid(row=1, column=2)
rate_stable_min_high.insert(0,0.085)

rate_stable_max = Label(frame_gen_scenarios, text="Rate stabilization mac ratio", anchor="w", justify=LEFT,
    bg='moccasin').grid(sticky = W, row=2, column=0)
rate_stable_max_low = Entry(frame_gen_scenarios, width=10)
rate_stable_max_low.grid(row=2, column=1)
rate_stable_max_low.insert(0,0)
rate_stable_max_high = Entry(frame_gen_scenarios, width=10)
rate_stable_max_high.grid(row=2, column=2)
rate_stable_max_high.insert(0,0.2)

var_cost = Label(frame_gen_scenarios, text="Variable cost operational fraction", anchor="w", justify=LEFT
    , bg='moccasin').grid(sticky = W, row=3, column=0)
var_cost_low = Entry(frame_gen_scenarios, width=10)
var_cost_low.grid(row=3, column=1)
var_cost_low.insert(0,0)
var_cost_high = Entry(frame_gen_scenarios, width=10)
var_cost_high.grid(row=3, column=2)
var_cost_high.insert(0,0.15)

opex_fixed = Label(frame_gen_scenarios, text="Annual budget fixed OPEX inflation rate", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=4, column=0)
opex_fixed_low = Entry(frame_gen_scenarios, width=10)
opex_fixed_low.grid(row=4, column=1)
opex_fixed_low.insert(0,0)
opex_fixed_high = Entry(frame_gen_scenarios, width=10)
opex_fixed_high.grid(row=4, column=2)
opex_fixed_high.insert(0,0.033)

demand_growth = Label(frame_gen_scenarios, text="Annual demand growth rate", anchor="w", justify=LEFT
    , bg='moccasin').grid(sticky = W, row=5, column=0)
demand_growth_low = Entry(frame_gen_scenarios, width=10)
demand_growth_low.grid(row=5, column=1)
demand_growth_low.insert(0,0)
demand_growth_high = Entry(frame_gen_scenarios, width=10)
demand_growth_high.grid(row=5, column=2)
demand_growth_high.insert(0,0.015)

next_fy = Label(frame_gen_scenarios, text="Next FY budgeted TBC delivery", anchor="w", justify=LEFT
    , bg='moccasin').grid(sticky = W, row=6, column=0)
next_fy_low = Entry(frame_gen_scenarios, width=10)
next_fy_low.grid(row=6, column=1)
next_fy_low.insert(0,0)
next_fy_high = Entry(frame_gen_scenarios, width=10)
next_fy_high.grid(row=6, column=2)
next_fy_high.insert(0,2000)

fixed_opex_factor = Label(frame_gen_scenarios, text="Fixed OPEX factor", anchor="w", justify=LEFT
    , bg='moccasin').grid(sticky = W, row=7, column=0)
fixed_opex_factor_low = Entry(frame_gen_scenarios, width=10)
fixed_opex_factor_low.grid(row=7, column=1)
fixed_opex_factor_low.insert(0,0)
fixed_opex_factor_high = Entry(frame_gen_scenarios, width=10)
fixed_opex_factor_high.grid(row=7, column=2)
fixed_opex_factor_high.insert(0,0.7)

var_opex_factor = Label(frame_gen_scenarios, text="Variable OPEX factor", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=8, column=0)
var_opex_factor_low = Entry(frame_gen_scenarios, width=10)
var_opex_factor_low.grid(row=8, column=1)
var_opex_factor_low.insert(0,0)
var_opex_factor_high = Entry(frame_gen_scenarios, width=10)
var_opex_factor_high.grid(row=8, column=2)
var_opex_factor_high.insert(0,0.9)

non_sale_rev = Label(frame_gen_scenarios, text="Non-sales revenue factor", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=9, column=0)
non_sale_rev_low = Entry(frame_gen_scenarios, width=10)
non_sale_rev_low.grid(row=9, column=1)
non_sale_rev_low.insert(0,0)
non_sale_rev_high = Entry(frame_gen_scenarios, width=10)
non_sale_rev_high.grid(row=9, column=2)
non_sale_rev_high.insert(0,1.5)

rate_stab_factor = Label(frame_gen_scenarios, text="Rate stabilization transfer factor", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=10, column=0)
rate_stab_factor_low = Entry(frame_gen_scenarios, width=10)
rate_stab_factor_low.grid(row=10, column=1)
rate_stab_factor_low.insert(0,0)
rate_stab_factor_high = Entry(frame_gen_scenarios, width=10)
rate_stab_factor_high.grid(row=10, column=2)
rate_stab_factor_high.insert(0,1.5)

r_transfer = Label(frame_gen_scenarios, text="R&R transfer factor", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=11, column=0)
rr_transfer_low = Entry(frame_gen_scenarios, width=10)
rr_transfer_low.grid(row=11, column=1)
rr_transfer_low.insert(0,0)
rr_transfer_high = Entry(frame_gen_scenarios, width=10)
rr_transfer_high.grid(row=11, column=2)
rr_transfer_high.insert(0,0.3)

other_transfer = Label(frame_gen_scenarios, text="Other transfer factors", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=12, column=0)
other_transfer_low = Entry(frame_gen_scenarios, width=10)
other_transfer_low.grid(row=12, column=1)
other_transfer_low.insert(0,0)
other_transfer_high = Entry(frame_gen_scenarios, width=10)
other_transfer_high.grid(row=12, column=2)
other_transfer_high.insert(0,1)

cip_factor = Label(frame_gen_scenarios, text="Required CIP factor", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=13, column=0)
cip_factor_low = Entry(frame_gen_scenarios, width=10)
cip_factor_low.grid(row=13, column=1)
cip_factor_low.insert(0,0)
cip_factor_high = Entry(frame_gen_scenarios, width=10)
cip_factor_high.grid(row=13, column=2)
cip_factor_high.insert(0,1.0)

opex_var = Label(frame_gen_scenarios, text="Annual budget variable OPEX inflation rate", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=14, column=0)
opex_var_low = Entry(frame_gen_scenarios, width=10)
opex_var_low.grid(row=14, column=1)
opex_var_low.insert(0,0)
opex_var_high = Entry(frame_gen_scenarios, width=10)
opex_var_high.grid(row=14, column=2)
opex_var_high.insert(0,0.033)

sales_threshold = Label(frame_gen_scenarios, text="TBW sales threshold fraction", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=15, column=0)
sales_threshold_low = Entry(frame_gen_scenarios, width=10)
sales_threshold_low.grid(row=15, column=1)
sales_threshold_low.insert(0,0)
sales_threshold_high = Entry(frame_gen_scenarios, width=10)
sales_threshold_high.grid(row=15, column=2)
sales_threshold_high.insert(0, 0.2)

energy_transfer = Label(frame_gen_scenarios, text="Energy transfer factor", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=16, column=0)
energy_transfer_low = Entry(frame_gen_scenarios, width=10)
energy_transfer_low.grid(row=16, column=1)
energy_transfer_low.insert(0,0)
energy_transfer_high = Entry(frame_gen_scenarios, width=10)
energy_transfer_high.grid(row=16, column=2)
energy_transfer_high.insert(0,1)

urf_deficit = Label(frame_gen_scenarios, text="URF deficit reduction fraction", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=17, column=0)
urf_deficit_low = Entry(frame_gen_scenarios, width=10)
urf_deficit_low.grid(row=17, column=1)
urf_deficit_low.insert(0,0)
urf_deficit_high = Entry(frame_gen_scenarios, width=10)
urf_deficit_high.grid(row=17, column=2)
urf_deficit_high.insert(0,0.75)

follow_schedule_label = Label(frame_gen_scenarios, text="Follow CIP schedule?", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=18, column=0)
follow_schedule = OptionMenu(frame_gen_scenarios, clicked_cip_schedule , *yes_no_dropdown )
follow_schedule.grid(row=18, column=1)
follow_schedule.config(bg='moccasin')

flex_spending_label = Label(frame_gen_scenarios, text="Enable flexible CIP spending?", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=19, column=0)
flex_spending = OptionMenu(frame_gen_scenarios, clicked_cip_spending , *yes_no_dropdown )
flex_spending.grid(row=19, column=1)
flex_spending.config(bg='moccasin')

keep_stable_label = Label(frame_gen_scenarios, text="Keep uniform rate stable?", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=20, column=0)
keep_stable = OptionMenu(frame_gen_scenarios, clicked_uniform_rate , *yes_no_dropdown )
keep_stable.grid(row=20, column=1)
keep_stable.config(bg='moccasin')

emptycol = Label(frame_gen_scenarios, text="", anchor="w", justify=LEFT, bg='moccasin').grid(sticky = W, row=19, column=3)

# Decision variables
covenant_threshold = Label(frame_gen_scenarios, text="Covenant threshold, net revenue, fund balance", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=1, column=4)
covenant_threshold_low = Entry(frame_gen_scenarios, width=10)
covenant_threshold_low.grid(row=1, column=5)
covenant_threshold_low.insert(0,0)
covenant_threshold_high = Entry(frame_gen_scenarios, width=10)
covenant_threshold_high.grid(row=1, column=6)
covenant_threshold_high.insert(0,1.25)

debt_covenant_threshold = Label(frame_gen_scenarios, text="Debt covenant required ratio", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=2, column=4)
debt_covenant_threshold_low = Entry(frame_gen_scenarios, width=10)
debt_covenant_threshold_low.insert(0,0)
debt_covenant_threshold_low.grid(row=2, column=5)
debt_covenant_threshold_high = Entry(frame_gen_scenarios, width=10)
debt_covenant_threshold_high.grid(row=2, column=6)
debt_covenant_threshold_high.insert(0,1.0)

unencum_budget = Label(frame_gen_scenarios, text="Unencumbered budget fraction", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=3, column=4)
unencum_budget_low = Entry(frame_gen_scenarios, width=10)
unencum_budget_low.grid(row=3, column=5)
unencum_budget_low.insert(0,0)
unencum_budget_high = Entry(frame_gen_scenarios, width=10)
unencum_budget_high.grid(row=3, column=6)
unencum_budget_high.insert(0,0.5)

managed_uniform_incr = Label(frame_gen_scenarios, text="Managed uniform rate increase rate", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=4, column=4)
managed_uniform_incr_low = Entry(frame_gen_scenarios, width=10)
managed_uniform_incr_low.grid(row=4, column=5)
managed_uniform_incr_low.insert(0,0)
managed_uniform_incr_high = Entry(frame_gen_scenarios, width=10)
managed_uniform_incr_high.grid(row=4, column=6)
managed_uniform_incr_high.insert(0, 0.01)

managed_uniform_decr = Label(frame_gen_scenarios, text="Managed uniform rate decrease rate", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=5, column=4)
managed_uniform_decr_low = Entry(frame_gen_scenarios, width=10)
managed_uniform_decr_low.grid(row=5, column=5)
managed_uniform_decr_low.insert(0,0)
managed_uniform_decr_high = Entry(frame_gen_scenarios, width=10)
managed_uniform_decr_high.grid(row=5, column=6)
managed_uniform_decr_high.insert(0,0.005)

prev_unacc = Label(frame_gen_scenarios, text="Previous unaccounted FY enterprise fund fraction", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=6, column=4)
prev_unacc_low = Entry(frame_gen_scenarios, width=10)
prev_unacc_low.grid(row=6, column=5)
prev_unacc_low.insert(0,0)
prev_unacc_high = Entry(frame_gen_scenarios, width=10)
prev_unacc_high.grid(row=6, column=6)
prev_unacc_high.insert(0,0.27)

debt_service_cap = Label(frame_gen_scenarios, text="Debt service cap fraction of GR", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=7, column=4)
debt_service_cap_low = Entry(frame_gen_scenarios, width=10)
debt_service_cap_low.grid(row=7, column=5)
debt_service_cap_low.insert(0,0)
debt_service_cap_high = Entry(frame_gen_scenarios, width=10)
debt_service_cap_high.grid(row=7, column=6)
debt_service_cap_high.insert(0,0.4)

rr_fraction = Label(frame_gen_scenarios, text="R&R fund fraction of GR", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=8, column=4)
rr_fraction_low = Entry(frame_gen_scenarios, width=10)
rr_fraction_low.grid(row=8, column=5)
rr_fraction_low.insert(0,0)
rr_fraction_high = Entry(frame_gen_scenarios, width=10)
rr_fraction_high.grid(row=8, column=6)
rr_fraction_high.insert(0,0.05)

cip_fund_fraction = Label(frame_gen_scenarios, text="FIP fund fraction of GR", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=9, column=4)
cip_fund_fraction_low = Entry(frame_gen_scenarios, width=10)
cip_fund_fraction_low.grid(row=9, column=5)
cip_fund_fraction_low.insert(0,0)
cip_fund_fraction_high = Entry(frame_gen_scenarios, width=10)
cip_fund_fraction_high.grid(row=9, column=6)
cip_fund_fraction_high.insert(0,0.05)

energy_fund_fraction = Label(frame_gen_scenarios, text="Energy fund fraction of GR", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=10, column=4)
energy_fund_fraction_low = Entry(frame_gen_scenarios, width=10)
energy_fund_fraction_low.grid(row=10, column=5)
energy_fund_fraction_low.insert(0,0)
energy_fund_fraction_high = Entry(frame_gen_scenarios, width=10)
energy_fund_fraction_high.grid(row=10, column=6)
energy_fund_fraction_high.insert(0,0.01)

rf_fund_fraction = Label(frame_gen_scenarios, text="Energy fund fraction of GR", anchor="w", justify=LEFT, 
    bg='moccasin').grid(sticky = W, row=11, column=4)
rf_fund_fraction_low = Entry(frame_gen_scenarios, width=10)
rf_fund_fraction_low.grid(row=11, column=5)
rf_fund_fraction_low.insert(0,0)
rf_fund_fraction_high = Entry(frame_gen_scenarios, width=10)
rf_fund_fraction_high.grid(row=11, column=6)
rf_fund_fraction_high.insert(0,0.1)

def scenarios_done():
    myLabel = Label(root, text="Scenarios generated. Proceed with 'Run Model'.").grid(row=6, column=0)

def gen_default_scenario():
    err_file = main_folder_loc_entry.get() + 'Output/error_files/err_generate_scenarios.txt'
    err = open(err_file, 'w')
    num_simulations = int(num_sim_entry.get())
    dvs = np.zeros((num_simulations,11), dtype=float)

    # if chose to use default, fill decision variable matrix with default values
    # reference: original DV variable file (now "financial_model_DVs.csv")
    dvs[:,0].fill(1.25)
    dvs[:,1].fill(1)
    dvs[:,2].fill(np.random.choice([0,1]))
    dvs[:,3].fill(0.01)
    dvs[:,4].fill(0.005)
    dvs[:,5].fill(0.27)
    dvs[:,6].fill(np.random.choice([0.4,9999]))
    dvs[:,7].fill(0.05)
    dvs[:,8].fill(0.05)
    dvs[:,9].fill(0.01)
    dvs[:,10].fill(0.1)

    dvs_filepath = main_folder_loc_entry.get() + "Data/parameters/financial_model_DVs.csv"
    np.savetxt(dvs_filepath, dvs, delimiter=",")

    #%%
    # DU factors
    dufs  = np.zeros((num_simulations,20), dtype=float)

    dufs[:,0].fill(0.085)
    dufs[:,1].fill(0.3)
    dufs[:,2].fill(0.15)
    dufs[:,3].fill(0.025)
    dufs[:,4].fill(0.033)
    dufs[:,5].fill(0.015)
    dufs[:,6].fill(2000)
    dufs[:,7].fill(0.7)
    dufs[:,8].fill(0.9)
    dufs[:,9].fill(1.5)
    dufs[:,10].fill(1.5)
    dufs[:,11].fill(0.3)
    dufs[:,12].fill(1)
    dufs[:,13].fill(1)
    dufs[:,14].fill(0.033)
    dufs[:,15].fill(0.02)
    dufs[:,16].fill(1)
    dufs[:,17].fill(0.75)
    dufs[:,18].fill(np.random.choice([0,1]))
    dufs[:,19].fill(np.random.choice([0,1]))

    dufs_filepath = main_folder_loc_entry.get() + "Data/parameters/financial_model_DUfactors.csv"
    np.savetxt(dufs_filepath, dufs, delimiter=",")
    
    myLabel = Label(frame_gen_scenarios, text="Done!", justify=LEFT, bg='moccasin').grid(row=18, column=5, sticky="we")

def gen_one_new_scenario():
    err_file_path = main_folder_loc_entry.get() + 'Output/error_files/err_generate_scenarios.txt'

    err = open(err_file_path, 'w')

    num_simulations = int(num_sim_entry.get())
    if num_simulations <= 1:
        err.write("ERROR: Too few simulations. \nPlease use two or more simulations if generating more than one alternative scenario.")

    # decision variables
    dvs = np.zeros((num_simulations,11), dtype=float)

    KEEP_UNIFORM_RATE_STABLE = 0

    if clicked_cip_schedule.get() == "Yes":
        KEEP_UNIFORM_RATE_STABLE = 1

    #%%
    # if user does not want to use default decision variable values
    # set decision variables
    covenant_threshold_net_revenue_plus_fund_balance = np.full((num_simulations,), float(covenant_threshold_high.get()))

    debt_covenant_required_ratio = np.full((num_simulations,), float(debt_covenant_threshold_high.get()))

    managed_uniform_rate_increase_rate = np.full((num_simulations,), float(managed_uniform_incr_high.get()))

    managed_uniform_rate_decrease_rate = np.full((num_simulations,), float(managed_uniform_decr_high.get()))

    previous_FY_unaccounted_fraction_of_total_enterprise_fund = np.full((num_simulations,), float(prev_unacc_high.get()))

    debt_service_cap_fraction_of_gross_revenues =  np.full((num_simulations,), float(debt_service_cap_high.get()))


    rr_fund_floor_fraction_of_gross_revenues = np.full((num_simulations,), float(rr_fraction_high.get()))

    cip_fund_floor_fraction_of_gross_revenues = np.full((num_simulations,), float(cip_fund_fraction_high.get()))

    energy_fund_floor_fraction_of_gross_revenues = np.full((num_simulations,), float(energy_fund_fraction_high.get()))

    reserve_fund_floor_fraction_of_gross_revenues = np.full((num_simulations,), float(rf_fund_fraction_high.get()))

    # fill decision variable matrix
    dvs[:,0] = covenant_threshold_net_revenue_plus_fund_balance
    dvs[:,1] = debt_covenant_required_ratio
    dvs[:,2].fill(KEEP_UNIFORM_RATE_STABLE)
    dvs[:,3] = managed_uniform_rate_increase_rate
    dvs[:,4] = managed_uniform_rate_decrease_rate
    dvs[:,5] = previous_FY_unaccounted_fraction_of_total_enterprise_fund
    dvs[:,6] = debt_service_cap_fraction_of_gross_revenues
    dvs[:,7] = rr_fund_floor_fraction_of_gross_revenues
    dvs[:,8] = cip_fund_floor_fraction_of_gross_revenues
    dvs[:,9] = energy_fund_floor_fraction_of_gross_revenues
    dvs[:,10] = reserve_fund_floor_fraction_of_gross_revenues

    dvs_filepath = main_folder_loc_entry.get()  + "Data/parameters/financial_model_DVs.csv"
    np.savetxt(dvs_filepath, dvs, delimiter=",")

    #%%
    # DU factors
    dufs  = np.zeros((num_simulations,20), dtype=float)

    FLEXIBLE_CIP_SCHEDULE_TOGGLE = 0
    FOLLOW_CIP_SCHEDULE_TOGGLE = 0

    # if user does not want to use default DU factor values
    # set decision variables
    rate_stabilization_minimum_ratio = np.full((num_simulations,), float(rate_stable_min_high.get()))

    rate_stabilization_maximum_ratio = np.full((num_simulations,), float(rate_stable_max_high.get()))

    fraction_variable_operational_cost = np.full((num_simulations,), float(var_cost_high.get()))

    budgeted_unencumbered_fraction = np.full((num_simulations,), float(unencum_budget_high.get()))

    annual_budget_fixed_operating_cost_inflation_rate = np.full((num_simulations,), float(opex_fixed_high.get()))

    annual_demand_growth_rate = np.full((num_simulations,), float(demand_growth_high.get()))

    next_FY_budgeted_tampa_tbc_delivery = np.full((num_simulations,), float(next_fy_high.get()))

    fixed_op_ex_factor = np.full((num_simulations,), float(fixed_opex_factor_high.get()))

    variable_op_ex_factor = np.full((num_simulations,), float(var_opex_factor_high.get()))

    non_sales_rev_factor = np.full((num_simulations,), float(non_sale_rev_high.get()))


    rate_stab_transfer_factor = np.full((num_simulations,), float(rate_stab_factor_high.get()))

    rr_transfer_factor = np.full((num_simulations,), float(rr_transfer_high.get()))

    other_transfer_factor = np.full((num_simulations,), float(other_transfer_high.get())) 

    required_cip_factor = np.full((num_simulations,), float(cip_factor_high.get()))

    annual_budget_variable_operating_cost_inflation_rate = np.full((num_simulations,), float(opex_var_high.get()))

    TAMPA_SALES_THRESHOLD_FRACTION = np.full((num_simulations,), float(sales_threshold_high.get()))

    energy_transfer_factor = np.full((num_simulations,), float(energy_transfer_high.get()))

    utility_reserve_fund_deficit_reduction_fraction = np.full((num_simulations,), float(urf_deficit_high.get()))

    dufs[:,0] = rate_stabilization_minimum_ratio
    dufs[:,1] = rate_stabilization_maximum_ratio
    dufs[:,2] = fraction_variable_operational_cost
    dufs[:,3] = budgeted_unencumbered_fraction
    dufs[:,4] = annual_budget_fixed_operating_cost_inflation_rate
    dufs[:,5] = annual_demand_growth_rate
    dufs[:,6] = next_FY_budgeted_tampa_tbc_delivery
    dufs[:,7] = fixed_op_ex_factor
    dufs[:,8] = variable_op_ex_factor
    dufs[:,9] = non_sales_rev_factor
    dufs[:,10] = rate_stab_transfer_factor
    dufs[:,11] = rr_transfer_factor
    dufs[:,12] = other_transfer_factor
    dufs[:,13] = required_cip_factor
    dufs[:,14] = annual_budget_variable_operating_cost_inflation_rate
    dufs[:,15] = TAMPA_SALES_THRESHOLD_FRACTION
    dufs[:,16] = energy_transfer_factor
    dufs[:,17] = utility_reserve_fund_deficit_reduction_fraction
    dufs[:,18].fill(FLEXIBLE_CIP_SCHEDULE_TOGGLE)
    dufs[:,19].fill(FOLLOW_CIP_SCHEDULE_TOGGLE)

    dufs_filepath = main_folder_loc_entry.get() + "Data/parameters/financial_model_DUfactors.csv"
    np.savetxt(dufs_filepath, dufs, delimiter=",")

    err.write('End error file.')
    err.close()

    myLabel =Label(frame_gen_scenarios, text="Done!", justify=LEFT, bg='moccasin').grid(row=19, column=5, sticky="we")

def gen_alt_scenarios():
    err_file_path = main_folder_loc_entry.get() + 'Output/error_files/err_generate_scenarios.txt'

    err = open(err_file_path, 'w')

    num_simulations = int(num_sim_entry.get())
    if num_simulations <= 1:
        err.write("ERROR: Too few simulations. \nPlease use two or more simulations if generating more than one alternative scenario.")

    # decision variables
    dvs = np.zeros((num_simulations,11), dtype=float)

    KEEP_UNIFORM_RATE_STABLE = 0

    if clicked_cip_schedule.get() == "Yes":
        KEEP_UNIFORM_RATE_STABLE = 1

    #%%
    # if user does not want to use default decision variable values
    # set decision variables
    covenant_threshold_net_revenue_plus_fund_balance = np.random.uniform(low=float(covenant_threshold_low.get()),
                                                         high=float(covenant_threshold_high.get()),
                                                         size=(num_simulations,))

    debt_covenant_required_ratio = np.random.uniform(low=float(debt_covenant_threshold_low.get()),
                                                         high=float(debt_covenant_threshold_high.get()),
                                                         size=(num_simulations,))

    managed_uniform_rate_increase_rate = np.random.uniform(low=float(managed_uniform_incr_low.get()),
                                                         high=float(managed_uniform_incr_high.get()),
                                                         size=(num_simulations,))

    managed_uniform_rate_decrease_rate = np.random.uniform(low=float(managed_uniform_decr_low.get()),
                                                         high=float(managed_uniform_decr_high.get()),
                                                         size=(num_simulations,))

    previous_FY_unaccounted_fraction_of_total_enterprise_fund = np.random.uniform(low=float(prev_unacc_low.get()),
                                                         high=float(prev_unacc_high.get()),
                                                         size=(num_simulations,))

    debt_service_cap_fraction_of_gross_revenues = np.random.uniform(low=float(debt_service_cap_low.get()),
                                                         high=float(debt_service_cap_high.get()),
                                                         size=(num_simulations,))

    rr_fund_floor_fraction_of_gross_revenues = np.random.uniform(low=float(rr_fraction_low.get()),
                                                         high=float(rr_fraction_high.get()),
                                                         size=(num_simulations,))

    cip_fund_floor_fraction_of_gross_revenues = np.random.uniform(low=float(cip_fund_fraction_low.get()),
                                                         high=float(cip_fund_fraction_high.get()),
                                                         size=(num_simulations,))

    energy_fund_floor_fraction_of_gross_revenues = np.random.uniform(low=float(energy_fund_fraction_low.get()),
                                                         high=float(energy_fund_fraction_high.get()),
                                                         size=(num_simulations,))

    reserve_fund_floor_fraction_of_gross_revenues = np.random.uniform(low=float(rf_fund_fraction_low.get()),
                                                         high=float(rf_fund_fraction_high.get()),
                                                         size=(num_simulations,))

    # fill decision variable matrix
    dvs[:,0] = covenant_threshold_net_revenue_plus_fund_balance
    dvs[:,1] = debt_covenant_required_ratio
    dvs[:,2].fill(KEEP_UNIFORM_RATE_STABLE)
    dvs[:,3] = managed_uniform_rate_increase_rate
    dvs[:,4] = managed_uniform_rate_decrease_rate
    dvs[:,5] = previous_FY_unaccounted_fraction_of_total_enterprise_fund
    dvs[:,6] = debt_service_cap_fraction_of_gross_revenues
    dvs[:,7] = rr_fund_floor_fraction_of_gross_revenues
    dvs[:,8] = cip_fund_floor_fraction_of_gross_revenues
    dvs[:,9] = energy_fund_floor_fraction_of_gross_revenues
    dvs[:,10] = reserve_fund_floor_fraction_of_gross_revenues

    dvs_filepath = main_folder_loc_entry.get()  + "Data/parameters/financial_model_DVs.csv"
    np.savetxt(dvs_filepath, dvs, delimiter=",")

    #%%
    # DU factors
    dufs  = np.zeros((num_simulations,20), dtype=float)

    FLEXIBLE_CIP_SCHEDULE_TOGGLE = 0
    FOLLOW_CIP_SCHEDULE_TOGGLE = 0

    # if user does not want to use default DU factor values
    # set decision variables
    rate_stabilization_minimum_ratio = np.random.uniform(low=float(rate_stable_min_low.get()),
                                                         high=float(rate_stable_min_high.get()),
                                                         size=(num_simulations,))

    rate_stabilization_maximum_ratio = np.random.uniform(low=float(rate_stable_max_low.get()),
                                                         high=float(rate_stable_max_high.get()),
                                                         size=(num_simulations,))

    fraction_variable_operational_cost = np.random.uniform(low=float(var_cost_low.get()),
                                                         high=float(var_cost_high.get()),
                                                         size=(num_simulations,))

    budgeted_unencumbered_fraction = np.random.uniform(low=float(unencum_budget_low.get()),
                                                         high=float(unencum_budget_high.get()),
                                                         size=(num_simulations,))

    annual_budget_fixed_operating_cost_inflation_rate = np.random.uniform(low=float(opex_fixed_low.get()),
                                                         high=float(opex_fixed_high.get()),
                                                         size=(num_simulations,))

    annual_demand_growth_rate = np.random.uniform(low=float(demand_growth_low.get()),
                                                         high=float(demand_growth_high.get()),
                                                         size=(num_simulations,))

    next_FY_budgeted_tampa_tbc_delivery = np.random.uniform(low=float(next_fy_low.get()),
                                                         high=float(next_fy_high.get()),
                                                         size=(num_simulations,))

    fixed_op_ex_factor = np.random.uniform(low=float(fixed_opex_factor_low.get()),
                                                         high=float(fixed_opex_factor_high.get()),
                                                         size=(num_simulations,))

    variable_op_ex_factor = np.random.uniform(low = float(var_opex_factor_low.get()),
                                                         high=float(var_opex_factor_high.get()),
                                                         size=(num_simulations,))

    non_sales_rev_factor = np.random.uniform(low = float(non_sale_rev_low.get()),
                                                         high=float(non_sale_rev_high.get()),
                                                         size=(num_simulations,))

    rate_stab_transfer_factor = np.random.uniform(low = float(rate_stab_factor_low.get()),
                                                         high=float(rate_stab_factor_high.get()),
                                                         size=(num_simulations,))

    rr_transfer_factor = np.random.uniform(low = float(rr_transfer_low.get()),
                                                         high=float(rr_transfer_high.get()),
                                                         size=(num_simulations,))

    other_transfer_factor = np.random.uniform(low = float(other_transfer_low.get()),
                                                         high=float(other_transfer_high.get()),
                                                         size=(num_simulations,))

    required_cip_factor = np.random.uniform(low = float(cip_factor_low.get()),
                                                         high=float(cip_factor_high.get()),
                                                         size=(num_simulations,))

    annual_budget_variable_operating_cost_inflation_rate = np.random.uniform(low=float(opex_var_low.get()),
                                                         high=float(opex_var_high.get()),
                                                         size=(num_simulations,))

    TAMPA_SALES_THRESHOLD_FRACTION = np.random.uniform(low=float(sales_threshold_low.get()),
                                                         high=float(sales_threshold_high.get()),
                                                         size=(num_simulations,))

    energy_transfer_factor = np.random.uniform(low=float(energy_transfer_low.get()),
                                                         high=float(energy_transfer_high.get()),
                                                         size=(num_simulations,))

    utility_reserve_fund_deficit_reduction_fraction = np.random.uniform(low=float(urf_deficit_low.get()),
                                                         high=float(urf_deficit_high.get()),
                                                         size=(num_simulations,))

    dufs[:,0] = rate_stabilization_minimum_ratio
    dufs[:,1] = rate_stabilization_maximum_ratio
    dufs[:,2] = fraction_variable_operational_cost
    dufs[:,3] = budgeted_unencumbered_fraction
    dufs[:,4] = annual_budget_fixed_operating_cost_inflation_rate
    dufs[:,5] = annual_demand_growth_rate
    dufs[:,6] = next_FY_budgeted_tampa_tbc_delivery
    dufs[:,7] = fixed_op_ex_factor
    dufs[:,8] = variable_op_ex_factor
    dufs[:,9] = non_sales_rev_factor
    dufs[:,10] = rate_stab_transfer_factor
    dufs[:,11] = rr_transfer_factor
    dufs[:,12] = other_transfer_factor
    dufs[:,13] = required_cip_factor
    dufs[:,14] = annual_budget_variable_operating_cost_inflation_rate
    dufs[:,15] = TAMPA_SALES_THRESHOLD_FRACTION
    dufs[:,16] = energy_transfer_factor
    dufs[:,17] = utility_reserve_fund_deficit_reduction_fraction
    dufs[:,18].fill(FLEXIBLE_CIP_SCHEDULE_TOGGLE)
    dufs[:,19].fill(FOLLOW_CIP_SCHEDULE_TOGGLE)

    dufs_filepath = main_folder_loc_entry.get() + "Data/parameters/financial_model_DUfactors.csv"
    np.savetxt(dufs_filepath, dufs, delimiter=",")

    err.write('End error file.')
    err.close()

    myLabel = Label(frame_gen_scenarios, text='Done!', 
        justify=LEFT, bg='moccasin').grid(row=20, column=5, sticky="we")

frame_run_model = LabelFrame(root, text="Setup financial model", padx=8, pady=8, 
    bg='palegreen', font=('HelvLight', 20))
frame_run_model.grid(row=0,column=0,padx=10,pady=10, sticky="ew")

gen_default_scenarios = Button(frame_gen_scenarios, text="Generate default scenarios", padx=10, pady=5, command=gen_default_scenario,
                               fg='antiquewhite', bg='burlywood', 
                               font=['HelvLight',10, 'bold']).grid(row=18, column=4, sticky='we')

gen_one_scenario = Button(frame_gen_scenarios, text="Explore one new scenario", padx=10, pady=5, command=gen_one_new_scenario,
                          fg='antiquewhite', bg='burlywood',
                          font=['HelvLight',10, 'bold']).grid(row=19, column=4, sticky='we')

gen_many_scenario = Button(frame_gen_scenarios, text="Explore many new scenarios", padx=10, pady=5, command=gen_alt_scenarios,
                           fg='antiquewhite', bg='burlywood',
                           font=['HelvLight',10, 'bold']).grid(row=20, column=4, sticky='we')

# Enter filenames
frame_set_filenames = LabelFrame(root, text="2-Enter data filenames", padx=8, pady=8, bg='thistle', 
    font=['HelvLight', 20,'normal'], width=650, height=350)
frame_set_filenames.grid(row=0,column=1,padx=10,pady=10, sticky="ew")
frame_set_filenames.grid_propagate(False)

file_description = Label(frame_set_filenames, text="File description", anchor="w", justify=LEFT, 
    bg='thistle', font=['HelvLight', '10', 'bold']).grid(sticky = W, row=0, column=0)

filename = Label(frame_set_filenames, text="Filename", anchor="w", justify=LEFT, 
    bg='thistle', font=['HelvLight', '10', 'bold']).grid(sticky = W, row=0, column=1)

prev_water = Label(frame_set_filenames, text="Previous year water sales and deliveries", anchor="w", justify=LEFT, 
    bg='thistle').grid(sticky = W, row=1, column=0)
prev_water_entry = Entry(frame_set_filenames, width=50)
prev_water_entry.insert(0,'water_sales_and_deliveries_all_2020.csv')
prev_water_entry.grid(row=1, column=1)

hist_est_budget = Label(frame_set_filenames, text="Historical estimated budgets", anchor="w", justify=LEFT, 
    bg='thistle').grid(sticky = W, row=2, column=0)
hist_est_budget_entry = Entry(frame_set_filenames, width=50)
hist_est_budget_entry.insert(0,'historical_budgets.csv')
hist_est_budget_entry.grid(row=2, column=1)

hist_act_budget = Label(frame_set_filenames, text="Historical actual budgets", anchor="w", justify=LEFT, 
    bg='thistle').grid(sticky = W, row=3, column=0)
hist_act_budget_entry = Entry(frame_set_filenames, width=50)
hist_act_budget_entry.insert(0,'historical_actuals.csv')
hist_act_budget_entry.grid(row=3, column=1)

ext_debt = Label(frame_set_filenames, text="Existing debt", anchor="w", justify=LEFT, 
    bg='thistle').grid(sticky = W, row=4, column=0)
ext_debt_entry = Entry(frame_set_filenames, width=50)
ext_debt_entry.insert(0,'existing_debt.csv')
ext_debt_entry.grid(row=4, column=1)

potential_projs = Label(frame_set_filenames, text="Potential projects", anchor="w", justify=LEFT, 
    bg='thistle').grid(sticky = W, row=5, column=0)
potential_projs_entry = Entry(frame_set_filenames, width=50)
potential_projs_entry.insert(0,'potential_projects.csv')
potential_projs_entry.grid(row=5, column=1)

curr_future_bonds = Label(frame_set_filenames, text="Current and future bond issues", anchor="w", justify=LEFT, 
    bg='thistle').grid(sticky = W, row=6, column=0)
curr_future_bonds_entry = Entry(frame_set_filenames, width=50)
curr_future_bonds_entry.insert(0,'Current_Future_BondIssues.xlsx')
curr_future_bonds_entry.grid(row=6, column=1)

og_cip_spending = Label(frame_set_filenames, text="Original CIP spending (all projects)", anchor="w", justify=LEFT, 
    bg='thistle').grid(sticky = W, row=7, column=0)
og_cip_spending_entry = Entry(frame_set_filenames, width=50)
og_cip_spending_entry.insert(0,'original_CIP_spending_all_projects.csv')
og_cip_spending_entry.grid(row=7, column=1)

og_cip_spending_major = Label(frame_set_filenames, text="Original CIP spending (major projects)", anchor="w", justify=LEFT, 
bg='thistle').grid(sticky = W, row=8, column=0)
og_cip_spending_major_entry = Entry(frame_set_filenames, width=50)
og_cip_spending_major_entry.insert(0,'original_CIP_spending_major_projects_fraction.csv')
og_cip_spending_major_entry.grid(row=8, column=1)

norm_cip_spending = Label(frame_set_filenames, text="Normalized CIP spending (all projects)", anchor="w", justify=LEFT, 
    bg='thistle').grid(sticky = W, row=9, column=0)
norm_cip_spending_entry = Entry(frame_set_filenames, width=50)
norm_cip_spending_entry.insert(0,'normalized_CIP_spending_all_projects.csv')
norm_cip_spending_entry.grid(row=9, column=1)

norm_cip_spending_major = Label(frame_set_filenames, text="Normalized CIP spending (major projects)", anchor="w", justify=LEFT, 
    bg='thistle').grid(sticky = W, row=10, column=0)
norm_cip_spending_major_entry = Entry(frame_set_filenames, width=50)
norm_cip_spending_major_entry.insert(0,'normalized_CIP_spending_major_projects_fraction.csv')
norm_cip_spending_major_entry.grid(row=10, column=1)

proj_rf_start_bal = Label(frame_set_filenames, text="Projected reserve fund starting balance", anchor="w", justify=LEFT, 
    bg='thistle').grid(sticky = W, row=11, column=0)
proj_rf_start_bal_entry = Entry(frame_set_filenames, width=50)
proj_rf_start_bal_entry.insert(0,'projected_FY21_reserve_fund_starting_balances.csv')
proj_rf_start_bal_entry.grid(row=11, column=1)

proj_rf_deposit = Label(frame_set_filenames, text="Projected reserve fund deposits", anchor="w", justify=LEFT, 
    bg='thistle').grid(sticky = W, row=12, column=0)
proj_rf_deposit_entry = Entry(frame_set_filenames, width=50)
proj_rf_deposit_entry.insert(0,'projected_reserve_fund_deposits.csv')
proj_rf_deposit_entry.grid(row=12, column=1)


df_filenames = pd.DataFrame([[prev_water_entry.get(), hist_est_budget_entry.get(), hist_act_budget_entry.get(), ext_debt_entry.get(),
                              potential_projs_entry.get(), curr_future_bonds_entry.get(), og_cip_spending_entry.get(), 
                              og_cip_spending_major_entry.get(), norm_cip_spending_entry.get(), norm_cip_spending_major_entry.get(),
                              proj_rf_start_bal_entry.get(), proj_rf_deposit_entry.get()]], 

                            columns = ['prev_water', 'hist_est_budget', 'hist_act_budget', 'ext_debt', 'potential_projs', 'curr_future_bonds',
                                       'og_cip_spending', 'og_cip_spending_major', 'norm_cip_spending', 'norm_cip_spending_major', 
                                       'proj_rf_bal', 'proj_rf_deposit'])

df_filenames_filepath = main_folder_loc_entry.get() + 'Data/model_input_data/input_filenames.xlsx'

df_filenames.to_excel(df_filenames_filepath, index=False)

# Run model frame
# Run the model
frame_run_model = LabelFrame(root, text="4-Run Model", padx=8, pady=8, 
    bg='honeydew', font=('HelvLight', 20), width=650, height=350)
frame_run_model.grid(row=1,column=1, padx=10, pady=10, sticky="ew")
frame_run_model.grid_propagate(False)

def running_model():
    model_file = main_folder_loc_entry.get() + 'Code/FinancialModeling/TBW_financial_model_vGUI.py'
    command = 'python ' + model_file
    os.system(command)
    
    myLabel = Label(frame_run_model, 
                    text="Model run complete.\nFind results in the 'Output/financial_model_results' folder.", 
                    justify=LEFT, bg='honeydew').grid(row=2, column=1, sticky = W)

run_model = Button(frame_run_model, text="Run Model", padx=10, pady=5, command=running_model,
                           fg='darkgreen', bg='palegreen', font=('HelvLight', 12, 'bold'), width=20).grid(row=2, column=0, sticky='W')

emptyLab_runmodel = Label(frame_run_model, text="", justify=LEFT, bg='honeydew').grid(row=3, column=0, sticky = 'we')
# Plot the figures

def plot_data():
    ACTUAL_VARIABLES = ['Fiscal Year', 'Uniform Rate (Full)', 'Uniform Rate (Variable Portion)',
                       'TBC Sales Rate', 'Interest Income', 'Gross Revenues', 'Debt Service',
                       'Acquisition Credits', 'Fixed Operational Expenses',
                       'Variable Operational Expenses', 'Utility Reserve Fund Balance (Total)',
                       'R&R Fund (Total)', 'R&R Fund (Deposit)', 'R&R Fund (Transfer In)',
                       'Rate Stabilization Fund (Deposit)', 'Rate Stabilization Fund (Total)',
                       'Rate Stabilization Fund (Transfer In)', 'Unencumbered Funds',
                       'CIP Fund (Total)', 'CIP Fund (Deposit)', 'CIP Fund (Transfer In)',
                       'Misc. Income', 'Insurance-Litigation-Arbitrage Income',
                       'Uniform Sales Revenues', 'Energy Savings Fund (Total)',
                       'Energy Savings Fund (Deposit)', 'Energy Savings Fund (Transfer In)']
    BUDGET_VARIABLES = ['Fiscal Year', 'Annual Estimate', 'Gross Revenues',
                           'Water Sales Revenue', 'Fixed Operating Expenses',
                           'Variable Operating Expenses', 'Net Revenues', 'Debt Service',
                           'Acquisition Credits', 'Unencumbered Carryover Funds',
                           'R&R Fund Deposit', 'Rate Stabilization Fund Deposit',
                           'Other Funds Deposit', 'Uniform Rate', 'Variable Uniform Rate',
                           'TBC Rate', 'Rate Stabilization Fund Transfers In',
                           'R&R Fund Transfers In', 'Other Funds Transfers In', 'Interest Income',
                           'CIP Fund Transfer In', 'CIP Fund Deposit',
                           'Energy Savings Fund Transfer In', 'Energy Savings Fund Deposit',
                           'Debt Service Deferred']
    METRICS_VARIABLES = ['Fiscal Year', 'Debt Covenant Ratio', 'Rate Covenant Ratio',
                           'Partial Debt Covenant Failure', 'Partial Rate Covenant Failure',
                           'Reserve Fund Balance Initial Failure',
                           'R&R Fund Balance Initial Failure',
                           'Cap on Rate Stabilization Fund Transfers In',
                           'Rate Stabilization Funds Transferred In', 'Required R&R Fund Deposit',
                           'Required Reserve Fund Deposit',
                           'Necessary Use of Other Funds (Rate Stabilization Supplement)',
                           'Final Net Revenues', 'Fixed Sales Revenue', 'Variable Sales Revenue',
                           'Reserve Fund Balancing Failure', 'Remaining Unallocated Deficit']

    data_names_to_plot = ['Rate Covenant Ratio', 'Debt Covenant Ratio', 'Uniform Rate',
                      'Debt Service', 'Debt Service Deferred', 'Remaining Unallocated Deficit',
                      'Utility Reserve Fund Balance (Total)', 'Rate Stabilization Fund (Total)',
                      'CIP Fund (Total)', 'R&R Fund (Total)', 'Energy Savings Fund (Total)']

    figures_out_path = main_folder_loc_entry.get() + 'Output/output_figures/'
    formulation_to_plot = [int(run_id_entry.get())]
    realization_to_plot = [x for x in range(1,int(num_reals_entry.get())+1)] # list which we want, IDs start at 1 not zero
    simulation_to_plot = [x for x in range(0,int(num_sim_entry.get()))]
    results_path = main_folder_loc_entry.get() + 'Output/financial_model_results/'

    metrics_test_read = pd.read_csv(results_path + 'financial_metrics_f' + str(formulation_to_plot[0]) +
                                '_s' + str(simulation_to_plot[0]) + '_r' + str(realization_to_plot[0]) + '.csv',
                                index_col = 0)

    dv_path = main_folder_loc_entry.get() + 'Data/parameters/'
    DVs = pd.read_csv(dv_path + 'financial_model_DVs.csv', header = None)
    DUFs = pd.read_csv(dv_path + 'financial_model_DUfactors.csv', header = None)
    err_filepath = main_folder_loc_entry.get() + 'Output/error_files/err_figures_gen.txt'
    err = open(err_filepath, 'w')

    figure_to_plot = clicked_figures.get()
    data_name_to_plot = ""

    if figure_to_plot == "Rate Covenant Ratio":
        data_name_to_plot = data_names_to_plot[0]
    elif figure_to_plot == "Debt Covenant Ratio":
        data_name_to_plot = data_names_to_plot[1]
    elif figure_to_plot == "Debt Service":
        data_name_to_plot = data_names_to_plot[3]
    elif figure_to_plot == "Debt Service Deferred":
        data_name_to_plot = data_names_to_plot[4]
    elif figure_to_plot == "Uniform Rate":
        data_name_to_plot = data_names_to_plot[2]
    elif figure_to_plot == "Remaining Unallocated Deficit":
        data_name_to_plot = data_names_to_plot[5]
    elif figure_to_plot == "Utility Reserve Fund Balance (Total)":
        data_name_to_plot = data_names_to_plot[6]
    elif figure_to_plot == "Rate Stabilization Fund (Total)":
        data_name_to_plot = data_names_to_plot[7]
    elif figure_to_plot == "CIP Fund (Total)":
        data_name_to_plot = data_names_to_plot[8]
    elif figure_to_plot == "R&R Fund (Total)":
        data_name_to_plot = data_names_to_plot[9]
    elif figure_to_plot == "Energy Savings Fund (Total)":
        data_name_to_plot = data_names_to_plot[10]

    # loop through all results to report data
    for f in range(0,len(formulation_to_plot)):
        print('Plotting output for Formulation ' + str(formulation_to_plot[f]))

        for r in range(0,len(realization_to_plot)):
            print('\t\tCollecting output for Realization ' + str(realization_to_plot[r]))

            if realization_to_plot[r] == 95:
                continue
            fig, axs = plt.subplots(1, 1, sharey = False, figsize = (7,7))
            # prepare data structure to hold collected data to plot
            hold_all_data_to_plot = np.zeros((int(num_sim_entry.get()), len(metrics_test_read['Fiscal Year'])))

            for s in range(0,len(simulation_to_plot)):
                print('\tPlotting output for Simulation ' + str(simulation_to_plot[s]))

                # identify simulation conditions
                #dvs = [x for x in DVs.iloc[simulation_to_plot[s],:]]
                #dufs = [x for x in DUFs.iloc[simulation_to_plot[s],:]]
                # read data input files
                actuals = pd.read_csv(results_path + 'budget_actuals_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '_r' + str(realization_to_plot[r]) + '.csv', index_col = 0)
                budgets = pd.read_csv(results_path + 'budget_projections_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '_r' + str(realization_to_plot[r]) + '.csv', index_col = 0)
                metrics = pd.read_csv(results_path + 'financial_metrics_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + '_r' + str(realization_to_plot[r]) + '.csv', index_col = 0)

                # collect data we want - reminder that actuals goes from
                # 2 years before first modeled year (so 2019, if starting 2021)
                # and ends at the final year (2039), budgets cover +1 year on
                # both sides (ex: 2020 to 2040), metrics are exact range (2021-2039)
                # so they need to be trimmed to match up in time with just the
                # modeled period...
                item = data_name_to_plot
                if item in actuals.columns:
                    print('\t\t\tCollecting ' + item + ' from actuals...') if r == 0 else None
                    hold_all_data_to_plot[s,:] = actuals[item].values[2:]

                elif item in budgets.columns:
                    print('\t\t\tCollecting ' + item + ' from budget...') if r == 0 else None
                    hold_all_data_to_plot[s,:] = budgets[item].values[1:-1]

                elif item in metrics.columns:
                    print('\t\t\tCollecting ' + item + ' from metrics...') if r == 0 else None
                    hold_all_data_to_plot[s,:] = metrics[item].values[:]

                else:
                    print('ERROR: CANNOT LOCATE ITEM: ' + item)
                    err.write('ERROR: CANNOT LOCATE ITEM: ' + item)
                    err.write("\n")

            #print(hold_all_data_to_plot)
            # plot a long row of subplots together for as many
            # variables as have been chosen to visualize
            #fig, axs = plt.subplots(1, 1, sharey = False, figsize = (5,5))

            # if plotting a single realization, make a special case
            if len(simulation_to_plot) == 1:
                #for ax, y_data, series_name in zip(axs, hold_all_data_to_plot, data_name_to_plot):
                axs.plot(metrics['Fiscal Year'].values, hold_all_data_to_plot[0])
                axs.set_title(data_name_to_plot)
                axs.set_xticklabels(metrics['Fiscal Year'].values.astype(int), rotation = 90)
            else:
                #for ax, y_data, series_name in zip(axs, hold_all_data_to_plot, data_name_to_plot):
                axs.boxplot(hold_all_data_to_plot[:][:])
                axs.set_title(data_name_to_plot)
                axs.set_xticklabels(metrics['Fiscal Year'].values.astype(int), rotation = 90)

            axs.set_xlabel('Fiscal Year')
            axs.set_ylabel("USD$")
        # output and close figure to avoid overloading memory
        plt.savefig(figures_out_path + data_name_to_plot + '_f' + str(formulation_to_plot[f]) + '_s' + str(simulation_to_plot[s]) + 
                    (('_SINGLE_REALIZATION_r' + str(realization_to_plot[r])) if len(realization_to_plot) == 1 else '') + '.png', bbox_inches= 'tight', dpi = 400)
        plt.show()
        '''
        canvas = FigureCanvasTkAgg(fig, master = frame_run_model)  
        canvas.draw()
  
        # placing the canvas on the Tkinter window
        canvas.get_tk_widget().grid(row=7, column=0)
        
        # creating the Matplotlib toolbar
        toolbar = NavigationToolbar2Tk(canvas,  frame_run_model)
        toolbar.update()
  
        # placing the toolbar on the Tkinter window
        canvas.get_tk_widget().grid(row=9, column=0)
        '''
        myLabel = Label(frame_run_model, text="Figure generated and\nstored in 'Output/output_figures/'",
            bg='honeydew', justify=LEFT).grid(row=6, column=1, sticky=W)


    err.write("End error file.")
    err.close()


# file descriptions
figures_dropdown = ['Rate Covenant Ratio', 'Debt Covenant Ratio', 'Uniform Rate',
                      'Debt Service', 'Debt Service Deferred', 'Remaining Unallocated Deficit',
                      'Utility Reserve Fund Balance (Total)', 'Rate Stabilization Fund (Total)',
                      'CIP Fund (Total)', 'R&R Fund (Total)', 'Energy Savings Fund (Total)']
clicked_figures = StringVar()
clicked_figures.set( 'Rate Covenant Ratio' )

figure_select = Label(frame_run_model, text="Select figure to plot from list ", anchor="w", justify=LEFT, bg='honeydew',
    font=('HelvLight',12)).grid(sticky = W, row=4, column=0)

figure_select = OptionMenu(frame_run_model, clicked_figures , *figures_dropdown )
figure_select.grid(row=4, column=1, columnspan=2, sticky='we')
figure_select.config(width = 30, font=['HelvLight','12', 'normal'], bg='honeydew')
emptyLab_figselect = Label(frame_run_model, text="", justify=LEFT, bg='honeydew').grid(row=5, column=0, sticky = 'W')
#simulation_to_plot = np.arange(0, num_sim, dtype=int)

plot_figures = Button(frame_run_model, text="Plot figure", padx=10, pady=5, command=plot_data,
                           fg='darkgreen', bg='palegreen', font=('HelvLight',12, 'bold'), width=20).grid(row=6, column=0, sticky='we')

emptyLab_plot = Label(frame_run_model, text="", justify=LEFT, bg='honeydew').grid(row=7, column=0, sticky = 'we')

root.mainloop()