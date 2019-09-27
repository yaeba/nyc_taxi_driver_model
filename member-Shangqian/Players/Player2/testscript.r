library(jsonlite)
playTurn <- function(currentDateTime, currentCell, neighbours){
  print(sample(neighbours,1))
  nextMove <- sample(neighbours,1)
  #statements
  #return(object)
  # state FORHIRE, UNAVAILABLE
  # action MOVE, STAY
  # if action is MOVE moveTo must be specified
  return(list(state = "FORHIRE", action="MOVE", moveTo = nextMove));
}


firstMove <- function(startDateTime){
  
  #Get day from calendar - in case of different strategies for different days
  print(weekdays(startDateTime))
  
  #### Select when and where to start
  
  #set start time - cannot be 00:00 must be at least 00:01
  startDateTime = startDateTime + 4*60*60 
  nextMove = "32:45"
  
  
  #### Respond object
  return(list(defer = startDateTime, moveTo = nextMove));
}



nextShift <- function(currentTime){
  startDateTime = currentTime + 9*60*60 
  nextMove = "32:45"
  
  
  #### Respond object
  return(list(defer = startDateTime, moveTo = nextMove));
}

#Open Stdin to read requests
f <- file("stdin")
open(f, blocking=TRUE)

#Loop forever or until the connection is closed
while(length(line <- readLines(f,n=1)) > 0) {
  print(paste("Got:",line))
  #Read JSON
  req <-fromJSON(line)
  type <- as.character(req$type)
  currentDateTime <- as.POSIXct(req$time,format="%Y-%m-%dT%H:%M")
  if(type=="FIRSTMOVE"){
    action<-firstMove(currentDateTime)
    #Create response named list that will be converted to JSON
    resp = list()
    resp[["defer"]]<-format(action$defer, "%Y-%m-%dT%H:%M")
    resp[["nextMove"]]="REPOSITION"
    resp[["moveTo"]]=action$moveTo
    
    write(paste("MAST30034:", toJSON(resp,auto_unbox = TRUE)), stdout())
  }else if(type=="PLAYTURN"){
    req <-fromJSON(line)
    currentDateTime <- as.POSIXct(req$time,format="%Y-%m-%dT%H:%M")
    currentCell <- as.character(req$currentCell)
    neighbours <- req$neighbours
    action<-playTurn(currentDateTime, currentCell, neighbours)
    
    write(paste("MAST30034:", toJSON(action,auto_unbox = TRUE)), stdout())
  }else if(type=="NEXTSHIFT"){
    action<-nextShift(currentDateTime)
    #Create response named list that will be converted to JSON
    resp = list()
    resp[["defer"]]<-format(action$defer, "%Y-%m-%dT%H:%M")
    resp[["nextMove"]]="REPOSITION"
    resp[["moveTo"]]=action$moveTo
    
    write(paste("MAST30034:", toJSON(resp,auto_unbox = TRUE)), stdout())
  }
  # process line
}
