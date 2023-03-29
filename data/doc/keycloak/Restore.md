From a previously exported youwol_realm.json
```shell
# Assuming kubectl context ctx_target is the target cluster into which inject data
kubectl config --get-contexts ctx_target

# Only once : inside the container, setup credentials for kcadm.sh
# Run an interactive shell inside the container
kubectl exec -it --namespace service/keycloak-service --container keycloak -- /bin/bash
# NB: Credentials details are already set in shell environment
/opt/keycloak/bin/kcadm.sh config credentials \
  --server http://localhost:8080/auth \
  --realm master \
  --user ${KEYCLOAK_ADMIN} \
  --password ${KEYCLOAK_ADMIN_PASSWORD}
  
# Restore realm from local file
cat youwol_realm.json | \
  kubectl --context ctx_target \
    --stdin=true \
    --namespace infra \
    exec service/keycloak-service \
    --container keycloak \
    -- /opt/keycloak/bin/kcadm.sh create realms -f -
```
