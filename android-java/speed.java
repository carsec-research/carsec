public class AppImpl extends SensorListAppBase {
    final float MPS_TO_KMPH = 1 / 0.621371f;

    public AppImpl(CLDataProvider cl, Context context) {
        super(cl, context);
        name = "watchfon_speed";
        middlewareName = MiddlewareImpl.APP;
        subscribe(PhoneSensors.DEVICE, PhoneSensors.GPS);
    }
    
    @Override
    public void newData(DataMarshal.DataObject dObject) {
        super.newData(dObject);

        Map<String, Float> gpsSplit = PhoneSensors.splitValues(dObject);
        Float speed = gpsSplit.get(PhoneSensors.GPS_SPEED) * MPS_TO_KMPH;
        outputData(MiddlewareImpl.APP, dObject, MiddlewareImpl.SPEED, speed);
    }
}
