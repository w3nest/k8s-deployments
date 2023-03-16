To access minio console :

1. Port forward the service
```shell
kubectl port-forward --namespace infra service/minio-console 8080:9001
```
2. Get minio console admin password
```shell
kubectl get --namespace infra secret/minio-admin-secret -o jsonpath="{.data.admin-secret-key}" | base64 -d
```

3. Login to http://localhost:8080 as user ```admin``` using console admin password


To access minio from local (i.e for use with [MinIO Client ```mc```](https://min.io/docs/minio/linux/reference/minio-mc.html)):
```shell
# Port forward the service
kubectl port-forward --namespace infra service/minio 9000:9000

# In another shell, add service to mc configuration
mc alias set youwol-minio http://localhost:9000
Enter Access Key:admin # the admin user
Enter Secret Key: # enter console admin password

# Check connexion
mc admin info youwol-minio
```
