package com.example.diamondspricesapplication.controller;

import com.example.diamondspricesapplication.model.DiamondPredictionInput;
import com.example.diamondspricesapplication.model.DiamondPredictionResponse;
import com.example.diamondspricesapplication.model.PredictionErrorResponse;
import com.example.diamondspricesapplication.service.PredictionExecutionException;
import com.example.diamondspricesapplication.service.PythonPredictionService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

@Controller
public class PredictionInputController
{

    private final PythonPredictionService pythonPredictionService;

    public PredictionInputController(PythonPredictionService pythonPredictionService) {
        this.pythonPredictionService = pythonPredictionService;
    }

    @GetMapping("/prediction-form")
    public String predictionForm() {
        return "forward:/prediction-form.html";
    }

    @PostMapping("/api/prediction-input")
    @ResponseBody
    public ResponseEntity<?> receivePredictionInput(@RequestBody DiamondPredictionInput input) {
        try {
            double predictedPrice = pythonPredictionService.predict(input);
            return ResponseEntity.ok(new DiamondPredictionResponse(predictedPrice, input));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(new PredictionErrorResponse(e.getMessage(), input));
        } catch (PredictionExecutionException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(new PredictionErrorResponse(e.getMessage(), input));
        }
    }
}
