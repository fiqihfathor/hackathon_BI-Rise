package com.fraud_detection.flink.process;

import com.fraud_detection.flink.model.EnrichedTransaction;
import org.apache.flink.api.common.state.ListState;
import org.apache.flink.api.common.state.ListStateDescriptor;
import org.apache.flink.api.common.typeinfo.TypeHint;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.util.Collector;

import java.util.ArrayList;
import java.util.List;

public class RollingSummaryProcessFunction extends KeyedProcessFunction<Tuple2<String, String>, EnrichedTransaction, EnrichedTransaction> {
    private transient ListState<Tuple2<Long, Double>> txnState;

    @Override
    public void open(Configuration parameters) {
        ListStateDescriptor<Tuple2<Long, Double>> desc =
            new ListStateDescriptor<>(
                "txnState",
                TypeInformation.of(new TypeHint<Tuple2<Long, Double>>() {})
            );
        txnState = getRuntimeContext().getListState(desc);
    }

    @Override
    public void processElement(EnrichedTransaction txn, Context ctx, Collector<EnrichedTransaction> out) throws Exception {
        long now = txn.getEventTimestamp();
        double amount = txn.getAmountAsDouble();

        // 1. Tambahkan transaksi saat ini ke state
        txnState.add(Tuple2.of(now, amount));

        // 2. Ambil semua transaksi dalam state
        List<Tuple2<Long, Double>> allTxns = new ArrayList<>();
        for (Tuple2<Long, Double> t : txnState.get()) {
            allTxns.add(t);
        }

        // 3. Hapus transaksi yang sudah lebih dari 5 menit
        long windowStart = now - 5 * 60 * 1000;
        allTxns.removeIf(t -> t.f0 < windowStart);

        // 4. Update state dengan transaksi yang masih valid
        txnState.update(allTxns);

        // 5. Hitung summary rolling window
        long count = allTxns.size();
        double sum = allTxns.stream().mapToDouble(t -> t.f1).sum();

        // 6. Set summary ke transaksi
        txn.setTxnCount5min(count);
        txn.setTxnAmountSum5min(sum);

        // 7. Emit transaksi hasil enrichment
        out.collect(txn);
    }
}
