import numpy as np

def norm (A):
    return A / np.linalg.norm(A)

def mmul(M, A):
    return np.array([
        A[0] * M[0, 0] + A[1] * M[0, 1] + A[2] * M[0, 2], 
        A[0] * M[1, 0] + A[1] * M[1, 1] + A[2] * M[1, 2], 
        A[0] * M[2, 0] + A[1] * M[2, 1] + A[2] * M[2, 2], 
            ])

def cross (A, B):
    cross = [
        A[1] * B[2] - A[2] * B[1],
        A[2] * B[0] - A[0] * B[2],
        A[0] * B[1] - A[1] * B[0] ]
    cross = np.array(cross)
    return cross


def calc_gps_delta (data, noiselevel_in_meters=0):
    import numpy.random as nr
    from haversine import haversine, Unit
    
    noiselevel_in_km = noiselevel_in_meters / 1000
    noise_array = (nr.rand(len(data)) - 0.5) * noiselevel_in_km

    lat = data['phone_gps_latitude']
    lng = data['phone_gps_longitude']
    _delta_speed = np.full(len(data), np.nan)
    for idx in range(1, len(_delta_speed)):
        distance_in_km = haversine(
                (lat[idx-1], lng[idx-1]),
                (lat[idx], lng[idx]),
                unit=Unit.KILOMETERS)
        
        distance_in_km += noise_array[idx]
        time_elapsed_in_ms = 100.0
        time_elapsed_in_hr = time_elapsed_in_ms / 1000.0 / 60.0 / 60.0
        _delta_speed[idx] = distance_in_km / time_elapsed_in_hr
        
    return _delta_speed




# COMPLEMENTARY FILTER:
# Basic equation: v = a * (v + acc * dt) + (1-a) * gps_speed
def complementary_filter(accel_mpss, gps_mps, alpha):
    dt = 0.1 # 100 ms
    
    v = np.full(len(gps_mps), np.nan)
    
    for i in range(len(v)):
        a = accel_mpss[i]
        g = gps_mps[i]
        
        if i == 0:
            if ~np.isnan(g):
                v[i] = g
        elif np.isnan(v[i-1]):
            if ~np.isnan(g):
                v[i] = g     
        elif ~np.isnan(a) and ~np.isnan(g):
            v[i] = alpha * (v[i-1] + a * dt) + (1-alpha) * g
        elif np.isnan(a) and ~np.isnan(g):
            v[i] = alpha * v[i-1] + (1-alpha) * g
        elif ~np.isnan(a) and np.isnan(g):
            v[i] = v[i-1] + a * dt # no contribution from g
        else:
            v[i] = v[i-1]
    
    return v



def get_rotation_matrix (Facing_Down, Facing_North):
    C = cross(Facing_North, Facing_Down)
    Facing_Down_normed = norm(Facing_Down)
    cross_normed = norm(C)
    reconstr_Facing_North = cross(Facing_Down_normed, cross_normed)
    rotation_matrix = np.array([
            cross_normed,
            reconstr_Facing_North,
            Facing_Down_normed,
    ])
    return rotation_matrix



def get_vehicle_pointing_direction (data):
    # N x 3 vectors
    magnet_vector = np.array(data[Magnet].tolist())
    gravity_vector = np.array(data[Gravity].tolist())
    lat = data['phone_gps_latitude']
    lng = data['phone_gps_longitude']

    bearing_vec = np.ndarray(shape=(len(lat), 2))
    END = len(data)-1
    for i in range(len(data)):
        p0 = np.array([lng[i], lat[i]])
        p1 = np.array([lng[min(END, i+SKIP_AHEAD)], lat[min(END, i+SKIP_AHEAD)]])
        bearing_vec[i, :] = norm(p1-p0)
    
    # rotate magnet vector around gravity
    vehicle_pointing = np.ndarray(shape=magnet_vector.shape)
    centroid_gravity = np.nanmean(gravity_vector, axis=0)

    for i in range(len(data)):
        M = norm(magnet_vector[i, :])
        G = norm(centroid_gravity)
        C = norm(np.cross(M, G))
        Mf = np.cross(G, C)
        transformation_matrix = np.array([C, Mf, G]).T

        in_world_frame = np.array([
            bearing_vec[i, 0],
            bearing_vec[i, 1],
            0])
        in_phone_frame = mmul(transformation_matrix, in_world_frame)
        vehicle_pointing[i, :] = in_phone_frame

    return vehicle_pointing



def get_vehicle_aligned_acceleration (data, vehicle_pointing):
    gravity_vector = np.array(data[Gravity].tolist()) # N x 3 vector
    unaligned_accel = np.array(data[PhoneAccel].tolist()) - gravity_vector
    centroid_g = np.nanmean(gravity_vector, axis=0)
    aligned_accel = np.ndarray(shape=unaligned_accel.shape)
    for i in range(len(data)):
        rotmat = get_rotation_matrix(
            centroid_gravity,
            vehicle_pointing[i, :])
        aligned_accel[i, :] = mmul(rotmat, unaligned_accel[i, :])
    
    return aligned_accel
    


def estimate(data):
    vehicle_pointing = get_vehicle_pointing_direction(data)
    aligned_accel = get_vehicle_aligned_acceleration(data, vehicle_pointing)
    gps_delta_kmph = calc_gps_delta(data)
        
    smoothed_gps_delta_kmph = smooth(gps_delta_kmph, smooth_factor=30) 
    gps_delta_mps = gps_delta_kmph / 3.6
    aligned_y_mpss = aligned_accel[:, 1].copy()
    estimate_speed_mps = complementary_filter(
        aligned_y_mpss, 
        gps_delta_mps, 
        alpha=alpha)
    
    return estimate_speed_mps
    