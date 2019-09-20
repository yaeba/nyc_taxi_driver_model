# Presentation Topic

**1st Speaker (Xuanken Tay)**
1. General outline of presentation.
2. Brief overview of problem description.
3. High-level workflow to problem (with diagram): pre-processing, training basic
models, evaluating, and using model with best performance.

**2nd Speaker (Geng Yuxiang))**
1. High-level fundamental heuristic: maximising total earnings rate; choosing
the cell with the highest total earnings rate.
2. Why predict average total earnings rate: why not just total earnings?
3.	Calculation of total earnings rate.
4.	Penalty terms: driving duration and frequency of trips.

**3rd Speaker (Li Shangqian)**
1.	Implementation: Overarching classification model which produces our move for
the current round; it does this by integrating the output of smaller models.
Smaller models will calculate information such as (for each separate model):
shortest path from one cell to another, average total earnings for a given
cell over a time interval, average frequency of trips picked up within a cell
over a fixed time interval.
2. Overarching classificaiton model integrates these smaller models' outputs
to produce a dataset containing all the standardised (to be fairly compared)
average total earnings rate; obtaining maximum to decide our next decision.

2.	Smaller models made to help inform our decision for the round. #Baseline models.
Smaller models to calculate each cells total earnings rate; or frequency rate.
Results are integrated to obtain a datastructure which has standardized total
earnings rate which cna help inform our next move (cell wiht highest standardised
total earnings rate).
2.	Why do we need classification?
3.	Classification flow-chart: explain diagram and uncertainty & risk factors.

**4th Speaker (Yin Zhou)**
1.	Evaluation: separate basic models are compared; performance in terms of 
overall earnings/profit can be produced on the local game; local game can be run
a lot of times to produce model mean and variance; comparison of basic model
earnings and profits. Reviewing the logs.
2. Job Allocation: Everyone attempts to produce different models. Competing
against each other; avoid bias against assumptions that one model is more suitable

Q & A Tips:
* Thank them for the question.
* Make sure they understand your answer.
