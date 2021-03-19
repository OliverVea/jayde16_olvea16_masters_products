package com.example.gnssclient;

import android.app.Activity;

import androidx.appcompat.app.AlertDialog;

public class CustomAlertDialog {
    private AlertDialog dialog;

    CustomAlertDialog(Activity activity, String title, String message, Runnable positiveCallback, Runnable negativeCallback) {
        AlertDialog.Builder builder = new AlertDialog.Builder(activity);
        builder.setMessage(message).setTitle(title);
        builder.setPositiveButton("Yes", (dialog1, id) -> positiveCallback.run());
        builder.setNegativeButton("No", (dialog1, id) -> negativeCallback.run());
        dialog = builder.create();
    }

    void show() {
        dialog.show();
    }
}
