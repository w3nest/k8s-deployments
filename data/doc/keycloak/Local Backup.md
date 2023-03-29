From old versions (wildfly) :
```shell
# Assuming kubectl context ctx_source is the source cluster from which backup data
kubectl config --get-contexts ctx_source

# Run a shell inside container
kubectl --context ctx_source exec -it --namespace infra service/keycloak-headless -- /bin/bash

# Inside the container
/opt/jboss/keycloak/bin/standalone.sh \
  -Djboss.socket.binding.port-offset=100 \
  -Dkeycloak.migration.action=export \
  -Dkeycloak.migration.provider=singleFile \
  -Dkeycloak.migration.realmName=youwol \
  -Dkeycloak.migration.usersExportStrategy=REALM_FILE \
  -Dkeycloak.migration.file=/tmp/youwol_realm.json
  
# Copy file to local
kubectl cp --context ctx_source infra/keycloak:/tmp/youwol_realm.json youwol_realm.json
```
