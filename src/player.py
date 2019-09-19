
import sys
import json
import datetime
from datetime import timedelta
import dateutil.parser
import random

def play_turn(current_datetime, current_cell, neighbours):
    """Processes a players turn:
        current_datetime: date of current round
        current_cell: string id of cell player is in
        neighbours: array of valid string ids of neighbours
   
    Returns a dictionary containing a minimum of state and action.
        state: "FORHIRE" or "UNAVAILABLE",
        action: "MOVE" or "STAY", 
                if "MOVE" dictionary must include moveTo
                containing id of one of this cells neighbours.
    """


    # randomly choose a move from the neighbours array
    next_move=random.choice (neighbours)
    # create a dictionary setting state, action, and if required moveTo
    return {"state":"FORHIRE","action":"MOVE","moveTo":next_move}

def first_move(start_datetime):
    """Decide first move, i.e. start time and location:
        start_datetime: start time of the game
    
    Returns a dictionary containing defer and moveTo.
        defer: datetime to start the first shift,
        moveTo: string id of cell to start in
    """
    # start playing 4 hours after the start of the game
    start_datetime = start_datetime + timedelta(hours=4)
    # start in the cell with id 32:45 
    next_move = "32:45"
    # return a dictionary with defer and moveTo set
    return {"defer":start_datetime,"moveTo":next_move}

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
    next_move = "32:45"
    # return a dictionary with defer and moveTo set
    return {"defer":start_datetime,"moveTo":next_move}

# loops until shutdown, waiting for new turn requests on StdIn
while(1) :
    #Read input from StdIn
    req = json.loads(sys.stdin.readline())
    reqtype = req['type']
    current_datetime = dateutil.parser.parse(req['time'])
    if(reqtype=="FIRSTMOVE"):
        action = first_move(current_datetime)
        #Create response named list that will be converted to JSON
        resp = {}
        resp["defer"]=action['defer'].strftime("%Y-%m-%dT%H:%M")
        resp["nextMove"]="REPOSITION"
        resp["moveTo"]=action['moveTo']
        print("MAST30034:" + json.dumps(resp))
        sys.stdout.flush()
    elif(reqtype=="PLAYTURN"):
        current_cell = req['currentCell']
        neighbours = req['neighbours']
        action=play_turn(current_datetime, current_cell, neighbours)
        print("MAST30034:" + json.dumps(action))
        sys.stdout.flush()
    elif(reqtype=="NEXTSHIFT"):
        action=next_shift(current_datetime)
        #Create response named list that will be converted to JSON
        resp = {}
        resp["defer"]=action['defer'].strftime("%Y-%m-%dT%H:%M")
        resp["nextMove"]="REPOSITION"
        resp["moveTo"]=action['moveTo']
        print("MAST30034:" + json.dumps(resp))
        sys.stdout.flush()

