
# Configuration


## Create namespaces

Following namespaces are required:

<k8sShell>
kubectl create namespace pgo
kubectl create namespace infra
kubectl create namespace apps
kubectl create namespace monitoring
kubectl create namespace cert-manager
kubectl create namespace webpm
kubectl create namespace data-manager
</k8sShell>

---

## Pull Image Secret

*  To pull docker image from gitlab:
   *  In `gitlab` create a token in the form `{"auths":{"registry.gitlab.com":{"username":"monte-pissis-puller","password":"gldt-xxx","auth":"yyy"}}}`
   *  base64 encode it `echo -n '{"auths":{"registry.gitlab.com":{"username":"monte-pissis-puller","password":"gldt-xxx","auth":"yyy"}}}' | base64`
   *  In `k8s-deployments/vendor/gitlab-docker` replace the value for `.dockerconfigjson` by the base64 encoded value
   
<k8sShell pwd="vendor/gitlab-docker">
kubectl apply -f gitlab-docker.yaml -n apps
kubectl apply -f gitlab-docker.yaml -n infra
kubectl apply -f gitlab-docker.yaml -n data-manager
kubectl apply -f gitlab-docker.yaml -n webpm
</k8sShell>

---

## Configure Cluster & Env

This deployment configure global config maps & secrets for given environment.

*  For **minikube**:
    <k8sShell pwd="configs">
helm install configs ./ --namespace=apps --set env=minikube
    </k8sShell>


*  For **w3nest.org**:
    <k8sShell pwd="configs">
helm install configs ./ --namespace=apps --set env=w3nest.org
    </k8sShell>

The secrets created here are duplicated by the associated deployments, the list is:

*  <k8sLink  kind='Secret'  namespace="app" target="keycloak-admin-secret"></k8sLink>
*  <k8sLink  kind='Secret'  namespace="app" target="keycloak-bootstrap-admin"></k8sLink>
*  <k8sLink  kind='Secret'  namespace="app" target="minio-app-secret"></k8sLink>
*  <k8sLink  kind='Secret'  namespace="app" target="openid-app-secret"></k8sLink>
*  <k8sLink  kind='Secret'  namespace="app" target="redis-app-secret"></k8sLink>


The cluster configuration can be found here:

<k8sLink kind="ConfigMap" namespace="apps" target="cluster-config"></k8sLink>.


<note level="warning" title="dry-run" expandable="true">
Things like duplicate secrets do not work when doing `dry-run`.
(There is no API call to k8s -> no original secrets)
</note>

---

## Setup Certificate

### minikube OVH

During cluster setup the following certificates have been created:
*  `/etc/letsencrypt/live/w3nest.org/*`
*  `/etc/letsencrypt/live/tooling.w3nest.org/*`


Copy created files into `./certificates/w3nest.org/` and `./certificates/tooling.w3nest.org/` respectively,
and set read permission (`chmod 644`).

Then create `platform-tls` and `tooling-tls` TLS secrets (in `infra`  & `monitoring` namespace respectively):

<k8sShell>
kubectl create secret tls platform-tls  --cert=~/certificates/w3nest.org/fullchain.pem   --key=~/certificates/w3nest.org/privkey.pem -n infra
kubectl create secret tls tooling-tls   --cert=~/certificates/tooling.w3nest.org/fullchain.pem   --key=~/certificates/tooling.w3nest.org/privkey.pem -n monitoring
<k8sShell>

### minikube PC

<k8sShell pwd="cert">
kubectl create secret tls platform-tls \
    --cert=w3nest.minikube.crt \
    --key=w3nest.minikube.key \
    --namespace=infra
</k8sShell>
