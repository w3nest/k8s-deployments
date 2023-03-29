To restore data in S3 buckets, the simplest is to use [MinIO client ```mc```](https://min.io/docs/minio/linux/reference/minio-mc.html) :

```shell
# Assuming the mc alias source will be the source to restore from 
# can be setup from kubectl port-forwarding, as below for target, or from a local instance of minio (see backup)
mc admin info source

# Assuming kubectl context ctx_target is the target cluster into which inject data
kubectl config --get-contexts ctx_target

# Port-forward minio from cluster target
kubectl --context ctx_target port-forward --namespace infra \
  service/minio \
  --address 127.0.0.5 \ # prevent ports conflict by using a specific local ip address
  9000:9000

# Add alias (see infra/minio/README.md for complete command)
mc alias set target http://127.0.0.5:9000

# Check target is correctly configured
mc admin info target

# Mirror source to target
mc mirror --overwrite --preserve --remove source target
```
