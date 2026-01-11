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

## Trigger job from cronjob

```bash
kubectl create job --from=cronjob/hana-autostart-hcx hana-autostart-hcx-manual-$(date +%s) -n hcx
```
