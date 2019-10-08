import os
import sys
import json
import datetime
from datetime import timedelta
import dateutil.parser
import random
import pandas as pd
import numpy as np
from collections import Counter, deque
import itertools

def extract_time(dt):
    weekend = dt.weekday() < 5
    hour = dt.hour
    minute = int(dt.minute / 10) * 10
    return (weekend, hour, minute)


def best_start_cells(start_datetime, manhattan_zones, trips_lookup):
    time_tuple = extract_time(start_datetime)
    poss = [(time_tuple + (zone,)) for zone in manhattan_zones.values()]
    best_zone = max(poss, key=trips_lookup.get)[3]
    return [cell for (cell, zone) in manhattan_zones.items() if zone == best_zone]


def normalise_frequency(trips_lookup, manhattan_zones):
    zone_ncells = dict(Counter(manhattan_zones.values()))

    for (key, value) in trips_lookup.items():
        weekend = key[0]
        zone = key[3]

        # Normalise frequency by number of cells
        value /= zone_ncells[zone]

        # Normalise frequency by number of days made up the lookup table
        if weekend:
            value /= 2
        else:
            value /= 5

        # Normalise frequency by minutes
        value /= 10

        trips_lookup[key] = value

    return trips_lookup

def compute_trip_prob(freq):
    freq_array = np.array(freq)
    prob_trip = freq_array / (1 + freq_array)
    prob_no_trip = np.cumprod([1] + list(1 - prob_trip))[:-1]
    return sum(prob_trip * prob_no_trip)

def best_moves(current_datetime, current_cell, graph, manhattan_zones, trips_lookup, k=5):
    start = (current_cell, tuple(), [], 0)
    queue = deque([start])
    leaves = dict()

    while queue:
        (cell, path, freqs, cost) = queue.popleft()

        if cost == k:
            leaves[path] = compute_trip_prob(freqs)
            continue

        for neighbour in bfs.get_neighbours(graph, cell):
            if neighbour not in manhattan_zones.keys():
                # Not a manhattan cell
                continue
            new_cost = cost + 1
            new_path = path + (neighbour,)
            new_datetime = current_datetime + timedelta(minutes=new_cost)
            new_freqs = freqs + [trips_lookup[extract_time(new_datetime) + (manhattan_zones[neighbour],)]]
            queue.append((neighbour, new_path, new_freqs, new_cost))

    best_prob = max(leaves.values())
    best_moves = [path[0] for (path, prob) in leaves.items() if prob >= best_prob]
    counts = Counter(best_moves)
    return max(best_moves, key=counts.get)


def zones_min_dist(costs, manhattan_zones):
    by_zone = lambda x: manhattan_zones[x[0]]
    it = itertools.groupby(sorted(costs.items(), key=by_zone), by_zone)
    return {k: min(list(g), key=lambda x: x[1]) for (k, g) in it}


def first_move(start_datetime, manhattan_zones, trips_lookup):
    """
    Decide first move, i.e. start time and location:
        start_datetime: start time of the game
    
    Returns a dictionary containing defer and moveTo.
        defer: datetime to start the first shift,
        moveTo: string id of cell to start in
    """

    # Start playing 4 hours after the start of the game
    start_datetime = start_datetime + timedelta(hours=4)

    # Start in zone with most number of trips per cell
    best_cells = best_start_cells(start_datetime, manhattan_zones, trips_lookup)
    next_move = random.choice(best_cells)

    # Return a dictionary with defer and moveTo set
    return {"defer":start_datetime,"moveTo":next_move}



def play_turn(current_datetime, current_cell, neighbours, graph, 
                manhattan_zones, trips_lookup):
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

    manhattan_cells = set(manhattan_zones.keys())
    decision = {"state": "FORHIRE"}
    next_move = None

        

    if current_cell in manhattan_cells:
        # Already in Manhattan, find series of moves that gives highest probability
        lookahead = 4
        next_move = best_moves(current_datetime, current_cell, 
            graph, manhattan_zones, trips_lookup, k=lookahead)
    else:
        # Head towards Manhattan

        # cost to all reachable cells
        costs = bfs.bfs(graph, current_cell)
        costs = {cell: cost for (cell, cost) in costs.items() if cell in manhattan_cells}

        if not costs:
            # Manhattan cells are not reachable
            next_move = random.choice(neighbours)
        else:
            # Move along the path to closest Manhattan cell
            closest = min(costs, key=costs.get)
            next_move = bfs.find_shortest_path(graph, current_cell, closest)[1]


    if next_move == current_cell:
        decision["action"] = "STAY"
    else:
        decision["action"] = "MOVE"
        decision["moveTo"] = next_move

    return decision


def next_shift(current_time, manhattan_zones, trips_lookup):
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

    # Start next shift in zone with most number of trips per cell
    best_cells = best_start_cells(start_datetime, manhattan_zones, trips_lookup)
    next_move = random.choice(best_cells)

    # Return a dictionary with defer and moveTo set
    return {"defer":start_datetime,"moveTo":next_move}


def play_game(graph, manhattan_zones, trips_lookup):
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
            action = first_move(current_datetime, manhattan_zones, trips_lookup)
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
            action=play_turn(current_datetime, current_cell, neighbours, graph, 
                            manhattan_zones, trips_lookup)
            print("MAST30034:" + json.dumps(action))
            sys.stdout.flush()

        elif(reqtype=="NEXTSHIFT"):
            action=next_shift(current_datetime, manhattan_zones, trips_lookup)
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
    # Find all cells in Manhattan
    cell2loc = pd.read_csv(os.path.join(root_path, "data/cell_to_location.csv"))
    manhattan = cell2loc[cell2loc["Borough"] == "Manhattan"]

    manhattan_zones = manhattan.set_index("Cell").to_dict()["Zone"]

    # Load lookup table of number of trips for each (Weekend, Hour, Min) 
    trips_lookup = pd.read_csv("zone_min_weekend.csv") \
        .set_index(["Weekend", "Pickup_hour", "Pickup_minute", "Zone"]) \
        .to_dict()["Number_trips"]

    # Normalise frequency in lookup table
    trips_lookup = normalise_frequency(trips_lookup, manhattan_zones)

    # Load graph for cost and path finding
    graph = bfs.load_graph(os.path.join(root_path, "data/graph.pkl"))

    # Start playing game
    play_game(graph, manhattan_zones, trips_lookup)


if __name__ == "__main__":
    # Root path is "group7/"
    script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    root_path = os.path.join(script_path, "../../../")

    sys.path.append(root_path)

    from src.utils import bfs
    main(root_path)