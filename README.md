# Real-Time Log Monitoring & Classification Alerting System

A comprehensive real-time log monitoring system that processes logs from multiple services, classifies them using NLP, stores in Elasticsearch, and provides real-time dashboard with alerting capabilities.

## Architecture

- **Kafka**: Message streaming platform for log ingestion
- **Spark Structured Streaming**: Real-time log processing with NLP classification
- **Elasticsearch**: Storage and search engine for processed logs
- **FastAPI**: Backend API for dashboard queries
- **React Dashboard**: Real-time monitoring interface
- **Alert System**: Slack/Telegram notifications for critical events

## Quick Start

1. Start the infrastructure:
```bash
docker-compose up -d
```

2. Run the Spark streaming job:
```bash
cd spark && python log_processor.py
```

3. Start the backend API:
```bash
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. Start the frontend dashboard:
```bash
cd frontend && npm start
```

## System Components

- `/docker` - Docker Compose configuration
- `/spark` - Spark Structured Streaming application
- `/backend` - FastAPI backend service
- `/frontend` - React dashboard
- `/producers` - Log producer applications
- `/config` - Configuration files
- `/scripts` - Utility scripts

## Features

- Real-time log ingestion from multiple services
- NLP-based log classification (Security, Performance, Business)
- Elasticsearch storage with advanced search capabilities
- Interactive dashboard with live updates
- Automated alerting for critical events
- Cloudflare tunnel support for remote access