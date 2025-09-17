#!/bin/bash

# Wait for Elasticsearch to be ready
echo "Waiting for Elasticsearch to be ready..."
sleep 60

# Create index template for logs
echo "Creating Elasticsearch index template..."

curl -X PUT "localhost:9200/_index_template/logs_classified_template" \
  -H "Content-Type: application/json" \
  -d '{
    "index_patterns": ["logs_classified*"],
    "template": {
      "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
      },
      "mappings": {
        "properties": {
          "@timestamp": {
            "type": "date"
          },
          "service_name": {
            "type": "keyword"
          },
          "message": {
            "type": "text",
            "analyzer": "standard"
          },
          "level": {
            "type": "keyword"
          },
          "host": {
            "type": "keyword"
          },
          "category": {
            "type": "keyword"
          },
          "processed_timestamp": {
            "type": "date"
          }
        }
      }
    }
  }'

echo "Elasticsearch index template created successfully!"

# Check cluster health
echo "Elasticsearch cluster health:"
curl -X GET "localhost:9200/_cluster/health?pretty"