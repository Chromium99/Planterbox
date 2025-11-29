package com.example.myapplication;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.URL;

import org.json.JSONObject;

public class ImageSenderServer {
    // For Android emulator use 10.0.2.2 to reach host machine; replace with your LAN IP on a device if needed.
    public static String PYTHON_SERVER_URL = "http://10.0.2.2:5000/process-image";
    private static final String BOUNDARY = "----WebKitFormBoundary" + System.currentTimeMillis();

    public static String sendImageToPythonServer(String imagePath) throws IOException {
        File imageFile = new File(imagePath);

        if (!imageFile.exists()) {
            throw new FileNotFoundException("Image file not found: " + imagePath);
        }

        URL url = new URL(PYTHON_SERVER_URL);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();

        // Set up connection for multipart/form-data
        connection.setDoOutput(true);
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "multipart/form-data; boundary=" + BOUNDARY);

        try (OutputStream output = connection.getOutputStream();
             PrintWriter writer = new PrintWriter(new OutputStreamWriter(output, "UTF-8"), true)) {

            // Write image file part
            writer.append("--").append(BOUNDARY).append("\r\n");
            writer.append("Content-Disposition: form-data; name=\"image\"; filename=\"")
                  .append(imageFile.getName()).append("\"\r\n");
            writer.append("Content-Type: image/jpeg\r\n\r\n");
            writer.flush();

            // Write image bytes (avoid java.nio.file for wider Android compatibility)
            try (InputStream inputStream = new FileInputStream(imageFile)) {
                byte[] buffer = new byte[8192];
                int bytesRead;
                while ((bytesRead = inputStream.read(buffer)) != -1) {
                    output.write(buffer, 0, bytesRead);
                }
            }
            output.flush();

            writer.append("\r\n");
            writer.append("--").append(BOUNDARY).append("--\r\n");
            writer.flush();
        }

        // Read response
        int responseCode = connection.getResponseCode();

        BufferedReader reader;
        if (responseCode >= 200 && responseCode < 300) {
            reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        } else {
            reader = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
        }

        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        reader.close();

        return response.toString();
    }

    public static void parseJsonResponse(String jsonString) {
        try {
            JSONObject json = new JSONObject(jsonString);

            String status = json.getString("status");
            String message = json.getString("message");

            System.out.println("\n=== Parsed Response ===");
            System.out.println("Status: " + status);
            System.out.println("Message: " + message);

            if (json.has("data")) {
                JSONObject data = json.getJSONObject("data");
                System.out.println("Filename: " + data.getString("filename"));
                System.out.println("Size: " + data.getInt("size_bytes") + " bytes");
                System.out.println("Received at: " + data.getString("received_at"));
                System.out.println("Saved path: " + data.getString("saved_path"));
            }

        } catch (Exception e) {
            System.err.println("Error parsing JSON: " + e.getMessage());
        }
    }
}
