from confluent_kafka.admin import AdminClient, NewTopic

TRANSACTIONS_RAW = "transactions_raw"
TRANSACTIONS_ENRICHED = "transactions_enriched"
TRANSACTIONS_FRAUD_INVESTIGATION = "fraud_investigation"
TRANSACTIONS_FRAUD_ALERT = "transactions_fraud_alert"
FRAUD_AI_RULE_BASE_INPUT = "fraud_ai_rule_base_input"
FRAUD_BSCORE_INPUT = "fraud_bscore_input"
FRAUD_AI_RULE_BASE_OUTPUT = "fraud_ai_rule_base_output"
FRAUD_BSCORE_OUTPUT = "fraud_bscore_output"

class KafkaTopicsManager:
    def __init__(self, bootstrap_servers='broker:29092'):
        self.admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})

    def create_topic(self, topic_name, num_partitions=1, replication_factor=1):
        topic_list = [NewTopic(topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
        fs = self.admin_client.create_topics(topic_list)

        for topic, f in fs.items():
            try:
                f.result()
                print(f"Topic '{topic}' berhasil dibuat.")
            except Exception as e:
                if 'TopicAlreadyExistsError' in str(e):
                    print(f"Topic '{topic}' sudah ada, lanjutkan tanpa error.")
                else:
                    print(f"Gagal membuat topic {topic}: {e}")

    def delete_topic(self, topic_name):
        """Menghapus topic Kafka (opsional)."""
        fs = self.admin_client.delete_topics([topic_name])
        for topic, f in fs.items():
            try:
                f.result()
                print(f"Topic '{topic}' berhasil dihapus.")
            except Exception as e:
                print(f"Gagal menghapus topic {topic}: {e}")

if __name__ == "__main__":
    ktm = KafkaTopicsManager()
    ktm.create_topic(TRANSACTIONS_RAW, num_partitions=3, replication_factor=1)
    ktm.create_topic(TRANSACTIONS_ENRICHED, num_partitions=3, replication_factor=1)
    ktm.create_topic(TRANSACTIONS_FRAUD_INVESTIGATION, num_partitions=3, replication_factor=1)
    ktm.create_topic(TRANSACTIONS_FRAUD_ALERT, num_partitions=3, replication_factor=1)
    ktm.create_topic(FRAUD_AI_RULE_BASE_INPUT, num_partitions=3, replication_factor=1)
    ktm.create_topic(FRAUD_BSCORE_INPUT, num_partitions=3, replication_factor=1)
    ktm.create_topic(FRAUD_AI_RULE_BASE_OUTPUT, num_partitions=3, replication_factor=1)
    ktm.create_topic(FRAUD_BSCORE_OUTPUT, num_partitions=3, replication_factor=1)
    import time
    print("Waiting Kafka to sync topics...")
    time.sleep(2)

