# Deployment

<!--
Domain name: `w3nest.org`

Managed by `godaddy`: `https://dcc.godaddy.com/control/portfolio/w3nest.org/settings`
Logged in with Google's `reinisch.gui@gmail.com` account.

See https://developer.godaddy.com/ 

For minikube, a **A record** has been created (to map to minikube.w3nest.org)
-->

This section outlines the process of creating a Kubernetes cluster and deploying various components of the
application using Helm charts. 
These charts define the deployment configurations for different resources, and their specifications can be found in 
the GitHub repository <github-link target="k8s-deployments">k8s-deployments</github-link>.

The deployment workflow is structured across several key stages, which should be followed sequentially:

- **<cross-link target="deploy.cluster-setup">K8s Cluster Setup</cross-link>**: Setting up a Kubernetes cluster in 
  various environments (currently, only Minikube is supported).
- **<cross-link target="deploy.config">Configuration</cross-link>**: Configuring namespaces, config maps, and secrets.
- **<cross-link target="deploy.infra">Infrastructure</cross-link>**: Deploying the infrastructure components.
- **<cross-link target="deploy.w3nest">W3Nest Services</cross-link>**: Deploying the core W3Nest services.

After successful deployment, refer to the **<cross-link target="db.restore">Restore Data</cross-link>** page for 
instructions on restoring data to the various databases.
