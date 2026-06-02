package com.example.diamondspricesapplication.model;

public class DiamondPredictionInput {

    private Double carat;
    private String cut;
    private String color;
    private String clarity;
    private Double depth;
    private Double table;
    private Double x;
    private Double y;
    private Double z;

    public DiamondPredictionInput() {
    }

    public Double getCarat() {
        return carat;
    }

    public void setCarat(Double carat) {
        this.carat = carat;
    }

    public String getCut() {
        return cut;
    }

    public void setCut(String cut) {
        this.cut = cut;
    }

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public String getClarity() {
        return clarity;
    }

    public void setClarity(String clarity) {
        this.clarity = clarity;
    }

    public Double getDepth() {
        return depth;
    }

    public void setDepth(Double depth) {
        this.depth = depth;
    }

    public Double getTable() {
        return table;
    }

    public void setTable(Double table) {
        this.table = table;
    }

    public Double getX() {
        return x;
    }

    public void setX(Double x) {
        this.x = x;
    }

    public Double getY() {
        return y;
    }

    public void setY(Double y) {
        this.y = y;
    }

    public Double getZ() {
        return z;
    }

    public void setZ(Double z) {
        this.z = z;
    }
}