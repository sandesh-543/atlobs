from flask import Flask, request, jsonify
import time
import random
import logging
import os
import json
import uuid
from datetime import datetime

# Set up OpenTelemetry
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio
from opentelemetry.semconv.trace import SpanAttributes

# Configure OpenTelemetry
resource = Resource(attributes={
    SERVICE_NAME: os.environ.get("OTEL_SERVICE_NAME", "sample-api")
})

# Configure sampling: 100% of error traces, 10% of normal traces
sampler = ParentBasedTraceIdRatio(0.1)

trace.set_tracer_provider(TracerProvider(resource=resource, sampler=sampler))
tracer = trace.get_tracer(__name__)

# Configure exporter
otlp_exporter = OTLPSpanExporter(endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"))
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Create Flask app
app = Flask(__name__)

# Instrument Flask
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# Configure JSON logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        
        # Add trace context if available
        current_span = trace.get_current_span()
        if current_span:
            span_context = current_span.get_span_context()
            if span_context.is_valid:
                log_record["trace_id"] = format(span_context.trace_id, '032x')
                log_record["span_id"] = format(span_context.span_id, '016x')
        
        # Add extra attributes from the log record
        if hasattr(record, 'extras'):
            log_record.update(record.extras)
            
        return json.dumps(log_record)

# Configure logger
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

# Middleware to add request ID
@app.before_request
def before_request():
    request.request_id = str(uuid.uuid4())
    
# Middleware to log request completion
@app.after_request
def after_request(response):
    # Add request details to log
    logger.info(
        f"Request completed: {request.method} {request.path}",
        extra={
            "extras": {
                "request_id": getattr(request, 'request_id', 'unknown'),
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "response_time_ms": getattr(request, 'response_time', 0),
                "user_agent": request.headers.get('User-Agent', 'unknown')
            }
        }
    )
    return response

# Simulated database functions
def query_database(query_type="read"):
    with tracer.start_as_current_span("database_query", attributes={
        "db.system": "postgres",
        "db.operation": query_type
    }) as span:
        # Simulate occasional slow queries
        if random.random() < 0.1:  # 10% chance of slow query
            delay = random.uniform(1.0, 3.0)
            span.set_attribute("db.slow_query", True)
            span.set_attribute("db.query_time_ms", delay * 1000)
            logger.warning(f"Slow database query detected: {delay:.2f}s", 
                          extra={"extras": {"query_type": query_type, "delay": delay}})
        else:
            delay = random.uniform(0.05, 0.2)
            span.set_attribute("db.query_time_ms", delay * 1000)
        
        # Simulate occasional errors
        if random.random() < 0.05:  # 5% chance of error
            span.set_attribute("db.error", True)
            span.set_status(trace.Status(trace.StatusCode.ERROR, "Database connection error"))
            logger.error("Database query failed", 
                        extra={"extras": {"query_type": query_type, "error": "connection_error"}})
            raise Exception("Database connection error")
            
        time.sleep(delay)
        return {"success": True, "query_type": query_type}

# Simulated external API call
def call_external_api(api_name):
    with tracer.start_as_current_span("external_api_call", attributes={
        "http.method": "GET",
        "http.url": f"https://api.example.com/{api_name}"
    }) as span:
        # Simulate variable latency
        delay = random.uniform(0.1, 0.8)
        span.set_attribute("http.response_time_ms", delay * 1000)
        
        # Simulate occasional timeouts
        if random.random() < 0.08:  # 8% chance of timeout
            long_delay = random.uniform(2.0, 5.0)
            span.set_attribute("http.timeout", True)
            span.set_status(trace.Status(trace.StatusCode.ERROR, "API timeout"))
            logger.warning(f"External API timeout: {api_name}", 
                          extra={"extras": {"api": api_name, "delay": long_delay}})
            time.sleep(long_delay)
            raise Exception("External API timeout")
            
        time.sleep(delay)
        return {"success": True, "api": api_name}

# Routes
@app.route('/health')
def health():
    return {"status": "healthy"}

@app.route('/api/users')
def get_users():
    start_time = time.time()
    
    try:
        # Record request count and tags in span
        current_span = trace.get_current_span()
        current_span.set_attribute("request.type", "get_users")
        current_span.set_attribute("tenant.id", request.args.get('tenant', 'default'))
        
        # Log the request
        logger.info("Processing get_users request", 
                   extra={"extras": {"tenant": request.args.get('tenant', 'default')}})
        
        # Query the "database"
        result = query_database("read")
        
        # Simulate processing time
        processing_time = random.uniform(0.01, 0.05)
        time.sleep(processing_time)
        
        # Prepare response
        users = [
            {"id": 1, "name": "Alice Johnson", "email": "alice@example.com"},
            {"id": 2, "name": "Bob Smith", "email": "bob@example.com"},
            {"id": 3, "name": "Charlie Davis", "email": "charlie@example.com"}
        ]
        
        # Record the total processing time for metrics
        request.response_time = (time.time() - start_time) * 1000
        
        return jsonify({"users": users, "count": len(users)})
    
    except Exception as e:
        # Record error in the current span
        current_span = trace.get_current_span()
        current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
        
        # Log the error
        logger.error(f"Error processing get_users request: {str(e)}", 
                    extra={"extras": {"error": str(e)}})
        
        # Record the response time even for errors
        request.response_time = (time.time() - start_time) * 1000
        
        return jsonify({"error": str(e)}), 500

@app.route('/api/products')
def get_products():
    start_time = time.time()
    
    try:
        # Span context
        current_span = trace.get_current_span()
        current_span.set_attribute("request.type", "get_products")
        
        # Log the request
        logger.info("Processing get_products request")
        
        # Query the "database"
        result = query_database("read")
        
        # Call "external" product catalog API
        catalog = call_external_api("product-catalog")
        
        # Simulate processing time
        processing_time = random.uniform(0.03, 0.08)
        time.sleep(processing_time)
        
        # Prepare response
        products = [
            {"id": 101, "name": "Laptop", "price": 999.99},
            {"id": 102, "name": "Smartphone", "price": 699.99},
            {"id": 103, "name": "Headphones", "price": 149.99}
        ]
        
        # Record processing time
        request.response_time = (time.time() - start_time) * 1000
        
        return jsonify({"products": products, "count": len(products)})
    
    except Exception as e:
        # Record error
        current_span = trace.get_current_span()
        current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
        
        # Log error
        logger.error(f"Error processing get_products request: {str(e)}", 
                    extra={"extras": {"error": str(e)}})
        
        # Record response time
        request.response_time = (time.time() - start_time) * 1000
        
        return jsonify({"error": str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    start_time = time.time()
    
    try:
        # Span context
        current_span = trace.get_current_span()
        current_span.set_attribute("request.type", "create_order")
        
        # Log the request
        logger.info("Processing create_order request")
        
        # Get request data
        data = request.get_json() or {}
        
        # Validate data in a child span
        with tracer.start_as_current_span("validate_order"):
            time.sleep(random.uniform(0.01, 0.03))
            if 'product_id' not in data:
                raise ValueError("Missing product_id in request")
        
        # Query inventory status
        with tracer.start_as_current_span("check_inventory"):
            call_external_api("inventory-service")
        
        # Write to database
        result = query_database("write")
        
        # Process payment
        with tracer.start_as_current_span("process_payment"):
            call_external_api("payment-gateway")
            # Simulate occasional payment failures
            if random.random() < 0.1:
                raise ValueError("Payment processing failed")
        
        # Record processing time
        request.response_time = (time.time() - start_time) * 1000
        
        return jsonify({"order_id": str(uuid.uuid4()), "status": "created"})
    
    except ValueError as e:
        # Record validation error
        current_span = trace.get_current_span()
        current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
        
        # Log validation error
        logger.warning(f"Validation error in create_order: {str(e)}", 
                      extra={"extras": {"error": str(e), "error_type": "validation"}})
        
        # Record response time
        request.response_time = (time.time() - start_time) * 1000
        
        return jsonify({"error": str(e)}), 400
        
    except Exception as e:
        # Record error
        current_span = trace.get_current_span()
        current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
        
        # Log error
        logger.error(f"Error processing create_order request: {str(e)}", 
                    extra={"extras": {"error": str(e)}})
        
        # Record response time
        request.response_time = (time.time() - start_time) * 1000
        
        return jsonify({"error": str(e)}), 500

@app.route('/api/orders/<order_id>')
def get_order(order_id):
    start_time = time.time()
    
    try:
        # Span context
        current_span = trace.get_current_span()
        current_span.set_attribute("request.type", "get_order")
        current_span.set_attribute("order.id", order_id)
        
        # Log request
        logger.info(f"Retrieving order details", extra={"extras": {"order_id": order_id}})
        
        # Query database
        result = query_database("read")
        
        # Simulate occasional 404 for invalid order IDs
        if order_id.startswith("inv"):
            logger.warning(f"Order not found", extra={"extras": {"order_id": order_id}})
            request.response_time = (time.time() - start_time) * 1000
            return jsonify({"error": "Order not found"}), 404
        
        # Record processing time
        request.response_time = (time.time() - start_time) * 1000
        
        return jsonify({
            "order_id": order_id,
            "status": "shipped",
            "items": [
                {"product_id": 101, "quantity": 1, "price": 999.99}
            ],
            "total": 999.99
        })
        
    except Exception as e:
        # Record error
        current_span = trace.get_current_span()
        current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
        
        # Log error
        logger.error(f"Error retrieving order: {str(e)}", 
                    extra={"extras": {"error": str(e), "order_id": order_id}})
        
        # Record processing time
        request.response_time = (time.time() - start_time) * 1000
        
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)