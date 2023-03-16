For keycloak administration, use keycloak-initial-admin secret :
```shell
# Keycloak initial username
kubectl get --namespace infra secret/keycloak-initial-admin -o jsonpath="{.data.username}" | base64 -d
# Keycloak initial password
kubectl get --namespace infra secret/keycloak-initial-admin -o jsonpath="{.data.password}" | base64 -d
```
