import numpy as np
import tensorflow as tf


def extract_features(data, feature_map, skip_nan=True):
    """
    feature map is a list which specifies how to extract features from data
    each entry of feature map is a tuple:
        ( sensorname, [negative indices offset] )
        e.g. feature_map could be:
            (ESTIMATORS[SPEED], [-40, -30, -20, -10, 0]),
    """
    
    num_indices = [len(ind) for _, ind in feature_map]
    extracted = np.full((len(data), sum(num_indices)), np.nan)
    
    for row_idx in range(len(data)):
        column_offset = 0
        for feature_name, time_offsets in feature_map:
            assert feature_name in data.dtype.names, 'Feature not not found in data'
            for t in time_offsets:
                _i = row_idx+t
                if _i >= 0 and _i < len(data):
                    extracted[row_idx, column_offset] = data[feature_name][_i]
                column_offset += 1
    
    if skip_nan:
        has_nan_mask = np.isnan(extracted).any(axis=1)
        return extracted[~has_nan_mask]
        
    # else
    return extracted


def one_hot_decode (encoded_values):
    gear_values = np.full((len(encoded_values), 1), np.nan)
    for idx, row in enumerate(encoded_values):
        gear_values[idx] = np.argmax(row) - 1
    return gear_values


def estimate(filename, data):
    vehicle = fname_to_vehicle(filename)
    feature_spec = FEATURE_SPECS[vehicle]
    features = extract_features(data, feature_spec, skip_nan=False)
    
    model_filename = vehicle_to_model(vehicle)
    model = tf.keras.models.load_model(model_filename)
    one_hot_predictions = model.predict(features)
    estimations = one_hot_decode(one_hot_predictions)
    return estimations
