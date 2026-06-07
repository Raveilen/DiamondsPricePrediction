package com.example.diamondspricesapplication.controller;

import com.example.diamondspricesapplication.model.DiamondPredictionInput;
import com.example.diamondspricesapplication.model.DiamondPredictionResponse;
import com.example.diamondspricesapplication.model.PredictionErrorResponse;
import com.example.diamondspricesapplication.service.PredictionExecutionException;
import com.example.diamondspricesapplication.service.PythonPredictionService;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class PredictionInputControllerTest {

    @Test
    void shouldReturnPredictionWhenScriptExecutionSucceeds() {
        PythonPredictionService pythonPredictionService = mock(PythonPredictionService.class);
        PredictionInputController controller = new PredictionInputController(pythonPredictionService);
        DiamondPredictionInput input = createValidInput();

        when(pythonPredictionService.predict(any(DiamondPredictionInput.class))).thenReturn(1234.56);

        ResponseEntity<?> response = controller.receivePredictionInput(input);

        assertEquals(HttpStatus.OK, response.getStatusCode());
        DiamondPredictionResponse body = assertInstanceOf(DiamondPredictionResponse.class, response.getBody());
        assertEquals(1234.56, body.getPredictedPrice());
        assertEquals(1.1, body.getInput().getCarat());
    }

    @Test
    void shouldReturnBadRequestWhenInputValidationFails() {
        PythonPredictionService pythonPredictionService = mock(PythonPredictionService.class);
        PredictionInputController controller = new PredictionInputController(pythonPredictionService);
        DiamondPredictionInput input = createValidInput();

        when(pythonPredictionService.predict(any(DiamondPredictionInput.class)))
                .thenThrow(new IllegalArgumentException("Missing required value: carat"));

        ResponseEntity<?> response = controller.receivePredictionInput(input);

        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode());
        PredictionErrorResponse body = assertInstanceOf(PredictionErrorResponse.class, response.getBody());
        assertEquals("Missing required value: carat", body.getMessage());
    }

    @Test
    void shouldReturnInternalServerErrorWhenScriptExecutionFails() {
        PythonPredictionService pythonPredictionService = mock(PythonPredictionService.class);
        PredictionInputController controller = new PredictionInputController(pythonPredictionService);
        DiamondPredictionInput input = createValidInput();

        when(pythonPredictionService.predict(any(DiamondPredictionInput.class)))
                .thenThrow(new PredictionExecutionException("Prediction script failed: test failure"));

        ResponseEntity<?> response = controller.receivePredictionInput(input);

        assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, response.getStatusCode());
        PredictionErrorResponse body = assertInstanceOf(PredictionErrorResponse.class, response.getBody());
        assertEquals("Prediction script failed: test failure", body.getMessage());
    }

    private DiamondPredictionInput createValidInput() {
        DiamondPredictionInput input = new DiamondPredictionInput();
        input.setCarat(1.1);
        input.setCut("Ideal");
        input.setColor("F");
        input.setClarity("VS1");
        input.setDepth(61.4);
        input.setTable(56.0);
        input.setX(6.7);
        input.setY(6.72);
        input.setZ(4.12);
        return input;
    }
}
