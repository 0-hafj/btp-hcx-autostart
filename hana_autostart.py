import os
import requests
import json

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = os.getenv("TOKEN_URL")  # must include /oauth/token
SERVICE_MANAGER_URL = os.getenv("SERVICE_MANAGER_URL")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")

def get_oauth_token():
    """Fetch OAuth token from BTP Service Manager"""
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(TOKEN_URL, data=data, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()["access_token"]

def get_instance(token):
    """Fetch HANA Cloud instance info from v1 Service Manager API"""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{SERVICE_MANAGER_URL}/v1/service_instances", headers=headers, timeout=10)
    resp.raise_for_status()
    instances = resp.json().get("items", [])

    for inst in instances:
        if inst["name"] == INSTANCE_NAME or inst.get("context", {}).get("instance_name") == INSTANCE_NAME:
            return inst

    raise ValueError(f"HANA instance '{INSTANCE_NAME}' not found")

def get_instance_parameters(token, instance_id):
    """Fetch HANA Cloud instance parameters to check actual service status"""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{SERVICE_MANAGER_URL}/v1/service_instances/{instance_id}/parameters", headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

def start_instance(token, instance_id):
    """Start HANA instance via PATCH request"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "parameters": {
            "data": {
                "serviceStopped": False
            }
        }
    }
    print(f"▶ Sending PATCH request to start instance {instance_id}...")
    resp = requests.patch(f"{SERVICE_MANAGER_URL}/v1/service_instances/{instance_id}", headers=headers, json=body, timeout=10)
    resp.raise_for_status()
    print(f"✅ Start request sent for instance ID {instance_id}")

def main():
    print("🔐 Fetching OAuth token...")
    token = get_oauth_token()

    print(f"🔍 Fetching HANA Cloud instance '{INSTANCE_NAME}' info...")
    instance = get_instance(token)
    instance_id = instance.get("id")
    print(f"ℹ️ Instance ID: {instance_id}")

    print("ℹ️ Fetching instance parameters to check service status...")
    params = get_instance_parameters(token, instance_id)
    service_stopped = params.get("data", {}).get("serviceStopped", True)
    state = "STOPPED" if service_stopped else "RUNNING"
    print(f"ℹ️ HANA Cloud instance state: {state}")

    if service_stopped:
        print("▶ Instance is stopped, starting now...")
        start_instance(token, instance_id)
    else:
        print("✅ Instance is already running")

if __name__ == "__main__":
    main()
