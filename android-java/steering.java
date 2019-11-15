public class AppImpl extends SensorListAppBase {
    final double INCHES_TO_METERS = 0.0254;
    final edu.umich.carlab.world_aligned_imu.MiddlewareImpl world_aligned_imu = new edu.umich.carlab.world_aligned_imu.MiddlewareImpl();
    final edu.umich.carlab.watchfon_speed.MiddlewareImpl watchfon_speed = new edu.umich.carlab.watchfon_speed.MiddlewareImpl();

    // Parameters
    float STEERING_RATIO = 14.8f;
    float VEHICLE_LENGTH = (float) (193.9 * INCHES_TO_METERS); // Finally in meters
    Float lastSpeed = null;
    Float lastYaw = null;

    public AppImpl(CLDataProvider cl, Context context) {
        super(cl, context);
        STEERING_RATIO = middleware.getParameterOrDefault(context, MiddlewareImpl.STEERING_RATIO, STEERING_RATIO);
        VEHICLE_LENGTH = middleware.getParameterOrDefault(context, MiddlewareImpl.VEHICLE_LENGTH, VEHICLE_LENGTH);
    }

    @Override
    public void newData(DataMarshal.DataObject dObject) {
        super.newData(dObject);

        if (lastSpeed != null && lastYaw != null) {
            Double steering = (double) (lastSpeed / lastYaw);
            steering = Math.asin(VEHICLE_LENGTH / steering);
            steering = STEERING_RATIO * steering;
            steering *= 180 / Math.PI;
            outputData(
                    MiddlewareImpl.APP,
                    dObject,
                    MiddlewareImpl.STEERING,
                    steering.floatValue()
            );
        }
    }
}
