#!/bin/bash

#JustQueue_bhist_2019_original.out is the original logfile of queue **** in 2019 of HPC (Security information has been filtered.)

#Step 1  modify the original *.out file to a proper format.
#cat JustQueue_bhist_2019_original.out | tr '\n' ' ' | sed 's/ //g' | sed 's/------Job</\nJob</g' >> JustQueue-bhist-2019-all.log

#Step 2  create namelist.txt (Attention: better check the result manually.)
#cat JustQueue-bhist-2019-all.log |  grep 'User<' | awk -F 'User<' '{print $2}' | awk -F '>,' '{print $1}' | sort | uniq >> namelist.txt

#Step 3  create log file of every user for the further exploration
for name in `cat namelist.txt`
  do
    mkdir JustQueue-2019-${name}
    cat JustQueue-bhist-2019-all.log | grep $name >> JustQueue-2019-${name}/JustQueue-2019-${name}.log
done

mkdir Intermediate_Files
cp namelist.txt   JustQueue-bhist-2019-all.log   JustQueue_bhist_2019_original.out   Creat_bhist_log_for_every_user.sh Intermediate_Files/
zip -rvm LogFile-JustQueue-2019-all-user.zip   JustQueue-2019-*   Intermediate_Files

#for name in `cat namelist.txt`
#  do 
#    rm -rf JustQueue-2019-${name}
#done

echo -e  "\n\tThe logfile for every user is now prepared...\n"
