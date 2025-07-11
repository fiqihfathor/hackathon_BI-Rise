package com.fraud_detection.flink.Deserializer;

import java.io.IOException;

import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.TypeExtractor;

import com.fraud_detection.flink.model.Transaction;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.DeserializationFeature;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class JSONValueDeserializationSchema implements DeserializationSchema<Transaction> {

    private static final long serialVersionUID = 1L;

    private static final Logger LOG = LoggerFactory.getLogger(JSONValueDeserializationSchema.class);

    private static final ObjectMapper objectMapper = new ObjectMapper()
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

    @Override
    public void open(InitializationContext context) throws Exception {
        DeserializationSchema.super.open(context);
    }

    @Override
    public Transaction deserialize(byte[] bytes) throws IOException {
        try {
            Transaction txn = objectMapper.readValue(bytes, Transaction.class);
            return txn;
        } catch (IOException e) {
            LOG.error("Failed to deserialize JSON to Transaction: {}", new String(bytes), e);
            return null;
        }
    }

    @Override
    public boolean isEndOfStream(Transaction nextElement) {
        return false;
    }

    @Override
    public TypeInformation<Transaction> getProducedType() {
        return TypeExtractor.getForClass(Transaction.class);
    }
}
