import numpy as np
from parameters import STEERING_RATIO, VEHICLE_LENGTH



MPSTOMPH = 2.23694 # meters per second to miles per hour
MPHTOMPS = 1/MPSTOMPH
KPHTOMPS = 0.277778


def estimate(filename, data):
    estimate_output = np.ndarray(len(data), dtype=np.float)
    speed = data[SPEED_KEY]
    aligned_gyro = -data[ALIGN_KEY]
    r = speed / aligned_gyro
    tire_angle = np.arcsin(VEHICLE_LENGTH(filename) / r)
    steering_angle = STEERING_RATIO(filename) * tire_angle
    steering_angle *= 180 / np.pi
    steering_angle *= -1
    
    # Scaling and smoothing factor specific to each car
    scale_smooth = SCALE_SMOOTH[fname_to_activity(filename)]
    smooth_by = scale_smooth['smooth']
    window = np.full(smooth_by, 1.0 / smooth_by)
    steering_angle_adj = np.convolve(steering_angle, window, mode='same')
    steering_angle_adj *= scale_smooth['scale']
    estimate_output = steering_angle_adj.copy()

    return estimate_output