To run redis client from cluster :
```shell
kubectl exec -it --namespace infra service/redis-master -c redis -- /opt/bitnami/redis/bin/redis-cli
```
