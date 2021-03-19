package com.example.gnssclient;

class GNSSData {
    private final String file = "GNSSData";

    private String[] fields = {};
    private String type = "", fix = "";

    private boolean valid = false;

    private double lat = -1, lon = -1;

    public GNSSData(String s) {
        fields = s.split(",");
        type = fields[0];

        if (type.equals("$GPGGA") && fields.length > 6) {
            fix = fields[6];

            String latString = fields[2];
            lat = Double.parseDouble(latString.substring(0, 2)) + Double.parseDouble(latString.substring(2)) / 60;
            String lonString = fields[4];
            lon = Double.parseDouble(lonString.substring(0, 3)) + Double.parseDouble(lonString.substring(3)) / 60;

            valid = true;
        }
    }

    public double getLatitude() { return lat; }
    public double getLongitude() { return lon; }
    public boolean isValid() { return valid; }
    public String[] getFields() { return fields; }
    public String getType() { return type; }
    public String getFix() { return fix; }
}
