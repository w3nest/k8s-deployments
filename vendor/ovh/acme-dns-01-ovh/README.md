# Acme Issuer solving DNS-01 challenges using OVH API

Leverage docker image & charts from [cert-manager-webhook-ovh](https://github.com/baarde/cert-manager-webhook-ovh) to
deploy an Acme Issuer solving DNS-01 challenges using OVH API named from the Helm release.

## Prerequisites

acme-dns-01-ovh deploy a cert-manager ClusterIssuer which will solve DNS-01 challenges using OVH API : if needed,
install cert-manager with its Custom Resource Definitions first:

```shell
helm install --namespace cert-manager \
  cert-manager \
  jetstack/cert-manager \
  --set installCRDs=true
```

Alternatively, a small configuration adding monitoring with Prometheus CRD is available in 
[prerequisites/cert-manager/values.yaml](../cert-manager/values.yaml).:

```shell
helm install --namespace cert-manager \
  cert-manager \
  jetstack/cert-manager \
  --values prerequisites/cert-manager/values.yaml
```

## Configuration

### Acme

```yaml
# file values.yaml
acme:
  accountEmail: jane.doe@example.com
  accountShared: true # see below
  server: https://acme-staging-v02.api.letsencrypt.org/directory
```

Acme account can be shared between various acme-dns-01-ovh ClusterIssuers, just use the same email for 
acme.accountEmail and set acme.accountShared to true.
If not, the ClusterIssuer will have its own account private key,
even if another ClusterIssuer has the same accountEmail.

Acme server can also be configured, to choose between Let’s Encrypt 
[staging environment](https://letsencrypt.org/docs/staging-environment/) or production environment,
or even some other provider implementing ACME protocol.

For reference, Let’s Encrypt servers :
  * Production : https://acme-v02.api.letsencrypt.org/directory
  * Staging : https://acme-staging-v02.api.letsencrypt.org/directory

### OVH API

```yaml
# file values.yaml
ovh:
  applicationKey: 1234567890abcdef
  consumerKey: fedcba0987654321afbedc9018273465
  applicationSecret: # Use an existing Secret, see below for providing applicationSecret when installing the chart.
    name: ovh-secret
    key: applicationSecret
```

First [create a new OVH API key](https://docs.ovh.com/gb/en/customer/first-steps-with-ovh-api/) with the following
rights, and no others :
   * `GET /domain/zone/*`
   * `PUT /domain/zone/*`
   * `POST /domain/zone/*`
   * `DELETE /domain/zone/*`

Application key and consumer key can be safely stored in [prerequisites/acm-dns-01-voh/values.yaml](./values.yaml).
For the applicationSecret, it can be retrieved from an existing Secret or provided when installing the chart.

## Install

Install the chart, passing the OVH applicationSecret via _--set_ if not using an existing secret:

```shell
helm install --namespace cert-manager \
  letsencrypt-issuer \
  . \
  --set ovh.applicationSecret=OVH_APPLICATION_SECRET
```

This will install a ClusterIssuer named 'letsencrypt-issuer' ready to solve DNS-01 challenges by manipulating DNS 
zones managed in OVH.
