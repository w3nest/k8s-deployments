# Migrations

## Infra

### Nginx Ingress (replace Kong)

`operators/nginx-ingress`  
`infra/kong`

* Check for ingressClassname in all charts
* Check for ingressClassname in data-manager
* Check if custom ingresses still necessary

_see https://kubernetes.github.io/ingress-nginx/deploy/_  
_see https://help.ovhcloud.com/csm/en-public-cloud-kubernetes-getting-source-ip-behind-loadbalancer?id=kb_article_view&sysparm_article=KB0049765__

### Minio Operator 

_see https://min.io/docs/minio/kubernetes/upstream/operations/install-deploy-manage/deploy-operator-helm.html_


### Minio Tenant (replace Minio)

`infra/minio`

* Create a minio tenant chart
* Import data

### Keycloak Operator (22.0.1 => 25.0.4)

`operators/keycloak-operator`

* Upgrade Keycloak Controller Cluster resources (CRD & roles)
* Upgrade Keycloak Operator

_See Keycloak_

### Keycloak (22.0.3 => 25.0.4)

`infra/keycloak`

* Upgrade Dockerfile
* Upgrade templates
    * CRD
    * postgres (v16)
    * Check if db-init still necessary
* Create realm importation (clients)
* Upgrade theme
* Import data

### PGO (5.3.0 => 5.6.1)

`operators/pgo`

* Use repository `oci://registry.developers.crunchydata.com/crunchydata`
* Upgrade CRD
    * Check PostgresCluster installed

### Scylla Manager (1.12.1 => 1.13.0)

`operators/scylla-manager`

### Scylla Operator (1.12.1 => 1.13.0)

`operators/scylla-operator`

* Upgrade CRD
    * Check installed CRD

### ScyllaDB

`infra/scylla-db`

* Upgrade CRD

## Prerequisites

### Cert-manager (1.11 => 1.15)

`prerequisites/cert-manager`

### Acme-dns-01-OVH

`vendor/ovh/acme-dns-01-ovh`

* Use helm charts from 0.3.1

### Loki Stack (2.8.9 => 2.10.2)

`prerequisites/loki-stack`

### Prometheus Stack (39.11.0 => 64.4.0)

`prerequisets/kube-prometheus-stack`


## Other

### Dashboard (6.0.0 => 7.5.0)

* Clean install

_see https://github.com/kubernetes/dashboard/blob/master/charts/kubernetes-dashboard/README.md_

### Taiga (????)

* Impacted by PGO & NginX Ingress
* Look for a replacement
