"""
Log producer for hsearch system
This should be integrated into your existing hsearch codebase
"""

import logging
import random
import time
from log_producer import LogProducer, setup_kafka_logging

def integrate_with_hsearch():
    """
    Integration example for hsearch system

    Add this to your existing hsearch application:
    1. Import the LogProducer class
    2. Initialize it at application startup
    3. Replace existing logging calls with Kafka-enabled logging
    """

    # Initialize log producer for hsearch
    log_producer = LogProducer("hsearch")

    # Example integration points:

    # 1. Search operations
    def handle_search_query(query, user_id=None, results_count=0, response_time=None):
        try:
            message = f"Search query: '{query}' returned {results_count} results"
            if user_id:
                message += f" for user {user_id}"
            if response_time:
                message += f" in {response_time}ms"

            log_producer.send_info(message)

            # Performance monitoring
            if response_time and response_time > 1000:
                log_producer.send_warning(f"Slow search query: '{query}' took {response_time}ms")

            # Business metrics
            if results_count == 0:
                log_producer.send_info(f"No results found for query: '{query}'")

        except Exception as e:
            log_producer.send_error(f"Search query failed: '{query}' - {str(e)}")

    # 2. Index operations
    def handle_index_operation(operation, document_count=None, success=True):
        if success:
            message = f"Index {operation} completed successfully"
            if document_count:
                message += f" - {document_count} documents processed"
            log_producer.send_info(message)
        else:
            log_producer.send_error(f"Index {operation} failed")

    # 3. User activity tracking
    def track_user_activity(user_id, action, details=None):
        message = f"User {user_id} performed action: {action}"
        if details:
            message += f" - {details}"
        log_producer.send_info(message)

    # 4. System health monitoring
    def monitor_system_health(metric, value, threshold=None):
        message = f"System metric {metric}: {value}"
        if threshold and value > threshold:
            log_producer.send_warning(f"High {metric}: {value} (threshold: {threshold})")
        else:
            log_producer.send_info(message)

    # 5. API endpoint monitoring
    def monitor_api_endpoint(endpoint, method, status_code, response_time):
        message = f"{method} {endpoint} - {status_code} ({response_time}ms)"

        if status_code >= 500:
            log_producer.send_error(message)
        elif status_code >= 400:
            log_producer.send_warning(message)
        elif response_time > 2000:
            log_producer.send_warning(f"Slow API response: {message}")
        else:
            log_producer.send_info(message)

    # 6. Security and authentication
    def security_event(event_type, user_id=None, ip_address=None, details=None):
        message = f"Security event: {event_type}"
        if user_id:
            message += f" - User: {user_id}"
        if ip_address:
            message += f" - IP: {ip_address}"
        if details:
            message += f" - {details}"

        log_producer.send_warning(message)

    return {
        'log_producer': log_producer,
        'handle_search_query': handle_search_query,
        'handle_index_operation': handle_index_operation,
        'track_user_activity': track_user_activity,
        'monitor_system_health': monitor_system_health,
        'monitor_api_endpoint': monitor_api_endpoint,
        'security_event': security_event
    }

def simulate_hsearch_logs():
    """Simulate logs from hsearch system for testing"""
    log_producer = LogProducer("hsearch")

    sample_queries = [
        "python tutorial", "machine learning", "react components",
        "docker deployment", "elasticsearch query", "kafka streaming",
        "neural networks", "data science", "web development", "cloud computing"
    ]

    sample_users = ["user_001", "user_002", "user_003", "user_004", "user_005"]
    sample_ips = ["192.168.1.100", "10.0.0.50", "172.16.0.25", "203.0.113.10"]

    events = [
        # Search events
        lambda: log_producer.send_info(
            f"Search query: '{random.choice(sample_queries)}' returned {random.randint(0, 1000)} results for user {random.choice(sample_users)} in {random.randint(50, 2000)}ms"
        ),
        lambda: log_producer.send_info(f"Popular search term trending: '{random.choice(sample_queries)}'"),
        lambda: log_producer.send_info(f"User {random.choice(sample_users)} clicked result #1 for query '{random.choice(sample_queries)}'"),

        # Index operations
        lambda: log_producer.send_info(f"Index update completed - {random.randint(100, 5000)} documents processed"),
        lambda: log_producer.send_info("Full index rebuild started"),
        lambda: log_producer.send_info(f"New document indexed: doc_id_{random.randint(1000, 9999)}"),

        # Performance events
        lambda: log_producer.send_warning(f"High memory usage: {random.randint(80, 95)}%"),
        lambda: log_producer.send_warning(f"Search cluster response time: {random.randint(2000, 5000)}ms"),
        lambda: log_producer.send_info(f"Cache hit ratio: {random.randint(70, 95)}%"),

        # API monitoring
        lambda: log_producer.send_info(f"GET /api/search - 200 ({random.randint(100, 1000)}ms)"),
        lambda: log_producer.send_warning(f"POST /api/index - 429 ({random.randint(500, 2000)}ms) - Rate limit exceeded"),
        lambda: log_producer.send_error(f"GET /api/search - 500 ({random.randint(3000, 8000)}ms) - Internal server error"),

        # Security events
        lambda: log_producer.send_warning(f"Multiple failed authentication attempts from IP {random.choice(sample_ips)}"),
        lambda: log_producer.send_warning(f"Suspicious search pattern detected for user {random.choice(sample_users)}"),
        lambda: log_producer.send_warning(f"Rate limit exceeded for IP {random.choice(sample_ips)}"),

        # Business events
        lambda: log_producer.send_info(f"New user registration: {random.choice(sample_users)}"),
        lambda: log_producer.send_info(f"User {random.choice(sample_users)} upgraded to premium"),
        lambda: log_producer.send_info(f"Daily search quota reached for user {random.choice(sample_users)}"),

        # System events
        lambda: log_producer.send_info("Search service started successfully"),
        lambda: log_producer.send_info("Configuration reloaded"),
        lambda: log_producer.send_warning("Disk space low on search index partition"),
        lambda: log_producer.send_error("Failed to connect to external data source"),

        # Debug events
        lambda: log_producer.send_debug(f"Processing search request for user {random.choice(sample_users)}"),
        lambda: log_producer.send_debug(f"Cache miss for query: '{random.choice(sample_queries)}'"),
        lambda: log_producer.send_debug("Garbage collection completed")
    ]

    print("Starting hsearch log simulation...")
    try:
        while True:
            # Send random event
            event = random.choice(events)
            event()

            # Wait 2-8 seconds between events (reduced load)
            time.sleep(random.uniform(2, 8))

    except KeyboardInterrupt:
        print("Stopping log simulation...")
    finally:
        log_producer.close()

if __name__ == "__main__":
    # Run simulation for testing
    simulate_hsearch_logs()