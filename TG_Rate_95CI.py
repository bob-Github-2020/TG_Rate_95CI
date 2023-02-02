#!/usr/bin/python3

# Last updated: 01-27-2023, by Guoquan (Bob) Wang, bob.g.wang@gmail.com

# The Python function is designed for calculating the rate of monthly MSL (b) and its 95% confidence interval
# The detailed methodology is adressed in:
# Wang, G. (2023). A methodology for calculating the 95% confidence interval of the mean sea-level rate derived from tide gauge data, submitted (2/1  /2023)

# You may install the module on your computer by: pip install TG_Rate_95CI
# https://pypi.org/project/TG-Rate-95CI/
# or get the source code from my GitHub site
# https://github.com/bob-Github-2020/TG_Rate_95CI

## You need to install The LATEST Pyts for SSA, carefully read the following website. 
# https://pyts.readthedocs.io/en/latest/install.html
  # You can get the LATEST version of pyts by cloning the repository:
  # git clone https://github.com/johannfaouzi/pyts.git
  # cd pyts
  # pip install .
## It may take a while installing the Latest SSA on your Windows system
  # https://pyts.readthedocs.io/en/latest/generated/pyts.decomposition.SingularSpectrumAnalysis.html#pyts.decomposition.SingularSpectrumAnalysis

## A detailed instruction is listed at the beginning of the main program, Main_cal_TG_Rate_95CI.py


import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statistics
from datetime import datetime
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.tsa.stattools import acf, pacf
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
from pyts.decomposition import SingularSpectrumAnalysis
from statistics import median, mean


plt.rcParams.update({'font.size': 14})

def cal_95CI(year,ts,TG,output,pltshow):

    """
    Calculate the rate of the monthly MSL data and its 95%CI

    Inputs
    -------
    year: decimal year, e.g., 2021.003 ...
    ts: MSL time series, in mm, 1957.7083;  6990; 0;000 (only the first two columns are used)
    TG: string, TG station name, e.g., for PSMSL data, 161.rlrdata, TG is "161"
    output: 'on' or 'off'. 'on' will plot figures (*.png, *.pdf) and write out data (*.txt).
    pltshow: 'on' or 'off'. 'on' will display the figures on the screen. You need to mannually close the figure to continue
         
    Returns
    --------
    b_L, 95CI
        
    Reference
    ---------
      Wang, G. (2023). A methodology for calculating the 95% confidence interval of the mean sea-level rate derived from tide gauge data, submitted xxx

    A Sample Main Routine
    ---------------------
    For how to calling the Python function, please read "Main_cal_TG_Rate_95CI.py"!
     
    """
    
    N=len(ts)             # Total measures
    T=year[N-1]-year[0]   # Total year range
          
# -----------------------------------------------------------------------------
# Step 1: Linear regresion on the whole time series
#         Eq.1: Li=a+b*ti+Ri, using OLS--Ordinary Least Squares
# -----------------------------------------------------------------------------
    ## remove the whole mean from ts
    ave = statistics.mean(ts)
    print (ts)  
    print('ave=',ave)
    ts = ts - ave
    #print (ts)

    ## add a column name to 'year'
    #  It is necessary to add name to year, otherwise "Rresult.params" will not identify [0], [1]
    Fyear = year.to_frame('Year')
       
    x = sm.add_constant(Fyear)
    model = sm.OLS(ts,x)
    Rresult = model.fit()
    
    print(Rresult.params)
    print(Rresult.resid)
    print(Rresult.df_resid)
    
    a = Rresult.params[0]
    b_L = Rresult.params[1]
    print ('a=', Rresult.params[0])
    print ('b=',Rresult.params[1])
  
    ## stand error for b
    s=np.sqrt(np.sum(Rresult.resid**2)/Rresult.df_resid)    # Eq.4
    SEs= s/np.sqrt(N)                                       
    SEb=SEs*2*np.sqrt(3.0)/T                                # Eq.3

    Li = a+b_L*year                                         # Eq.2
   
# -----------------------------------------------------------------------------
# Step 2: Setup the SSA model, calculate Si and b_P
#         The data gap needs to be filled 
# -----------------------------------------------------------------------------  
    Ri = ts - Li
        
    # cal RMS of Ri, for printing on final figure
    RMS_rm_L= math.sqrt(np.square(Ri).mean())
    print('RMS_rm_L=', RMS_rm_L)   
            
    def decimalYear2Date(dyear):
        year = int(dyear)
        yearFraction = float(dyear) - year
        doy = int(round(yearFraction * 365.25-0.5)) + 1
        ydoy = str(year) + "-" + str(doy)
        r = datetime.strptime(ydoy, "%Y-%j").strftime("%Y-%m-%d")
        return r  

    # Preparing for filling gaps
    # Use a loop converting original decimal year to date, e.g., 2021-05-25
    ymdR = []
    for line  in year:
        ymdi = decimalYear2Date(line)
        ymdR.append(ymdi)
    
    # convert row to column
    ymd = pd.DataFrame (ymdR)
    
    # combine column ymd and Ri
    ymd_and_res = pd.concat([ymd, Ri], axis=1)

    # add column name to the DataFrame
    ymd_and_res.columns = ['Date', 'RES']
    df = ymd_and_res

    # Convert column "Date" to DateTime format
    df.Date = pd.to_datetime(df.Date, format='%Y-%m-%d')
    df = df.set_index('Date')

    # Firstly, fill the gap in YMD seris and give NaN for the RES time series
    df_con_nan = df.resample('1M').mean()      # 1M-- one month
    y_con_nan=df_con_nan['RES']                # used for output
    y_con_nan=y_con_nan.reset_index()

    # Secondly, fill the NaN in RES column as a number, use assign, or random, prefer random
    def fill_with_random(df2, column):
        '''Fill df2's column  with random data based on non-NaN data from the same column'''
        df = df2.copy()
        df[column] = df[column].apply(lambda x: np.random.choice(df[column].dropna().values) if np.isnan(x) else x)
        return df
    
    df = fill_with_random(df_con_nan,'RES')
  
    df = df.reset_index()
    df = pd.DataFrame(df)
    x_con = df.iloc[:,0]
    y_con = df.iloc[:,1]

    # Build continuous decimal year time series, xt
    x0 = year[0]
    npts = len(y_con) 
    xt=np.zeros(npts)
       
    for i in range(npts):
        xt[i] = x0 + (i-0.5)*1/12
         
    # The SSA model for decomposition
    def ssa_model(y):
        R = pd.DataFrame(y).to_numpy()
        X = R.reshape(1,-1)
       
        # Singular Spectrum Analysis
        nws=round(0.45*npts)
        ssa = SingularSpectrumAnalysis(window_size=nws, groups=None, chunksize=1500, n_jobs=1)
        X_ssa = ssa.fit_transform(X)
        
        Si=X_ssa[0]+X_ssa[1]+X_ssa[2]+X_ssa[3]+X_ssa[4]+X_ssa[5]+X_ssa[6]+X_ssa[7]+X_ssa[8]+X_ssa[9] \
           +X_ssa[10]+X_ssa[11]+X_ssa[12]+X_ssa[13]+X_ssa[14]
     
        return Si, X_ssa
    # End SSA      
    
    result_ssaM= ssa_model(y_con)
    Pi=result_ssaM[0]
    X_ssa=result_ssaM[1]
           
    # calculate the linear trend of Pi
    x = sm.add_constant(xt)
       
    model = sm.OLS(Pi,x)
    results = model.fit()
    b_P = results.params[1]
    #print(results.params)
    #print('b_P=', b_P)

# -----------------------------------------------------------------------------
# Step 3: calculate the Effect Sample Size, Neff--Eq.13, and SEbc--Eq.15
#         work on ri, yi=Li+NLi+Si+ri, Eq.9 
# -----------------------------------------------------------------------------
    ri = y_con - Pi
    
    ## I compared RMS and MAD. Not shown in figures.
    def mad(x):
        """Median Absolute Deviation"""
        return median(abs(x-median(x)))

    def nmad(x):
        """Normalized Median Absolute Deviation"""
        return mad(x)/0.6745
    
    # cal RMS of ri
    RMS_ri= math.sqrt(np.square(ri).mean())
    
    # cal MAD of ri
    NMAD_ri=nmad(ri)
    
    data = np.array(ri)
    
    ## cal PACF. could be slow. In fact, it does not need PACF in determining 95%CI
       #lagPACF = round(len(ri)*0.45)
       #lag_pacf = pacf(data, nlags=lagPACF, method='ols')
       ## write PACF
       #yp = pd.DataFrame(lag_pacf)
       #yp.to_csv(TG +'_PACF.col', index = True, header=False)
       #plot_pacf(data, lags=lagPACF,zero=False)
       #plt.savefig(TG +"_PACF.pdf")
       #plt.show()

    ## cal ACF
    if len(ri) < 480:
       maxlag = len(ri)-1
    else:
       maxlag=480 

    lag_acf = acf(data, nlags=maxlag,fft=True)
    ## write ACF
    ya = pd.DataFrame(lag_acf)
    ya.to_csv(TG + '_ACF.col', index = True, header=True)
       
    ## Plot ACF. I prefer the one that I configured.
    #plot_acf(data,lags=maxlag,fft=True, zero=False)
    #plt.savefig(TG +"_ACF_tmp.pdf")
    #plt.show()
   
    ## self configured ACF plot
    x=np.arange(0,len(ya),1)
    x=np.array(x)
    y=np.array(ya)
    plt.plot(x,y,'k.',markersize=2)
    if y[2]>=0.5:
       y2=ya[2]
    else:
       y2=0.5

    plt.ylim(top=y2)
    plt.xlim(right=maxlag)

    y=y.ravel()
    plt.fill_between(x, y)
    plt.xlabel('Time-lag (Months)')
    plt.ylabel('ACF')
    plt.title('ACF: ID '+TG)
                  
    plt.savefig(TG + "_ACF.pdf")
    plt.savefig(TG + "_ACF.png")
    if pltshow == 'on':
       plt.show()
      
   # determine Tau, autocorrelation time , Eq. 11       
    sum = 0
    i=0
    for acfi in lag_acf:
        if acfi >= 0:
           i=i+1
           sum = sum + acfi
        else:
            print("Found lag-M at", i)
            break
    Nfit=len(ri)
    tau = 1 + 2*sum               # Eq.11
    Neff = int(Nfit/tau)          # Eq.10
    SEbc=np.sqrt(tau)*SEb         # Eq.12, same as SEbc=np.sqrt(N/Neff)*SEb
    print('Nfit=', Nfit, 'tau=', tau, 'Neff=', Neff, 'SEb=', SEb, 'SEbc=', SEbc)
 
# -----------------------------------------------------------------------------
# Step 4: calculate the 95%CI--Eq.13, and projected 95%CI--Eq.14
# -----------------------------------------------------------------------------
    b95CI = 1.96 * SEbc + abs(b_P)     #Eq.13
  
    ## NOAA Model, Zervas 2009.
    # b95CI_mod = 395.5/math.pow(T,1.64)
    ## UH Global Model, Wang 2023. Eq. 14
    b95CI_mod = 185/math.pow(T,1.3)
       
# -----------------------------------------------------------------------------
# Step 5: Write out data and Plot Figures, if output = on
# -----------------------------------------------------------------------------
    if output == 'on':

       ## plot and write out SSA.
       y = pd.DataFrame({'ssa0': X_ssa[0], 'ssa1': X_ssa[1], 'ssa2': X_ssa[2], \
                         'ssa3': X_ssa[3], 'ssa4': X_ssa[4], 'ssa5': X_ssa[5],\
                         'ssa6': X_ssa[6], 'ssa7': X_ssa[7], 'ssa8': X_ssa[8], \
                         'ssa9': X_ssa[9], 'ssa10': X_ssa[10]})
               
      
       y.to_csv(TG + '_SSA.col', index = True, header=True)
       
       # Plot SSA. This is just a draft figure for illustrating purposes
       plt.figure(figsize=(16,14))
     
       #mticker.Locator.MAXTICKS = 2000
       ax1 = plt.subplot(121)
       
       ax1.plot(ts, 'o-', label='TS (with gaps)')
       ax1.plot(Li, '-', label='Trend L(i)')
       #ax1.plot(y_con, 'o-', label='De_Linear')
       ax1.plot(Pi, '-', label='Periodic P(i) (gap filled)')
       #ax1.plot(Si, 'o-', label='Periodics')
       ax1.legend(loc='best', fontsize=14)
       ax1.set_xlabel('Time (Months)')     

       ax2 = plt.subplot(122)
       ax2.plot(X_ssa[0]-100, '-', label='SSA0')
       ax2.plot(X_ssa[1]-50, '-', label='SSA1')
       ax2.plot(X_ssa[2], '-', label='SSA2')
       ax2.plot(X_ssa[3]+50, '-', label='SSA3')
       ax2.plot(X_ssa[4]+100, '-', label='SSA4')
       ax2.plot(X_ssa[5]+150, '-', label='SSA5')
       ax2.plot(X_ssa[6]+200, '-', label='SSA6')
       ax2.plot(X_ssa[7]+250, '-', label='SSA7')
       ax2.plot(X_ssa[8]+300, '-', label='SSA8')
       ax2.plot(X_ssa[9]+350, '-', label='SSA9')
       ax2.plot(X_ssa[10]+400, '-', label='SSA10')
       ax2.plot(X_ssa[11]+450, '-', label='SSA11')
       ax2.plot(X_ssa[12]+500, '-', label='SSA12')

       ax2.legend(loc='best', fontsize=14)
       ax2.set_xlabel('Time (Months)')
       plt.suptitle('Singular Spectrum Analysis, ID '+TG, fontsize=20, y=0.93)

       plt.tight_layout()
       plt.subplots_adjust(top=0.88)
       
       plt.savefig(TG +'_SSA.png')
       plt.savefig(TG +'_SSA.pdf')
       
       if pltshow == 'on':
          plt.show()
             
       ## Plot decomposition figure, Fig. 3
       #  This figure can be directly used in publication
       fig, (fig1,fig2,fig3) = plt.subplots(3, figsize=(16,14))
       fig.subplots_adjust(hspace=0.4)
       fig.suptitle('Decomposition of TG-Derived Monthly MSL Time Series: ID '+ TG, size=16,  y=0.93);
     
       #fig1.plot(year, ts, 'b-',linewidth=0.5)
       fig1.plot(year, ts, 'k.')
       fig1.plot(year, Li, 'r',linewidth=2)
       fig1.set_ylim(bottom=min(ts)*1.0, top=max(ts)*1.0)
       
       str_bL=str(round(b_L,2))
       str_bP=str(round(b_P,2))
       str_b95CI=str(round(b95CI,2))
       str_b95CI_mod=str(round(b95CI_mod,2))   # mm/year
       str_SEb=str(round(SEb,2))
       str_SEbc=str(round(SEbc,2))
       
       str_RMS_rm_L=str(round(RMS_rm_L,1))
       str_RMS_ri=str(round(RMS_ri,1))
       str_NMAD_ri=str(round(NMAD_ri,1))
               
       fig1.text(0.5, 0.9, 'Site velocity: '+ str_bL + '$\pm$' + str_b95CI+' mm/year', ha='center', va='center', transform=fig1.transAxes,backgroundcolor='1',alpha=1)
       fig1.text(0.1, 0.07, '$SE_b$= '+ str_SEb + ' mm/year', ha='center', va='center', transform=fig1.transAxes)
       fig1.text(0.3, 0.07, '$SE_{bc}$= '+ str_SEbc + ' mm/year', ha='center', va='center', transform=fig1.transAxes)
       fig1.text(0.7, 0.07, 'Calculated vs. Projected 95%CI: '+ str_b95CI + ' vs. '+ str_b95CI_mod + ' mm/year', ha='center', va='center', transform=fig1.transAxes)
   
       fig2.plot(xt, y_con,'.',c='0.7')
       fig2.plot(xt, Pi, 'r', linewidth=1.5)
       fig2.text(0.1, 0.9, 'RMS: '+ str_RMS_rm_L + ' mm', ha='center', va='center', transform=fig2.transAxes)
       fig2.text(0.1, 0.07, '$b_P$: '+ str_bP + ' mm/year', ha='center', va='center', transform=fig2.transAxes)
             
       fig3.plot(xt, ri,'r.')
       fig3.text(0.1, 0.9, 'RMS: '+ str_RMS_ri + ' mm', ha='center', va='center', transform=fig3.transAxes)
       #fig3.text(0.3, 0.9, 'NMAD: '+ str_NMAD_ri + ' mm', ha='center', va='center', transform=fig3.transAxes)

       fig1.set_ylabel('MSL (mm)')
       fig2.set_ylabel('MSL (mm)')
       fig3.set_ylabel('MSL (mm)')
    
       fig3.set_xlabel('Year', labelpad=12, fontsize=15)

       fig1.set_title('(a) Monthly MSL time series y(i) & Linear trend L(i)')
       fig2.set_title('(b) The periodic time series P(i) obtained from Singular Spectrum Analysis (SSA)')
       fig3.set_title('(c) The noise time series r(i)')
       
       fig.savefig(TG + '_Decomposition.png')
       fig.savefig(TG + '_Decomposition.pdf')  
       
       if pltshow == 'on':
          plt.show()
            
       # output the time series, original and filled
       f1_out = TG + "_Linear.col"

       # build the DataFrame
       df = pd.concat([year, ts, Li, Ri], axis=1)
       # add column name to the DataFrame
       df.columns = ['Year', 'Dis(mm)','Linear','Residue']
       df.to_csv(f1_out, header=True, index=None, sep=' ', mode='w', float_format='%.5f')

       xt=pd.DataFrame(xt)
       Pi=pd.DataFrame(Pi)
    
       y_con=pd.DataFrame(y_con)
       ri=pd.DataFrame(ri)
       
       f2_out = TG + "_Ri_Pi_ri.col"
       df = pd.concat([xt, y_con,Pi,ri], axis=1)
       df.columns = ['Year_con', 'Ri_filled', 'Pi','ri']
       df.to_csv(f2_out, header=True, index=None, sep=' ', mode='w', float_format='%.5f')
       
       ## output all parameters
       f3_out = TG + "_AllParameters.txt"
      
       Columns=['TG','T(Years)','N','Npts','Neff','Vel(mm/y)','95%CI(mm/y)','NOAA95%CI(mm/y)', \
                'b_P(mm/y)', 'SEb(mm/y)', 'SEbc(mm/y)','RMS_rm_L(mm)','RMS_ri(mm)','NMAD_ri(mm)']
       Parameters=[T, N, npts,Neff,b_L, b95CI, b95CI_mod,  \
                   b_P, SEb, SEbc, RMS_rm_L, RMS_ri, NMAD_ri]
                   
       with open(f3_out, 'w') as f:
            for col in Columns:
                f.write(col)
                f.write('  ')
       with open(f3_out, 'a') as f: 
            f.write('\n') 
            f.write(TG)
            f.write('  ')
            for val in Parameters:
                f.write(str(round(val,2)))
                f.write('  ')
      
    else: 
       print('Output is off!')  
       
    
    return b_L, b95CI
 







    
  



