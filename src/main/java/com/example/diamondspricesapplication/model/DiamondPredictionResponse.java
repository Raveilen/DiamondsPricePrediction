package com.example.diamondspricesapplication.model;

public class DiamondPredictionResponse {

    private Double predictedPrice;
    private DiamondPredictionInput input;

    public DiamondPredictionResponse() {
    }

    public DiamondPredictionResponse(Double predictedPrice, DiamondPredictionInput input) {
        this.predictedPrice = predictedPrice;
        this.input = input;
    }

    public Double getPredictedPrice() {
        return predictedPrice;
    }

    public void setPredictedPrice(Double predictedPrice) {
        this.predictedPrice = predictedPrice;
    }

    public DiamondPredictionInput getInput() {
        return input;
    }

    public void setInput(DiamondPredictionInput input) {
        this.input = input;
    }
}
