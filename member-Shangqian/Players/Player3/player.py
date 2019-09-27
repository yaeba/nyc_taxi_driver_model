import sys
import json
import datetime
from datetime import timedelta
import dateutil.parser
import random
def play_turn(current_datetime, currentCell, neighbours):
    next_move=random.choice (neighbours)
    print("NextMove:"+next_move)
    return {"state":"FORHIRE","action":"MOVE","moveTo":next_move}
def first_move(start_datetime):
    start_datetime = start_datetime + timedelta(hours=4) 
    next_move = "32:45"
    return {"defer":start_datetime,"moveTo":next_move}
def next_shift(current_time):
    start_datetime = current_time + timedelta(hours=9) 
    next_move = "32:45"
    return {"defer":start_datetime,"moveTo":next_move}

while(1) :
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

