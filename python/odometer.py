from haversine import haversine
    
import numpy as np

Previous_Odometer = None

def estimate(data):
    estimate_output = np.ndarray(len(data), dtype=np.float)
    
    for idx in range(len(data)):
        row = data[idx]

        first_row = (idx == 0) or \
                    np.isnan(data[idx-1][GPS_LAT_KEY]) or \
                    np.isnan(data[idx-1][GPS_LNG_KEY]) or \
                    np.isnan(data[idx-1][ODOMETER_KEY]) or \
                    Previous_Odometer is None

        if first_row:
            Previous_Odometer = row[ODOMETER_KEY]
            estimate_output[idx] = row[ODOMETER_KEY]
        else:
            prev_row = data[idx-1]
            prev_coord = (prev_row[GPS_LAT_KEY], prev_row[GPS_LNG_KEY])
            curr_coord = (row[GPS_LAT_KEY], row[GPS_LNG_KEY])
            distance = haversine(prev_coord, curr_coord)
            
            estimate = Previous_Odometer + distance
            Previous_Odometer = estimate
            estimate_output[idx] = estimate
    
    return estimate_output