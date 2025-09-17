# Real-Time Log Monitoring System - Setup Guide

## Overview

This comprehensive guide will help you set up the Real-Time Log Monitoring & Classification Alerting System on your mini PC home server.

## System Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended) or macOS
- **RAM**: Minimum 8GB, recommended 16GB
- **CPU**: 4+ cores
- **Storage**: 50GB+ free space
- **Network**: Stable internet connection for Cloudflare tunnel

## Prerequisites

1. **Docker & Docker Compose**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Python 3.8+**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

3. **Git**
   ```bash
   sudo apt install git
   ```

## Installation Steps

### 1. Clone and Setup Project

```bash
# Clone the repository
git clone <your-repo-url>
cd real-time-log-monitoring-classification-alerting-system

# Make scripts executable
chmod +x scripts/*.sh

# Copy environment configuration
cp .env.example .env
```

### 2. Configure Environment

Edit the `.env` file with your specific settings:

```bash
nano .env
```

Update the following values:
- `SLACK_WEBHOOK_URL`: Your Slack webhook URL for alerts
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (optional)
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID (optional)
- `API_SECRET_TOKEN`: A secure token for API authentication

### 3. Start the System

```bash
# Start all services
bash scripts/start-system.sh
```

This script will:
- Start Kafka, Elasticsearch, Spark cluster
- Create required Kafka topics
- Set up Elasticsearch indices
- Start the backend API and frontend dashboard
- Launch the Spark streaming job
- Start alert consumers
- Run test log producers

### 4. Verify Installation

Check that all services are running:

```bash
# Check Docker containers
docker ps

# Check service health
curl http://localhost:8000/health

# Check frontend
open http://localhost:3000
```

## Integration with Existing Systems

### Music Recommender Integration

1. **Copy the log producer**:
   ```bash
   cp producers/log_producer.py /path/to/music-recommender/
   ```

2. **Install dependencies**:
   ```bash
   cd /path/to/music-recommender/
   pip install kafka-python
   ```

3. **Add to your application**:
   ```python
   from log_producer import LogProducer

   # Initialize at startup
   log_producer = LogProducer("music-recommender")

   # Use throughout your application
   log_producer.send_info("User login successful")
   log_producer.send_error("Database connection failed")
   ```

### HSearch Integration

Follow the same steps as above, but use `"hsearch"` as the service name:

```python
log_producer = LogProducer("hsearch")
```

## Cloudflare Tunnel Setup

### 1. Install Cloudflared

```bash
# Run the setup script
bash scripts/setup-cloudflare-tunnel.sh
```

### 2. Configure Tunnel

```bash
# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create log-monitoring

# Note the tunnel ID and update config/cloudflare-tunnel.yml
```

### 3. Set DNS Records

```bash
# Replace YOUR_TUNNEL_ID with actual tunnel ID
cloudflared tunnel route dns log-monitoring logs.yourdomain.com
cloudflared tunnel route dns log-monitoring logs-api.yourdomain.com
cloudflared tunnel route dns log-monitoring kafka-ui.yourdomain.com
```

### 4. Start Tunnel

```bash
# Test the tunnel
cloudflared tunnel --config config/cloudflare-tunnel.yml run

# Install as service (for production)
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

## System Monitoring

### Access Points

- **Dashboard**: http://localhost:3000 (or https://logs.yourdomain.com)
- **API**: http://localhost:8000 (or https://logs-api.yourdomain.com)
- **Kafka UI**: http://localhost:8080
- **Kibana**: http://localhost:5601
- **Spark UI**: http://localhost:8081
- **Elasticsearch**: http://localhost:9200

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Elasticsearch health
curl http://localhost:9200/_cluster/health

# Kafka topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

## Troubleshooting

### Common Issues

1. **Out of Memory**
   - Increase Docker memory limits
   - Reduce Spark executor memory in docker-compose.yml

2. **Port Conflicts**
   - Check if ports 3000, 8000, 8080, 9200 are available
   - Update port mappings in docker-compose.yml if needed

3. **Slow Performance**
   - Increase system RAM
   - Adjust Kafka and Elasticsearch settings
   - Optimize Spark configuration

### Log Locations

```bash
# Docker container logs
docker-compose logs -f [service-name]

# Spark streaming logs
tail -f spark/logs/streaming.log

# Alert consumer logs
tail -f backend/logs/alerts.log
```

### Restart Services

```bash
# Restart specific service
docker-compose restart [service-name]

# Full system restart
bash scripts/stop-system.sh
bash scripts/start-system.sh
```

## Maintenance

### Regular Tasks

1. **Monitor disk space**
   ```bash
   df -h
   docker system df
   ```

2. **Clean old logs**
   ```bash
   # Clean Elasticsearch indices older than 30 days
   curl -X DELETE "localhost:9200/logs_classified-$(date -d '30 days ago' +%Y.%m.%d)"
   ```

3. **Update system**
   ```bash
   git pull
   docker-compose pull
   bash scripts/stop-system.sh
   bash scripts/start-system.sh
   ```

### Backup Strategy

```bash
# Backup Elasticsearch data
docker exec elasticsearch elasticsearch-dump \
  --input=http://localhost:9200/logs_classified \
  --output=/backup/logs_$(date +%Y%m%d).json

# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/ .env
```

## Security Considerations

1. **Network Security**
   - Use Cloudflare tunnel instead of exposing ports directly
   - Configure firewall rules appropriately
   - Enable HTTPS through Cloudflare

2. **Authentication**
   - Change default API token in .env
   - Implement proper authentication for production use
   - Regularly rotate tokens and passwords

3. **Data Protection**
   - Encrypt sensitive log data
   - Implement log retention policies
   - Monitor access patterns

## Performance Tuning

### Elasticsearch

```yaml
# Add to docker-compose.yml elasticsearch environment
ES_JAVA_OPTS: "-Xms2g -Xmx2g"
```

### Kafka

```yaml
# Increase Kafka heap size
KAFKA_HEAP_OPTS: "-Xmx1G -Xms1G"
```

### Spark

```yaml
# Optimize Spark resources
SPARK_EXECUTOR_MEMORY: "4g"
SPARK_EXECUTOR_CORES: "4"
```

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review logs for error messages
3. Check system resources (CPU, memory, disk)
4. Verify network connectivity
5. Ensure all dependencies are properly installed

## Next Steps

1. Integrate with your existing music-recommender and hsearch systems
2. Configure alert channels (Slack/Telegram)
3. Set up monitoring and alerting rules
4. Implement log retention policies
5. Scale the system based on log volume