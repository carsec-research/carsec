public class AppImpl extends SensorListAppBase {
    final edu.umich.carlab.watchfon_speed.MiddlewareImpl watchfon_speed = new edu.umich.carlab.watchfon_speed.MiddlewareImpl();

    Interpreter tflite;

    // It's a 10-sized one-hot encoding
    float[][] labelProb = new float[1][10];
    float[][] inputBuffer = new float[5][1];
    Object runningPredictionLock = new Object();

    public AppImpl(CLDataProvider cl, Context context) {
        super(cl, context);
        String vehicleName = middleware.getParameterOrDefault(context, middleware.VEHICLE_NAME, "");

        try {
            // 1. Get model filename by taking MD5 hash
            String hex = new String(Hex.encodeHex(DigestUtils.md5(vehicleName)));
            String modelfilename = String.format("%s.jpg", hex);
            
            // 2. Load model file using tensorflow lite Interpreter
            AssetManager assetManager = context.getAssets();
            tflite = new Interpreter(loadModelFile(assetManager, modelfilename), null);
        } catch (Exception e) {
            Log.e(TAG, "Unable to find the model file");
        }
    }

    /**
     * Memory-map the model file in Assets.
     */
    private static MappedByteBuffer loadModelFile(AssetManager assets, String modelFilename)
            throws IOException {
        AssetFileDescriptor fileDescriptor = assets.openFd(modelFilename);
        FileInputStream inputStream = new FileInputStream(fileDescriptor.getFileDescriptor());
        FileChannel fileChannel = inputStream.getChannel();
        long startOffset = fileDescriptor.getStartOffset();
        long declaredLength = fileDescriptor.getDeclaredLength();
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength);
    }

    @Override
    public void newData(DataMarshal.DataObject dObject) {
        super.newData(dObject);
    
        if (tflite == null) {
            Log.e(TAG, "Tensor Flow Lite model not initialized");
            return;
        }

        synchronized (runningPredictionLock) {
            // Get the speed samples at the last [-4, -3, -2, -1, 0] seconds
            DataSample f1 = getDataAt(watchfon_speed.APP, watchfon_speed.SPEED, 4000L);
            DataSample f2 = getDataAt(watchfon_speed.APP, watchfon_speed.SPEED, 3000L);
            DataSample f3 = getDataAt(watchfon_speed.APP, watchfon_speed.SPEED, 2000L);
            DataSample f4 = getDataAt(watchfon_speed.APP, watchfon_speed.SPEED, 1000L);
            DataSample f5 = getDataAt(watchfon_speed.APP, watchfon_speed.SPEED, 0L);

            inputBuffer[0][0] = f1.value;
            inputBuffer[1][0] = f2.value;
            inputBuffer[2][0] = f3.value;
            inputBuffer[3][0] = f4.value;
            inputBuffer[4][0] = f5.value;

            // Use feature set to make prediction
            tflite.run(inputBuffer, labelProb);

            // Use reverse one-hot encoding to output the gear value
            float gearValue = oneHotDecode(labelProb);
            outputData(middleware.APP, middleware.GEAR, (float) gearValue);
        }
    }

    Integer oneHotDecode(float[][] labelProb) {
        float maxVal = labelProb[0][0];
        int maxIdx = 0;
        float val;

        for (int i = 1; i < labelProb[0].length; i++) {
            val = labelProb[0][i];
            if (val > maxVal) {
                maxVal = val;
                maxIdx = i;
            }
        }

        return maxIdx - 1;
    }
}
