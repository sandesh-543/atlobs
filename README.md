This repository contains a comprehensive observability solution designed to improve the debugging experience for engineering teams. It addresses the common challenges of slow, manual, and inconsistent debugging processes that depend heavily on experienced engineers.

## Solution Overview

The solution implements a modern observability stack with:
- **Prometheus**: For metrics collection and alerting
- **Loki**: For log aggregation and querying
- **Tempo**: For distributed tracing
- **Grafana**: For unified visualization
- **OpenTelemetry**: For standardized instrumentation

## Key Features

- **Unified Dashboard**: Integrated view of metrics, logs, and traces
- **Correlated Data**: TraceIDs link all observability data for seamless navigation
- **API Performance Focus**: Specialized dashboards for API endpoint monitoring
- **Guided Debugging**: Pre-built queries and workflows for common issues
- **Low Overhead**: Efficient instrumentation with minimal performance impact

## Setup Instructions

1. Clone this repository
   ```
   git clone https://github.com/yourusername/obsatl.git
   cd obsatl
   ```

2. Start the observability stack
   ```
   docker-compose up -d
   ```

3. Start the sample application
   ```
   docker-compose -f docker-compose.sample-app.yaml up -d
   ```

4. Generate sample load
   ```
   ./scripts/demo-load.sh
   ```

5. Access Grafana
   ```
   Open http://localhost:3000 in your browser
   Login with admin/admin
   ```

## Directory Structure

- `/config`: Configuration files for all observability components
- `/sample-app`: Sample application with instrumentation for demonstration
- `/docs`: Documentation and diagrams
- `/scripts`: Utility scripts for setup and demo

## Dashboard Access

- **API Performance Dashboard**: http://localhost:3000/d/api-performance/api-performance-dashboard
- **Error Analysis Dashboard**: http://localhost:3000/d/error-analysis/error-analysis-dashboard
- **Trace Explorer**: http://localhost:3000/d/trace-explorer/trace-explorer
