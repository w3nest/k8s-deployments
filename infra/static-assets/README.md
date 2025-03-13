# Static-assets

### Deployed objects

This Helm chart deploy an [Nginx Docker image](https://hub.docker.com/_/nginx/)
using a [Kubernetes Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

It uses the folder `/assets` for its data:
* The `templates` directory is mounted at `/etc/nginx/templates` 
* The `sites` directory is mounted at `/usr/share/nginx`.

It is exposed through a ConfigMap, with content taken from 
[includes/assets.zip.b64](./includes/assets.zip.b64).
This is the base-64 encoded version of `/assets`, to generate it:

`zip -r assets.zip assets/ && base64 assets.zip > includes/assets.zip.b64 && rm assets.zip`

At each update of '/assets`, this command should be re-run and the chart upgraded 
(`helm upgrade static-assets ./ --namespace=infra`).

Also deployed is a ConfigMap, whose content is mounted at `/usr/share/nginx/includes/maintenance/details.txt`.
That content is taken from [includes/maintenance-details.txt](./includes/maintenance-details.txt).

Kubernetes [Ingresses](https://kubernetes.io/docs/concepts/services-networking/ingress/) 
& [Services](https://kubernetes.io/docs/concepts/services-networking/service/) 
for the hosts served by the Nginx instance are also deployed:

* `static-assets`: Publicly exposed as the route `/static/`.
* `default-route`: Is the 
  [defaultBackend](https://kubernetes.io/docs/concepts/services-networking/ingress/#default-backend) for 
  Kubernetes Ingresses.
* `maintenance`: Masks routes starting with `/auth/realms/youwol/`, `/api/` and `/application/`

_NB: The `maintenance` Ingress, by default, does not have a `ingressClassname` attribute, which effectively disable it._

### Maintenance mode

By setting the attribute `ingressClassname` of the `maintenance` ingress to `kong`, every routes for Keycloak realm
`youwol`, `/api/` and `/application/` will be redirected to the `maintenance` host served by the Nginx instance.

Unsetting the same attribute will restore these routes.

The content of the ConfigMap can be used to customize the maintenance page, provided the served page (from the data) includes the right file.

### Customization

See comments in [values.yaml](./values.yaml).
