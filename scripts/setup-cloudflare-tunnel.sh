#!/bin/bash

# Cloudflare Tunnel Setup Script
# This script helps set up Cloudflare tunnel for remote access

echo "=== Cloudflare Tunnel Setup ==="

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "Installing cloudflared..."

    # For Linux
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
        sudo dpkg -i cloudflared-linux-amd64.deb
        rm cloudflared-linux-amd64.deb

    # For macOS
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install cloudflared

    # For Windows (requires manual download)
    else
        echo "Please download cloudflared from: https://github.com/cloudflare/cloudflared/releases"
        echo "And add it to your PATH"
        exit 1
    fi
fi

echo "cloudflared version:"
cloudflared version

echo ""
echo "=== Setup Instructions ==="
echo "1. Login to Cloudflare:"
echo "   cloudflared tunnel login"
echo ""
echo "2. Create a new tunnel:"
echo "   cloudflared tunnel create log-monitoring"
echo ""
echo "3. Configure DNS records for your domain:"
echo "   cloudflared tunnel route dns log-monitoring logs.yourdomain.com"
echo "   cloudflared tunnel route dns log-monitoring logs-api.yourdomain.com"
echo "   cloudflared tunnel route dns log-monitoring kafka-ui.yourdomain.com"
echo "   cloudflared tunnel route dns log-monitoring kibana.yourdomain.com"
echo "   cloudflared tunnel route dns log-monitoring spark.yourdomain.com"
echo ""
echo "4. Update the tunnel ID in config/cloudflare-tunnel.yml"
echo ""
echo "5. Copy your credentials file:"
echo "   sudo mkdir -p /etc/cloudflared"
echo "   sudo cp ~/.cloudflared/YOUR_TUNNEL_ID.json /etc/cloudflared/credentials.json"
echo ""
echo "6. Install the tunnel as a system service:"
echo "   sudo cloudflared service install"
echo ""
echo "7. Start the tunnel:"
echo "   sudo systemctl start cloudflared"
echo "   sudo systemctl enable cloudflared"
echo ""
echo "Or run the tunnel manually:"
echo "   cloudflared tunnel --config config/cloudflare-tunnel.yml run"
echo ""
echo "=== Important Notes ==="
echo "- Replace 'yourdomain.com' with your actual domain"
echo "- Make sure your domain is managed by Cloudflare"
echo "- Update the tunnel ID in the config file after creation"
echo "- Ensure all local services are running before starting the tunnel"