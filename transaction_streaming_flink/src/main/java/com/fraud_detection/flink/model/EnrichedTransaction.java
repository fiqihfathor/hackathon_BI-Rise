package com.fraud_detection.flink.model;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.io.Serializable;

/**
 * Representasi transaksi yang telah diperkaya (enriched),
 * termasuk fitur tambahan, context, dan summary statistik.
 */
public class EnrichedTransaction implements Serializable {

    @JsonProperty("source_transaction_id")
    private String sourceTransactionId;

    @JsonProperty("source_user_id")
    private String sourceUserId;

    @JsonProperty("source_account_id")
    private String sourceAccountId;

    @JsonProperty("source_merchant_code")
    private String sourceMerchantCode;

    @JsonProperty("amount")
    private String amount;

    @JsonProperty("currency")
    private String currency;

    @JsonProperty("transaction_type")
    private String transactionType;

    @JsonProperty("transaction_time")
    private String transactionTime;

    @JsonProperty("location")
    private String location;

    @JsonProperty("device_id")
    private String deviceId;

    @JsonProperty("device_type")
    private String deviceType;

    @JsonProperty("os_version")
    private String osVersion;

    @JsonProperty("app_version")
    private String appVersion;

    @JsonProperty("is_emulator")
    private String isEmulator;

    @JsonProperty("ip_address")
    private String ipAddress;

    @JsonProperty("ip_location")
    private String ipLocation;

    @JsonProperty("is_proxy")
    private String isProxy;

    @JsonProperty("notes")
    private String notes;

    @JsonProperty("transaction_id")
    private String transactionId;

    @JsonProperty("received_time")
    private String receivedTime;

    @JsonProperty("bank_id")
    private String bankId;

    @JsonProperty("currency_exchange_rate")
    private String currencyExchangeRate;

    @JsonProperty("amount_idr")
    private String amountIdr;

    @JsonProperty("hour_of_day")
    private int hourOfDay;

    @JsonProperty("day_of_week")
    private int dayOfWeek;

    @JsonProperty("is_weekend")
    private boolean isWeekend;

    @JsonProperty("is_night")
    private boolean isNight;

    @JsonProperty("ip_is_private")
    private boolean ipIsPrivate;

    @JsonProperty("device_type_category")
    private String deviceTypeCategory;

    @JsonProperty("txn_count_5min")
    private long txnCount5min;

    @JsonProperty("txn_amount_sum_5min")
    private double txnAmountSum5min;

    public long getTxnCount5min() {
        return txnCount5min;
    }
    public void setTxnCount5min(long txnCount5min) {
        this.txnCount5min = txnCount5min;
    }
    public double getTxnAmountSum5min() {
        return txnAmountSum5min;
    }
    public void setTxnAmountSum5min(double txnAmountSum5min) {
        this.txnAmountSum5min = txnAmountSum5min;
    }

    // ✅ Field tambahan untuk summary enrichment
    private long summaryCount;
    private double summaryTotalAmount;

    public EnrichedTransaction() {
    }

    public EnrichedTransaction(Transaction tx) {
        this.sourceTransactionId = tx.getSourceTransactionId();
        this.sourceUserId = tx.getSourceUserId();
        this.sourceAccountId = tx.getSourceAccountId();
        this.sourceMerchantCode = tx.getSourceMerchantCode();
        this.amount = tx.getAmount();
        this.currency = tx.getCurrency();
        this.transactionType = tx.getTransactionType();
        this.transactionTime = tx.getTransactionTime();
        this.location = tx.getLocation();
        this.deviceId = tx.getDeviceId();
        this.deviceType = tx.getDeviceType();
        this.osVersion = tx.getOsVersion();
        this.appVersion = tx.getAppVersion();
        this.isEmulator = tx.getIsEmulator();
        this.ipAddress = tx.getIpAddress();
        this.ipLocation = tx.getIpLocation();
        this.isProxy = tx.getIsProxy();
        this.notes = tx.getNotes();
        this.transactionId = tx.getTransactionId();
        this.receivedTime = tx.getReceivedTime();
        this.bankId = tx.getBankId();
        this.currencyExchangeRate = tx.getCurrencyExchangeRate();
    }

    // === Getter & Setter ===

    public String getSourceUserId() { return sourceUserId; }
    public void setSourceUserId(String sourceUserId) { this.sourceUserId = sourceUserId; }

    public String getBankId() { return bankId; }
    public void setBankId(String bankId) { this.bankId = bankId; }

    public String getTransactionTime() { return transactionTime; }
    public void setTransactionTime(String transactionTime) { this.transactionTime = transactionTime; }

    public String getIpAddress() { return ipAddress; }
    public void setIpAddress(String ipAddress) { this.ipAddress = ipAddress; }

    public String getDeviceType() { return deviceType; }
    public void setDeviceType(String deviceType) { this.deviceType = deviceType; }

    public String getIsEmulator() { return isEmulator; }
    public void setIsEmulator(String isEmulator) { this.isEmulator = isEmulator; }

    public String getIsProxy() { return isProxy; }
    public void setIsProxy(String isProxy) { this.isProxy = isProxy; }

    public String getAmount() { return amount; }
    public void setAmount(String amount) { this.amount = amount; }

    public String getCurrencyExchangeRate() { return currencyExchangeRate; }
    public void setCurrencyExchangeRate(String currencyExchangeRate) { this.currencyExchangeRate = currencyExchangeRate; }

    public String getAmountIdr() { return amountIdr; }
    public void setAmountIdr(String amountIdr) { this.amountIdr = amountIdr; }

    public int getHourOfDay() { return hourOfDay; }
    public void setHourOfDay(int hourOfDay) { this.hourOfDay = hourOfDay; }

    public int getDayOfWeek() { return dayOfWeek; }
    public void setDayOfWeek(int dayOfWeek) { this.dayOfWeek = dayOfWeek; }

    public boolean isWeekend() { return isWeekend; }
    public void setIsWeekend(boolean isWeekend) { this.isWeekend = isWeekend; }

    public boolean isNight() { return isNight; }
    public void setIsNight(boolean isNight) { this.isNight = isNight; }

    public boolean isIpIsPrivate() { return ipIsPrivate; }
    public void setIpIsPrivate(boolean ipIsPrivate) { this.ipIsPrivate = ipIsPrivate; }

    public String getDeviceTypeCategory() { return deviceTypeCategory; }
    public void setDeviceTypeCategory(String deviceTypeCategory) { this.deviceTypeCategory = deviceTypeCategory; }

    
    

    
    

    public long getSummaryCount() { return summaryCount; }
    public void setSummaryCount(long summaryCount) { this.summaryCount = summaryCount; }

    public double getSummaryTotalAmount() { return summaryTotalAmount; }
    public void setSummaryTotalAmount(double summaryTotalAmount) { this.summaryTotalAmount = summaryTotalAmount; }

    public String getSourceTransactionId() { return sourceTransactionId; }
    public String getSourceAccountId() { return sourceAccountId; }
    public String getSourceMerchantCode() { return sourceMerchantCode; }
    public String getCurrency() { return currency; }
    public String getTransactionType() { return transactionType; }
    public String getLocation() { return location; }
    public String getDeviceId() { return deviceId; }
    public String getOsVersion() { return osVersion; }
    public String getAppVersion() { return appVersion; }
    public String getIpLocation() { return ipLocation; }
    public String getNotes() { return notes; }
    public String getTransactionId() { return transactionId; }
    public String getReceivedTime() { return receivedTime; }
    // === Helper Methods ===

    public double getAmountAsDouble() {
        if (amount == null) return 0.0;
        try {
            return Double.parseDouble(amount);
        } catch (NumberFormatException e) {
            return 0.0;
        }
    }

    public long getEventTimestamp() {
        try {
            java.time.Instant instant = java.time.Instant.parse(transactionTime);
            return instant.toEpochMilli();
        } catch (Exception e) {
            return 0L;
        }
    }
}
