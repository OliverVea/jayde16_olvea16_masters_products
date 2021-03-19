package com.example.gnssclient;

import android.view.View;

import androidx.core.content.res.ResourcesCompat;

public class CustomButton {
    private View buttonView;

    private boolean enabled = true;

    private int enabledColor, disabledColor;

    CustomButton(View buttonView, int enabledColor, int disabledColor) {
        this.buttonView = buttonView;
        this.enabledColor = enabledColor;
        this.disabledColor = disabledColor;
    }

    boolean getEnabled() {
        return enabled;
    }

    void setEnabled(boolean state) {
        enabled = state;
        if (state) buttonView.setBackgroundColor(enabledColor);
        else buttonView.setBackgroundColor(disabledColor);
    }

    void setCallback(Runnable fun) {
        this.buttonView.setOnClickListener((View.OnClickListener) v -> {
            fun.run();
        });
    }
}
