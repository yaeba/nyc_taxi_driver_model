#!/usr/bin/env bash
## Script to collect all players and run the game
## Usage: ./run_game.sh  <config.json>

CONFIG=$1
GAME_JAR=../Game_Release/NYCTaxiGame.jar
PLAYERS_DIR=players.txt

# Find directories with player.json and convert to json
players_json=$(find $(cat $PLAYERS_DIR) -type f -name "player.json" -exec realpath {} + |
	   xargs dirname |
	   sed 's/^/gitDir=/' |
	   jq -Rs '[ split("\n")[] | select(length > 0) | split("=") | {(.[0]): .[1]} ]' )

# Append element to json object
final_json=$(jq --slurpfile dirs <(echo $players_json) '.players=$dirs[0]' $CONFIG)

echo "Config:"
echo $final_json | jq .

# Running the game
java -jar $GAME_JAR play <(echo $final_json)
