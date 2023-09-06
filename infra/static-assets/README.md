# Static-assets

### Deployed objects

This Helm chart deploy an [Nginx Docker image](https://hub.docker.com/_/nginx/)
using a [Kubernetes Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

It uses the git repository
[cluster-static-assets](https://github.com/youwol/cluster-static-assets) for its data:
* The appVersion defined in
[Chart.yaml](./Chart.yaml) will be used as the _branch_ to clone, where _branch_ could be
a specific branch name or (better for immutability) a specific tag.
* The `templates` directory is mounted at `/etc/nginx/templates` 
* The `sites` directory is mounted at `/usr/share/nginx`.

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
