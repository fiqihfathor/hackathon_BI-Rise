package com.fraud_detection.flink.mapper;

import org.apache.flink.api.common.functions.FilterFunction;
import java.math.BigDecimal;
import com.fraud_detection.flink.model.EnrichedTransaction;

public class FraudFilter implements FilterFunction<EnrichedTransaction> {

    @Override
    public boolean filter(EnrichedTransaction txn) {
        try {
            BigDecimal amount = new BigDecimal(txn.getAmount());
            int hour = txn.getHourOfDay();
            long txnCount = txn.getTxnCount5min();
            boolean isEmulator = Boolean.parseBoolean(txn.getIsEmulator()); // assuming isEmulator is String "true"/"false"
            boolean isProxy = Boolean.parseBoolean(txn.getIsProxy());       // same here
            boolean ipPrivate = txn.isIpIsPrivate();

            String deviceType = txn.getDeviceTypeCategory() != null ? txn.getDeviceTypeCategory().toLowerCase() : "";

            boolean isNormalDevice = !isEmulator && (deviceType.equals("mobile") || deviceType.equals("other"));

            boolean ruleA = amount.compareTo(new BigDecimal("5000000")) > 0
                    && (hour < 6 || hour > 22)
                    && (isEmulator || isProxy);

            boolean ruleB = txnCount > 5 && ipPrivate;

            boolean ruleC = amount.compareTo(new BigDecimal("10000000")) > 0 && isEmulator;

            boolean ruleD = isNormalDevice
                    && amount.compareTo(new BigDecimal("10000000")) > 0
                    && hour < 6
                    && txnCount > 5;

            boolean ruleE = isNormalDevice
                    && amount.compareTo(new BigDecimal("20000000")) > 0
                    && hour >= 6 && hour <= 22;

            return ruleA || ruleB || ruleC || ruleD || ruleE;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }
}
