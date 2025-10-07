#!/bin/bash

# Master Integration Script
# Sets up log monitoring for all projects

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Log Monitoring System - Project Integration Setup  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Select projects to integrate:${NC}"
echo "1) Music Recommender"
echo "2) HSearch"
echo "3) Both"
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}Integrating Music Recommender...${NC}"
        bash "$SCRIPT_DIR/integrate-music-recommender.sh"
        ;;
    2)
        echo ""
        echo -e "${GREEN}Integrating HSearch...${NC}"
        bash "$SCRIPT_DIR/integrate-hsearch.sh"
        ;;
    3)
        echo ""
        echo -e "${GREEN}Integrating Music Recommender...${NC}"
        bash "$SCRIPT_DIR/integrate-music-recommender.sh"
        echo ""
        echo -e "${GREEN}Integrating HSearch...${NC}"
        bash "$SCRIPT_DIR/integrate-hsearch.sh"
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              Integration Summary                     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ Project integration(s) completed successfully!${NC}"
echo ""
echo -e "${YELLOW}Access your log monitoring system:${NC}"
echo "  • Dashboard:    https://log.myghty.cloud"
echo "  • API:          https://log-api.myghty.cloud"
echo "  • Kafka UI:     https://log-kafka.myghty.cloud"
echo "  • Kibana:       https://log-kibana.myghty.cloud"
echo "  • Spark UI:     https://log-spark.myghty.cloud"
echo ""
echo -e "${YELLOW}Local access:${NC}"
echo "  • Dashboard:    http://localhost:3003"
echo "  • API:          http://localhost:8000"
echo "  • Kafka UI:     http://localhost:8088"
echo "  • Kibana:       http://localhost:5602"
echo "  • Spark UI:     http://localhost:8082"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Add 'import logger_config' to your application's main file"
echo "2. Restart your application(s)"
echo "3. Check the dashboard to see your logs in real-time!"
echo ""
