# btp-hcx-autostart

Python script to check if HANA Cloud Instance is running and if not start it

## Requirements

    - Service Manager with subAccount Admin plan created within HANA Cloud SubAccount  
    - Service binding for authn
    - Authn details as os env, docker env or k8s secrets

## Trigger job from cronjob
    ```bash
    kubectl create job --from=cronjob/hana-autostart-hcx hana-autostart-hcx-manual-$(date +%s) -n hcx  
    ```
