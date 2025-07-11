package com.fraud_detection.flink;

import com.fraud_detection.flink.mapper.FeatureExtractor;
import com.fraud_detection.flink.mapper.FraudFilter;
import com.fraud_detection.flink.model.Transaction;
import com.fraud_detection.flink.model.EnrichedTransaction;
import com.fraud_detection.flink.model.SummaryAccumulator;
import com.fraud_detection.flink.Deserializer.JSONValueDeserializationSchema;
import com.fraud_detection.flink.Serializer.EnrichedTransactionSerializer;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.state.MapStateDescriptor;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.functions.KeySelector;

import java.time.Duration;
import java.time.Instant;

public class FlinkJob {

    /**
     * KeySelector implementation for extracting user and bank ID as a composite key
     */
    public static class UserBankKeySelector implements KeySelector<EnrichedTransaction, Tuple2<String, String>> {
        @Override
        public Tuple2<String, String> getKey(EnrichedTransaction txn) throws Exception {
            return Tuple2.of(txn.getSourceUserId(), txn.getBankId());
        }
    }

    public static final MapStateDescriptor<Tuple2<String, String>, SummaryAccumulator> SUMMARY_STATE_DESCRIPTOR =
            new MapStateDescriptor<>(
                    "summary-broadcast-state",
                    org.apache.flink.api.common.typeinfo.TypeInformation.of(new org.apache.flink.api.common.typeinfo.TypeHint<Tuple2<String, String>>() {}),
                    TypeInformation.of(SummaryAccumulator.class)
            );

    public static void main(String[] args) throws Exception {
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(1);

        String topic_streaming = "transactions_raw";
        String topic_enriched = "transactions_enriched";
        String topic_fraud = "fraud_investigation";

        // Kafka Source
        KafkaSource<Transaction> kafkaSource = KafkaSource.<Transaction>builder()
                .setBootstrapServers("broker:29092")
                .setTopics(topic_streaming)
                .setGroupId("flink-fraud-detection")
                .setStartingOffsets(OffsetsInitializer.earliest())
                .setValueOnlyDeserializer(new JSONValueDeserializationSchema())
                .build();

        DataStream<Transaction> transactionStream = env.fromSource(
                kafkaSource,
                WatermarkStrategy.<Transaction>forBoundedOutOfOrderness(Duration.ofSeconds(10))
                        .withTimestampAssigner((txn, ts) -> {
                            try {
                                return Instant.parse(txn.getTransactionTime()).toEpochMilli();
                            } catch (Exception e) {
                                return ts;
                            }
                        }),
                "KafkaSource"
        );

        // Feature extraction
        DataStream<EnrichedTransaction> enrichedTxn = transactionStream
                .map(new FeatureExtractor());

        // Keyed stream dan enrichment rolling window 5 menit per user+bank
        DataStream<EnrichedTransaction> enrichedWithSummary = enrichedTxn
                .keyBy(new org.apache.flink.api.java.functions.KeySelector<EnrichedTransaction, org.apache.flink.api.java.tuple.Tuple2<String, String>>() {
                    @Override
                    public org.apache.flink.api.java.tuple.Tuple2<String, String> getKey(EnrichedTransaction txn) {
                        return org.apache.flink.api.java.tuple.Tuple2.of(txn.getSourceUserId(), txn.getBankId());
                    }
                })
                .process(new com.fraud_detection.flink.process.RollingSummaryProcessFunction());

        // Filter fraud
        DataStream<EnrichedTransaction> fraud = enrichedWithSummary
                .filter(new FraudFilter());

        // Kafka Sink untuk transaksi enriched
        KafkaSink<String> kafkaSinkEnriched = KafkaSink.<String>builder()
                .setBootstrapServers("broker:29092")
                .setRecordSerializer(
                        KafkaRecordSerializationSchema.builder()
                                .setTopic(topic_enriched)
                                .setValueSerializationSchema(new SimpleStringSchema())
                                .build()
                )
                .build();

        // Kafka Sink untuk transaksi fraud
        KafkaSink<String> kafkaSinkFraud = KafkaSink.<String>builder()
                .setBootstrapServers("broker:29092")
                .setRecordSerializer(
                        KafkaRecordSerializationSchema.builder()
                                .setTopic(topic_fraud)
                                .setValueSerializationSchema(new SimpleStringSchema())
                                .build()
                )
                .build();

        // Sink enriched transaksi
        enrichedWithSummary
                .map(new EnrichedTransactionSerializer())
                .sinkTo(kafkaSinkEnriched)
                .name(topic_enriched);


        // Sink transaksi fraud
        fraud
                .map(new EnrichedTransactionSerializer())
                .sinkTo(kafkaSinkFraud)
                .name(topic_fraud);

        env.execute("Flink Real-Time Fraud Detection with Modularized ProcessFunctions");
    }
}
