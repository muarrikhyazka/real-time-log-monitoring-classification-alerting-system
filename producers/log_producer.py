import json
import logging
import os
import socket
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError

class LogProducer:
    def __init__(self, service_name, kafka_servers='localhost:9092'):
        self.service_name = service_name
        self.hostname = socket.gethostname()

        # Configure Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=[kafka_servers],
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            acks=1,  # Changed from 'all' to reduce latency
            retries=3,
            retry_backoff_ms=1000,
            request_timeout_ms=60000,  # 1 minute
            max_block_ms=10000,  # 10 seconds max blocking
            linger_ms=100,  # Batch messages for better throughput
            compression_type='gzip'  # Compress messages to reduce network load
        )

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def send_log(self, message, level='INFO'):
        """Send a log message to Kafka"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'service_name': self.service_name,
                'message': message,
                'level': level,
                'host': self.hostname
            }

            # Send to Kafka
            future = self.producer.send('logs', value=log_entry)

            # Optional: Wait for confirmation (synchronous)
            # result = future.get(timeout=10)

            self.logger.debug(f"Log sent: {log_entry}")

        except KafkaError as e:
            self.logger.error(f"Failed to send log to Kafka: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error sending log: {e}")

    def send_info(self, message):
        """Send INFO level log"""
        self.send_log(message, 'INFO')

    def send_warning(self, message):
        """Send WARNING level log"""
        self.send_log(message, 'WARN')

    def send_error(self, message):
        """Send ERROR level log"""
        self.send_log(message, 'ERROR')

    def send_debug(self, message):
        """Send DEBUG level log"""
        self.send_log(message, 'DEBUG')

    def close(self):
        """Close the producer"""
        if self.producer:
            self.producer.close()

# Custom logging handler to send logs to Kafka
class KafkaLogHandler(logging.Handler):
    def __init__(self, service_name, kafka_servers='localhost:9092'):
        super().__init__()
        self.log_producer = LogProducer(service_name, kafka_servers)

    def emit(self, record):
        """Send log record to Kafka"""
        try:
            message = self.format(record)
            level = record.levelname
            self.log_producer.send_log(message, level)
        except Exception:
            self.handleError(record)

    def close(self):
        """Close the handler"""
        self.log_producer.close()
        super().close()

# Example usage function
def setup_kafka_logging(service_name, kafka_servers='localhost:9092'):
    """Set up logging to send logs to Kafka"""
    logger = logging.getLogger()

    # Create Kafka handler
    kafka_handler = KafkaLogHandler(service_name, kafka_servers)
    kafka_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    kafka_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(kafka_handler)

    return logger

if __name__ == "__main__":
    # Example usage
    producer = LogProducer("test-service")

    # Send some test logs
    producer.send_info("Application started successfully")
    producer.send_warning("High memory usage detected")
    producer.send_error("Database connection failed")
    producer.send_info("User login successful")

    producer.close()