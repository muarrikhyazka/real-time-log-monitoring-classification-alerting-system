#!/bin/bash

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
sleep 30

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