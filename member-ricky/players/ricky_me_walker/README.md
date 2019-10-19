# Zone-Minute-Weekend Walker

Inherits behaviour from Manhattan Walker, except that instead of moving randomly in Manhattan, it stays/moves to cell that believed to increase its chance of getting a trip. Uses a crude lookup table of `(Weekend, Pickup_hour, Pickup_minute (rounded to nearest 10), Zone) : Number_trips` to make its decision.

-  Start time (unchanged)
-  Next shift time (unchanged)
-  Start shift in "best" Manhattan cell given current datetime
