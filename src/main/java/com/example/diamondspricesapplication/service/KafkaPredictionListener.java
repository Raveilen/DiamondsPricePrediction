package com.example.diamondspricesapplication.service;

import com.example.diamondspricesapplication.model.PredictionMessage;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

@Service
public class KafkaPredictionListener {

    private final SimpMessagingTemplate messagingTemplate;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public KafkaPredictionListener(SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    @KafkaListener(
            topics = "${app.kafka.topic}",
            groupId = "${spring.kafka.consumer.group-id}",
            containerFactory = "kafkaListenerContainerFactory"
    )
    public void listen(String messageJson) {
        System.out.println("KAFKA RAW MESSAGE RECEIVED: " + messageJson);
        try {
            PredictionMessage message = objectMapper.readValue(messageJson, PredictionMessage.class);
            messagingTemplate.convertAndSend("/topic/predictions", message);
            System.out.println("WEBSOCKET MESSAGE SENT TO /topic/predictions");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}