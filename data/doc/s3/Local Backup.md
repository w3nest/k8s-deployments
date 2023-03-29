To locally backup data from S3 buckets, the simplest is to use [MinIO client ```mc```](https://min.io/docs/minio/linux/reference/minio-mc.html) :

```shell
# Assuming kubectl context ctx_source is the source cluster to backup
kubectl config --get-contexts ctx_source

# Port-forward minio from cluster source
kubectl --context ctx_source port-forward --namespace infra \
  service/minio \
  --address 127.0.0.5 \ # prevent ports conflict by using a specific local ip address
  9000:9000

# Add alias (see infra/minio/README.md for complete command) 
mc alias set source http://127.0.0.5:9000

# Check configuration
mc admin info source

# Run locally an instance of minio with docker
#   * storing data in folder "backup/minio" 
#   * access key will be "admin"
#   * access secret will be "secret"
docker run --rm \
  -p 127.0.0.17:9000:9000 \ # prevent ports conflict by using a specific local ip address
  --name minio-backup \
  -v "backup/minio/:/data" \
  -e "MINIO_ROOT_USER=admin" \
  -e "MINIO_ROOT_PASSWORD=secret" \
  quay.io/minio/minio server /data

# Add alias for local instance (using access key and access secret from previous command)
mc alias set target http://127.0.0.17:9000

# Check configuration
mc admin info target

# Mirror source to target
mc mirror --overwrite --preserve --remove source target
```
