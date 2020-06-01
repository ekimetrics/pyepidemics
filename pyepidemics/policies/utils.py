

import numpy as np


def sigmoid_response(t,start_date,start,end,duration,interval = 0.95):
    """Sigmoid response
    Normally formula is end + (start - end) / ( 1 + exp(-k(-t + inflection)))
    Here for more control, we replace k by two parameters to control duration for a shift of an intensity of an interval
    By reversing the formula we get k = 2/duration * log (interval/(1-interval))
    Inflection becomes simply start_date + duration/2
    """
    k = 2/duration * np.log(interval/(1 - interval))
    inflection = start_date + duration/2
    return (start-end) / (1 + np.exp(-k*(-t+inflection))) + end


def multiple_sigmoid_response(t,start,values,dates,durations = 4,interval = 0.95):

    duration = durations[0] if isinstance(durations,list) else durations

    yt = sigmoid_response(t,dates[0],start,values[0],duration,interval)

    for i in range(len(values[1:])):
        i = i+1
        duration = durations[i] if isinstance(durations,list) else durations
        yt += sigmoid_response(t,dates[i],0,values[i] - values[i-1],duration,interval)

    return yt


def piecewise_response(t,start,values,dates):
    all_dates = [0]+list(dates)
    all_values = [start]+list(values)
    intervals = [(all_dates[i],all_dates[i+1]) for i in range(len(all_dates) - 1)]
    for i in range(len(all_dates) - 1):
        if all_dates[i] <= t < all_dates[i+1]:
            return all_values[i]
    return all_values[-1]


def make_dynamic_fn(values,transition = 4,sigmoid = True):
    start,values = values[0],values[1:]

    if len(values[0]) == 2:

        values,dates = list(zip(*values))

    elif len(values[0]) == 3:
        values,dates,transition = list(zip(*values))
        transition = list(transition)

    else:
        raise Exception(f"Invalid values {values}")

    if sigmoid:
        return lambda t : multiple_sigmoid_response(t,start,values,dates,transition)
    else:
        return lambda t : piecewise_response(t,start,values,dates)




