# Presentation Topic

**1st Speaker (Xuanken Tay)**
1. General outline of presentation.
2. Brief overview of problem description.
3. High-level workflow to address problem (with diagram): pre-processing,
training basic models, evaluating, using model with best performance, etc.

**2nd Speaker (Geng Yuxiang))**
1. High-level fundamental heuristic: maximising total earnings rate; choosing
the cell with the highest total earnings rate.
2. Why predict average total earnings rate: why not just total earnings?
3.	Calculation of total earnings rate.
4.	Penalty terms: driving duration and frequency of trips.

**3rd Speaker (Li Shangqian)**
1.	Implementation: Overarching classification model which outputs the decision
for the current round; it does this by integrating the output of smaller models.
2. Functions of smaller models, including: shortest path identifier, average
total earnings for each cell (for a given time interval), average trip duration
for each cell (for a given time interval).
3. Overarching classification model integrates these outputs to produce a
dataset containing each cell's corresponding 'standardised' average total
earnings rate. 'Standardised' in the sense that each cell can be directly
compared fairly.
4. Cell with highest 'standardised' average total earnings rate becomes the
next cell we move and stay for customers.
5. Why do we need classification?
6. Classification flow-chart: explain diagram and uncertainty & risk factors.

**4th Speaker (Yin Zhou)**
1.	Evaluation: separate basic models are compared; performance in terms of 
overall earnings/profit can be produced on the local game; local game can be run
a lot of times to produce model mean and variance; comparison of basic model
earnings and profits. Reviewing the logs.
2. Job Allocation: Everyone attempts to produce different models; which are
compared. Still deciding how work can be distributed to not overlap.

Q & A Tips:
* Thank them for the question.
* Make sure they understand your answer.
