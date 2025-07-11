package com.fraud_detection.flink.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Transaction {

    @JsonProperty("source_transaction_id")
    private String sourceTransactionId;

    @JsonProperty("source_user_id")
    private String sourceUserId;

    @JsonProperty("source_account_id")
    private String sourceAccountId;

    @JsonProperty("source_merchant_code")
    private String sourceMerchantCode;

    private String amount;
    private String currency;

    @JsonProperty("transaction_type")
    private String transactionType;

    @JsonProperty("transaction_time")
    private String transactionTime;

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
    private String isEmulator; // Kalau di Kafka JSON tipe String "True"/"False", gunakan String dulu, bisa parse nanti ke boolean

    @JsonProperty("ip_address")
    private String ipAddress;

    @JsonProperty("ip_location")
    private String ipLocation;

    @JsonProperty("is_proxy")
    private String isProxy; // Sama seperti isEmulator

    private String notes;

    @JsonProperty("transaction_id")
    private String transactionId;

    @JsonProperty("received_time")
    private String receivedTime;

    @JsonProperty("bank_id")
    private String bankId;

    @JsonProperty("currency_exchange_rate")
    private String currencyExchangeRate;

    public Transaction() {}

    public String getSourceTransactionId() { return sourceTransactionId; }
    public void setSourceTransactionId(String sourceTransactionId) { this.sourceTransactionId = sourceTransactionId; }

    public String getSourceUserId() { return sourceUserId; }
    public void setSourceUserId(String sourceUserId) { this.sourceUserId = sourceUserId; }

    public String getSourceAccountId() { return sourceAccountId; }
    public void setSourceAccountId(String sourceAccountId) { this.sourceAccountId = sourceAccountId; }

    public String getSourceMerchantCode() { return sourceMerchantCode; }
    public void setSourceMerchantCode(String sourceMerchantCode) { this.sourceMerchantCode = sourceMerchantCode; }

    public String getAmount() { return amount; }
    public void setAmount(String amount) { this.amount = amount; }

    public String getCurrency() { return currency; }
    public void setCurrency(String currency) { this.currency = currency; }

    public String getTransactionType() { return transactionType; }
    public void setTransactionType(String transactionType) { this.transactionType = transactionType; }

    public String getTransactionTime() { return transactionTime; }
    public void setTransactionTime(String transactionTime) { this.transactionTime = transactionTime; }

    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }

    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }

    public String getDeviceType() { return deviceType; }
    public void setDeviceType(String deviceType) { this.deviceType = deviceType; }

    public String getOsVersion() { return osVersion; }
    public void setOsVersion(String osVersion) { this.osVersion = osVersion; }

    public String getAppVersion() { return appVersion; }
    public void setAppVersion(String appVersion) { this.appVersion = appVersion; }

    public String getIsEmulator() { return isEmulator; }
    public void setIsEmulator(String isEmulator) { this.isEmulator = isEmulator; }

    public String getIpAddress() { return ipAddress; }
    public void setIpAddress(String ipAddress) { this.ipAddress = ipAddress; }

    public String getIpLocation() { return ipLocation; }
    public void setIpLocation(String ipLocation) { this.ipLocation = ipLocation; }

    public String getIsProxy() { return isProxy; }
    public void setIsProxy(String isProxy) { this.isProxy = isProxy; }

    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }

    public String getTransactionId() { return transactionId; }
    public void setTransactionId(String transactionId) { this.transactionId = transactionId; }

    public String getReceivedTime() { return receivedTime; }
    public void setReceivedTime(String receivedTime) { this.receivedTime = receivedTime; }

    public String getBankId() { return bankId; }
    public void setBankId(String bankId) { this.bankId = bankId; }

    public String getCurrencyExchangeRate() { return currencyExchangeRate; }
    public void setCurrencyExchangeRate(String currencyExchangeRate) { this.currencyExchangeRate = currencyExchangeRate; }
}
