# System Architecture

## Overview

The Real-Time Log Monitoring & Classification Alerting System is a comprehensive solution that processes logs from multiple services in real-time, classifies them using NLP, stores them in Elasticsearch, and provides a web dashboard with alerting capabilities.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Music Recommender│    │     HSearch     │    │  Other Services │
│     System      │    │     System      │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │ Log Producer         │ Log Producer         │
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Apache Kafka                             │
│                     Topic: "logs"                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              Apache Spark Structured Streaming                  │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Parse     │  │   Classify  │  │    Windowed             │  │
│  │   JSON      │  │   with NLP  │  │    Aggregation          │  │
│  │   Logs      │  │   Pipeline  │  │    for Alerts           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────┬───────────────────┬───────────────────────────────────┘
          │                   │
          ▼                   ▼
┌─────────────────┐    ┌─────────────────┐
│  Elasticsearch  │    │  Kafka Topic    │
│                 │    │    "alerts"     │
│ Index:          │    └─────────┬───────┘
│ logs_classified │              │
└─────────┬───────┘              ▼
          │              ┌─────────────────┐
          │              │ Alert Consumer  │
          │              │                 │
          │              │ ┌─────────────┐ │
          │              │ │    Slack    │ │
          │              │ │  Webhook    │ │
          │              │ └─────────────┘ │
          │              │ ┌─────────────┐ │
          │              │ │  Telegram   │ │
          │              │ │     Bot     │ │
          │              │ └─────────────┘ │
          │              └─────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │    REST     │  │  WebSocket  │  │    Authentication      │  │
│  │     API     │  │   Streams   │  │      & Security         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   React Dashboard                               │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Real-time │  │   Charts &  │  │    Log Search &         │  │
│  │   Log Table │  │   Metrics   │  │    Filtering            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Cloudflare Tunnel                             │
│                                                                 │
│     Secure remote access to dashboard and APIs                  │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Log Sources

#### Music Recommender System
- **Purpose**: Generates logs from music recommendation service
- **Log Types**: User activities, recommendations, performance metrics, errors
- **Integration**: Python log producer sends structured JSON logs to Kafka

#### HSearch System
- **Purpose**: Search service log generation
- **Log Types**: Search queries, indexing operations, API calls, security events
- **Integration**: Python log producer integrated into existing codebase

### 2. Message Streaming Layer

#### Apache Kafka
- **Role**: Central message broker for log ingestion
- **Topics**:
  - `logs`: Raw log messages from all services
  - `alerts`: Processed alert messages
- **Configuration**: 3 partitions for `logs` topic, 1 partition for `alerts`
- **Retention**: 7 days for logs, 24 hours for alerts

### 3. Stream Processing Layer

#### Apache Spark Structured Streaming
- **Role**: Real-time log processing and classification
- **Features**:
  - JSON parsing and validation
  - NLP-based log classification
  - Windowed aggregation for alert detection
  - Multiple output sinks

#### NLP Classification Pipeline
- **Algorithm**: TF-IDF + Naive Bayes
- **Categories**: Security, Performance, Business, General
- **Training Data**: Pre-configured with common log patterns
- **Performance**: Real-time classification with <100ms latency

### 4. Storage Layer

#### Elasticsearch
- **Role**: Searchable log storage and analytics
- **Index**: `logs_classified` with time-based partitioning
- **Features**:
  - Full-text search on log messages
  - Aggregations for dashboard metrics
  - Retention policies for data management

### 5. API Layer

#### FastAPI Backend
- **Role**: REST API and WebSocket server
- **Endpoints**:
  - `/logs/search` - Log search with filters
  - `/logs/stats` - Aggregated statistics
  - `/logs/trends` - Time-series data
  - `/health` - System health check
- **WebSocket**: Real-time log streaming to frontend

### 6. Presentation Layer

#### React Dashboard
- **Features**:
  - Real-time log table with auto-refresh
  - Interactive charts (line charts, pie charts)
  - Advanced filtering and search
  - Alert notifications
  - Responsive design with Tailwind CSS

### 7. Alerting System

#### Alert Consumer
- **Role**: Processes alert messages from Kafka
- **Channels**: Slack webhooks, Telegram bot
- **Triggers**: Configurable thresholds for different log categories

### 8. Remote Access

#### Cloudflare Tunnel
- **Role**: Secure remote access without exposing ports
- **Features**:
  - HTTPS termination
  - DDoS protection
  - Access control
  - Multiple subdomain routing

## Data Flow

### 1. Log Ingestion
```
Application → Log Producer → Kafka (logs topic) → Spark Streaming
```

### 2. Processing Pipeline
```
Raw Log → JSON Parse → NLP Classification → Enrichment → Multiple Outputs
```

### 3. Storage and Retrieval
```
Enriched Log → Elasticsearch → FastAPI → React Dashboard
```

### 4. Alert Flow
```
High-severity Events → Windowed Aggregation → Kafka (alerts topic) → Alert Consumer → Slack/Telegram
```

### 5. Real-time Updates
```
New Logs → Kafka Consumer → WebSocket → Dashboard Updates
```

## Scalability Design

### Horizontal Scaling
- **Kafka**: Add more brokers and increase partitions
- **Spark**: Add worker nodes to the cluster
- **Elasticsearch**: Scale to multi-node cluster
- **Backend**: Deploy multiple API instances behind load balancer

### Vertical Scaling
- **Memory**: Increase heap sizes for JVM applications
- **CPU**: Allocate more cores for compute-intensive tasks
- **Storage**: Upgrade to faster SSDs for better I/O performance

## Security Architecture

### Network Security
- **Cloudflare Tunnel**: All external access through encrypted tunnel
- **Internal Network**: Services communicate within Docker network
- **Port Isolation**: No direct port exposure to internet

### Data Security
- **API Authentication**: Token-based authentication
- **Data Encryption**: TLS for all external communications
- **Log Sanitization**: Automatic removal of sensitive data patterns

### Access Control
- **Role-based Access**: Different access levels for different users
- **Audit Logging**: All system access logged and monitored
- **Rate Limiting**: API rate limiting to prevent abuse

## Monitoring and Observability

### System Metrics
- **Infrastructure**: CPU, memory, disk usage via Docker stats
- **Application**: Custom metrics from each service
- **Performance**: Response times, throughput, error rates

### Health Checks
- **Service Health**: Individual service health endpoints
- **Dependency Health**: Database and message broker connectivity
- **End-to-end Health**: Full pipeline health validation

### Alerting Strategy
- **Critical Alerts**: System failures, data loss
- **Warning Alerts**: Performance degradation, resource constraints
- **Info Alerts**: Deployment notifications, configuration changes

## Performance Characteristics

### Throughput
- **Log Ingestion**: 5,000+ logs per second
- **Processing Latency**: <2 seconds end-to-end
- **Query Performance**: <100ms for dashboard queries
- **Alert Latency**: <5 seconds for critical alerts

### Resource Requirements
- **Minimum**: 8GB RAM, 4 CPU cores, 50GB storage
- **Recommended**: 16GB RAM, 8 CPU cores, 200GB storage
- **Network**: 100Mbps for remote access via Cloudflare tunnel

## Fault Tolerance

### Data Durability
- **Kafka**: Replication factor for message durability
- **Elasticsearch**: Index replicas for data redundancy
- **Backup Strategy**: Regular snapshots of critical data

### Service Recovery
- **Auto-restart**: Docker restart policies for service recovery
- **Circuit Breakers**: Graceful degradation during service failures
- **Graceful Shutdown**: Clean shutdown procedures for maintenance

### Disaster Recovery
- **Configuration Backup**: Version-controlled configuration files
- **Data Backup**: Regular Elasticsearch snapshots
- **Infrastructure as Code**: Reproducible environment setup