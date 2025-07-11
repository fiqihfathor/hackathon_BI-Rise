package com.fraud_detection.flink.mapper;

import com.fraud_detection.flink.model.Transaction;
import com.fraud_detection.flink.model.EnrichedTransaction;

import org.apache.flink.api.common.functions.MapFunction;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.math.BigDecimal;
import java.time.ZonedDateTime;
import java.time.format.DateTimeParseException;
import java.time.DayOfWeek;
import java.time.ZoneId;

public class FeatureExtractor implements MapFunction<Transaction, EnrichedTransaction> {

    @Override
    public EnrichedTransaction map(Transaction tx) throws Exception {
        EnrichedTransaction enriched = new EnrichedTransaction(tx);

        ZoneId indoZone = ZoneId.of("Asia/Jakarta");
        int hourOfDay = -1;
        int dayOfWeek = -1;
        boolean isWeekend = false;
        boolean isNight = false;

        if (tx.getTransactionTime() != null) {
            try {
                ZonedDateTime dtUtc = ZonedDateTime.parse(tx.getTransactionTime()); // parse UTC/Zulu
                ZonedDateTime dtLocal = dtUtc.withZoneSameInstant(indoZone); // convert ke WIB
        
                hourOfDay = dtLocal.getHour();
                dayOfWeek = dtLocal.getDayOfWeek().getValue();
                isWeekend = (dtLocal.getDayOfWeek() == DayOfWeek.SATURDAY || dtLocal.getDayOfWeek() == DayOfWeek.SUNDAY);
                isNight = (hourOfDay >= 0 && hourOfDay < 6);
            } catch (DateTimeParseException e) {
                // logging error
            }
        }

        enriched.setHourOfDay(hourOfDay);
        enriched.setDayOfWeek(dayOfWeek);
        enriched.setIsWeekend(isWeekend);
        enriched.setIsNight(isNight);

        // IP private check
        boolean ipIsPrivate = false;
        if (tx.getIpAddress() != null) {
            try {
                InetAddress addr = InetAddress.getByName(tx.getIpAddress());
                ipIsPrivate = addr.isSiteLocalAddress();
            } catch (UnknownHostException e) {
                // Optional logging
            }
        }
        enriched.setIpIsPrivate(ipIsPrivate);

        // Device category
        String deviceCategory;
        if ("true".equalsIgnoreCase(tx.getIsEmulator())) {
            deviceCategory = "emulator";
        } else if ("android".equalsIgnoreCase(tx.getDeviceType()) || "ios".equalsIgnoreCase(tx.getDeviceType())) {
            deviceCategory = "mobile";
        } else {
            deviceCategory = "other";
        }
        enriched.setDeviceTypeCategory(deviceCategory);

        // Amount in IDR
        BigDecimal amount = BigDecimal.ZERO;
        BigDecimal rate = BigDecimal.ONE;

        try {
            amount = new BigDecimal(tx.getAmount());
        } catch (Exception e) {}

        try {
            rate = new BigDecimal(tx.getCurrencyExchangeRate());
        } catch (Exception e) {}

        enriched.setAmountIdr(amount.multiply(rate).toPlainString());

        return enriched;
    }
}
