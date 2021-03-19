package com.example.gnssclient;

import android.util.Log;


public class Util {
    final static int REQUEST_EXTERNAL_STORAGE = 1;
    final static int REQUEST_IMAGE_CAPTURE = 2;


    static void print(String[] row, String originFile) {
        String sRow = "[";
        for (String s : row) sRow += s + ", ";
        sRow = sRow.substring(0, sRow.length() - 2);
        sRow += "]";

        print(sRow, originFile);
    }

    static void print(String s, String originFile) {
        //System.out.println(s);
        Log.d("AAXIOCustomTag_" + originFile, s);
    }
}
