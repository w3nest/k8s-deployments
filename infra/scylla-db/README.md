To run scylla-db client (cqlsh)
```shell
kubectl exec -it --namespace infra service/scylla-db-client -c scylla -- /usr/bin/cqlsh
```

To run nodetool
```shell
kubectl exec -it --namespace infra service/scylla-db-client -c scylla -- /usr/bin/nodetool help
```


To access scylla-db from local
```shell
kubectl port-forward --namespace infra service/scylla-db-client 9042:9042
```
