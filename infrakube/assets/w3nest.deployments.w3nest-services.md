
# W3Nest Services Deployment

The `w3nest` Helm chart defines the deployment specifications for `w3nest` backend services, which form part of 
the `shared_api` python module of `py_w3nest`. 
Each backend is deployed as a sub-chart within the `apps` namespace, with configurations managed centrally 
in `w3nest/values.yaml`.


## Backend Services

- **`accounts`**: Manages user accounts.
- **`assets-gateway`**: Serves as the gateway portal for accessing assets and handling authorization.
- **`assets`**: Provides management services for assets.
- **`files`**: Handles file-based asset storage.
- **`webpm`**: Operates the Web Package Manager backend, resolving the dependency trees and managing access 
  to package resources.
- **`explorer`**: Organizes assets in a file-system-like explorer.
- **`webpm-apps-server`**: Serves applications hosted in WebPM.
- **`webpm-sessions-storage`**: Manages storage for WebPM packages associated with a specific user.


To deploy `w3nest` in the `apps` namespace, run:

<k8sShell pwd="w3nest">
helm install w3nest ./ --namespace=apps
</k8sShell>

### Ingress Endpoints

The following external access points are created:

*  <ingress namespace="apps" target="accounts"></ingress>

*  <ingress namespace="apps" target="assets-gateway"></ingress>

*  <ingress namespace="apps" target="webpm-sessions-storage"></ingress>

*  <ingress namespace="apps" target="webpm-apps-server"></ingress>

### Internal Services

These services are available within the cluster:

*  <service namespace="apps" target="accounts"></service>

*  <service namespace="apps" target="assets-gateway"></service>

*  <service namespace="apps" target="assets"></service>

*  <service namespace="apps" target="files"></service>

*  <service namespace="apps" target="webpm"></service>

*  <service namespace="apps" target="explorer"></service>

*  <service namespace="apps" target="webpm-apps-server"></service>

*  <service namespace="apps" target="webpm-sessions-storage"></service>
