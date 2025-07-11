package com.fraud_detection.flink.utils;

import com.fasterxml.jackson.databind.ObjectMapper;

public class JsonUtils {

    private static final ObjectMapper mapper = new ObjectMapper();

    public static <T> T fromJson(String json, Class<T> clazz) {
        try {
            return mapper.readValue(json, clazz);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public static String toJson(Object obj) {
        try {
            return mapper.writeValueAsString(obj);
        } catch (Exception e) {
            e.printStackTrace();
            return "";
        }
    }
}
