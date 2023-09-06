For keycloak administration, use keycloak-initial-admin secret :
```shell
# Keycloak initial username
kubectl get --namespace infra secret/keycloak-initial-admin -o jsonpath="{.data.username}" | base64 -d
# Keycloak initial password
kubectl get --namespace infra secret/keycloak-initial-admin -o jsonpath="{.data.password}" | base64 -d
```

### Custom theme `youwol` 

_NB: current deployment use a basic docker image for copying theme into Keycloak docker image,
Helm chart has been updated but not yet deployed_

A custom theme `youwol` is available in the deployed Keycloak instance. That theme is taken from a git repository 
by cloning it and mounting its directory `theme` at `/opt/keycloak/themes/youwol`.
See [values.yaml](./values.yaml) for configuring that repository URL and the _branch_ 
(either a specific branch or, better for immutability, a specific tag) to pass to the `git clone` command.
