import os
import sys
import json
import datetime
from datetime import timedelta
import dateutil.parser
import random
import pandas as pd
import numpy as np

def first_move(start_datetime, bronx_cells):
    """
    Decide first move, i.e. start time and location:
        start_datetime: start time of the game
    
    Returns a dictionary containing defer and moveTo.
        defer: datetime to start the first shift,
        moveTo: string id of cell to start in
    """

    # Start playing 4 hours after the start of the game
    start_datetime = start_datetime + timedelta(hours=4)

    # Start in any bronx cell
    next_move = random.choice(list(bronx_cells))

    # Return a dictionary with defer and moveTo set
    return {"defer":start_datetime,"moveTo":next_move}



def play_turn(current_datetime, current_cell, neighbours, graph, bronx_cells):
    """
    Processes a players turn:
        current_datetime: date of current round
        current_cell: string id of cell player is in
        neighbours: array of valid string ids of neighbours
   
    Returns a dictionary containing a minimum of state and action.
        state: "FORHIRE" or "UNAVAILABLE",
        action: "MOVE" or "STAY", 
                if "MOVE" dictionary must include moveTo
                containing id of one of this cells neighbours.
    """

    decision = {"state": "FORHIRE"}
    next_move = None

    if current_cell in bronx_cells:
        # Already in bronx, choose STAY or MOVE within Manhattan
        poss = [cell for cell in neighbours 
                if cell in bronx_cells] + [current_cell]
        next_move = random.choice(poss)
    else:
        # Head towards bronx
        costs = bfs.bfs(graph, current_cell)
        all_costs = [(costs[cell], cell) for cell in bronx_cells if cell in costs]

        if not all_costs:
            # bronx cells are not reachable
            next_move = random.choice(neighbours)
        else:
            # Move along the path to closest bronx cell
            closest = min(all_costs)[1]
            next_move = bfs.find_shortest_path(graph, current_cell, closest)[1]


    if next_move == current_cell:
        decision["action"] = "STAY"
    else:
        decision["action"] = "MOVE"
        decision["moveTo"] = next_move

    return decision


def next_shift(current_time, bronx_cells):
    """
    Called at the end of shift to determine next shifts
    start time and start location:
        current_time: current date time in the game
    
    Returns a dictionary containing defer and moveTo.
        defer: datetime to start the next shift,
                must be at least 8 hours in the future
        moveTo: string id of cell to start in
    """

    # Start next shift 9 hours after this shift
    start_datetime = current_time + timedelta(hours=9) 

    # Start shift in random bronx cell
    next_move = random.choice(list(bronx_cells))

    # Return a dictionary with defer and moveTo set
    return {"defer":start_datetime,"moveTo":next_move}


def play_game(graph, bronx_cells):
    """
    Output decisions, loops until shutdown
    """

    # Waiting for new turn requests on StdIn
    while(1) :

        # Read input from StdIn
        req = json.loads(sys.stdin.readline())
        reqtype = req['type']
        current_datetime = dateutil.parser.parse(req['time'])

        if(reqtype=="FIRSTMOVE"):
            action = first_move(current_datetime, bronx_cells)
            # Create response named list that will be converted to JSON
            resp = {}
            resp["defer"]=action['defer'].strftime("%Y-%m-%dT%H:%M")
            resp["nextMove"]="REPOSITION"
            resp["moveTo"]=action['moveTo']
            print("MAST30034:" + json.dumps(resp))
            sys.stdout.flush()

        elif(reqtype=="PLAYTURN"):
            current_cell = req['currentCell']
            neighbours = req['neighbours']
            action=play_turn(current_datetime, current_cell, neighbours, graph, bronx_cells)
            print("MAST30034:" + json.dumps(action))
            sys.stdout.flush()

        elif(reqtype=="NEXTSHIFT"):
            action=next_shift(current_datetime, bronx_cells)
            # Create response named list that will be converted to JSON
            resp = {}
            resp["defer"]=action['defer'].strftime("%Y-%m-%dT%H:%M")
            resp["nextMove"]="REPOSITION"
            resp["moveTo"]=action['moveTo']
            print("MAST30034:" + json.dumps(resp))
            sys.stdout.flush()



def main(root_path):
    """
    Called at the start of the game
    """
    # Find all cells in bronx
    cell2loc = pd.read_csv(os.path.join(root_path, "data/cell_to_location.csv"))
    boroughs = cell2loc.set_index("Cell").to_dict()["Borough"]
    bronx_cells = {cell for (cell, borough) in boroughs.items() 
                        if borough == "Bronx"}


    # Load graph for cost and path finding
    graph = bfs.load_graph(os.path.join(root_path, "data/graph.pkl"))

    # Start playing game
    play_game(graph, bronx_cells)


if __name__ == "__main__":
    # Root path is "group7/"
    script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    root_path = os.path.join(script_path, "../../../")

    sys.path.append(root_path)

    from src.utils import bfs
    main(root_path)
