### Breakdown
#### Game Rule 
* Period: 1 week
* Round: 1 minute
* Shift: <= 6
* Duration of shift: <= 12 hours, >= 8 hours rest, <= 10 hours transporting passengers.
* Winning: Fare + tips 


### Basic Model Design:
Depending on the current location (cell) of our yellow taxi, we calculate the 
associated profit rates of each and every cell of New York City (including the 
one we currently occupy). The profit rates are adjusted appropriately to allow
fair comparison between all cells. The cell with the highest profit rate is
chosen as the next location for pickups.

**Profit Rate**

The profit rate of a cell is determined by the average total earnings per minute
for pickups/hires made in the cell within an ‘x’ minute interval for a specific
day of the week. This will be computed over the entire available dataset. New
datasets representing each day of the week will be made to contain these profit
rates; including attributes such as:
* Pickup Cell: The cell where the hire/pickup was made.
* Interval: The starting time of the ‘x’ minute time interval.
* Profit Rate: The average total earnings per minute for pickups/hires made in the pickup cell.

We extract the relevant data from our datasets depending on both the current
time and location; applying adjustments to obtain comparable profit rates for
all cells.

**Adjustments**

Adjustments are made for each cell depending on the cell’s location from the
current cell. Moving between cells will take time. Assuming we know how long it
takes to move from cell to cell, we can appropriately adjust our profit rates.

Initially, we can extract the relevant profit rates from the new datasets that
we create. Knowing the time it will take to reach a specific cell from our
current cell, we can determine what time it will be when and if we arrive at
that specific cell. We can then extract the profit rate for the corresponding
time interval (for the arrival time).

We must also apply a penalty term to account for the loss of potential earnings
while travelling towards a different cell. A possible approach is to replace
the original denominator of the total earnings rate by the sum of the original
number of minutes and the travelling time (in minutes).

#### Extra Thoughts

*  The above approach can be thought of as determining a new total earnings rate.
Since the initial drive towards the location yields zero earnings but consumes
time, we add zero to the numerator and the time in the denominator.
*  Outliers: In summarising the data to produce the average total earnings rates
per cell for each day of the week, outliers should be removed, or the median
should be used. The randomisation procedure of the game affects the consistency
of anomalies appearing at expected times; thus favouring profit rates that reflect general trends. 
