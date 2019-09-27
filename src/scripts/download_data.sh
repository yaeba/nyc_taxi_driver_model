#!/usr/bin/sh
## Script to download all the tripdata from Cloudstor

cat /home/ubuntu/group7/data/files | while read line
do
    wget -q --show-progress -O $line "https://cloudstor.aarnet.edu.au/plus/s/wMKnyI13UCYxATD/download?path=%2Fdata&files=$line"
done
