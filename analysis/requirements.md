### Requirements
##### Driving Duration - DD
Overview
* Time taken for driving from current cell to destination cell.

Implementation 
* Calculate `Shortest Cell Path` between current cell and destination cell using `Shortest Path Algorithm`
* Driving Duration is calculated as

<div style="text-align:center"><img src="https://latex.codecogs.com/gif.latex?\text{Driving&space;Duration}&space;=&space;\text{Shortest&space;Cell&space;Path}&space;*&space;\text{1&space;min/cell}" title="\text{Driving Duration} = \text{Shortest Cell Path} * \text{1 min/cell}" /></div>

##### Avg Total Earnings - Avg(TE)
Average total earning for a single trip at destination cell.

Implementation
* Model
    * Predictor: pickup_cell.x, pickup_cell.y, dest_cell.x, dest_cell.y, min_of_day, day_of_week
    * Response: total_amount + tip_amount
* Model type: ***to be determined***

##### Avg Trip Duration - Avg(TD)
Average trip duration for a single trip at destination cell.

Implementation
* Model
    * Predictor: pickup_cell.x, pickup_cell.y, dest_cell.x, dest_cell.y, min_of_day, day_of_week 
    * Response: driving_duration (in seconds)
* Model type: ***to be determined***

##### Average Total Earnings Rate - Avg(TER)
Implementation
* Avg(TER) is calculated as
<div style="text-align:center"><img src="https://latex.codecogs.com/gif.latex?\text{AVG(TER)}&space;=&space;\frac{\text{AVG(TE)}}{\text{AVG(TD)}}" title="\text{AVG(TER)} = \frac{\text{AVG(TE)}}{\text{AVG(TD)}}" /></div>
##### Trip Frequency
Average number of trips at destination cell in 1 minute.

Implementation
* Variables
    * Predictor: dest_cell.x, dest_cell.y
    * Response: trip_count (in minute)

##### Delay 
If not getting a trip in n minute, recalculate next move.

##### State
Set state to `For Hire` at all time