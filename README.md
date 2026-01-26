# btp-hcx-autostart

Python script to check if HANA Cloud Instance is running and if not start it

## Requirements

    - Service Manager with subAccount Admin plan created within HANA Cloud SubAccount  
    - Service binding for authn
    - Variables in script (required as OS Env, Docker Env or k8s secret)
        - CLIENT_ID: Client ID from SM Service Binding
        - CLIENT_SECRET: Client Secret from SM Service Binding
        - TOKEN_URL: Token endpoint from SM Service Binding (https://<domain>.authentication.<BTP Region>.hana.ondemand.com/oauth/token"
        - SERVICE_MANAGER_URL: From SM Service Binding (https://service-manager.cfapps.<BTP Region>.hana.ondemand.com)
        - INSTANCE_NAME: Actual name of the HANA Cloud Instance

## Run in bash

```bash
export CLIENT_ID=''
export CLIENT_SECRET=''
export TOKEN_URL=""
export SERVICE_MANAGER_URL=""
export INSTANCE_NAME=""
pip install pip install --no-cache-dir requests
python3 hana_autostart.py -<argument>
```

## Build + Run with docker

```bash
docker build -t <imageName>(:<tag>) .
docker run --rm \
-e CLIENT_ID='' \
-e CLIENT_SECRET='' \
-e TOKEN_URL="" \
-e SERVICE_MANAGER_URL="" \
-e INSTANCE_NAME="" \
<imageName:(tag)> <argument>
```

## Kubernetes

Make required changes to manifests

```bash
kubectl apply -f <manifest files>
```

## Argumments

- start - starts HANA Cloud instance
- stop - stops HANA Cloud instance
- status - check status of HANA Cloud instance
- autostart - check current state of instance and starts if stopped

## Kubernetes Trigger job from cronjob

```bash
kubectl create job --from=cronjob/hana-autostart-hcx hana-autostart-hcx-manual-$(date +%s) -n hcx
```
