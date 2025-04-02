import json
import os

TARGETS_FILE = "/etc/prometheus/targets.json"

def load_targets():
    """Load the existing targets from the JSON file."""
    if not os.path.exists(TARGETS_FILE):
        return []
    with open(TARGETS_FILE, "r") as f:
        return json.load(f)

def save_targets(targets):
    """Save the updated targets to the JSON file."""
    with open(TARGETS_FILE, "w") as f:
        json.dump(targets, f, indent=2)
    print(f"✅ Updated {TARGETS_FILE} with new targets.")

def add_new_api(api_host, api_port):
    """Add a new API endpoint to Prometheus monitoring."""
    targets = load_targets()
    
    new_target = f"{api_host}:{api_port}"
    # Checking if the API is already being monitored
    if any(new_target in entry["targets"] for entry in targets):
        print(f"⚠️ API {new_target} is already being monitored.")
        return
    
    # Add new API target
    targets.append({"targets": [new_target], "labels": {"job": "sample-api"}})
    save_targets(targets)

    print(f"🚀 Added new API: {new_target}")

if __name__ == "__main__":
    api_host = input("Enter new API hostname (e.g., new-api): ")
    api_port = input("Enter API port (e.g., 8080): ")
    add_new_api(api_host, api_port)
