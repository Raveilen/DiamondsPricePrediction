package com.example.diamondspricesapplication.service;

import com.example.diamondspricesapplication.model.DiamondPredictionInput;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

@Service
public class PythonPredictionService {

    private final String pythonExecutable;
    private final String pythonScriptPath;
    private final long timeoutSeconds;

    public PythonPredictionService(
            @Value("${prediction.python.executable:python3}") String pythonExecutable,
            @Value("${prediction.python.script-path:src/main/resources/scripts/diamond_predict.py}") String pythonScriptPath,
            @Value("${prediction.python.timeout-seconds:30}") long timeoutSeconds) {
        this.pythonExecutable = pythonExecutable;
        this.pythonScriptPath = pythonScriptPath;
        this.timeoutSeconds = timeoutSeconds;
    }

    public double predict(DiamondPredictionInput input) {
        validateInput(input);

        List<String> command = new ArrayList<>();
        command.add(pythonExecutable);
        command.add(Paths.get(pythonScriptPath).toAbsolutePath().toString());
        command.add(String.valueOf(input.getCarat()));
        command.add(input.getCut());
        command.add(input.getColor());
        command.add(input.getClarity());
        command.add(String.valueOf(input.getDepth()));
        command.add(String.valueOf(input.getTable()));
        command.add(String.valueOf(input.getX()));
        command.add(String.valueOf(input.getY()));
        command.add(String.valueOf(input.getZ()));

        ProcessBuilder processBuilder = new ProcessBuilder(command);
        try {
            Process process = processBuilder.start();

            CompletableFuture<String> stdoutFuture = CompletableFuture.supplyAsync(() -> {
                try {
                    return new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8).trim();
                } catch (IOException e) {
                    return "";
                }
            });

            CompletableFuture<String> stderrFuture = CompletableFuture.supplyAsync(() -> {
                try {
                    return new String(process.getErrorStream().readAllBytes(), StandardCharsets.UTF_8).trim();
                } catch (IOException e) {
                    return "";
                }
            });

            boolean finished = process.waitFor(timeoutSeconds, TimeUnit.SECONDS);

            if (!finished) {
                process.destroyForcibly();
                throw new PredictionExecutionException("Prediction script timed out after " + timeoutSeconds + " seconds.");
            }

            String stdout = stdoutFuture.get(5, TimeUnit.SECONDS);
            String stderr = stderrFuture.get(5, TimeUnit.SECONDS);

            if (process.exitValue() != 0) {
                throw new PredictionExecutionException(buildExecutionError(stderr, stdout));
            }

            if (stdout.isEmpty()) {
                throw new PredictionExecutionException("Prediction script did not return any output.");
            }

            try {
                String firstLine = stdout.split("[\\r\\n]+")[0].trim();
                return Double.parseDouble(firstLine);
            } catch (NumberFormatException e) {
                throw new PredictionExecutionException("Prediction script returned non-numeric output: " + stdout, e);
            }
        } catch (IOException e) {
            throw new PredictionExecutionException("Unable to execute prediction script: " + e.getMessage(), e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new PredictionExecutionException("Prediction execution was interrupted.", e);
        } catch (ExecutionException | TimeoutException e) {
            throw new PredictionExecutionException("Failed to read process output: " + e.getMessage(), e);
        }
    }

    private void validateInput(DiamondPredictionInput input) {
        if (input == null) {
            throw new IllegalArgumentException("Request body is required.");
        }

        requireValue(input.getCarat(), "carat");
        requireText(input.getCut(), "cut");
        requireText(input.getColor(), "color");
        requireText(input.getClarity(), "clarity");
        requireValue(input.getDepth(), "depth");
        requireValue(input.getTable(), "table");
        requireValue(input.getX(), "x");
        requireValue(input.getY(), "y");
        requireValue(input.getZ(), "z");
    }

    private void requireValue(Double value, String fieldName) {
        if (value == null) {
            throw new IllegalArgumentException("Missing required value: " + fieldName);
        }
    }

    private void requireText(String value, String fieldName) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("Missing required value: " + fieldName);
        }
    }

    private String buildExecutionError(String stderr, String stdout) {
        String details = !stderr.isBlank() ? stderr : stdout;
        if (details.isBlank()) {
            details = "No error output from script.";
        }
        return "Prediction script failed: " + details;
    }
}