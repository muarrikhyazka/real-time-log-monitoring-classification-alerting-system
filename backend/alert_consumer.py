import json
import os
import requests
import logging
from kafka import KafkaConsumer
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self):
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

    def send_slack_alert(self, alert_data):
        """Send alert to Slack"""
        if not self.slack_webhook_url:
            logger.warning("Slack webhook URL not configured")
            return

        try:
            window = alert_data.get('window', {})
            start_time = window.get('start', 'Unknown')
            end_time = window.get('end', 'Unknown')

            message = {
                "text": "🚨 Log Alert Triggered",
                "attachments": [
                    {
                        "color": "danger",
                        "fields": [
                            {
                                "title": "Service",
                                "value": alert_data.get('service_name', 'Unknown'),
                                "short": True
                            },
                            {
                                "title": "Category",
                                "value": alert_data.get('category', 'Unknown'),
                                "short": True
                            },
                            {
                                "title": "Count",
                                "value": str(alert_data.get('count', 0)),
                                "short": True
                            },
                            {
                                "title": "Time Window",
                                "value": f"{start_time} - {end_time}",
                                "short": True
                            }
                        ],
                        "footer": "Log Monitoring System",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }

            response = requests.post(
                self.slack_webhook_url,
                json=message,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("Alert sent to Slack successfully")
            else:
                logger.error(f"Failed to send Slack alert: {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")

    def send_telegram_alert(self, alert_data):
        """Send alert to Telegram"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            logger.warning("Telegram configuration not set")
            return

        try:
            window = alert_data.get('window', {})
            start_time = window.get('start', 'Unknown')
            end_time = window.get('end', 'Unknown')

            message = f"""🚨 *Log Alert Triggered*

*Service:* {alert_data.get('service_name', 'Unknown')}
*Category:* {alert_data.get('category', 'Unknown')}
*Count:* {alert_data.get('count', 0)}
*Time Window:* {start_time} - {end_time}
*Alert Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """

            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"

            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info("Alert sent to Telegram successfully")
            else:
                logger.error(f"Failed to send Telegram alert: {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")

    def process_alert(self, alert_data):
        """Process and send alert via configured channels"""
        logger.info(f"Processing alert: {alert_data}")

        # Send to Slack (disabled for now, but code kept for future use)
        # self.send_slack_alert(alert_data)

        # Send to Telegram
        self.send_telegram_alert(alert_data)

def main():
    """Main function to consume alerts and send notifications"""
    logger.info("Starting Alert Consumer...")

    alert_manager = AlertManager()

    # Kafka consumer configuration
    consumer = KafkaConsumer(
        'alerts',
        bootstrap_servers=[os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest',
        group_id='alert_consumer_group',
        enable_auto_commit=True,
        auto_commit_interval_ms=5000,
        max_poll_interval_ms=300000,  # 5 minutes
        max_poll_records=10,
        session_timeout_ms=30000,  # 30 seconds
        heartbeat_interval_ms=10000,  # 10 seconds
        request_timeout_ms=60000  # 1 minute (must be > session_timeout_ms)
    )

    logger.info("Listening for alerts...")

    try:
        for message in consumer:
            alert_data = message.value
            alert_manager.process_alert(alert_data)

    except KeyboardInterrupt:
        logger.info("Shutting down alert consumer...")
    except Exception as e:
        logger.error(f"Error in alert consumer: {e}")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()