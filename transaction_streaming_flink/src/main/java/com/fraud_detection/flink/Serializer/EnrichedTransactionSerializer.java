package com.fraud_detection.flink.Serializer;

import com.fraud_detection.flink.model.EnrichedTransaction;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.api.common.functions.MapFunction;

public class EnrichedTransactionSerializer implements MapFunction<EnrichedTransaction, String> {

    private static final ObjectMapper mapper = new ObjectMapper();

    @Override
    public String map(EnrichedTransaction value) throws Exception {
        return mapper.writeValueAsString(value);
    }
}
