package com.example.gnssclient;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.provider.MediaStore;

import androidx.core.content.FileProvider;

import java.io.File;
import java.io.IOException;

import static androidx.core.app.ActivityCompat.startActivityForResult;

public class CustomCamera {
    private String file = "CustomCamera";

    private File folder;
    private Activity activity;

    CustomCamera(Activity activity, File folder) {
        this.folder = folder;
        this.activity = activity;
    }

    private File createImageFile(String imageFileName) throws IOException {
        File image = new File(folder, imageFileName);
        return image;
    }

    public void captureImage(String imageFileName) {
        Util.print(imageFileName, file);
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        try {
            File imageFile = createImageFile(imageFileName);
            Util.print(imageFile.toString(), file);
            Uri photoURI = FileProvider.getUriForFile(activity, "com.example.android.fileprovider", imageFile);
            Util.print(photoURI.toString(), file);
            takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
            startActivityForResult(activity, takePictureIntent, Util.REQUEST_IMAGE_CAPTURE, null);
        } catch (ActivityNotFoundException | IOException e) {
            Util.print(e.toString(), file);
        }
    }
}
