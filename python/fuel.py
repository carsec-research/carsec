import numpy as np
from parameters import MAX_TANK_CAPACITY, AVERAGE_MPG

GALLONS_PER_LITER = 0.26417217685
MILE_PER_KM = 0.621371
EPSILON = 1e-5

Previous_Fuel = None

def estimate(filename, data):
    estimate_output = np.ndarray(len(data), dtype=np.float)
    
    for idx in range(len(data)):
        row = data[idx]
        
        first_row = (idx == 0) or \
                    np.isnan(data[idx-1][GROUNDTRUTH_KEY]) or \
                    np.isnan(data[idx-1][ESTIMATE_ODO_KEY])
        
        if first_row:
            Previous_Fuel = row[GROUNDTRUTH_KEY]
            estimate_output[idx] = row[GROUNDTRUTH_KEY]
        else:
            prev_row = data[idx-1]
            odo_delta = row[ESTIMATE_ODO_KEY] - prev_row[ESTIMATE_ODO_KEY]
            odo_delta *= MILE_PER_KM
            this_gallons = odo_delta / AVERAGE_MPG(filename)

            estimate = Previous_Fuel
            estimate -= (this_gallons / GALLONS_PER_LITER)
            Previous_Fuel = estimate
            estimate_output[idx] = estimate

    return estimate_output