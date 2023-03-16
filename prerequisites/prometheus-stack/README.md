To get credentials for grafana
```shell
# Get admin-user
kubectl --namespace monitoring get secret/grafana-secret -o jsonpath="{.data.admin-user}" | base64 -d
# Get admin-password
kubectl --namespace monitoring get secret/grafana-secret -o jsonpath="{.data.admin-password}" | base64 -d
```
