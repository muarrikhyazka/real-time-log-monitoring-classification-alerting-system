from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from elasticsearch import Elasticsearch
from kafka import KafkaConsumer
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
import logging
from pydantic import BaseModel
import threading
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Log Monitoring API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Elasticsearch client
es = Elasticsearch([os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")])

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Pydantic models
class LogEntry(BaseModel):
    timestamp: str
    service_name: str
    message: str
    level: str
    host: str
    category: str

class LogQuery(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    service_name: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    limit: int = 100

class LogStats(BaseModel):
    total_logs: int
    categories: dict
    services: dict
    levels: dict

# Authentication (simple implementation)
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Simple token verification - replace with proper JWT validation
    if credentials.credentials != "your-secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials

@app.get("/")
async def root():
    return {"message": "Log Monitoring API", "status": "running"}

@app.get("/health")
async def health_check():
    try:
        # Check Elasticsearch connection
        es_health = es.ping()
        return {
            "status": "healthy",
            "elasticsearch": "connected" if es_health else "disconnected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/logs/search")
async def search_logs(query: LogQuery):
    try:
        # Build Elasticsearch query
        es_query = {
            "query": {
                "bool": {
                    "must": []
                }
            },
            "sort": [
                {"@timestamp": {"order": "desc"}}
            ],
            "size": query.limit
        }

        # Add filters
        if query.start_time or query.end_time:
            time_range = {}
            if query.start_time:
                time_range["gte"] = query.start_time
            if query.end_time:
                time_range["lte"] = query.end_time

            es_query["query"]["bool"]["must"].append({
                "range": {"@timestamp": time_range}
            })

        if query.service_name:
            es_query["query"]["bool"]["must"].append({
                "term": {"service_name": query.service_name}
            })

        if query.category:
            es_query["query"]["bool"]["must"].append({
                "term": {"category": query.category}
            })

        if query.level:
            es_query["query"]["bool"]["must"].append({
                "term": {"level": query.level}
            })

        # Execute search
        response = es.search(index="logs_classified", body=es_query)

        logs = []
        for hit in response["hits"]["hits"]:
            logs.append(hit["_source"])

        return {
            "logs": logs,
            "total": response["hits"]["total"]["value"],
            "took": response["took"]
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs/stats")
async def get_log_stats():
    try:
        # Get overall stats
        total_query = {"query": {"match_all": {}}}
        total_response = es.count(index="logs_classified", body=total_query)
        total_logs = total_response["count"]

        # Get category aggregation
        agg_query = {
            "size": 0,
            "aggs": {
                "categories": {
                    "terms": {"field": "category"}
                },
                "services": {
                    "terms": {"field": "service_name"}
                },
                "levels": {
                    "terms": {"field": "level"}
                }
            }
        }

        agg_response = es.search(index="logs_classified", body=agg_query)

        categories = {bucket["key"]: bucket["doc_count"]
                     for bucket in agg_response["aggregations"]["categories"]["buckets"]}
        services = {bucket["key"]: bucket["doc_count"]
                   for bucket in agg_response["aggregations"]["services"]["buckets"]}
        levels = {bucket["key"]: bucket["doc_count"]
                 for bucket in agg_response["aggregations"]["levels"]["buckets"]}

        return LogStats(
            total_logs=total_logs,
            categories=categories,
            services=services,
            levels=levels
        )

    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs/trends")
async def get_log_trends(hours: int = 24):
    try:
        start_time = datetime.now() - timedelta(hours=hours)

        trend_query = {
            "size": 0,
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": start_time.isoformat()
                    }
                }
            },
            "aggs": {
                "logs_over_time": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "fixed_interval": "1h"
                    },
                    "aggs": {
                        "categories": {
                            "terms": {"field": "category"}
                        }
                    }
                }
            }
        }

        response = es.search(index="logs_classified", body=trend_query)

        trends = []
        for bucket in response["aggregations"]["logs_over_time"]["buckets"]:
            timestamp = bucket["key_as_string"]
            total = bucket["doc_count"]
            categories = {cat["key"]: cat["doc_count"]
                         for cat in bucket["categories"]["buckets"]}

            trends.append({
                "timestamp": timestamp,
                "total": total,
                "categories": categories
            })

        return {"trends": trends}

    except Exception as e:
        logger.error(f"Trends error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task for streaming logs to WebSocket
async def stream_logs():
    """Stream new logs to WebSocket clients"""
    try:
        consumer = KafkaConsumer(
            'logs',
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest'
        )

        for message in consumer:
            log_data = message.value
            await manager.broadcast(json.dumps(log_data))

    except Exception as e:
        logger.error(f"Log streaming error: {e}")

# Background task for streaming alerts
async def stream_alerts():
    """Stream alerts to WebSocket clients"""
    try:
        consumer = KafkaConsumer(
            'alerts',
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest'
        )

        for message in consumer:
            alert_data = message.value
            await manager.broadcast(json.dumps({
                "type": "alert",
                "data": alert_data
            }))

    except Exception as e:
        logger.error(f"Alert streaming error: {e}")

# Start background tasks
@app.on_event("startup")
async def startup_event():
    # Start background streaming tasks
    asyncio.create_task(stream_logs())
    asyncio.create_task(stream_alerts())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)