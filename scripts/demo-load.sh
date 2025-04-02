#!/bin/bash

# Variables
API_ENDPOINT="http://localhost:8000"
DURATION=300  # 5 minutes
REQUESTS_PER_SECOND=10

echo "Generating load for the sample API for $DURATION seconds at $REQUESTS_PER_SECOND RPS..."

# Function to make a random API request
make_request() {
    # Array of endpoints
    endpoints=("/api/users" "/api/products" "/api/orders" "/api/status")
    
    # Select a random endpoint
    endpoint=${endpoints[$RANDOM % ${#endpoints[@]}]}
    
    # Make request and capture status code
    status_code=$(curl -s -o /dev/null -w "%{http_code}" $API_ENDPOINT$endpoint)
    
    # Log the request
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $endpoint - $status_code"
}

# Calculate delay between requests based on RPS
delay=$(bc -l <<< "scale=4; 1/$REQUESTS_PER_SECOND")

# Start time
start_time=$(date +%s)
end_time=$((start_time + DURATION))

# Counter for requests
request_count=0

# Make requests until duration is reached
while [ $(date +%s) -lt $end_time ]; do
    make_request &
    request_count=$((request_count + 1))
    
    # Sleep to maintain the desired RPS
    sleep $delay
    
    # Show progress every 50 requests
    if [ $((request_count % 50)) -eq 0 ]; then
        echo "Made $request_count requests..."
    fi
done
wait
echo "Load generation completed. Total requests made: $request_count"
echo "You can now check the observability stack for metrics and logs."
echo "Grafana dashboards should be updated with the new data."
echo "Access Grafana at: http://localhost:3000"
echo "Default credentials: admin/admin"
echo "Remember to stop the observability stack when done."