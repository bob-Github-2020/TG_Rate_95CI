# TG_Rate_95CI.py

Last updated: 1-27-2023, by Guoquan (Bob) Wang.

Calculating the MSL rate and its 95%CI. Please read the main routine "Main_cal_TG_Rate_95CI.py" for using the Python module, "TG_Rate_95CI.py". The detailed methodology for calculating the 95%CI is adressed in:

Wang, G. (2023). A methodoly for calculating the 95% confidence interval of the mean sea-level rate derived from tide gauge data, submitted xxx (02/03/2023)

You may install the module on your computer by: pip install TG_Rate_95CI

       https://pypi.org/project/TG_Rate_95%CI/ 
       
or download the source code (TG_Rate_95CI.py) to your working directory

       https://github.com/bob-Github-2020/TG_Rate_95CI

## Test the module

Copy Main_cal_TG_Rate_95CI.py, TG_Rate_95CI.py, and the sample PSMSL data (e.g., 828.rlrdata) to your working directory.

type "./Main_cal_TG_Rate_95CI.py"  in a Linux terminal

or type "python Main_cal_TG_Rate_95CI.py" or "py Main_cal_TG_Rate_95CI.py"  in a Windows CMD terminal. 

## Important notes

The PSMSL dataset *.rlrdata is organized as the following, the unit of MSL is mm

       1957.7083;  6990; 0;000
       1957.7917;  6975; 0;000
       .......
       1965.1250;-99999;00;000
       1965.2083;-99999;00;000
       1965.2917;-99999;00;000

PSMSL fills the data gap as -99999. These gap lines need to be removed before inputting the data into Main_cal_TG_Rate_95CI.py and TG_Rate_95CI.py.  Only the first two columns are used. I wrote a Bash script, "do_remove_PSMSL_gap_lines", for doing the pre-process.

## Required Python Modules

You may need to install several Python modules (e.g., pandas, statistics) on your computer if you have not installed them before. Those modules are: pandas, numpy, matplitlib, statsmodels, statistics, datetime, and Pyts (the LATEST Pyts). Do this by:

     pip install module-name
 
For installing the LATEST Pyts Module for using the SSA module, carefully read the following website.

    https://pyts.readthedocs.io/en/latest/install.html
    
You should get the LATEST version of pyts by cloning the Github repository:

       git clone https://github.com/johannfaouzi/pyts.git
       cd pyts
       pip install .
       
### It may take a while installing the Latest SSA on your Windows system

First, install "git" on your Windows computer, https://git-scm.com/downloads

Second, Use the git Bash window, run the following commands:
       
          git clone https://github.com/johannfaouzi/pyts.git
          cd pyts
          pip install .
          
If the system report "can not find the module pyts", you may try to do the following in the CMD window:
    
          cd pyts   
          py -m pip install .
  
## Some useful hints for Windows-Python users

I know that you use the CMD terminal. Rember to "cd" to your working directory that you installed the Python files and TG data
For running the program: type 
      python Main_cal_TG_Rate_95CI.py
      
or type
      py Main_cal_TG_Rate_95CI.py  

For installing Python modules, if the system still can not find the module after  "pip install module-name",
       you may try 
       
       py -m pip install module-name 


# For NOAA data users

The Main program "Main_cal_TG_Rate_95CI.py" is designed for reading PSMSL data. NOAA data is organized in a slight different way (e.g., 9457292_meantrend.txt):
   
    Year   Month    Monthly_MSL       
    1949   9        -0.622                                                           
    1949   10       -0.663                                                           
    1949   11       -0.568                                                           
    1949   12       -0.804 

If you are working on NOAA data, please use the following Python program:

     #! /usr/bin/python3
     ## for reading NOAA MSL data and calling "TG_Rate_95CI.py"
     import os
     import pandas as pd
     from TG_Rate_95CI import cal_95CI
  
     directory = './'
       for fin in os.listdir(directory):
           if fin.endswith("meantrend.txt"):
              print(fin)
              ns=len(fin)
              TG = fin[0:7]    # station name, e.g., 8771450
              ts_noaa = []
              ts_noaa = pd.read_csv (fin, header=0, delim_whitespace=True)
              year = ts_noaa.iloc[:,0]    # year
              mm = ts_noaa.iloc[:,1]
              msl = ts_noaa.iloc[:,2]     # Monthly_MSL
            
              ts = msl*1000              # m to mm

              dy = year + (mm-0.5)/12
              result=cal_95CI(dy, ts, TG, output='on', pltshow='on')
              b=round(result[0],2)           # Trend
              b_95CI=round(result[1],2)      # 95%CI
 
              os.remove (fin)     
            else:
              pass

## I wish a good luck for Windows users! 

## Example outputs

Some example figures for the Galveston Pleasure Pier TG (PSMSL ID: 828) output from the Python Module:

![828_ACF](https://user-images.githubusercontent.com/65426380/215299095-5fc5fad6-4c80-44b3-acf3-d488bdbaf9ea.png)
![828_SSA](https://user-images.githubusercontent.com/65426380/215297920-23bcb64c-5c1f-47f1-9f90-9e6b21287cb5.png)
![828_Decomposition](https://user-images.githubusercontent.com/65426380/215297927-fe6a8aaa-1c36-46ac-a1e4-088ebfdc0619.png)
