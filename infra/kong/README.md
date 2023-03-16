Once kong is deployed, load balancer IP address can be obtained with :
```shell
kubectl get --namespace infra service/kong-proxy -o jsonpath="{.status.loadBalancer.ingress[0].ip}"
```
