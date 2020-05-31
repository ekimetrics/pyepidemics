

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


def multiple_sigmoid_response(t,start,values,dates,durations,interval = 0.95):

    duration = durations[0] if isinstance(durations,list) else durations

    yt = sigmoid_response(t,dates[0],start,values[0],duration,interval)

    for i in range(len(values[1:])):
        i = i+1
        duration = durations[i] if isinstance(durations,list) else durations
        yt += sigmoid_response(t,dates[i],0,values[i] - values[i-1],duration,interval)

    return yt




