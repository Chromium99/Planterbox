package com.example.myapplication;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

public class ResponseActivity extends AppCompatActivity {

    public static final String EXTRA_RESPONSE_BODY = "extra_response_body";
    Button button;
    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_response);

        TextView textView = findViewById(R.id.text_response);
        String body = getIntent().getStringExtra(EXTRA_RESPONSE_BODY);
        if (body == null) {
            body = "No response received.";
        }
        textView.setText(body);
        button = findViewById(R.id.backButton);

        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(ResponseActivity.this, MainActivity.class);
                startActivity(intent);
            }
        });
    }
}
