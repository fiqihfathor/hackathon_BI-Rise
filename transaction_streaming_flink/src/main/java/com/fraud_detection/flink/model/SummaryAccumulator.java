package com.fraud_detection.flink.model;

import java.io.Serializable;

/**
 * Menyimpan ringkasan transaksi per user & bank.
 * Akan digunakan dalam broadcast state untuk enrichment.
 */
import org.apache.flink.api.java.tuple.Tuple2;

public class SummaryAccumulator implements Serializable {
    public Tuple2<String, String> getKeyTuple() {
        return Tuple2.of(userId, bankId);
    }

    private String userId;
    private String bankId;
    private long count = 0;
    private double totalAmount = 0.0;

    public SummaryAccumulator() {
    }

    public SummaryAccumulator(String userId, String bankId) {
        this.userId = userId;
        this.bankId = bankId;
    }

    public void addTransaction(EnrichedTransaction txn) {
        count++;
        totalAmount += txn.getAmountAsDouble();
    }

    public String getUserId() {
        return userId;
    }

    public String getBankId() {
        return bankId;
    }

    public long getCount() {
        return count;
    }

    public double getTotalAmount() {
        return totalAmount;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public void setBankId(String bankId) {
        this.bankId = bankId;
    }

    public void setCount(long count) {
        this.count = count;
    }

    public void setTotalAmount(double totalAmount) {
        this.totalAmount = totalAmount;
    }
}
