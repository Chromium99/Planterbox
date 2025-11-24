package com.example.myapplication;
import android.graphics.Bitmap;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
public class frontend {
    private static final String TAG = "ImageUploader";
    private static final String SERVER_URL =  "http://192.168.1.17:5000/upload"; // Change to your server IP

    private static final ExecutorService executorService = Executors.newSingleThreadExecutor();
    private static final Handler mainHandler = new Handler(Looper.getMainLooper());

    public interface UploadCallback {
        void onSuccess(JSONObject response);

        void onError(String error);
    }

    public static void uploadImage(Bitmap bitmap, UploadCallback callback) {
        executorService.execute(() -> {
            String[] result = uploadImageTask(bitmap); // Change to return array: [result, errorMessage]
            mainHandler.post(() -> {
                if (result[0] != null) {
                    try {
                        JSONObject jsonResponse = new JSONObject(result[0]);
                        if (callback != null) {
                            callback.onSuccess(jsonResponse);
                        }
                    } catch (Exception e) {
                        Log.e(TAG, "Error parsing JSON: " + e.getMessage());
                        if (callback != null) {
                            callback.onError("Error parsing response: " + e.getMessage());
                        }
                    }
                } else {
                    if (callback != null) {
                        callback.onError(result[1] != null ? result[1] : "Unknown error");
                    }
                }
            });
        });
    }

    private static String[] uploadImageTask(Bitmap bitmap) { // Return String array
        HttpURLConnection connection = null;
        String errorMessage = null;

        try {
            // Convert Bitmap to byte array
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            bitmap.compress(Bitmap.CompressFormat.JPEG, 90, outputStream);
            byte[] imageBytes = outputStream.toByteArray();

            // Create connection
            URL url = new URL(SERVER_URL);
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setDoOutput(true);
            connection.setDoInput(true);
            connection.setConnectTimeout(10000); // 10 seconds
            connection.setReadTimeout(10000); // 10 seconds
            connection.setRequestProperty("Content-Type", "image/jpeg");
            connection.setRequestProperty("Content-Length", String.valueOf(imageBytes.length));

            // Send image data
            OutputStream os = connection.getOutputStream();
            os.write(imageBytes);
            os.flush();
            os.close();

            // Get response
            int responseCode = connection.getResponseCode();
            Log.d(TAG, "Response Code: " + responseCode);

            if (responseCode == HttpURLConnection.HTTP_OK) {
                InputStream inputStream = connection.getInputStream();
                StringBuilder response = new StringBuilder();
                byte[] buffer = new byte[1024];
                int bytesRead;

                while ((bytesRead = inputStream.read(buffer)) != -1) {
                    response.append(new String(buffer, 0, bytesRead));
                }
                inputStream.close();

                return new String[]{response.toString(), null};
            } else {
                errorMessage = "Server returned error code: " + responseCode;
                return new String[]{null, errorMessage};
            }

        } catch (IOException e) {
            Log.e(TAG, "Error uploading image: " + e.getMessage());
            errorMessage = "Network error: " + e.getMessage();
            return new String[]{null, errorMessage};
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }
}