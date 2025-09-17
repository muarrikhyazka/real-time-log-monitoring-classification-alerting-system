#!/bin/bash

# Start Log Monitoring System
# This script starts all components of the log monitoring system

set -e

echo "=== Starting Log Monitoring System ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose not found. Please install Docker Compose."
    exit 1
fi

# Step 1: Start infrastructure services
print_status "Starting infrastructure services (Kafka, Elasticsearch, Spark)..."
docker-compose up -d kafka elasticsearch kibana spark-master spark-worker kafka-ui

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Step 2: Set up Kafka topics
print_status "Setting up Kafka topics..."
bash scripts/setup-kafka-topics.sh

# Step 3: Set up Elasticsearch index
print_status "Setting up Elasticsearch index..."
bash scripts/setup-elasticsearch.sh

# Step 4: Start backend services
print_status "Starting backend API..."
docker-compose up -d backend

# Step 5: Start frontend
print_status "Starting frontend dashboard..."
docker-compose up -d frontend

# Step 6: Start alert consumer (in background)
print_status "Starting alert consumer..."
cd backend
python alert_consumer.py &
ALERT_PID=$!
cd ..

# Step 7: Start Spark streaming job (in background)
print_status "Starting Spark streaming job..."
cd spark
python log_processor.py &
SPARK_PID=$!
cd ..

# Step 8: Start log producers for testing (optional)
print_status "Starting log producers (for testing)..."
cd producers
python music_recommender_producer.py &
MUSIC_PID=$!

python hsearch_producer.py &
HSEARCH_PID=$!
cd ..

# Save PIDs for cleanup
echo "$ALERT_PID" > .alert_consumer.pid
echo "$SPARK_PID" > .spark_processor.pid
echo "$MUSIC_PID" > .music_producer.pid
echo "$HSEARCH_PID" > .hsearch_producer.pid

echo ""
print_status "=== System Status ==="
print_status "✅ Infrastructure services started"
print_status "✅ Kafka topics created"
print_status "✅ Elasticsearch index configured"
print_status "✅ Backend API started"
print_status "✅ Frontend dashboard started"
print_status "✅ Alert consumer started"
print_status "✅ Spark streaming job started"
print_status "✅ Log producers started (for testing)"

echo ""
print_status "=== Access URLs ==="
print_status "Dashboard:        http://localhost:3000"
print_status "API:              http://localhost:8000"
print_status "Kafka UI:         http://localhost:8080"
print_status "Kibana:           http://localhost:5601"
print_status "Spark UI:         http://localhost:8081"
print_status "Elasticsearch:    http://localhost:9200"

echo ""
print_status "=== Next Steps ==="
print_status "1. Open the dashboard at http://localhost:3000"
print_status "2. Check the API health at http://localhost:8000/health"
print_status "3. Monitor Kafka topics at http://localhost:8080"
print_status "4. Configure alerts in backend/alert_consumer.py"
print_status "5. Set up Cloudflare tunnel for remote access"

echo ""
print_warning "To stop the system, run: bash scripts/stop-system.sh"

echo ""
print_status "System startup completed! 🚀"