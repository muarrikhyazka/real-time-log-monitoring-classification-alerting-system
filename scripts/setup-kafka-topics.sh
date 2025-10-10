#!/bin/bash

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
  if docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1; then
    echo "Kafka is ready!"
    break
  fi
  echo "Waiting for Kafka... (attempt $((attempt+1))/$max_attempts)"
  sleep 2
  attempt=$((attempt+1))
done

if [ $attempt -eq $max_attempts ]; then
  echo "Error: Kafka failed to start in time"
  exit 1
fi

# Create Kafka topics
echo "Creating Kafka topics..."

# Create logs topic
docker exec kafka kafka-topics --create \
  --topic logs \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1 \
  --if-not-exists

# Create alerts topic
docker exec kafka kafka-topics --create \
  --topic alerts \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1 \
  --if-not-exists

echo "Kafka topics created successfully!"

# List topics to verify
echo "Current topics:"
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092