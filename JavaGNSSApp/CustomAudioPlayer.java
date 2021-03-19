package com.example.gnssclient;

import android.content.Context;
import android.media.MediaPlayer;
import android.net.Uri;

import java.security.cert.Extension;

public class CustomAudioPlayer {

    MediaPlayer mp = null;

    CustomAudioPlayer ()  { }

    void play(Context context, int sound) {
        try {
            if (mp != null && mp.isPlaying()) {
                mp.stop();
                mp.release();
            }
            mp = MediaPlayer.create(context, sound);
            mp.start();
        } catch (Exception e) {

        }
    }

}
