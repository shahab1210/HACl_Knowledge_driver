package com.iot.iotfaultdiagnosis.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
public class RestClientConfig {

    @Value("${app.ai.bridge.url:http://localhost:5001}")
    private String aiBridgeUrl;

    @Bean
    public RestClient aiRestClient() {
        org.springframework.http.client.SimpleClientHttpRequestFactory factory = new org.springframework.http.client.SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(java.time.Duration.ofSeconds(10));
        factory.setReadTimeout(java.time.Duration.ofSeconds(120));

        return RestClient.builder()
                .baseUrl(aiBridgeUrl)
                .requestFactory(factory)
                .build();
    }
}
