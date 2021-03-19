package com.example.gnssclient;

import com.opencsv.CSVReader;
import com.opencsv.CSVWriter;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class CSVFile {
    private final String file = "CSVFile";
    File csvFile;

    CSVFile(File dir, String filename) throws IOException {
        if(!dir.exists()){
            Util.print("Making dir: " + dir.getPath(), file);
            dir.mkdirs();
        }

        Util.print("Starting file creation: " + dir + "/" + filename, file);
        csvFile = new File(dir, filename);
        if (!csvFile.isFile()) {
            csvFile.createNewFile();
            Util.print("Created file.", file);
        } else Util.print("Loaded file.", file);
    }

    public int getMaxId() throws IOException {
        List<String[]> rows = readFile();
        int maxId = -1;
        Util.print("Reading rows:", file);
        for (String[] row : rows) {
            Util.print(row, file);
            Util.print("ID: " + row[0], file);
            maxId = Integer.max(maxId, Integer.parseInt(row[0]));
        }
        Util.print("maxId = " + maxId, file);

        return maxId;
    }

    public List<String[]> readFile() throws IOException {
        FileReader fileReader = new FileReader(csvFile.getAbsolutePath());
        CSVReader reader = new CSVReader(fileReader);
        Util.print("Created reader.", file);
        List<String[]> rows = reader.readAll();
        Util.print("Read rows in reader.", file);
        reader.close();
        fileReader.close();

        return rows;
    }

    private void write(List<String[]> rows) throws IOException {
        FileWriter fileWriter = new FileWriter(csvFile);
        CSVWriter writer = new CSVWriter(fileWriter);
        Util.print("Created writer: " + writer.toString(), file);

        writer.writeAll(rows, true);
        Util.print("Wrote " + rows.size() + "rows.", file);

        writer.close();
        fileWriter.close();
    }

    public void deleteFeature(final int featureId) throws IOException {
        if (featureId < 0 || featureId > getMaxId()) return;
        List<String[]> rows = readFile();
        write(deleteFeature(rows, featureId));
    }

    private List<String[]> deleteFeature(List<String[]> rows, final int featureId) {
        ArrayList<String[]> newRows = new ArrayList<>();
        for (String[] row : rows) if (!row[0].equals(String.valueOf(featureId))) newRows.add(row);
        return newRows;
    }

    public void addFeature(GNSSFeature feature) throws IOException {
        if (feature == null) return;

        List<String[]> rows = readFile();
        rows = deleteFeature(rows, feature.getFeatureId());

        for (GNSSData data : feature.getData()) {
            String[] fields = data.getFields();
            String[] row = new String[fields.length + 2];

            row[0] = String.valueOf(feature.getFeatureId());
            row[1] = String.valueOf(data.getLatitude());
            row[2] = String.valueOf(data.getLongitude());
            System.arraycopy(fields, 1, row, 3, fields.length - 1);

            rows.add(row);
            write(rows);
            Util.print("Writing row:", file);
            Util.print(row, file);
        }

        getMaxId();
    }
}
