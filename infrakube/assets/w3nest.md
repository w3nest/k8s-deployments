# **W3Nest Kubernetes Cluster**
This page provides an overview of the W3Nest Kubernetes cluster. For detailed information on its deployment, 
refer to the <cross-link target="deployments">Deployments page</cross-link>.

The global configuration of the cluster is stored in the
<k8sLink kind="ConfigMap" namespace="apps" target="cluster-config"></k8sLink> config map.

The `ingress-nginx-controller` service acts as the central point that **interprets all ingress resources** and 
configures NGINX to handle the incoming traffic accordingly. 
This is the only service that can be reached from outside the cluster (type is **LoadBalancer**).

<service target='ingress-nginx-controller' namespace='ingress-nginx'></service>

They are 2 kinds of ingresses:
*  **Application ingresses**: 
   they map to services associated to the application itself, accessible by all users.
*  **Monitoring ingresses**: 
   they map to services associated to the debug & monitoring part, accessible by developers only (need auth. secrets).

<note level="question" title="ingress flow" expandable="true">
1. **Client Device** sends an **HTTP/HTTPS request** to `example.com`.
2. **DNS Resolution** translates `example.com` to the **LoadBalancer IP** of the **NGINX Ingress Controller**.
3. The **NGINX Ingress Controller** receives the request and refers to the **Ingress Resource** to determine routing.
4. Based on the **Ingress rules** (host/path), NGINX forwards the request to the appropriate **Service** within the cluster.
5. The **Service** selects the matching **Pod(s)** using its **selector** and load balances the traffic.
6. The **Pod** processes the request and sends the response back through the **Service** and **Ingress Controller** to the **Client Device**.
</note>

---

## 📊 Monitoring

Access the monitoring and management web applications via the following ingresses.

### 🔧 Kubernetes Dashboard

<ingress namespace="monitoring" target="dashboard"></ingress>

To log in the application, generate the access token from the service account
<k8sLink  kind='ServiceAccount'  namespace="monitoring" target="dashboard-access"></k8sLink>.

### 🔐 Keycloak

<ingress namespace="infra" target="keycloak"></ingress>

To connect to the administration console, use `username` and `password` from the
<k8sLink kind='Secret' namespace="infra" target="keycloak-bootstrap-admin"></k8sLink> secret.

<note level="hint" title="`psql` CLI" expandable="true">
You can run `psql` CLI from a pod from `keycloak-00-t5mp` stateful set:

`kubectl exec -it keycloak-00-t5mp-0 -n infra -- psql -h localhost -U $USERNAME --password -p $PORT $DBNAME`

*  Use <k8sLink kind='Secret' namespace="infra" target="keycloak-pguser-keycloak"></k8sLink> secret regarding
   `$USERNAME`, `$PORT`, `$DBNAME` and the prompted password.
</note>

### 📈 Grafana

<ingress namespace="monitoring" target="prometheus-stack-grafana"></ingress>

To log in the application:
*  **as user**: use `user` and `password` from the
   <k8sLink kind='Secret' namespace="monitoring" target="grafana-secret"></k8sLink> secret.
*  **as admin**: use `user` and `password` from the
   <k8sLink kind='Secret' namespace="monitoring" target="grafana-admin"></k8sLink> secret.

### 🗄️ Minio

*  <portForward target="minio-console" hostPort="9001" namespace="infra"></portForward>,
*  `admin` as username and the value of the secret `admin-secret-key` from
<k8sLink kind='Secret' namespace="infra" target="minio-admin-secret"></k8sLink> as password to login.

### 🐘 PgAdmin4

*  <portForward target="pgadmin" hostPort="9002" namespace="infra"></portForward>,
*  `pgadmin@w3nest.com` as email and the value of the secret `password-key` from
   <k8sLink kind='Secret' namespace="infra" target="pgadmin-secret"></k8sLink> as password to login.

---

## 🌍 Public facing end-points

These public-facing endpoints are consumed by the web applications hosted in **WebPM** and served through the
**webpm-apps-server** service. They can be accessed by:

*  Registered and logged-in users.

*  Unregistered users, for whom a temporary session will be created.

The available access points are:

*  <ingress namespace="apps" target="accounts"></ingress>

*  <ingress namespace="apps" target="assets-gateway"></ingress>

*  <ingress namespace="apps" target="webpm-sessions-storage"></ingress>

*  <ingress namespace="apps" target="webpm-apps-server"></ingress>

---

<!--
## **Storage**
Kubernetes provides flexible storage solutions for stateful applications. This page will detail how we manage
persistent storage, including Persistent Volumes (PVs), Persistent Volume Claims (PVCs), and storage classes, 
enabling data persistence and management.

## **Monitoring and Logging**
Monitoring and logging are essential for maintaining the health and performance of applications. This section will
describe the tools and practices we use to monitor our Kubernetes cluster, collect logs, and visualize metrics, 
ensuring that we can quickly respond to issues.

## **Networking**
Networking in Kubernetes facilitates communication between Pods and external resources. This page will explain the
networking model, including cluster networking, services, and network policies, ensuring secure and efficient 
communication across the cluster.

## **Scaling and Load Balancing**
One of Kubernetes' core strengths is its ability to scale applications seamlessly. This section will explore how we
implement horizontal and vertical scaling, as well as the load balancing strategies used to distribute traffic 
effectively across our applications.

## **CI/CD Integration**
Continuous Integration and Continuous Deployment (CI/CD) are vital for efficient software development. 
This section will cover how we integrate CI/CD pipelines into our Kubernetes workflow, allowing for automated testing,
building, and deployment of applications.

## **Security**
In addition to authentication, this page will discuss overall security practices within our Kubernetes cluster, 
including network security, pod security policies, and secrets management to protect sensitive data.
-->