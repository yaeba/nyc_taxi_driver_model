**Summary of Individual Assignments - Applicable Ideas**

**Dataset Selection**
* For the yellow taxi data, most trips (more than 80%) occur in the Manhattan
region. By observing the green taxi data (restricted to pick-ups outside of 
Manhattan), we can better analyse trips outside of Manhattan.

**Pre-Processing & Cleansing**
* How to reasonably process all the available past data?
* Randomly sub-sample a fixed number of trips from each month, where each month
is the combined green and yellow taxi data.
* Cleanse before sub-sampling, since Chris states that "whilst it might be
tempting to sample first to reduce the computational effort, it can lead to
unrepresentative samples and even incorrect cleaning.
* Incorrect times also appear in the datasets; for instance, 2008 trip data
in the 2017 dataset.
* Granularity of the bins and the binning implementation. Round the times to the
nearest minute when binning by minute?
* How to handle missing values for bins with no instances?
* Justify use of random sup-sampling.

**Outlier Detection**
* "Eyeballing” with histograms.
* Generating descriptive statistics.
* Generating the five-number summary, eliminating outliers using the standard
boxplot definition of outliers: Any values less than (Q1 - 1.5 * IQR) or more
than (Q3 + 1.5 * IQR).
* Justification: Due to the random nature of the game whereby trips within a
cell for any given round (minute in-game) are randomised; therefore, we want
a 'realistic' view of the trips we should expect, not skewed from outliers
(if, for instance, we use mean to aggregate trips).

**Observed Trends**
* Inspecting Xuanken's visualisation (Assignment 1; Section 4.2) of the frequency
of green taxi trips for each hour, each day of the week, we see the following
pattern: higher trip frequencies during the day for Mondays to Thursdays, and
higher trip frequencies during the night for Fridays to Sundays.
* Longer trips (relatively, above the 75% percentile) occur more frequently
during weekend nights for green taxis.
* The green taxi data shows trip duration to be more strongly correlated to the
fare amount than trip distance; nonethles, both show strong positive correlation
with the fare amount.
* From the yellow taxi data, average tips in Manhattan tend to stay aroud 1-1.5
USD, increasing in the norhtern regions of Manhattan to a max of 3.7 USD.

**Model Fitting**
* For regression models, where and why should we apply standardisation?
* How to test assumptions of a regression model; what assumptions are there?
* Distribution fitting diagnostics.
* Diagnostic tests for regression fitting (e.g. GLM).