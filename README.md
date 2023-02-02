## Rread Me for calling TG_Rate_95CI.py

Last updated: 1-28-2023, by Guoquan (Bob) Wang.  

Feel free to contact me by: bob.g.wang@gmail.com

## Main function

Calculating the MSL rate and its 95% confidence interval. 

Please read the main routine "Main_cal_TG_Rate_95CI.py" for calling the Python module "TG_Rate_95CI.py". The detailed methodology for calculating the 95%CI is adressed in:

Wang, G. (2023). A methodoly for calculating the 95% confidence interval of the mean sea-level rate derived from tide gauge data, submitted xxx (02/01/2023)

You may install the module on your computer by: 

       pip install TG_Rate_95CI

Please visit the PyPi site:

      https://pypi.org/project/TG_Rate_95%CI
       
or download the source code (Main_cal_TG_Rate_95CI.py, TG_Rate_95CI.py) to your working directory

       https://github.com/bob-Github-2020/TG_Rate_95CI

## Test the module

Copy Main_cal_TG_Rate_95CI.py, TG_Rate_95CI.py, and the sample PSMSL data (e.g., 828.rlrdata) to your working directory. Run the following command in a Linux terminal:

       ./Main_cal_TG_Rate_95CI.py
       
or run (in a Windows CMD terminal):

       python Main_cal_TG_Rate_95CI.py
       
or 

       python3 Main_cal_TG_Rate_95CI.py
       
or    

       py Main_cal_TG_Rate_95CI.py

## Important notices

The PSMSL dataset *.rlrdata is organized as the following, the unit of MSL is mm.

       1957.7083;  6990; 0;000
       1957.7917;  6975; 0;000
       .......
       1965.1250;-99999;00;000
       1965.2083;-99999;00;000
       1965.2917;-99999;00;000

PSMSL fills the data gap as -99999. These gap lines need to be removed before inputting the data into Main_cal_TG_Rate_95CI.py and TG_Rate_95CI.py. Only the first two columns are used. You may use the follwing Bash command to remove gap lines:
 
        sed -e '/-99999/d' -i 828.rlrdata 

I wrote a Bash script, "do_PSMSL_Pre_Process.sh", for doing the pre-process, removing gap lines, excluding datasets shorter than 20 years or with gaps over half of the year range.

     #!/bin/bash
     #12-27-2022, by Bob Wang
     #* Pre-process PEMSL data: (1) remove -99999 lines (gap lines), 
     #  (2) remove dataset less than 20 years, or have data gaps over half of the time span. 

     for file in *.rlrdata;
       do
       echo $file
     ## Remove "-99999" lines, lines with no measures
       sed -e '/-99999/d' -i $file 
   
     ## Idenfiy stations less than 20 years, gaps > half year range 

     # total lines, measures
       lines=$(wc -l < $file);
       echo 'lines=' $lines
      
     # read the firstline-firstrow
       diff_real () {
       echo "df=($1 - $2); if (df < 0) { df=df* -1}; print df" | bc -l;}

       y1=$(head -1 $file | cut -d";" -f 1);
       y2=$(tail -1 $file | cut -d";" -f 1);
    
       T=$(diff_real $y2 $y1)
    
       echo $y1 $y2 $T

     # conver T to integer
       IT=${T%.*}
       npts=$(($IT*12))
       nl=$((lines*2))
       echo $IT $npts $nl
    
       file_size=$(du -b $file | awk '{print $1}');
       echo $file_size

     #  remove stations spanning less than 20 years or with over half-missing, 2*nlines < T*12

      if [ $IT -le 20 -o $nl -le $npts ]; then
        echo $T
        echo "Deleting file:" $file
        rm $file
      fi;
     done


## Required Python Modules

You may need to install several Python standard modules on your computer if you have not installed them before. Those modules are: pandas, numpy, matplitlib, statsmodels, statistics, datetime, and Pyts (Must be the LATEST Pyts). Do this by:

     pip install module-name
 
For installing the LATEST pyts module for using the SSA module, please carefully read the following website.

    https://pyts.readthedocs.io/en/latest/install.html
    
You should get the LATEST version of pyts by cloning the Github repository:

       git clone https://github.com/johannfaouzi/pyts.git
       cd pyts
       pip install .
       
### It may take a while installing the LATEST pyts on your Windows system

First, install "git" on your Windows computer, https://git-scm.com/downloads

Second, Use the git Bash window, run the following commands:
       
          git clone https://github.com/johannfaouzi/pyts.git
          cd pyts
          pip install .
          
If the system report "can not find the module pyts", you may try to do the following in the CMD terminal:
    
          cd pyts   
          py -m pip install .
  
## Some useful hints for Windows-Python users

Rember to "cd" to your working directory that you installed the Python files and TG data.

For running the program:

      python Main_cal_TG_Rate_95CI.py
      
or run

      py Main_cal_TG_Rate_95CI.py  

If the system still can not find the standard Python module after "pip install module-name", you may try:
       
       py -m pip install module-name 


# For NOAA data users

The Main program "Main_cal_TG_Rate_95CI.py" is designed for reading PSMSL data. NOAA data is organized in a slight different way (e.g., 9457292_meantrend.txt). The unit of MSL is in meters.
   
    Year   Month    Monthly_MSL       
    1949   9        -0.622                                                           
    1949   10       -0.663                                                           
    1949   11       -0.568                                                           
    1949   12       -0.804 

If you are working on NOAA data, please use the following Python program for calling the module, TG_Rate_95CI.py:

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
              
              # For processing a bunch datasets, may set pltshow='off'
              result=cal_95CI(dy, ts, TG, output='on', pltshow='on')
              b=round(result[0],2)           # Trend
              b_95CI=round(result[1],2)      # 95%CI
 
              #os.remove (fin)     
            else:
              pass

## I wish a good luck for Windows-Python users! 

## Example outputs

Some example figures for the Galveston Pleasure Pier TG (PSMSL ID: 828) output from the Python Module:

![828_ACF](https://user-images.githubusercontent.com/65426380/215344521-fa8f2041-255a-4e4a-888a-d75ad069e869.png)
![828_SSA](https://user-images.githubusercontent.com/65426380/215344556-f8960f17-214a-4f86-a8a0-f42d44d55ac4.png)
![828_Decomposition](https://user-images.githubusercontent.com/65426380/215344568-90f68bdb-2b39-46e6-9349-5d1af790b1c5.png)

