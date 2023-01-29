#! /usr/bin/python3

# Last updated: 1-27-2023, by Guoquan (Bob) Wang, bob.g.wang@gmail.com

# The is an example Python routine for calling the Python module, TG_Rate_95CI.py.
# The main routine is designed for reading PSMSL data. For reading NOAA data, please read the "README.md" file. 

## The detailed methodology for calculating the 95%CI is adressed in:
   # Wang, G. (2023). A methodoly for calculating the 95% confidence interval of the mean sea-level rate derived from tide gauge data, submitted xxx (02/03/2023)

# You may install the module on your computer by: pip install TG_Rate_95CI
  # https://pypi.org/project/TG_Rate_95%CI/ 
# or download the source code (TG_Rate_95CI.py) to your working directory
  # https://github.com/bob-Github-2020/TG_Rate_95CI

## Test the module:
# Copy Main_cal_TG_Rate_95CI.py, TG_Rate_95CI.py,and the sample PSMSL data (e.g., 828.rlrdata) to your working directory.
# For running the program:
# type "./Main_cal_TG_Rate_95CI.py"  in a Linux terminal,
# or type "python Main_cal_TG_Rate_95CI.py" or "py Main_cal_TG_Rate_95CI.py"  in a Windows CMD terminal. 

## Important notes
# The PSMSL dataset ('fin'): *.rlrdata is organized as the following, the unit of MSL is in millimeters.
  # 1957.7083;  6990; 0;000
  # 1957.7917;  6975; 0;000
  # 1957.8750;  6926; 0;000
  # 1957.9583;  6713; 0;000
  # .......
  #  1965.0417;  6670; 0;000
  #  1965.1250;-99999;00;000
  #  1965.2083;-99999;00;000
  #  1965.2917;-99999;00;000
  #  1965.3750;-99999;00;000

## PSMSL fills the data gap as -99999
  # These gap lines need to be removed before inputting the data into Main_cal_TG_Rate_95CI.py and TG_Rate_95CI.py
  # I wrote a Bash script, "do_PSMSL_Pre_Process.sh", for doing the pre-process.

## You may need to install several Python modules on your computer if you have not installed them before.
    # Those modules are: pandas, numpy, matplitlib, statsmodels, statistics, datetime, and Pyts (the LATEST Pyts)
    # do this by "pip install module-name"
    
## For installing the LATEST pyts Module for using the SSA module, carefully read the following website.
  # https://pyts.readthedocs.io/en/latest/install.html
  # You can get the LATEST version of pyts by cloning the Github repository:
    #git clone https://github.com/johannfaouzi/pyts.git
    #cd pyts
    #pip install .
  
## Some useful hints for Windows-Python users 
   # Rember to "cd" to your working directory that you installed the Python files and TG data
   # For running the program: type "python Main_cal_TG_Rate_95CI.py" or "py Main_cal_TG_Rate_95CI.py"  

   # For installing Python modules: If the system still can not find the module after  "pip install module-name",
     # you may try "py -m pip install module-name" 

   # It may take a while installing the Latest pyts on your Windows system
     # First, install "git" on your Windows computer, https://git-scm.com/downloads
     # Second, Use the git Bash window, run the following commands:
       #git clone https://github.com/johannfaouzi/pyts.git
       #cd pyts
       #pip install .
     # if the system report "can not find the module pyts", you may try to do the following in the CMD window:
       #cd pyts   (You need to get into this folder, e.g., c:\users\gwang\pyts)
       #py -m pip install .

## I wish a good luck for Windows users! 

import sys 
print (sys.executable)
import os
import pandas as pd
from TG_Rate_95CI import cal_95CI

directory = './'
# This is for reading the PSMSL data. Slight adjustments are needed for reading NOAA data.
for fin in os.listdir(directory):
    if fin.endswith(".rlrdata"):
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
       

