import numpy as np
from parameters import GEAR_RATIOS, TIRE_CIRCUMFERENCE, FINAL_DRIVE_RATIO 

def estimate(filename, data):
    estimate_output  = np.ndarray(len(data), dtype=np.float)

    for idx in range(len(data)):
        row = data[idx]
        _speed = row[SPEED_KEY]
        _gear = row[GEAR_KEY]

        if _gear not in GEAR_RATIOS(filename): 
            estimate_output[idx] = np.nan

        # rpm = v * (final-drive-ratio * transmission-gear-ratio) / tire_circumference
        _gear_ratio = GEAR_RATIOS(filename)[_gear]
        _estimate = _speed * (FINAL_DRIVE_RATIO(filename, _gear) * _gear_ratio) / TIRE_CIRCUMFERENCE(filename)
        _estimate /= 60 # from RPH to RPM
        
        # per-vehicle configuration
        _scale_idle = SCALE_IDLE_RPM[fname_to_vehicle(filename)]
        _estimate *= _scale_idle['scale']
        estimate_output[idx] =  max(_estimate, _scale_idle['idle'])
    
    return estimate_output

