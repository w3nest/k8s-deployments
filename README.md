# K8S Cluster

Deploy a Youwol Cluster

## How to use this repository

The recommended way to use this repository is to fork or clone it and use a branch per deployment.
Updating an existing deployment will involve fetching new changes and merge or rebase its branch.

For instance :

```shell
git clone git@github.com:youwol/k8s-deployment/
cd ./k8s-deployment
git branch 
```

### Installation steps

To install Youwol clusters :

1. Meet the prerequisites
2. Decide for each services which ones will be managed outside the cluster
3. Configure & install helm chart configs
4. Install helm chart infra
5. Install helm chart apps

## Prerequisites

In order to proceed, the following tools must be installed & configured locally :

* kubectl
* helm

Additionally a Kubernetes cluster must be ready, with cert-manager and optionally prometheus.

### Certificates management with cert-manager

The Helm charts in this repository expect a ClusterIssuer from cert-manager.
There is a acme-dns-01-ovh chart at [./prerequisites/acme-dns-01-ovh](./prerequisites/acme-dns-01-ovh) for provisioning
an acme ClusterIssuer solving DNS-01 challenges with OVH API, but it is not supported by Youwol.

### Monitoring with Prometheus

The Helm charts in this repository can use CRD from prometheus.

## Services

For each of the following services, the Helm charts in this repository can be configured to use an existing service
or will provision it using Operator’s CRD, without further configuration.

#### Provisioned service

For each service, a managed service, either external or inside the cluster can be used.
In this case access to the service must be provisioned beforehand and Helm chart configs configured
with the necessary information.

#### Provisioning via Helm charts

For each service, a Kubernetes Operator with corresponding CRDs can be installed.
Installation of said Operators can be done with the Helm charts in the [operators directory](./operators).
In this case access to the service will be provisioned by Helm charts and no further configuration is needed.

#### Postgres

Postgres databases can be managed outside of the cluster or automatically provisioned using PGO.

For installing PGO, run the following command:

```shell
helm install --namespace pgo \
  pgo \
  operators/pgo
```

If not using PGO, databases and users must be provisioned beforehand and Helm chart configs must be configured
accordingly.
See below for details.

#### S3 Storage

__TODO: currently there is no Operator, provision of the database is directly done instead__

S3 buckets can be managed outside of the cluster or a Minio instance can be installed.

For installing a provisioned Minio instance, run the following command:

__NB : since Minio Operator is not supported for the moment,
this installation must be done AFTER the deployment of Helm chart configs !__

```shell
helm install --namespace infra \
  minio \
  operators/minio
```

If managed outside, users must be provisioned beforehand and Helm chart configs must be configured accordingly.
See below for details.

#### Cassandra DB

__TODO: external management not supported at the moment__

Cassandra database can be managed outside of the cluster or automatically provisioned using ScyllaDB Operator.

For installing ScyllaDB Operator, run the following command:

```shell
helm install --namespace scylla-operotor \
  scylla-operotor \
  operator/scylla-operator
```

If managed outside, database and users must be provisioned beforehand and Helm chart configs must be configured
accordingly.
See below for details.

#### Keycloak

__TODO: external management not supported at the moment__

Keycloak can be managed outside of the cluster or automatically provisioned using Keycloak Operator.

For installing Keycloak Operator, run the following command:

```shell
helm install --namespace keycloak-operator \
  keycloak-operator \
  operators/keycloak-operator
```

If managed outside, realm and administrative user must be provisioned beforehand and Helm chart configs must be
configured accordingly.
See below for details

## Configuration

The Helm chart configs must be configured, through its values.yaml file, before deployment. Additionally 
sensibled informations, such as password or API keys, shall be passed to installation command using `--set` and not 
recorded in values.yaml.

The values.yaml is well documented, here’s a short recap of the options available :


#### TODO : infra
