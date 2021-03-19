package com.example.gnssclient;

import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;
import androidx.core.app.ActivityCompat;
import androidx.core.content.res.ResourcesCompat;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbDeviceConnection;
import android.hardware.usb.UsbManager;
import android.os.Bundle;
import android.os.Environment;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.widget.TextView;

import com.hoho.android.usbserial.driver.*;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    private final String file = "Main";

    private final File root = Environment.getExternalStorageDirectory();
    private final File dirPath = new File (root, "Documents/GNSSData");

    public GNSSData lastPos;
    public GNSSFeature activeFeature = null;

    private GNSSThread gnssThread;
    private CSVFile csvFile = null;

    private CustomButton camera, measure, add, map;
    CustomCamera customCamera  = new CustomCamera(this, new File(dirPath, "Images"));
    private final CustomAudioPlayer audioPlayer = new CustomAudioPlayer();

    private int nImages = 0;

    private long lastUpdate = -1;
    private final CircularQueue freqQueue = new CircularQueue(20);

    public void clearUI() {
        runOnUiThread(() -> {
            ((TextView) findViewById(R.id.t_lat)).setText("");
            ((TextView) findViewById(R.id.t_lon)).setText("");
            ((TextView) findViewById(R.id.t_frequency)).setText("");
            ((TextView) findViewById(R.id.t_fix)).setText("");

            int offColor = ResourcesCompat.getColor(getResources(), R.color.ConnectionOff, null);
            ((CardView)findViewById(R.id.fixstatuscard)).setCardBackgroundColor(offColor);
        });
    }

    private void vibrate(int amplitude, int milliseconds) {
        Vibrator vib = (Vibrator)this.getSystemService(VIBRATOR_SERVICE);
        VibrationEffect effect = VibrationEffect.createOneShot(milliseconds, amplitude);
        vib.vibrate(effect);
    }

    private void loadCSV() {
        if (csvFile == null) {
            try {
                Util.print("Creating new file at: " + dirPath + "/data.csv", file);
                csvFile = new CSVFile(dirPath, "data.csv");
                Util.print("File created successfully.", file);
            } catch (IOException e) {
                Util.print(e.toString(), file);
            }
        }
    }

    public int addFeature(GNSSFeature feature) {
        try {
            if (feature != null) {
                    csvFile.deleteFeature(feature.getFeatureId());
                    csvFile.addFeature(feature);
            }
            return csvFile.getMaxId() + 1;
        } catch (IOException e) { Util.print(e.toString(), file); }
        return -1;
    }

    public void freshActiveFeature() {
        try {
            activeFeature = new GNSSFeature(csvFile.getMaxId() + 1);
        }
        catch (IOException e) {
            activeFeature = new GNSSFeature(0);
        }
    }

    public void addMeasurement(GNSSData data) {
        if (activeFeature == null) freshActiveFeature();

        activeFeature.addData(data);
        int nextID = addFeature(activeFeature);

        if (!add.getEnabled()) activeFeature = new GNSSFeature(nextID);
        else add.setEnabled(false);

        audioPlayer.play(this, R.raw.single_high);
        vibrate(255, 40);
    }

    class UIUpdate implements ConnectionChangeCallback {
        @Override
        public void onChange(boolean newStatus) {
            if (!newStatus) {
                freqQueue.clear();
                clearUI();
            }

            CardView connectCard = findViewById(R.id.connection_card);
            CardView bar = findViewById(R.id.connectionstatuscard);
            TextView connection = findViewById(R.id.t_connection);

            int color;
            if (newStatus) color = ResourcesCompat.getColor(getResources(), R.color.ConnectionOn, null);
            else color = ResourcesCompat.getColor(getResources(), R.color.ConnectionOff, null);

            String text;
            if (newStatus) text = "Connected";
            else text = "Not Connected";

            runOnUiThread(() -> {
                connectCard.setClickable(!newStatus);
                bar.setCardBackgroundColor(color);
                connection.setText(text);
            });

            if (newStatus) audioPlayer.play(getApplicationContext(), R.raw.ascending_3);
            else audioPlayer.play(getApplicationContext(), R.raw.descending_3);
        }
    }

    class GNSSDataUpdate implements GNSSDataCallback {
        @Override
        public void onGetData(GNSSData data) {
            if (data.getType().equals("$GPGGA")) {
                if (!(lastPos == null) && lastPos.getFix().equals("4") && !data.getFix().equals("4"))
                    audioPlayer.play(getApplicationContext(), R.raw.double_low);
                if ((lastPos == null || !lastPos.getFix().equals("4")) && data.getFix().equals("4"))
                    audioPlayer.play(getApplicationContext(), R.raw.double_high);

                lastPos = data;
                long receivedAt = System.currentTimeMillis();
                runOnUiThread(() -> {
                    if (data.isValid()) {
                        ((TextView) findViewById(R.id.t_lat)).setText(String.valueOf(data.getLatitude()));
                        ((TextView) findViewById(R.id.t_lon)).setText(String.valueOf(data.getLongitude()));
                        ((TextView) findViewById(R.id.t_fix)).setText(String.valueOf(data.getFix()));

                        int color;
                        if (data.getFix().equals("4"))
                            color = ResourcesCompat.getColor(getResources(), R.color.ConnectionOn, null);
                        else if (data.getFix().equals("5"))
                            color = ResourcesCompat.getColor(getResources(), R.color.ConnectionMeh, null);
                        else
                            color = ResourcesCompat.getColor(getResources(), R.color.ConnectionOff, null);

                        ((CardView) findViewById(R.id.fixstatuscard)).setCardBackgroundColor(color);

                        if (lastUpdate != -1) {
                            ((TextView) findViewById(R.id.t_frequency)).setText(freqQueue.average() + " Hz");
                            double freq = 1000.0 / (double) (receivedAt - lastUpdate);
                            freqQueue.push(freq);
                        }
                        lastUpdate = receivedAt;
                    }
                });
            }
        }
    }

    public void connect() {
        gnssThread = new GNSSThread();

        GNSSThread.registerConnectionChangeCallback(new UIUpdate());
        GNSSThread.registerGNSSDataCallback(new GNSSDataUpdate());

        gnssThread.connect(this);
        gnssThread.start();

        Util.print("Listener thread started successfully.", file);
    }

    @SuppressLint("DefaultLocale")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_main);

        findViewById(R.id.connection_card).setOnClickListener(v -> connect());

        int colorButtonDefault = ResourcesCompat.getColor(getResources(), R.color.DefaultButton, null);
        int colorButtonEnabled = ResourcesCompat.getColor(getResources(), R.color.ActiveButton, null);
        int colorButtonDisabled = ResourcesCompat.getColor(getResources(), R.color.InactiveButton, null);

        Activity activity = this;
        measure = new CustomButton(findViewById(R.id.b_measure), colorButtonDefault, colorButtonDisabled);
        measure.setCallback(() -> {
            if (lastPos == null || !lastPos.isValid()) return;
            if (lastPos.getFix().equals("4")) addMeasurement(lastPos);
            else {
                CustomAlertDialog dialog = new CustomAlertDialog(activity,
                        "Suboptimal measurement.",
                        "Are your sure you want to take measurement with fix " + lastPos.getFix() + "?",
                        () -> addMeasurement(lastPos),
                        () -> {});
                dialog.show();
            }
        });

        add = new CustomButton(findViewById(R.id.b_add), colorButtonDefault, colorButtonDisabled);
        add.setEnabled(false);
        add.setCallback(() -> add.setEnabled(!add.getEnabled()));

        camera = new CustomButton(findViewById(R.id.b_camera), colorButtonDefault, colorButtonDisabled);
        camera.setCallback(() -> {
            if (activeFeature != null) {
                customCamera.captureImage("" + String.format("%04d", activeFeature.getFeatureId()) + "_" + activeFeature.getImageAmount() + ".jpg");
                activeFeature.setImageAmount(activeFeature.getImageAmount() + 1);
            }
        });

        map = new CustomButton(findViewById(R.id.b_map), colorButtonDefault, colorButtonDisabled);
        map.setCallback(() -> {
            Intent intent = new Intent(this, MapActivity.class);
            startActivity(intent);
        });

        loadCSV();
        try {
            ((TextView)findViewById(R.id.t_id)).setText(String.valueOf(csvFile.getMaxId() + 1));
            activeFeature = new GNSSFeature(csvFile.getMaxId() + 1);
        } catch (IOException e) {
            Util.print(e.toString(), file);
        }
    }
}