package com.example.diamondspricesapplication.model;

public class PredictionErrorResponse {

    private String message;
    private DiamondPredictionInput input;

    public PredictionErrorResponse() {
    }

    public PredictionErrorResponse(String message, DiamondPredictionInput input) {
        this.message = message;
        this.input = input;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public DiamondPredictionInput getInput() {
        return input;
    }

    public void setInput(DiamondPredictionInput input) {
        this.input = input;
    }
}
