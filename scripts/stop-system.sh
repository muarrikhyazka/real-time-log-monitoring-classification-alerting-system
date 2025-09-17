#!/bin/bash

# Stop Log Monitoring System
# This script stops all components of the log monitoring system

set -e

echo "=== Stopping Log Monitoring System ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to kill process by PID file
kill_process() {
    local pid_file=$1
    local process_name=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            print_status "Stopping $process_name (PID: $pid)..."
            kill "$pid"
            rm "$pid_file"
        else
            print_warning "$process_name process not running"
            rm "$pid_file"
        fi
    else
        print_warning "$process_name PID file not found"
    fi
}

# Stop background processes
print_status "Stopping background processes..."
kill_process ".alert_consumer.pid" "Alert Consumer"
kill_process ".spark_processor.pid" "Spark Processor"
kill_process ".music_producer.pid" "Music Producer"
kill_process ".hsearch_producer.pid" "HSearch Producer"

# Stop Docker services
print_status "Stopping Docker services..."
docker-compose down

# Optional: Remove volumes (uncomment if you want to clean data)
# print_warning "Removing volumes and data..."
# docker-compose down -v

# Kill any remaining processes
print_status "Cleaning up any remaining processes..."
pkill -f "log_processor.py" 2>/dev/null || true
pkill -f "alert_consumer.py" 2>/dev/null || true
pkill -f "music_recommender_producer.py" 2>/dev/null || true
pkill -f "hsearch_producer.py" 2>/dev/null || true

# Clean up temporary files
print_status "Cleaning up temporary files..."
rm -f .*.pid
rm -rf /tmp/checkpoint*

echo ""
print_status "=== System Stopped ==="
print_status "✅ Background processes stopped"
print_status "✅ Docker services stopped"
print_status "✅ Temporary files cleaned"

echo ""
print_status "System shutdown completed! 🛑"

echo ""
print_status "To start the system again, run: bash scripts/start-system.sh"