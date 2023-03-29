In order to restore Scylla-DB data for one table, the following command can be used :

```shell
# Assuming kubectl context ctx_target is the source cluster into which restore data
kubectl config --get-contexts ctx_target

# Restore table "keyspace.table_name" from a local file "keyspace.table_name.csv"
cat keyspace.table_name.csv | \
kubectl --stdin=true --context ctx_target exec --namespace infra \
  service/scylla-db-client \
  --container scylla \
  -- /usr/bin/cqlsh -e "CONSISTENCY ALL; COPY keyspace.table_name FROM STDIN"
```

Based from the file list_tables.txt and a previous backup, a shell loop can be used to restore all tables :
```shell
for table in $(cat list_tables.txt); do
  echo "Restore $table from $table.csv"
  cat $table.csv | \
    kubectl --stdin=true --context ctx_target exec --namespace infra \
      service/scylla-db-client \
      --container scylla \
      -- /usr/bin/cqlsh -e "CONSISTENCY ALL; COPY $table FROM STDIN" 
done

```
