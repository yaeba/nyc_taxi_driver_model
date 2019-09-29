#!/usr/bin/env bash
## Script to collect all players and run the game
## Usage: ./run_simulations.sh  <game_count> <config.json> [output_dir]

COUNT=$1
CONFIG=$(realpath $2)
OUTDIR=$(realpath $3)

CWD=$(pwd -P)
GAME_JAR=$(realpath ../Game_Release/NYCTaxiGame.jar)
PLAYERS_DIR=$(realpath players.txt)
AGGREGATE_SCRIPT=$(realpath ./aggregate_summaries.sh)

# Find directories with player.json and convert to json
players_json=$(find $(cat $PLAYERS_DIR) -type f -name "player.json" -exec realpath {} + |
	   xargs dirname |
	   sed 's/^/gitDir=/' |
	   jq -Rs '[ split("\n")[] | select(length > 0) | split("=") | {(.[0]): .[1]} ]' )

# Append element to json object
final_json=$(jq --slurpfile dirs <(echo $players_json) '.players=$dirs[0]' $CONFIG |
	sed "s/\"gameCount\": 1/\"gameCount\": $COUNT/")

# Create directory if specified
if [ ! -z "$OUTDIR" ];
then
	mkdir -p $OUTDIR
	final_json="${final_json//../$CWD/..}"
	cd $OUTDIR
fi

echo "Config:"
echo $final_json | jq .

echo "Running simulation(s) in $(pwd)"

# Running the game
java -jar $GAME_JAR play <(echo $final_json)

# Aggregate summaries
start=$(cat summaries/* | grep "GameDate:" | cut -d' ' -f2,3)

bash $AGGREGATE_SCRIPT logs/ |
	sed "s/$/,$start/" | 
	sed "0,/$start/s/$start/start/" > results.csv

echo "Results saved to $(pwd)/results.csv"

[[ -z "$OUTDIR" ]] || cd $CWD
