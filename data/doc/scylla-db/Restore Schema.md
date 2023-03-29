To restore Scylla-DB schema, first download the latest backup from MinIO bucket scylla-cluster-backup :
```shell
# Assuming minio instance source is configured in mc
mc admin info source

# List backups
mc ls source/scylla-cluster-backup/backup/schema/cluster/<scylla cluster UUID>/

# Get backup archive
mc cp source/scylla-cluster-backup/backup/schema/cluster/<scylla cluster UUID>/task_[…].tgz .

# Decompress archive
tar xvf task_*.tgz

# Remove system keyspaces
rm system_*.cql
```

Each CQL file is a CQL script that can be used to restore a keyspace. To run a specific script into the cluster :

```shell
# Assuming kubectl context ctx_target is the target cluster into which inject data
kubectl config --get-contexts ctx_target

# Pipe a script to CQLSH in the cluster
cat prod_assets.cql | \
kubectl exec --context ctx_target --namespace infra \
  --stdin=true \
  service/scylla-db-client \
  -c scylla \
  -- /usr/bin/cqlsh
```  

Using a shell loop over all scripts, this will be :
```shell
for script in *.cql; do
  echo "Running script $script"
  cat $script | \
    kubectl exec --context ctx_target --namespace infra \
      --stdin=true \
      service/scylla-db-client \
      -c scylla \
      -- /usr/bin/cqlsh
done 
```
