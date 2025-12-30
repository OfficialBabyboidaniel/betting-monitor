#!/bin/bash

# Deployment script for Ubuntu server

echo "🚀 Deploying Rebel Betting Monitor..."

# Stop existing container if running
docker compose down

# Build and start the container
docker compose up -d --build

# Show logs
echo "📊 Container started. Showing logs..."
docker compose logs -f betting-monitor