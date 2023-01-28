#! /usr/bin/python3
# Last updated: 1-27-2023, by Guoquan (Bob) Wang.

# The is an example main Python routine for calling the Python module, TG_Rate_95CI.py
# https://pypi.org/project/TG_Rate_95%CI/
# https://github.com/bob-Github-2020/TG_Rate_95CI

# You may install the module on your computer by: pip install TG_Rate_95CI
# or download the source code (TG_Rate_95CI.py) to your working directory ()

## Test the module:
# Copy Main_cal_TG_Rate_95CI.py, TG_Rate_95CI.py,and the sample PSMSL data (e.g., 828.rlrdata) to your working directory.
# For running the program:
# type "./Main_cal_TG_Rate_95CI.py in a Linux terminal,
# or type "python Main_cal_TG_Rate_95CI.py" in a Windows CMD terminal. 

## Important notes
# The PSMSL dataset ('fin'): 828.rlrdata is organized as the following, the unit of MSL is mm
  # 1957.7083;  6990; 0;000
  # 1957.7917;  6975; 0;000
  # 1957.8750;  6926; 0;000
  # 1957.9583;  6713; 0;000
  # .......
# PSMSL fills the data gap as -99999
  #  1965.0417;  6670; 0;000
  #  1965.1250;-99999;00;000
  #  1965.2083;-99999;00;000
  #  1965.2917;-99999;00;000
  #  1965.3750;-99999;00;000
# These gap lines need to be removed before inputting the data to Main_cal_TG_Rate_95CI.py
# Please read the Bash script: "do_remove_PSMSL_gap_lines"

## You may need to install several Python modules on your computer of you have not installed before
  # do this by "pip install module-name"

## The detailed methodology for calculating the 95%CI is adressed in:
   # Wang, G. (2023). The 95% confidence interval for the rates of relative sea-level derived from tide gauge data, submitted xxx (02/03/2023)

import sys 
print (sys.executable)
import os
import pandas as pd
from TG_Rate_95CI import cal_95CI

directory = './'
# for reading PSMSL data. Slight adjustments are needed for reading NOAA data
for fin in os.listdir(directory):
    if fin.endswith("828.rlrdata"):
       print(fin)
       ns=len(fin)
       TG = fin[0:ns-8]    # station name, e.g., 468
       ts_psmsl = []

       ts_psmsl = pd.read_csv (fin, header=None, sep = ';')
       year = ts_psmsl.iloc[:,0]
       ts = ts_psmsl.iloc[:,1]
            
       result=cal_95CI(year, ts, TG, output='on', pltshow='on')
       b=round(result[0],2)           # rate b
       b_95CI=round(result[1],2)      # 95%CI of b
       
       #os.remove (fin)
    else:
       pass
       


