package com.example.gnssclient;

class CircularQueue {
    double[] arr;
    int currentIndex = 0;
    int size = 0;

    public CircularQueue(int len) {
        arr = new double[len];
        for (int i = 0; i < len; i++) arr[i] = 0;
    }

    public void push(double val) {
        arr[currentIndex] = val;
        currentIndex = (currentIndex + 1) % arr.length;
        size = Integer.min((size + 1), arr.length);
    }

    public double average() {
        double val = 0;
        for (int i = 0; i < size; i++) val += arr[i];
        val /= size;
        return Math.round(val * 10.0) / 10.0;
    }

    public void clear() {
        currentIndex = 0;
        size = 0;
    }
}
