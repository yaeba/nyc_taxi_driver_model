#!/usr/bin/env bash
## Script to convert trips.log to csv containing {datetime, cell, action}
## ./extract_movement.sh <trips.log>

LOG=$(realpath $1)

cat <(echo "Date,Cell,Action") $LOG |
    sed 's/T/ /g' |
    awk -F',' '{if (NF == 4) {print $1","$2",Pickup"; print $3","$4",Dropoff"} 
    	      	else {print $1","$2",Move"}}'
