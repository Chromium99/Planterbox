package com.example.myapplication;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import androidx.activity.result.ActivityResult;
import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity {


    private static final String TAG = "takePicture";
    private static final int CAMERA_PERMISSION_CODE = 100;
    private ImageView imageView;
    private Button btnCamera;
    private ActivityResultLauncher<Intent> cameraLauncher;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Log.d(TAG, "========== onCreate called ==========");

        imageView = findViewById(R.id.imageView);
        btnCamera = findViewById(R.id.btn_camera);

        // Set up button click listener
        btnCamera.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "========== BUTTON CLICKED ==========");
                Toast.makeText(MainActivity.this, "Button clicked! Opening camera...", Toast.LENGTH_LONG).show();
                takePhoto();
            }
        });

        // Initialize the ActivityResultLauncher
        cameraLauncher = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                new ActivityResultCallback<ActivityResult>() {
                    @Override
                    public void onActivityResult(ActivityResult result) {
                        if (result.getResultCode() == RESULT_OK) {
                            Log.i(TAG, "onActivityResult: RESULT OK");
                            Intent data = result.getData();
                            if (data != null && data.getExtras() != null) {
                                Bitmap bitmap = (Bitmap) data.getExtras().get("data");
                                imageView.setImageBitmap(bitmap);
                                Toast.makeText(MainActivity.this, "Photo captured!", Toast.LENGTH_SHORT).show();

                                // Send image to backend
                                sendImageToBackend(bitmap);
                            }
                        } else if (result.getResultCode() == RESULT_CANCELED) {
                            Log.i(TAG, "onActivityResult: RESULT CANCELED");
                            Toast.makeText(MainActivity.this, "Photo cancelled", Toast.LENGTH_SHORT).show();
                        }
                    }
                }
        );

        // Request camera permission on startup
        checkCameraPermission();
    }

    private void checkCameraPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED) {
            Log.d(TAG, "Requesting camera permission...");
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.CAMERA},
                    CAMERA_PERMISSION_CODE);
        } else {
            Log.d(TAG, "Camera permission already granted");
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == CAMERA_PERMISSION_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Log.d(TAG, "Camera permission GRANTED by user");
                Toast.makeText(this, "Camera permission granted", Toast.LENGTH_SHORT).show();
            } else {
                Log.d(TAG, "Camera permission DENIED by user");
                Toast.makeText(this, "Camera permission denied", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void takePhoto() {
        Log.d(TAG, "takePhoto() method called");

        // Check if camera permission is granted
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED) {
            Log.d(TAG, "Camera permission NOT granted");
            Toast.makeText(this, "Camera permission required! Please allow.", Toast.LENGTH_LONG).show();
            checkCameraPermission();
            return;
        }

        Log.d(TAG, "Camera permission granted, launching camera...");
        Toast.makeText(this, "Opening camera...", Toast.LENGTH_SHORT).show();

        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);

        // Try to launch camera even if resolveActivity returns null
        try {
            Log.d(TAG, "Attempting to launch camera...");
            cameraLauncher.launch(intent);
        } catch (Exception e) {
            Log.e(TAG, "Error launching camera: " + e.getMessage());
            Toast.makeText(this, "Error: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void sendImageToBackend(Bitmap bitmap) {
        Toast.makeText(this, "Uploading image...", Toast.LENGTH_SHORT).show();

        frontend.uploadImage(bitmap, new frontend.UploadCallback() {
            @Override
            public void onSuccess(org.json.JSONObject response) {
                runOnUiThread(() -> {
                    try {
                        Log.d(TAG, "Response from server: " + response.toString());
                        Toast.makeText(MainActivity.this,
                                "Success! Response: " + response.toString(),
                                Toast.LENGTH_LONG).show();
                    } catch (Exception e) {
                        Log.e(TAG, "Error handling response: " + e.getMessage());
                    }
                });
            }

            @Override
            public void onError(String error) {
                runOnUiThread(() -> {
                    Log.e(TAG, "Upload error: " + error);
                    Toast.makeText(MainActivity.this, "Upload failed: " + error, Toast.LENGTH_LONG).show();
                });
            }
        });
    }
}