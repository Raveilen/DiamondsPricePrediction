package com.example.diamondspricesapplication.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class AppInfoController {

    // Captured once when the application starts — a new value is produced
    // on every restart, which the frontend uses to detect stale stored data.
    private final long startedAt = System.currentTimeMillis();

    @GetMapping("/api/startup-token")
    public Map<String, Long> startupToken() {
        return Map.of("startedAt", startedAt);
    }
}