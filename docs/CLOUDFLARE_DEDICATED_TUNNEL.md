# Setting Up Dedicated Cloudflare Tunnel for Log Monitoring

This guide shows you how to create a dedicated Cloudflare tunnel specifically for the log monitoring system.

## Why a Dedicated Tunnel?

- **Isolated**: Separate from your other applications
- **Easier networking**: All services on same Docker network
- **Simpler configuration**: No IP address conflicts

## Setup Steps

### 1. Create a New Tunnel in Cloudflare Dashboard

1. Go to https://one.dash.cloudflare.com
2. Navigate to **Zero Trust** → **Networks** → **Tunnels**
3. Click **Create a tunnel**
4. Choose **Cloudflared**
5. Name it: `log-monitoring`
6. Click **Save tunnel**

### 2. Get the Tunnel Token

After creating the tunnel, you'll see an **Install connector** page with a token. Copy the entire token (it looks like a long string).

### 3. Add Token to Environment File

On your server:

```bash
cd ~/real-time-log-monitoring-classification-alerting-system

# Create .env file
nano .env
```

Add this line (replace with your actual token):
```bash
CLOUDFLARE_TUNNEL_TOKEN=your_very_long_token_here
```

Save and exit (Ctrl+X, Y, Enter).

### 4. Configure Public Hostnames

Back in Cloudflare Dashboard, go to your new tunnel's **Public Hostname** tab and add these:

| Subdomain | Domain | Type | URL |
|-----------|--------|------|-----|
| log | myghty.cloud | HTTP | log-monitoring-frontend:3000 |
| log-api | myghty.cloud | HTTP | log-monitoring-backend:8000 |
| log-kafka | myghty.cloud | HTTP | kafka-ui:8080 |
| log-kibana | myghty.cloud | HTTP | kibana:5601 |
| log-spark | myghty.cloud | HTTP | spark-master:8080 |

**Note:** Use the container names directly since cloudflared will be on the same Docker network!

### 5. Start Cloudflared Container

```bash
cd ~/real-time-log-monitoring-classification-alerting-system

# Start cloudflared
docker compose -f docker-compose.yml -f docker-compose.cloudflare.yml up -d cloudflared

# Check logs
docker logs log-monitoring-cloudflared -f
```

You should see: `Connection <UUID> registered`

### 6. Test Access

```bash
curl -I https://log.myghty.cloud
```

You should get HTTP 200!

Open in browser:
- https://log.myghty.cloud
- https://log-api.myghty.cloud
- https://log-kafka.myghty.cloud
- https://log-kibana.myghty.cloud
- https://log-spark.myghty.cloud

## Troubleshooting

### Check if cloudflared is running:
```bash
docker ps | grep cloudflared
```

### Check cloudflared logs:
```bash
docker logs log-monitoring-cloudflared --tail 50
```

### Verify network connectivity:
```bash
# Check if cloudflared is on the right network
docker inspect log-monitoring-cloudflared | grep -A 10 Networks

# Test connection to frontend from cloudflared
docker exec log-monitoring-cloudflared wget -O- http://log-monitoring-frontend:3000 2>&1 | head -10
```

### Restart cloudflared:
```bash
docker restart log-monitoring-cloudflared
```

## Managing the Tunnel

### Stop cloudflared:
```bash
docker stop log-monitoring-cloudflared
```

### Start cloudflared:
```bash
docker start log-monitoring-cloudflared
```

### Remove cloudflared:
```bash
docker rm -f log-monitoring-cloudflared
```

## Benefits of This Approach

✅ **Simple container names**: Use `log-monitoring-frontend:3000` instead of IP addresses
✅ **Same network**: All services can communicate directly
✅ **Easy management**: Part of your docker-compose stack
✅ **Isolated**: Doesn't interfere with existing tunnels
✅ **Automatic startup**: Restarts with `unless-stopped` policy

## Alternative: Quick Start Script

Create a file `start-with-tunnel.sh`:

```bash
#!/bin/bash
echo "Starting Log Monitoring System with Cloudflare Tunnel..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create .env with your CLOUDFLARE_TUNNEL_TOKEN"
    exit 1
fi

# Start everything including cloudflared
docker compose -f docker-compose.yml -f docker-compose.cloudflare.yml up -d

echo "✓ All services started!"
echo ""
echo "Access your dashboard at: https://log.myghty.cloud"
```

Make it executable and run:
```bash
chmod +x start-with-tunnel.sh
./start-with-tunnel.sh
```
