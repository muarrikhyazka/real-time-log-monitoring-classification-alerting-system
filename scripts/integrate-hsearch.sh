#!/bin/bash

# Integration Script for HSearch
# This script sets up log monitoring integration for the hsearch project

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== HSearch Log Monitoring Integration ===${NC}"

# Check if hsearch directory exists
if [ ! -d "$HOME/hsearch" ]; then
    echo -e "${RED}Error: hsearch directory not found at $HOME/hsearch${NC}"
    echo "Please specify the correct path:"
    read -r HSEARCH_DIR
    if [ ! -d "$HSEARCH_DIR" ]; then
        echo -e "${RED}Directory not found. Exiting.${NC}"
        exit 1
    fi
else
    HSEARCH_DIR="$HOME/hsearch"
fi

echo -e "${YELLOW}Using directory: $HSEARCH_DIR${NC}"

# Step 1: Copy log producer
echo -e "${GREEN}[1/4] Copying log producer...${NC}"
cp producers/log_producer.py "$HSEARCH_DIR/"
echo "✓ log_producer.py copied"

# Step 2: Create logger config
echo -e "${GREEN}[2/4] Creating logger configuration...${NC}"
cat > "$HSEARCH_DIR/logger_config.py" << 'EOF'
"""
Kafka Logger Configuration for HSearch
This module sets up automatic log forwarding to the log monitoring system
"""
from log_producer import LogProducer
import logging
import os

# Initialize log producer
KAFKA_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
log_producer = LogProducer("hsearch", kafka_servers=KAFKA_SERVERS)

class KafkaHandler(logging.Handler):
    """Custom handler that sends logs to Kafka"""

    def emit(self, record):
        try:
            msg = self.format(record)
            if record.levelno >= logging.ERROR:
                log_producer.send_error(msg)
            elif record.levelno >= logging.WARNING:
                log_producer.send_warning(msg)
            else:
                log_producer.send_info(msg)
        except Exception:
            self.handleError(record)

# Add Kafka handler to root logger
kafka_handler = KafkaHandler()
kafka_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
kafka_handler.setFormatter(formatter)
logging.getLogger().addHandler(kafka_handler)

print("✓ Kafka log monitoring enabled for hsearch")
EOF
echo "✓ logger_config.py created"

# Step 3: Install dependencies
echo -e "${GREEN}[3/4] Installing kafka-python...${NC}"
if [ -f "$HSEARCH_DIR/requirements.txt" ]; then
    if ! grep -q "kafka-python" "$HSEARCH_DIR/requirements.txt"; then
        echo "kafka-python==2.0.2" >> "$HSEARCH_DIR/requirements.txt"
        echo "✓ Added kafka-python to requirements.txt"
    else
        echo "✓ kafka-python already in requirements.txt"
    fi
fi

# Try to install
if command -v pip &> /dev/null; then
    pip install kafka-python==2.0.2
    echo "✓ kafka-python installed"
else
    echo -e "${YELLOW}Warning: pip not found. Please install kafka-python manually:${NC}"
    echo "  pip install kafka-python==2.0.2"
fi

# Step 4: Create integration guide
echo -e "${GREEN}[4/4] Creating integration guide...${NC}"
cat > "$HSEARCH_DIR/LOG_MONITORING_INTEGRATION.md" << 'EOF'
# Log Monitoring Integration

## Setup Complete! ✓

Your hsearch project is now integrated with the log monitoring system.

## Usage

Add this line to the top of your main application file (e.g., `app.py`, `main.py`):

```python
import logger_config  # Enable log monitoring
```

That's it! All your existing logging will now be automatically sent to the monitoring system.

## Example

```python
import logger_config  # Add this at the top
import logging

logger = logging.getLogger(__name__)

# Your existing code - no changes needed!
logger.info(f"Search query received: {query}")
logger.error(f"Search failed: {error}")
logger.warning("Search performance degraded")
```

## Access Logs

- **Dashboard**: https://log.myghty.cloud
- **API**: https://log-api.myghty.cloud
- **Kibana**: https://log-kibana.myghty.cloud

## Environment Variables

You can customize the Kafka server connection:

```bash
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
```

## Testing

To test the integration, run:

```python
import logger_config
import logging

logging.info("Test log from hsearch")
```

Then check the dashboard at https://log.myghty.cloud
EOF
echo "✓ Integration guide created at $HSEARCH_DIR/LOG_MONITORING_INTEGRATION.md"

echo ""
echo -e "${GREEN}=== Integration Complete! ===${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Add 'import logger_config' to your main app file"
echo "2. Read the integration guide: $HSEARCH_DIR/LOG_MONITORING_INTEGRATION.md"
echo "3. Restart your hsearch application"
echo "4. Check logs at https://log.myghty.cloud"
echo ""
