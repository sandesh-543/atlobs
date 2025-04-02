# **Observability Solution for API Debugging**

This repository contains a **comprehensive observability solution** designed to enhance the debugging experience for engineering teams. It addresses common challenges such as **slow, manual, and inconsistent debugging processes**, which often rely heavily on experienced engineers.  

## **Solution Overview**  

This solution implements a modern observability stack with:  
- **Prometheus** – Metrics collection and alerting  
- **Loki** – Log aggregation and querying  
- **Tempo** – Distributed tracing  
- **Grafana** – Unified visualization  
- **OpenTelemetry** – Standardized instrumentation  

## **Key Features**  

✅ **Unified Dashboard** – Integrated view of **metrics, logs, and traces**  
✅ **Correlated Data** – **TraceIDs link logs, metrics, and traces** for seamless debugging  
✅ **API Performance Focus** – Specialized **RED-method-based dashboards** for API monitoring  
✅ **Proactive Alerting** – **Predefined alert rules** for high error rates & latency spikes  
✅ **Guided Debugging** – Pre-built **queries & workflows** for common issues  
✅ **Low Overhead** – Efficient instrumentation with **~2-5ms per request latency impact**  

## **Setup Instructions**  

1. **Clone this repository**  
   ```bash
   git clone https://github.com/yourusername/obsatl.git
   cd obsatl
   ```
2. **Start the observability stack**  
   ```bash
   docker-compose up -d
   ```
3. **Start the sample application**  
   ```bash
   docker-compose -f docker-compose.sample-app.yaml up -d
   ```
4. **Generate sample load**  
   ```bash
   ./scripts/demo-load.sh
   ```
5. **Access Grafana**  
   - Open [http://localhost:3000](http://localhost:3000)  
   - Login with `admin/admin`  

## **Debugging & Troubleshooting**  

### **How to Investigate an API Issue?**  
- **Step 1:** Check the **API Performance Dashboard** → Look for **error rate spikes or high latency**  
- **Step 2:** Navigate to **Trace Explorer** → Filter by **TraceID** to track slow or failing requests  
- **Step 3:** Jump to **Loki Logs** → Use the same TraceID to view **corresponding logs**  
- **Step 4:** If an alert was triggered, check **AlertManager** logs for further diagnosis  

---

## **Alerting Setup (Prometheus & AlertManager)**  

The system automatically triggers **alerts when critical conditions occur**:  

| **Alert Name**    | **Condition**                                      | **Severity** | **Threshold** |
|-------------------|--------------------------------------------------|-------------|--------------|
| **High Error Rate**  | More than **5% API errors** over 5 minutes  | 🔴 Critical | `rate(http_server_requests_seconds_count{status!~"2.."}[5m]) > 0.05` |
| **High Latency** | p95 latency exceeds **1 second** for 3 intervals | 🟡 Warning  | `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1` |

Modify alert rules in [`config/alertmanager/alerts.yml`](config/alertmanager/alerts.yml) if needed.  

---

## **Directory Structure**  

```
/config         → Configuration files for all observability components  
/sample-app     → Sample application with OpenTelemetry instrumentation  
/docs          → Documentation, diagrams, and architecture details  
/scripts       → Utility scripts for setup and demo  
```

---

## **Dashboard Access**  

- 🔍 **[API Performance Dashboard](http://localhost:3000/d/api-performance/api-performance-dashboard)**  
- 🔴 **[Error Analysis Dashboard](http://localhost:3000/d/error-analysis/error-analysis-dashboard)**  
- 📌 **[Trace Explorer](http://localhost:3000/d/trace-explorer/trace-explorer)**  

---
