package com.example.diamondspricesapplication.service;

public class PredictionExecutionException extends RuntimeException {

    public PredictionExecutionException(String message) {
        super(message);
    }

    public PredictionExecutionException(String message, Throwable cause) {
        super(message, cause);
    }
}
