package com.example.diamondspricesapplication.service;

import com.example.diamondspricesapplication.model.DiamondPredictionInput;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class PythonPredictionServiceTest {

    @Test
    void shouldRejectMissingRequiredValuesBeforeExecutingScript() {
        PythonPredictionService service = new PythonPredictionService(
                "python3",
                "src/main/resources/scripts/diamond_predict.py",
                10
        );

        DiamondPredictionInput input = new DiamondPredictionInput();
        input.setCut("Ideal");
        input.setColor("F");
        input.setClarity("VS1");
        input.setDepth(61.4);
        input.setTable(56.0);
        input.setX(6.7);
        input.setY(6.72);
        input.setZ(4.12);

        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class,
                () -> service.predict(input));

        assertEquals("Missing required value: carat", exception.getMessage());
    }
}
