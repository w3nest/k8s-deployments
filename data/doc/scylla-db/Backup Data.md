In order to backup Scylla-DB data for one table, the following command can be used :

```shell
# Assuming kubectl context ctx_source is the source cluster from which backup data
kubectl config --get-contexts ctx_source

# Backup table "keyspace.table_name" to a local file "keyspace.table_name.csv"
kubectl --context ctx_source exec --namespace infra \
  service/scylla-db-client \
  --container scylla \
  -- /usr/bin/cqlsh -e "CONSISTENCY ALL; COPY keyspace.table_name TO STDOUT" \
  > keyspace.table_name.csv
```

Based from the file list_tables.txt, a shell loop can be used to backup all tables :
```shell
for table in $(cat list_tables.txt); do
  echo "Backup $table into $table.csv"
  kubectl --context ctx_source exec --namespace infra \
    service/scylla-db-client \
    --container scylla \
    -- /usr/bin/cqlsh -e "CONSISTENCY ALL; COPY $table TO STDOUT" \
    > $table.csv  
done

```
