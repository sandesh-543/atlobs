#!/bin/bash

# Exit on error
set -e

echo "Setting up Observability..."

# Create required directories
mkdir -p config/prometheus
mkdir -p config/loki
mkdir -p config/tempo
mkdir -p config/otel-collector
mkdir -p config/grafana/provisioning/dashboards
mkdir -p config/grafana/provisioning/datasources
mkdir -p config/promtail
mkdir -p docs/screenshots

# Set permissions
chmod -R 777 config/

# Start the infrastructure
echo "Starting observability stack..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

echo "Checking service health..."
# Check if Grafana is running
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Grafana is running"
else
    echo "❌ Grafana is not responding"
fi

# Check if Prometheus is running
if curl -s http://localhost:9090/-/healthy > /dev/null; then
    echo "✅ Prometheus is running"
else
    echo "❌ Prometheus is not responding"
fi

# Check if Loki is running
if curl -s http://localhost:3100/ready > /dev/null; then
    echo "✅ Loki is running"
else
    echo "❌ Loki is not responding"
fi

# Check if Tempo is running
if curl -s http://localhost:3200/ready > /dev/null; then
    echo "✅ Tempo is running"
else
    echo "❌ Tempo is not responding"
fi

echo "Setup complete! Your observability stack is running."
echo "Access Grafana at: http://localhost:3000"
echo "Default credentials: admin/admin"
echo ""
echo "To generate sample traffic, run: ./scripts/demo-load.sh"