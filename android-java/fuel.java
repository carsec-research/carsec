public class AppImpl extends App {
    final Double MILE_PER_KM = 0.621371;
    final Double GALLONS_PER_LITER = 0.26417217685;
    final edu.umich.carlab.watchfon_odometer.MiddlewareImpl watchfon_odometer = new edu.umich.carlab.watchfon_odometer.MiddlewareImpl();
    
    // Parameters
    Float AVERAGE_MPG = 23f;
    Float MAX_FUEL_CAPACITY = 18f;
    MiddlewareImpl middleware = new MiddlewareImpl();

    Double previousFuelLevel; // in liters
    Double lastOdometer, currOdometer;
    Double distance, fuelConsumed;

    public AppImpl(CLDataProvider cl, Context context) {
        super(cl, context);

        previousFuelLevel = loadValue(FUEL_KEY, (double) MAX_FUEL_CAPACITY);
        AVERAGE_MPG = middleware.getParameterOrDefault(context, middleware.AVERAGE_MPG, AVERAGE_MPG);
        MAX_FUEL_CAPACITY = middleware.getParameterOrDefault(
                context,
                middleware.MAX_FUEL_CAPACITY,
                MAX_FUEL_CAPACITY);
    }

    @Override
    public void newData(DataMarshal.DataObject dObject) {
        super.newData(dObject);
    
        currOdometer = dObject.value[0].doubleValue();
        if (lastOdometer != null) {
            distance = currOdometer - lastOdometer; // in meters
            distance = distance / 1000 * MILE_PER_KM; // in miles;
            fuelConsumed = distance / AVERAGE_MPG / GALLONS_PER_LITER; // in gallons
            previousFuelLevel -= fuelConsumed;
            outputData(MiddlewareImpl.APP, dObject, MiddlewareImpl.FUEL, previousFuelLevel.floatValue());
        }
    }
}
