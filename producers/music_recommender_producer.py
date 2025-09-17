"""
Log producer for music-recommender system
This should be integrated into your existing music-recommender codebase
"""

import logging
import random
import time
from log_producer import LogProducer, setup_kafka_logging

def integrate_with_music_recommender():
    """
    Integration example for music-recommender system

    Add this to your existing music-recommender application:
    1. Import the LogProducer class
    2. Initialize it at application startup
    3. Replace existing logging calls with Kafka-enabled logging
    """

    # Initialize log producer for music-recommender
    log_producer = LogProducer("music-recommender")

    # Example integration points:

    # 1. User authentication events
    def handle_user_login(user_id, success=True):
        if success:
            log_producer.send_info(f"User {user_id} logged in successfully")
        else:
            log_producer.send_warning(f"Failed login attempt for user {user_id}")

    # 2. Music recommendation events
    def generate_recommendations(user_id, song_count):
        try:
            # Your existing recommendation logic here
            log_producer.send_info(f"Generated {song_count} recommendations for user {user_id}")

            # Business metrics
            log_producer.send_info(f"Recommendation request processed for user {user_id}")

        except Exception as e:
            log_producer.send_error(f"Failed to generate recommendations for user {user_id}: {str(e)}")

    # 3. Performance monitoring
    def monitor_api_performance(endpoint, response_time):
        if response_time > 5.0:
            log_producer.send_warning(f"Slow API response: {endpoint} took {response_time}s")
        else:
            log_producer.send_info(f"API {endpoint} responded in {response_time}s")

    # 4. Database operations
    def database_operation(operation, success=True, duration=None):
        if success:
            log_producer.send_info(f"Database {operation} completed successfully")
        else:
            log_producer.send_error(f"Database {operation} failed")

        if duration and duration > 2.0:
            log_producer.send_warning(f"Slow database operation: {operation} took {duration}s")

    # 5. Security events
    def security_event(event_type, user_id=None, details=None):
        message = f"Security event: {event_type}"
        if user_id:
            message += f" for user {user_id}"
        if details:
            message += f" - {details}"

        log_producer.send_warning(message)

    return {
        'log_producer': log_producer,
        'handle_user_login': handle_user_login,
        'generate_recommendations': generate_recommendations,
        'monitor_api_performance': monitor_api_performance,
        'database_operation': database_operation,
        'security_event': security_event
    }

def simulate_music_recommender_logs():
    """Simulate logs from music-recommender system for testing"""
    log_producer = LogProducer("music-recommender")

    sample_users = ["user_123", "user_456", "user_789", "user_101", "user_202"]
    sample_songs = ["song_a", "song_b", "song_c", "song_d", "song_e"]

    events = [
        # Business events
        lambda: log_producer.send_info(f"User {random.choice(sample_users)} played song {random.choice(sample_songs)}"),
        lambda: log_producer.send_info(f"Generated playlist for user {random.choice(sample_users)}"),
        lambda: log_producer.send_info(f"User {random.choice(sample_users)} liked song {random.choice(sample_songs)}"),
        lambda: log_producer.send_info(f"New user registration: {random.choice(sample_users)}"),

        # Performance events
        lambda: log_producer.send_warning(f"High CPU usage: {random.randint(80, 95)}%"),
        lambda: log_producer.send_warning(f"Database query took {random.uniform(3.0, 8.0):.2f}s"),
        lambda: log_producer.send_info(f"API response time: {random.uniform(0.1, 2.0):.2f}s"),

        # Security events
        lambda: log_producer.send_warning(f"Multiple failed login attempts for user {random.choice(sample_users)}"),
        lambda: log_producer.send_warning(f"Suspicious activity detected from IP {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"),

        # Error events
        lambda: log_producer.send_error("Failed to connect to recommendation service"),
        lambda: log_producer.send_error("Memory allocation error in music processing"),
        lambda: log_producer.send_error(f"Failed to load user profile for {random.choice(sample_users)}"),

        # General events
        lambda: log_producer.send_info("Music recommendation service started"),
        lambda: log_producer.send_info("Cache refreshed successfully"),
        lambda: log_producer.send_debug(f"Processing recommendation request for {random.choice(sample_users)}")
    ]

    print("Starting music-recommender log simulation...")
    try:
        while True:
            # Send random event
            event = random.choice(events)
            event()

            # Wait 1-5 seconds between events
            time.sleep(random.uniform(1, 5))

    except KeyboardInterrupt:
        print("Stopping log simulation...")
    finally:
        log_producer.close()

if __name__ == "__main__":
    # Run simulation for testing
    simulate_music_recommender_logs()