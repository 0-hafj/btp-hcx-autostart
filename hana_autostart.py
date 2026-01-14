#!/usr/bin/env python3

import os
import requests
import argparse
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
    """Fetch HANA Cloud instance info"""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{SERVICE_MANAGER_URL}/v1/service_instances",
        headers=headers,
        timeout=10
    )
    resp.raise_for_status()

    for inst in resp.json().get("items", []):
        if inst["name"] == INSTANCE_NAME or inst.get("context", {}).get("instance_name") == INSTANCE_NAME:
            return inst

    raise ValueError(f"HANA instance '{INSTANCE_NAME}' not found")


def get_instance_parameters(token, instance_id):
    """Fetch instance parameters (real runtime state)"""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{SERVICE_MANAGER_URL}/v1/service_instances/{instance_id}/parameters",
        headers=headers,
        timeout=10
    )
    resp.raise_for_status()
    return resp.json()


def patch_service_state(token, instance_id, service_stopped: bool):
    """Start or stop HANA Cloud instance"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "parameters": {
            "data": {
                "serviceStopped": service_stopped
            }
        }
    }

    action = "Stopping" if service_stopped else "Starting"
    print(f"▶ {action} HANA Cloud instance {instance_id}...")

    resp = requests.patch(
        f"{SERVICE_MANAGER_URL}/v1/service_instances/{instance_id}",
        headers=headers,
        json=body,
        timeout=10
    )
    resp.raise_for_status()

    print(f"✅ {action} request accepted")


def main():
    parser = argparse.ArgumentParser(
        description="HANA Cloud instance control tool"
    )
    parser.add_argument(
        "action",
        choices=["status", "start", "stop", "autostart"],
        help="Action to perform"
    )
    args = parser.parse_args()

    # Get token and instance info
    token = get_oauth_token()
    instance = get_instance(token)
    instance_id = instance["id"]

    # Get parameters
    params = get_instance_parameters(token, instance_id)

    data = params.get("data", {})
    service_stopped = data.get("serviceStopped")
    requested_op = data.get("requestedOperation")

    # Debug output
    print("ℹ️ Instance parameters:")
    print(json.dumps(
        {
            "serviceStopped": service_stopped,
            "requestedOperation": requested_op
        },
        indent=2
    ))

    # Determine current state
    if service_stopped is True:
        state = "STOPPED"
    elif service_stopped is False:
        state = "RUNNING"
    else:
        state = "UNKNOWN"

    print(f"ℹ️ Instance '{INSTANCE_NAME}' state: {state}")

    # Guard: skip if operation in progress
    if requested_op:
        print(f"⏳ Instance has ongoing operation: {requested_op}")
        print("⏭ Skipping action to avoid 422 error")
        return

    # Perform actions
    if args.action == "status":
        return

    if args.action == "start":
        if service_stopped is False:
            print("✅ Instance already running")
        else:
            patch_service_state(token, instance_id, service_stopped=False)

    elif args.action == "stop":
        if service_stopped is True:
            print("✅ Instance already stopped")
        else:
            patch_service_state(token, instance_id, service_stopped=True)

    elif args.action == "autostart":
        if service_stopped is True or service_stopped is None:
            patch_service_state(token, instance_id, service_stopped=False)
        else:
            print("✅ Instance already running (autostart skipped)")


if __name__ == "__main__":
    main()
