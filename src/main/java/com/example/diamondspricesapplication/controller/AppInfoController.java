package com.example.diamondspricesapplication.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class AppInfoController
{
    private final long startedAt = System.currentTimeMillis();

    @GetMapping("/api/startup-token")
    public Map<String, Long> startupToken() {
        return Map.of("startedAt", startedAt);
    }
}