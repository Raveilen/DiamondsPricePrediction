package com.example.diamondspricesapplication.controller;

import com.example.diamondspricesapplication.model.DiamondPredictionInput;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

@Controller
public class PredictionInputController {

    @GetMapping("/prediction-form")
    public String predictionForm() {
        return "forward:/prediction-form.html";
    }

    @PostMapping("/api/prediction-input")
    @ResponseBody
    public ResponseEntity<DiamondPredictionInput> receivePredictionInput(
            @RequestBody DiamondPredictionInput input) {

        System.out.println("Received prediction input:");
        System.out.println("carat=" + input.getCarat());
        System.out.println("cut=" + input.getCut());
        System.out.println("color=" + input.getColor());
        System.out.println("clarity=" + input.getClarity());
        System.out.println("depth=" + input.getDepth());
        System.out.println("table=" + input.getTable());
        System.out.println("x=" + input.getX());
        System.out.println("y=" + input.getY());
        System.out.println("z=" + input.getZ());

        return ResponseEntity.ok(input);
    }
}