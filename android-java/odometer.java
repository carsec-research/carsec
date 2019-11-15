public class AppImpl extends SensorListAppBase {
    Map<String, Float> lastValues = null;
    Location lastLoc, currLoc;

    // Distance in meters
    Double distance = 0d;

    public AppImpl(CLDataProvider cl, Context context) {
        super(cl, context);
        lastLoc = new Location("");
        currLoc = new Location("");
        distance = loadValue(DISTANCE_KEY, 0d);
    }

    @Override
    public void newData(DataMarshal.DataObject dObject) {
        super.newData(dObject);
        if (lastValues != null) {
            lastLoc.setLatitude(lastValues.get(PhoneSensors.GPS_LATITUDE));
            lastLoc.setLongitude(lastValues.get(PhoneSensors.GPS_LONGITUDE));
            currLoc.setLatitude(values.get(PhoneSensors.GPS_LATITUDE));
            currLoc.setLongitude(values.get(PhoneSensors.GPS_LONGITUDE));
            distance += currLoc.distanceTo(lastLoc);
            outputData(
                    MiddlewareImpl.APP,
                    dObject,
                    MiddlewareImpl.DISTANCE,
                    distance.floatValue()
            );

        }
        lastValues = values;
    }
}
