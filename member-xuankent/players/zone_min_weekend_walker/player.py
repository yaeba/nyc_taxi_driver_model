import os
import sys
import json
import datetime
from datetime import timedelta
import dateutil.parser
import random
import pandas as pd
import numpy as np
from collections import Counter
import itertools
import bisect


################### Functions to get next shifts ###################

def shifts(start_time):
    date_range = [start_time + datetime.timedelta(days=x) for x in range(6)]
    return list(map(wday_to_shift, date_range))

def wday_to_shift(dt):
    switch = {
        0: 14,
        1: 14,
        2: 14,
        3: 15,
        4: 16,
        5: 17}
    wday = dt.weekday()
    return dt.replace(hour=switch[wday])

def get_next_shift(current_datetime, all_shifts):
    idx = bisect.bisect(all_shifts, current_datetime)
    next_shift = all_shifts[idx]
    diff = next_shift - current_datetime

    if diff < datetime.timedelta(hours=8):
        # Rest for 8 hours before continuing
        return current_datetime + datetime.timedelta(hours=8)
    else:
        return next_shift

###################################################################



################# Functions for lookup table ######################


def extract_time(dt):
    weekend = dt.weekday() >= 5
    hour = dt.hour
    minute = int(dt.minute / 10) * 10
    return (weekend, hour, minute)


def form_tuple(dt, cell_id, manhattan_zones):
    return extract_time(dt) + (manhattan_zones[cell_id],)


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


###################################################################




def predict_prob_trip(current_datetime, current_cell, manhattan_zones, trips_lookup):
    key = form_tuple(current_datetime, current_cell, manhattan_zones)
    if key not in trips_lookup:
        return 0

    def odds_to_prob(freq):
        return freq / (1 + freq)

    return odds_to_prob(trips_lookup[key])



####################### Best move ################################
## Function to get next move that maximises 
## probability of getting a trip

def best_move(current_datetime, current_cell, graph, manhattan_cells, predict_func, k=5):
    """
    Get next move that maximises Pr(getting a trip) in next `k` minutes
    :param Datetime current_datetime: python datetime object
    :param str current_cell: string of cell id
    :param Graph graph: Graph object
    :param set/list manhattan_cells: Collection of all manhattan cells
    :param function predict_func: A function that accepts (datetime, cell) and
                                return probabilty of getting trip
    :(opt) param int k: Lookahead value, min of 1, recommended 10~15
    :return: Cell id to move to
    """

    time = current_datetime
    visited = {current_cell: (0, 1, None)}

    for _ in range(k):
        time += timedelta(minutes=1)

        prev = visited.copy()
        for cell in list(visited.keys()):
            (cumprob, cumprob_bar, counts) = prev[cell]
            for neighbour in bfs.get_neighbours(graph, cell):
                if not neighbour in manhattan_cells:
                    continue

                prob = predict_func(time, neighbour)
                new_cumprob = cumprob + cumprob_bar * prob
                
                new_cumprob_bar = cumprob_bar * (1 - prob)
                new_counts = counts

                if new_counts is None:
                    # First move
                    new_counts = Counter([neighbour])
                else:
                    new_counts = new_counts.copy()
                if not neighbour in visited:
                    visited[neighbour] = (new_cumprob, new_cumprob_bar, new_counts)
                else:
                    # Visited before, compare
                    (old_cumprob, old_cumprob_bar, old_counts) = visited[neighbour]
                    if new_cumprob >= old_cumprob:
                        if new_cumprob == old_cumprob and not old_counts is None:
                            # Append
                            new_counts += old_counts
                        # Replace
                        visited[neighbour] = (new_cumprob, new_cumprob_bar, new_counts)

    best_prob = max(visited.values(), key=lambda x: x[0])[0]
    best_moves = [count for (cumprob, _, count) in visited.values() if cumprob >= best_prob]
    best_moves = sum(best_moves, Counter())

    return max(best_moves, key=best_moves.get)


###################################################################

def first_move(start_datetime, all_shifts, manhattan_zones, trips_lookup):
    """
    Decide first move, i.e. start time and location:
        start_datetime: start time of the game
    
    Returns a dictionary containing defer and moveTo.
        defer: datetime to start the first shift,
        moveTo: string id of cell to start in
    """

    start_datetime = get_next_shift(start_datetime, all_shifts)

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
        # Already in Manhattan, find move that gives highest probability

        # consider few rounds ahead
        lookahead = 10

        predict_func = lambda time, cell: \
                    predict_prob_trip(time, cell, manhattan_zones, trips_lookup)
        next_move = best_move(current_datetime, current_cell, graph,
                        manhattan_cells, predict_func, k=lookahead)
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


def next_shift(current_datetime, all_shifts, manhattan_zones, trips_lookup):
    """
    Called at the end of shift to determine next shifts
    start time and start location:
        current_datetime: current date time in the game
    
    Returns a dictionary containing defer and moveTo.
        defer: datetime to start the next shift,
                must be at least 8 hours in the future
        moveTo: string id of cell to start in
    """

    start_datetime = get_next_shift(current_datetime, all_shifts) 

    # Start next shift in zone with most number of trips per cell
    best_cells = best_start_cells(start_datetime, manhattan_zones, trips_lookup)
    next_move = random.choice(best_cells)

    # Return a dictionary with defer and moveTo set
    return {"defer":start_datetime,"moveTo":next_move}


def play_game(graph, manhattan_zones, trips_lookup):
    """
    Output decisions, loops until shutdown
    """

    all_shifts = None
    # Waiting for new turn requests on StdIn
    while(1) :

        # Read input from StdIn
        req = json.loads(sys.stdin.readline())
        reqtype = req['type']
        current_datetime = dateutil.parser.parse(req['time'])

        if(reqtype=="FIRSTMOVE"):
            all_shifts = shifts(current_datetime)
            action = first_move(current_datetime, all_shifts, manhattan_zones, trips_lookup)
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
            action=next_shift(current_datetime, all_shifts, manhattan_zones, trips_lookup)
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

    # Dictionary that maps cell id to zone
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
    # Script path is path to player.py
    script_path = os.path.abspath(os.path.dirname(sys.argv[0]))

    # Root path is "group7/"
    root_path = os.path.join(script_path, "../../../")

    # Append so that script can import bfs.py under "src/utils/"
    # remove if bfs.py is in player.py
    sys.path.append(root_path)

    from src.utils import bfs
    main(root_path)