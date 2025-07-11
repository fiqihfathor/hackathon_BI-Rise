set -e
echo "📦  Copying JAR to container..."
docker cp transaction_streaming_flink/target/transaction_streaming_flink-1.0-SNAPSHOT.jar flink-jobmanager:/opt/flink/fraud-detection-job.jar

echo "🚀  Submitting job to Flink..."
docker exec -i flink-jobmanager flink run -d -c com.fraud_detection.flink.FlinkJob /opt/flink/fraud-detection-job.jar

echo "Job submit selesai."
exit 0