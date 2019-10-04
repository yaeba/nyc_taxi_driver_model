import sys
import json
import datetime
from datetime import datetime
from datetime import timedelta
import dateutil.parser
import random

import pandas as pd
import pickle
import bfs
import numpy as np

# Load graph and compute cost for all cells
import os
dirname = os.path.dirname(__file__)

graph_path = os.path.join(dirname, '../data/graph.pkl')
graph = bfs.load_graph(graph_path)

# Load models and encoders
lr_path = os.path.join(dirname, '../model/lr.pickle')
with open(lr_path, 'rb') as handle:
    lr = pickle.load(handle)

ohe_path = os.path.join(dirname, '../model/lr.pickle')
with open(ohe_path, 'rb') as handle:
    ohe = pickle.load(handle)


def play_turn(current_datetime, current_cell, neighbours):

    current_datetime = pd.to_datetime(current_datetime)
    weekday = str(current_datetime.weekday())

    costs = bfs.bfs(graph, current_cell)
    cost_dict = dict(list(costs.items()))

    # Compute destination cells with arrival time, return 2d array
    pred_list = [[k, weekday, (current_datetime + timedelta(minutes=v)).time().replace(second=0).strftime("%H:%M:%S")]
                 for k, v in cost_dict.items()]
    pred_arr = np.array(pred_list)
    df = pd.DataFrame(pred_arr)

    # Compute predicted frequencies for all cells
    freq_dict = cost_dict.copy()
    for i, (k, v) in enumerate(cost_dict.items()):
        arr = df.values[i].reshape(1, -1)
        try:
            pred = ohe.transform(arr).toarray()
            freq_dict[k] = lr.predict(pred)[0]
        except ValueError:
            freq_dict[k] = 0

    # Compute scores for all cells
    score_dict = cost_dict.copy()
    for (k1, v1), (k2, v2) in zip(freq_dict.items(), cost_dict.items()):
        try:
            score_dict[k1] = v1/v2
        except ZeroDivisionError:
            score_dict[k1] = v1/0.0000001

    # Determine destination cells to move to
    dest_cell = max(score_dict, key=score_dict.get)

    # Compute path array until destination
    path = bfs.find_shortest_path(graph, current_cell, dest_cell)

    next_move = path[1]
    # create a dictionary setting state, action, and if required moveTo
    return {"state": "FORHIRE", "action": "MOVE", "moveTo": next_move}


def first_move(start_datetime):
    """Decide first move, i.e. start time and location:
        start_datetime: start time of the game

    Returns a dictionary containing defer and moveTo.
        defer: datetime to start the first shift,
        moveTo: string id of cell to start in
    """
    # start playing 4 hours after the start of the game

    start_datetime = start_datetime + timedelta(hours=7)
    # start in the cell with id 32:45
    next_move = "23:60"
    # return a dictionary with defer and moveTo set
    return {"defer": start_datetime, "moveTo": next_move}


def next_shift(current_time):
    """Called at the end of shift to determine next shifts
    start time and start location:
        current_time: current date time in the game

    Returns a dictionary containing defer and moveTo.
        defer: datetime to start the next shift,
                must be at least 8 hours in the future
        moveTo: string id of cell to start in
    """
    # start next shift 9 hours after this shift
    start_datetime = current_time + timedelta(hours=9)
    # start shift in cell 32:45
    next_move = "23:60"
    # return a dictionary with defer and moveTo set
    return {"defer": start_datetime, "moveTo": next_move}


# loops until shutdown, waiting for new turn requests on StdIn
while(1):
    # Read input from StdIn
    req = json.loads(sys.stdin.readline())
    reqtype = req['type']
    current_datetime = dateutil.parser.parse(req['time'])
    if(reqtype == "FIRSTMOVE"):
        action = first_move(current_datetime)
        # Create response named list that will be converted to JSON
        resp = {}
        resp["defer"] = action['defer'].strftime("%Y-%m-%dT%H:%M")
        resp["nextMove"] = "REPOSITION"
        resp["moveTo"] = action['moveTo']
        print("MAST30034:" + json.dumps(resp))
        sys.stdout.flush()
    elif(reqtype == "PLAYTURN"):
        current_cell = req['currentCell']
        neighbours = req['neighbours']
        action = play_turn(current_datetime, current_cell, neighbours)
        print("MAST30034:" + json.dumps(action))
        sys.stdout.flush()
    elif(reqtype == "NEXTSHIFT"):
        action = next_shift(current_datetime)
        # Create response named list that will be converted to JSON
        resp = {}
        resp["defer"] = action['defer'].strftime("%Y-%m-%dT%H:%M")
        resp["nextMove"] = "REPOSITION"
        resp["moveTo"] = action['moveTo']
        print("MAST30034:" + json.dumps(resp))
        sys.stdout.flush()
