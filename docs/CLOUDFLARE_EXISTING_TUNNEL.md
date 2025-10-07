# Adding Log Monitoring to Existing Cloudflare Tunnel

Since you already have a Cloudflare tunnel running on your server, you don't need to create a new one. Just add the log monitoring routes to your existing configuration.

## Option 1: Add Routes to Existing Tunnel Config (Recommended)

### Step 1: Locate Your Existing Tunnel Config

Your existing tunnel config is likely at:
```bash
/etc/cloudflared/config.yml
```

Or find it with:
```bash
sudo find /etc -name "config.yml" | grep cloudflared
```

### Step 2: Backup Your Config

```bash
sudo cp /etc/cloudflared/config.yml /etc/cloudflared/config.yml.backup
```

### Step 3: Add Log Monitoring Routes

Edit your existing config:
```bash
sudo nano /etc/cloudflared/config.yml
```

Add these routes to your existing `ingress:` section (BEFORE the catch-all rule):

```yaml
  # Log Monitoring Dashboard
  - hostname: log.myghty.cloud
    service: http://localhost:3003

  # Log Monitoring API
  - hostname: log-api.myghty.cloud
    service: http://localhost:8000

  # Kafka UI (optional)
  - hostname: log-kafka.myghty.cloud
    service: http://localhost:8088

  # Kibana (optional)
  - hostname: log-kibana.myghty.cloud
    service: http://localhost:5602

  # Spark UI (optional)
  - hostname: log-spark.myghty.cloud
    service: http://localhost:8082
```

**Example of complete config:**
```yaml
tunnel: YOUR_EXISTING_TUNNEL_ID
credentials-file: /path/to/your/credentials.json

ingress:
  # Your existing routes
  - hostname: existing-app.myghty.cloud
    service: http://localhost:8080

  # Add these new log monitoring routes
  - hostname: log.myghty.cloud
    service: http://localhost:3003
  - hostname: log-api.myghty.cloud
    service: http://localhost:8000
  - hostname: log-kafka.myghty.cloud
    service: http://localhost:8088
  - hostname: log-kibana.myghty.cloud
    service: http://localhost:5602
  - hostname: log-spark.myghty.cloud
    service: http://localhost:8082

  # Catch-all rule (must be last)
  - service: http_status:404
```

### Step 4: Add DNS Records

Use your existing tunnel ID:
```bash
# Find your tunnel ID
cloudflared tunnel list

# Add DNS records (replace TUNNEL_ID with your actual tunnel ID)
cloudflared tunnel route dns TUNNEL_ID log.myghty.cloud
cloudflared tunnel route dns TUNNEL_ID log-api.myghty.cloud
cloudflared tunnel route dns TUNNEL_ID log-kafka.myghty.cloud
cloudflared tunnel route dns TUNNEL_ID log-kibana.myghty.cloud
cloudflared tunnel route dns TUNNEL_ID log-spark.myghty.cloud
```

### Step 5: Restart Cloudflared

```bash
sudo systemctl restart cloudflared
sudo systemctl status cloudflared
```

### Step 6: Verify

Check the logs:
```bash
sudo journalctl -u cloudflared -f
```

Test the URLs:
```bash
curl -I https://log.myghty.cloud
```

## Option 2: Use Cloudflare Dashboard (GUI Method)

If you prefer using the Cloudflare dashboard:

1. Go to **Zero Trust** → **Networks** → **Tunnels**
2. Click on your existing tunnel
3. Go to **Public Hostname** tab
4. Click **Add a public hostname**

Add each of these:

| Subdomain | Domain | Service Type | URL |
|-----------|--------|--------------|-----|
| log | myghty.cloud | HTTP | localhost:3003 |
| log-api | myghty.cloud | HTTP | localhost:8000 |
| log-kafka | myghty.cloud | HTTP | localhost:8088 |
| log-kibana | myghty.cloud | HTTP | localhost:5602 |
| log-spark | myghty.cloud | HTTP | localhost:8082 |

5. Click **Save** for each hostname

No restart needed - changes are applied immediately!

## Troubleshooting

### Check if tunnel is running:
```bash
sudo systemctl status cloudflared
```

### View tunnel configuration:
```bash
sudo cat /etc/cloudflared/config.yml
```

### List all DNS routes:
```bash
cloudflared tunnel route dns list
```

### Check tunnel logs:
```bash
sudo journalctl -u cloudflared -n 100 --no-pager
```

### Test local services first:
```bash
curl http://localhost:3003  # Dashboard
curl http://localhost:8000/health  # API health check
```

## Access Your Services

Once configured, access your log monitoring system at:

- 📊 **Dashboard**: https://log.myghty.cloud
- 🔧 **API**: https://log-api.myghty.cloud
- 📈 **Kafka UI**: https://log-kafka.myghty.cloud
- 📉 **Kibana**: https://log-kibana.myghty.cloud
- ⚡ **Spark UI**: https://log-spark.myghty.cloud

All secured with HTTPS automatically by Cloudflare! 🔒
