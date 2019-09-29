#!/usr/bin/env bash
## Extract duration and player's name
## Aggregate summaries of different players from logs/
## Usage: ./aggregate_summaries.sh <path_to_logs/>

LOGS=$1

extract_duration_distance() {
	local log=$1

	# Extract duration from log
	cat $log |
	    grep "pickedup"  |
	    cut -d',' -f4,5 |
	    awk -F',' -v q='"' '{"date -d"q $1 q" +%s"|getline d1;
	    		"date -d"q $2 q" +%s"|getline d2;print(d2-d1)/60}' |
	    awk -F',' '{ sum1 += $1 } END { print sum1 }'	
}

export -f extract_duration_distance

update_player_summary() {
	local player_dir=$1
	local player_name=$(basename $player_dir)

	# Update all games' summary
	csv=$(find $player_dir -type f -name "*.log" -printf "%T+\t%p\n" | 
		grep -v "trips\|debug" | 
		sort | 
		cut -f2 |
		xargs -I% bash -c 'extract_duration_distance %' |
		cat <(echo "duration") - |
		sed "s/$/,$player_name/" |
		sed "0,/$player_name/s/$player_name/player/")


	find $player_dir -type f -name "*Summary*" |
		xargs cat |
		paste -d'\0' - <(echo "$csv")
}

export -f update_player_summary


players=$(find $LOGS -type f -name "*.log" |
	xargs dirname |
	sort |
	uniq)

# Aggregate results of all players
echo "$players" |
	xargs -I% bash -c 'update_player_summary %' |
	sed '2,${/^earnings/d;}'
