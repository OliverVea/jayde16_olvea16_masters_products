package com.example.gnssclient;

import android.annotation.SuppressLint;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbDeviceConnection;
import android.hardware.usb.UsbManager;
import android.widget.TextView;

import androidx.cardview.widget.CardView;
import androidx.core.content.res.ResourcesCompat;

import com.hoho.android.usbserial.driver.UsbSerialDriver;
import com.hoho.android.usbserial.driver.UsbSerialPort;
import com.hoho.android.usbserial.driver.UsbSerialProber;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

interface ConnectionChangeCallback {
    void onChange(boolean newStatus);
}

interface GNSSDataCallback {
    void onGetData(GNSSData data);
}

public class GNSSThread extends Thread {
    public static GNSSData lastPos;

    private String file = "GNSSThread";

    UsbManager manager = null;
    UsbSerialDriver driver = null;
    UsbDevice device = null;
    UsbDeviceConnection connection = null;
    UsbSerialPort port = null;

    boolean connected = false;

    public GNSSThread() {
        Util.print("1 1 GNSS listener thread created.", file);
    }

    public boolean connect(Context context) {
        try {
            if (port != null) port.close();
        } catch (IOException e) {

        }
        setConnected(false);

        manager = (UsbManager)context.getSystemService(Context.USB_SERVICE);
        List<UsbSerialDriver> availableDrivers = UsbSerialProber.getDefaultProber().findAllDrivers(manager);

        if (availableDrivers.isEmpty()) {
            Util.print("No devices found.", file);
            return false;
        }

        Util.print("Found " + availableDrivers.size() + " devices.", file);

        driver = null;
        final int productId = 24577; //The product ID of the serial chip in the GNSS

        for (UsbSerialDriver d : availableDrivers) {
            if (d.getDevice().getProductId() == productId) {
                driver = d;
                Util.print("Driver " + d.toString() + " product id matches " + productId + ".", file);
            }
        }

        if (driver == null) {
            Util.print("No valid driver found.", file);
            return false;
        }

        device = driver.getDevice();

        if (!manager.hasPermission(device)) {
            Util.print("Requesting permission.", file);
            String ACTION_USB_PERMISSION = "com.android.example.USB_PERMISSION";
            PendingIntent permissionIntent = PendingIntent.getBroadcast(context, 0, new Intent(ACTION_USB_PERMISSION), 0);
            manager.requestPermission(device, permissionIntent);

            int t = 0;
            while(!manager.hasPermission(device) && t < 10000) {
                int sleepTime = 10;
                try {
                    sleep(sleepTime);
                }
                catch (Exception ignored) {

                }
                t += sleepTime;
            }
        }

        if (!manager.hasPermission(device)) {
            Util.print("Could not acquire permission.", file);
            return false;
        }

        Util.print("Permission acquired. Opening device.", file);
        connection = manager.openDevice(device);

        if (connection == null) {
            Util.print("No valid connection found.", file);
            return false;
        }

        List<UsbSerialPort> ports = driver.getPorts();

        if (ports.isEmpty()) {
            Util.print("No valid port in UsbSerialDriver.", file);
            return false;
        }

        Util.print("" + ports.size() + " ports found. Using the first one.", file);

        port = driver.getPorts().get(0);

        try {
            port.open(connection);
            port.setParameters(115200, 8, UsbSerialPort.STOPBITS_1, UsbSerialPort.PARITY_NONE);
        } catch (IOException e) {
            Util.print("Could not connect through port.", file);
            return false;
        }

        Util.print("Connected through port.", file);

        setConnected(true);

        return true;
    }

    static private List<ConnectionChangeCallback> connectionChangeCallbacks = new ArrayList<>();
    static public void registerConnectionChangeCallback(ConnectionChangeCallback cb) {
        connectionChangeCallbacks.add(cb);
    }

    private void setConnected(boolean connected) {
        if (this.connected == connected) return;
        this.connected = connected;

        for (ConnectionChangeCallback cb : connectionChangeCallbacks) cb.onChange(connected);
    }

    static private List<GNSSDataCallback> dataCallbacks = new ArrayList<>();
    static public void registerGNSSDataCallback(GNSSDataCallback c) {
        dataCallbacks.add(c);
    }

    private void onGNSSDataUpdate(GNSSData data) {
        for (GNSSDataCallback cb : dataCallbacks) {
            if (cb != null) cb.onGetData(data);
        }
    }

    public void run() {
        try {
            Util.print("Setting up for communication.", file);

            String partialMessage = "";
            final int bufferLength = 1024;
            byte[] byteBuffer = new byte[bufferLength];

            setConnected(true);
            while (connected) {
                try {
                    int nBytes = port.read(byteBuffer, 0);

                    partialMessage += new String(byteBuffer, 0, nBytes, StandardCharsets.UTF_8);

                    int messageStart = 0;
                    for (int i = 0; i < partialMessage.length() - 1; i++) {
                        String subS = partialMessage.substring(i, i + 2);
                        if (subS.equals("\r\n")) {
                            String message = partialMessage.substring(messageStart, i);
                            GNSSData data = new GNSSData(message);
                            onGNSSDataUpdate(data);
                            messageStart = i + 2;
                        }

                        if (partialMessage.toCharArray()[i] == '$') messageStart = i;
                    }

                    if (messageStart == partialMessage.length()) partialMessage = "";
                    else partialMessage = partialMessage.substring(messageStart);

                } catch (IOException e) {
                    Util.print("Connection error " + e + ".", file);
                    setConnected(false);
                }
            }
        } catch (Exception e) {
            Util.print("Something went wrong. See exception: " + e.toString(), file);
            setConnected(false);
        }
    }
}

