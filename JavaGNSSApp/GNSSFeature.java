package com.example.gnssclient;

import java.util.ArrayList;
import java.util.List;

public class GNSSFeature {
    private List<GNSSData> data;
    private int imageAmount = 0;
    private String note = "";

    private final int featureId;

    public GNSSFeature(final int featureId) {
        this.featureId = featureId;
        this.data = new ArrayList<GNSSData>();
    }

    public final int getFeatureId() {
        return featureId;
    }

    public void addData(GNSSData data) {
        this.data.add(data);
    }

    public void setImageAmount(int n) {
        imageAmount = n;
    }

    public int getImageAmount() {
        return imageAmount;
    }

    public List<GNSSData> getData() {
        return this.data;
    }

    public void setNote(String note) {
        if (this.note.length() > 0) this.note = this.note + ", " + note;
        else this.note = note;
    }
}
