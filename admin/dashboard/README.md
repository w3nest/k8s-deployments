To access dashboard :

1. Port forward the service
```shell
kubectl port-forward --namespace monitoring service/dashboard 8443:https
```

2. Get access token
```shell
kubectl --namespace monitoring create token dashboard-access
```

3. Login at https://localhost:8433
