#!/bin/bash

#12-27-2022, by Bob Wang
# Pre-process PEMSL data: (1) remove -99999 lines (gap lines), (2) remove dataset less than 20 years, or have data gaps over half of the time span. 

for file in *.rlrdata;
  do
    echo $file
    ## Remove "-99999" lines, lines with no measures
      sed -e '/-99999/d' -i $file 
   
    ## Idenfiy stations less than 20 years, gaps > half range 

    # total lines, measures
      lines=$(wc -l < $file);
      echo 'lines=' $lines
      
    # read the firstline-firstrow
    diff_real () {
       echo "df=($1 - $2); if (df < 0) { df=df* -1}; print df" | bc -l;
     }

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

    #  remove stations spanning less than 20 years
    #  or with over half-missing, 2*nlines < T*12

    if [ $IT -le 20 -o $nl -le $npts ]; then
       echo $T
       echo "Deleting file: ", $file
       rm $file
    fi;
    
done

