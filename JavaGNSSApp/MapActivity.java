package com.example.gnssclient;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.res.ResourcesCompat;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.os.Environment;
import android.widget.ImageView;

import java.io.File;
import java.io.IOException;
import java.util.List;

public class MapActivity extends AppCompatActivity {
    private final File root = Environment.getExternalStorageDirectory();
    private final File dirPath = new File (root, "Documents/GNSSData");
    Drawable backgroundDrawable;
    GNSSData lastPos;
    long lastUpdate = System.currentTimeMillis();
    private String file = "MapActivity";
    private CSVFile csvFile = null;
    private double cLat, cLon, dLon, dLat;
    private CustomButton suburb, park, harbor, sdu, downtown, road;

    private void setActive(CustomButton button) {
        for (CustomButton b : new CustomButton[]{sdu, park, harbor, road, downtown, suburb}) b.setEnabled(false);
        if (button != null) button.setEnabled(true);
    }

    private void setArea(String area) {
        Util.print("Area: " + area, file);

        int drawableID;
        switch (area) {
            case "suburb":
                cLat = 55.3761308;
                cLon = 10.3860752;
                dLat = 55.37701122577254 - 55.37525035253972;
                dLon = 10.38768425070361 - 10.384466220745304;
                setActive(suburb);
                drawableID = R.drawable.map_suburb;
                break;

            case "harbor":
                cLat = 55.4083756;
                cLon = 10.3787729;
                dLat = 55.40925611115864 - 55.40749506713455;
                dLon = 10.380383112122665 - 10.377162759471311;
                setActive(harbor);
                drawableID = R.drawable.map_harbor;
                break;

            case "sdu":
                cLat = 55.3685818;
                cLon = 10.4317584;
                dLat = 55.369461621502516 - 55.36770195677667;
                dLon = 10.433368145371817 - 10.430148726037793;
                setActive(sdu);
                drawableID = R.drawable.map_sdu;
                break;

            case "downtown":
                cLat = 55.3947509;
                cLon = 10.3833619;
                dLat = 55.39563135509928 - 55.39387042320067;
                dLon = 10.384971654193262 - 10.381752217339194;
                setActive(downtown);
                drawableID = R.drawable.map_downtown;
                break;

            case "park":
                cLat = 55.3916561;
                cLon = 10.3828329;
                dLat = 55.39253656324151 - 55.39077561506136;
                dLon = 10.38444251564794 - 10.381223355870736;
                setActive(park);
                drawableID = R.drawable.map_park;
                break;

            case "road":
                cLat = 55.372005;
                cLon = 10.403568;
                dLat = 55.39253656324151 - 55.39077561506136;
                dLon = 10.38444251564794 - 10.381223355870736;
                setActive(road);
                drawableID = R.drawable.map_road;
                break;

            default:
                setActive(null);
                Util.print("default", file);
                drawableID = R.drawable.map_placeholder;
        }

        dLon = 2252.0 / dLon;
        dLat = 2252.0 / dLat;

        Util.print("x: " + dLon + ", y: " + dLat, file);

        backgroundDrawable = ResourcesCompat.getDrawable(getResources(), drawableID, null);
        updateImage();
    }

    private void updateImage() {
        Bitmap bitmap = Bitmap.createBitmap(backgroundDrawable.getIntrinsicWidth(), backgroundDrawable.getIntrinsicHeight(), Bitmap.Config.ARGB_8888);

        Canvas canvas = new Canvas(bitmap);
        backgroundDrawable.setBounds(0, 0, canvas.getWidth(), canvas.getHeight());
        backgroundDrawable.draw(canvas);

        Paint redPaint = new Paint();
        redPaint.setColor(Color.RED);
        redPaint.setStyle(Paint.Style.FILL_AND_STROKE);
        redPaint.setAntiAlias(true);

        Paint bluePaint = new Paint();
        bluePaint.setColor(Color.BLUE);
        bluePaint.setStyle(Paint.Style.FILL_AND_STROKE);
        bluePaint.setAntiAlias(true);

        Position pos;
        if (lastPos != null) {
            pos = new Position(lastPos.getLatitude(), lastPos.getLongitude());
            canvas.drawCircle((float)pos.x(), (float)pos.y(), 10, bluePaint);
        }

        try {
            List<String[]> rows = csvFile.readFile();

            for (String[] row : rows) {
                pos = new Position(Double.valueOf(row[1]), Double.valueOf(row[2]));
                canvas.drawCircle((float)pos.x(), (float)pos.y(), 7, redPaint);
            }
        } catch (Exception e) { Util.print(e.toString(), file); }

        ImageView map = findViewById(R.id.i_map);
        map.setImageBitmap(bitmap);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_map);

        try { csvFile = new CSVFile(dirPath, "data.csv"); }
        catch (IOException e) { Util.print(e.toString(), file); }

        int colorButtonDefault = ResourcesCompat.getColor(getResources(), R.color.DefaultButton, null);
        int colorButtonEnabled = ResourcesCompat.getColor(getResources(), R.color.ActiveButton, null);
        int colorButtonDisabled = ResourcesCompat.getColor(getResources(), R.color.InactiveButton, null);

        suburb = new CustomButton(findViewById(R.id.b_suburb), colorButtonDefault, colorButtonDisabled);
        suburb.setEnabled(false);
        suburb.setCallback(() -> setArea("suburb"));

        harbor = new CustomButton(findViewById(R.id.b_harbor), colorButtonDefault, colorButtonDisabled);
        harbor.setEnabled(false);
        harbor.setCallback(() -> setArea("harbor"));

        park = new CustomButton(findViewById(R.id.b_park), colorButtonDefault, colorButtonDisabled);
        park.setEnabled(false);
        park.setCallback(() -> setArea("park"));

        downtown = new CustomButton(findViewById(R.id.b_downtown), colorButtonDefault, colorButtonDisabled);
        downtown.setEnabled(false);
        downtown.setCallback(() -> setArea("downtown"));

        sdu = new CustomButton(findViewById(R.id.b_sdu), colorButtonDefault, colorButtonDisabled);
        sdu.setEnabled(false);
        sdu.setCallback(() -> setArea("sdu"));

        road = new CustomButton(findViewById(R.id.b_road), colorButtonDefault, colorButtonDisabled);
        road.setEnabled(false);
        road.setCallback(() -> setArea("road"));

        GNSSThread.registerGNSSDataCallback(new GNSSUpdate());

    }

    class GNSSUpdate implements GNSSDataCallback {
        @Override
        public void onGetData(GNSSData data) {
            if (data.getType().equals("$GPGGA"))
            {
                long receivedTime = System.currentTimeMillis();
                if (receivedTime - lastUpdate < 3500) return;
                lastPos = data;
                lastUpdate = receivedTime;
                updateImage();
            }
        }
    }

    class Position {
        private double lat, lon;

        Position(double lat, double lon) {
            this.lat = lat;
            this.lon = lon;
        }

        double y() { return (cLat - lat) * dLat + 1126; }
        double x() { return (lon - cLon) * dLon + 1126; }
    }
}