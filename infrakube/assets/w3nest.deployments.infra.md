# InfraStructure

This page provides an overview of the essential components that support the functionality and
scalability of the application. These tools and services ensure the smooth operation of both the backend and 
frontend systems, providing critical services like logging, monitoring, storage, authentication, 
and database management.

This section covers key infrastructure components such as PostgreSQL for database management, 
Prometheus & Grafana for monitoring, Loki for log aggregation,
Keycloak for identity and access management, Minio for object storage, Redis for caching, Cert Manager for managing 
SSL/TLS certificates, and static assets hosting.



## 🛠️ Kubernetes Dashboard

Instead of using Minikube's built-in dashboard, you can deploy the official Kubernetes Dashboard using **Helm**:

<k8sShell pwd="admin/dashboard">
sh ./generate_values.sh 
helm install dashboard ./ --namespace=monitoring
</k8sShell>

Once the deployment is complete, an Ingress will be created for accessing the dashboard:

<ingress namespace="monitoring" target="dashboard"></ingress>

To log in, you need to generate an **access token** from the associated **ServiceAccount**:
<k8sLink  kind='ServiceAccount'  namespace="monitoring" target="dashboard-access"></k8sLink>.




---

## 🐘 PostgreSQL

**PostgreSQL** is a powerful, open-source relational database system known for its reliability, flexibility,
and support for complex queries. It is ACID-compliant, ensuring data integrity, and supports both SQL and NoSQL 
features like JSON, making it ideal for a wide range of applications.

- **Key Features**: Advanced indexing, full-text search, custom extensions (e.g., PostGIS for geospatial data), 
  and scalability through replication.
- **Security**: Offers SSL connections, granular access control, and various authentication methods.
- **Use Cases**: Suitable for transactional systems, data warehousing, geospatial apps, and applications
   requiring complex queries.

PostgreSQL is widely adopted for both small-scale and enterprise-level applications, and can be deployed in cloud, 
on-premise, or containerized environments like Kubernetes.

<note level="hint" title="**Services Using `PGO`**" expandable="true"> 
The following components rely on the PostgreSQL Operator:  
- **Keycloak** – Stores user authentication data.  
- **Prometheus** – Uses PostgreSQL for storing long-term monitoring metrics.  
- **Grafana** – Can integrate with PostgreSQL as a data source.  
- **W3Nest Backends** – Various backend services depend on PostgreSQL.  

</note>



The **PostgreSQL Operator (PGO)** is responsible for **instantiating and managing PostgreSQL databases** in a 
Kubernetes environment. It automates deployment, scaling, backup, and monitoring for PostgreSQL clusters.  
To install the PostgreSQL Operator in the `pgo` namespace using Helm:  


<k8sShell pwd="operators/pgo">
helm install pgo ./ --namespace=pgo
</k8sShell>


<note level="hint" title="Notes" expandable="true">  

**Docker Image Pull Issues**  
- Sometimes, pulling PGO-related Docker images results in **`connection reset by peer`** errors.  
- If this happens, retry after **10-20 minutes**—it often resolves itself.  

**Helm Chart Source**  
- The Helm chart used in deployment is based on:  
  [Crunchy Data PGO Helm Example](https://github.com/CrunchyData/postgres-operator-examples/tree/main/helm/install)  
- The Helm chart reference:  
  [w3nest/k8s-deployments](https://github.com/w3nest/k8s-deployments/blob/249d61d5e7cbf6556b9a9109c59f3f732c893059/operators/pgo/Chart.yaml#L14)  
- Instead of using a locally built chart, we **may be able** to install directly from the official registry:  
  ```sh
  helm install pgo oci://registry.developers.crunchydata.com/crunchydata/pgo
  ```  
  - **Not yet tested** – verify if this method works.  
  - Official documentation:  
    [Installing PGO from the OCI registry](https://access.crunchydata.com/documentation/postgres-operator/latest/installation/helm#installing-directly-from-the-registry)  

**Write-Ahead Log (WAL) Growth Issue**  
- **Problem:** The Write-Ahead Log (WAL) folder (`pg15_wal`) **does not get cleaned up automatically**, eventually filling up storage.  
- **Relevant Keywords & Solutions:**  
  - `pgbackrest` – The utility responsible for handling backups (`kind: PostgresCluster → spec.backups.pgbackrest`).  
  - **Possible Fix:** Adjust `storage retention` settings.  
  - **Disabling Backups (if needed):**  
    [Turning Off Backups in PGO](https://access.crunchydata.com/documentation/postgres-operator/latest/guides/optional-backups#turning-off-backups)  

</note>  

### PgAdmin4

**pgAdmin** is a popular open-source administration and management tool for PostgreSQL. 
It provides a graphical interface to interact with PostgreSQL databases, allowing users to manage and query databases, 
execute SQL queries, and visualize data. pgAdmin is widely used for database management, development, 
and troubleshooting, offering features like role-based access control, user-friendly query editors, and reporting tools.


<k8sShell pwd="infra/pgadmin">
helm install pgadmin ./ --namespace=infra --set overrideSecrets.pgadmin-secret.password-key=pgadmin
</k8sShell>

<note level="warning">
It can take a couple of minutes for the persistent volume claim to be found. Until then, there are errors.
</note>

To access `pgadmin` from your browser:
*  <portForward target="pgadmin" hostPort="9002" namespace="infra"></portForward>,
*  `pgadmin@w3nest.com` as email and the value of the secret `password-key` from
   <k8sLink kind='Secret' namespace="infra" target="pgadmin-secret"></k8sLink> as password to login.


---

## 📊 Monitoring

### **Prometheus & Grafana**

Prometheus and Grafana are widely used open-source tools for monitoring and observability in cloud-native environments.

- **Prometheus**: A powerful time-series database that collects and stores metrics from various sources, 
  including applications, servers, and services. It provides robust querying capabilities to help track system 
  performance, health, and resource usage.
  
- **Grafana**: A data visualization tool that integrates with Prometheus and other data sources. 
  It allows you to create customizable dashboards to display metrics collected by Prometheus, providing insightful 
  visualizations and alerts to monitor the state of your applications and infrastructure.

Together, Prometheus and Grafana form a complete monitoring solution, enabling real-time data collection, alerting, 
and visualization for maintaining the health of your systems.


<note level="warning" title="`ServiceMonitor` CRD">
This deployment also define the Custom Resource Definition (CRD) `ServiceMonitor` required by other deployments.
</note>


<k8sShell pwd="prerequisites/prometheus-stack">
sh ./generate_values.sh 
helm install prometheus-stack ./ --namespace=monitoring
</k8sShell>

Upon completion, the following ingress is created providing access to the **Grafana Dashboard**:

<ingress namespace="monitoring" target="prometheus-stack-grafana"></ingress>

To log in the application, generate the access token from the service account
<k8sLink  kind='Secret'  namespace="monitoring" target="grafana-admin"></k8sLink>.

The secret `grafana-admin` is also used internally by grafana for updates regarding the dashboards list.

<note level="warning" title="`grafana-admin` vs `grafana-secret`" expandable="true">
This is now `grafana-admin` everywhere.
We should be able to use directly keycloak to connect.
</note>


### Loki

**Loki** is an open-source log aggregation system designed to collect, store, and query logs in a highly efficient way. 
It is often used in conjunction with **Prometheus** for a complete observability stack. 

- **Log Aggregation**: Loki ingests logs from various sources, such as applications, services, and containers,
   and indexes them for fast, efficient searching. Unlike other logging systems, Loki indexes only the metadata
   (e.g., labels and timestamps) rather than the full log content, making it more scalable and cost-effective.

- **Integration with Grafana**: Loki integrates seamlessly with **Grafana**, allowing you to view, search, and 
  analyze logs alongside your Prometheus metrics in a single interface. This tight integration enables a unified 
  observability experience, making it easier to correlate logs and metrics for troubleshooting and monitoring.

Loki provides a simple yet powerful solution for log management, especially when working in cloud-native environments with Kubernetes.

<k8sShell pwd="prerequisites/loki-stack">
helm install loki-stack ./ --namespace=monitoring
</k8sShell>

To access **Loki Dashboard**, navigate **Explorer** from the left side nav panel of **Grafana Dashboard**, and 
select **Loki** for data source. 

<note level="hint" title="Increased `fs.inotify.max_user_instances`" expandable="true">
The default value for `fs.inotify.max_user_instances` was increased in the `values.yaml` by modifying the 
`InitContainer` value in `promtail`. 

This change is necessary because, without it, the deployment fails on Minikube.

For more details, refer to the following resources:
*  [Issue on Liki GitHub](https://github.com/grafana/loki/issues/1153).
*  [Promtal values.yaml](https://github.com/grafana/helm-charts/blob/promtail-6.16.6/charts/promtail/values.yaml#L82)

<note level="bug" title="`too many open files`" expandable="true">

If the error is encountered, Loki show the following error:
`caller=main.go:170 msg="error creating promtail" error="failed to make file target manager: too many open files"`

The error `too many open files` indicates that Promtail (part of Loki) has hit the limit for open file descriptors in 
the environment it's running in. This limit, often called the "ulimit," restricts the number of files or network 
connections a process can open simultaneously.
</note>

</note>


📊 **Register Loki Dashboard**

After installing Loki, you can add a pre-configured dashboard in Grafana to visualize your logs.

1. In Grafana, navigate to **Dashboard > New Dashboard**.
2. Click **Import** to add a new dashboard.
3. In a new tab, open [Grafana Dashboard Directory](https://grafana.com/grafana/dashboards/).
4. Find and install the **Loki Kubernetes Logs** dashboard (ID: **15141**).
5. After installation, go to **Home > Explore > Loki** to begin exploring your logs.


---

## 🔐 Keycloak

**Keycloak** is an open-source identity and access management (IAM) solution that provides authentication and 
authorization services for modern applications and services. It simplifies the process of securing applications 
by offering a central platform for managing user identities, roles, and permissions.

- **Authentication and SSO**: Keycloak enables Single Sign-On (SSO) for applications, allowing users to log in once 
  and gain access to multiple services without needing to authenticate again. It supports standard protocols 
  like OAuth2, OpenID Connect, and SAML for secure authentication.

- **Identity Federation**: Keycloak allows integration with external identity providers such as Google, Facebook, 
  or LDAP, enabling users to authenticate using their existing credentials.

- **Role-Based Access Control (RBAC)**: With Keycloak, you can manage user roles and permissions, ensuring that 
  the right users have the appropriate level of access to your applications and services.

Keycloak streamlines user management and security, making it an ideal choice for applications in both monolithic 
and microservices architectures.

<note level="question" title="OAuth2 vs OpenID Connect" expandable="true">

- **OAuth 2.0** is an **authorization** protocol.
- **OpenID Connect (OIDC)** is an **authentication** layer built **on top of OAuth 2.0**.

They work together but serve different purposes.


**🔍 Key Differences**

| Aspect               | OAuth 2.0                          | OpenID Connect (OIDC)                         |
| -------------------- | ---------------------------------- | --------------------------------------------- |
| **Purpose**          | Grants access                      | Verifies identity                             |
| **Provides**         | Access token                       | Access token **+ ID token**                   |
| **Token type**       | Access Token                       | Access Token + **ID Token (JWT)**             |
| **User Info**        | Not specified                      | `/userinfo` provides user profile             |
| **Built on**         | -                                  | **Extends OAuth 2.0**                         |
| **Use case**         | Accessing APIs                     | Logging & verifying users identity            |


**🧠 How They Work Together**

OIDC uses OAuth 2.0’s authorization flows (like `authorization code` or `implicit`) but adds:
- A **`scope=openid`** parameter to indicate it's an OIDC request.
- An **ID Token** (a JWT) that includes info about the user (like name, email, sub).
- An optional **/userinfo** endpoint to retrieve more user attributes.

**🧭 Analogy**

Imagine OAuth 2.0 as a **hotel keycard**: it lets you **access** the gym, pool, or your room.

OIDC is like **checking in at the front desk with ID**: it **proves who you are** before you're given the keycard.

Let me know if you want diagrams or real-world examples!
</note>

First, setup cluster resources:

<k8sShell pwd="operators/keycloak-operator/cluster-resources">
helm install keycloak-operator-cluster-resources ./ --namespace=infra
</k8sShell>

Then, the operator:

<k8sShell pwd="operators/keycloak-operator/operator">
helm install keycloak-operator ./ --namespace=infra
</k8sShell>

Wait for operator installation, then, finally:

<k8sShell pwd="infra/keycloak">
helm install keycloak ./ --namespace=infra
</k8sShell>

<note level="warning">
It can take a couple of minutes for the persistent volume claim to be found. Until then, there are errors.

I often have `connection reset by peer` when pulling docker images related to `crunchydata` repository.
It worked after 10/20 minutes.
</note>

Upon installation, the following ingress pointing to the administration console is available:

<ingress namespace="infra" target="keycloak"></ingress>

To login, use `username` and `password` from the

<k8sLink kind='Secret' namespace="infra" target="keycloak-bootstrap-admin"></k8sLink> secret.

Then:
*  Import the realm into keycloak from a backup
*  Regenerate the secret for the 2 clients:
    *  `admin-cli` : then update the secret  `keycloak-admin-secret.keycloak_admin_client_secret` in namespace `apps`.
    *  `oidc-token-generator` : then update the secret  `openid-app-secret.openid_client_secret` in namespace `apps`.

<note level="hint" title="Service and Pods created by PGO" expandable="true">

The Keycloak service uses the following resources to connect to the PostGres database.
Connection parameters (`$USERNAME`, `$PASSWORD`, `$PORT`, *etc.* ) are gathered in 
<k8sLink kind='Secret' namespace="infra" target="keycloak-pguser-keycloak"></k8sLink> secret.

**1. `keycloak-primary` (Headless Service)**:
  - **`keycloak-primary`** is the name of a **Kubernetes Headless Service** associated with the Keycloak deployment
    to connect to the PostGres DB.
  - **Headless Service**: Unlike a regular Kubernetes service, a **headless service** does not provide a stable 
    cluster IP. Instead, it creates DNS records for each pod in the service, allowing direct communication between 
    services and individual pods. This is useful when you need to route traffic to specific pods 
    (e.g., in a StatefulSet) rather than load-balancing across multiple pods.
  - **Function**: The **headless service** enables DNS resolution for pods in the Keycloak deployment to PostGres DB, 
    typically used when you need direct access to a specific pod or for StatefulSets where pods are identified by 
    their names. For instance, the headless service can be used to connect to the Keycloak pods during data export 
    tasks using the `kc.sh export` command. See <cross-link target="db.restore">Restore Data</cross-link> 
    for more details.

**2. `keycloak-00-t5mp` (StatefulSet)**:
  - **`keycloak-00-t5mp`** refers to a **StatefulSet** that manages the Keycloak PostgreSQL database.
  - There is currently **one pod** in this StatefulSet, named `keycloak-00-t5mp-0`. However, the number of pods 
    can be adjusted in the StatefulSet configuration, resulting in pod names like `keycloak-00-t5mp-1`, 
    `keycloak-00-t5mp-2`, etc.
  - These pods manage persistent storage for Keycloak's PostgreSQL database. You can **port-forward** to a 
    specific pod's for local database access, for example:
    ```bash
    kubectl port-forward keycloak-00-t5mp-0 -n infra $PORT:$PORT
    ```
    This is commonly used when setting up **pgAdmin**.
    You can as well run `psql` within a pod:
    ```bash
    kubectl exec -it keycloak-00-t5mp-0 -n infra -- psql -h localhost -U $USERNAME --password -p $PORT $DBNAME
    ```

</note>


To register the PostGres database in `pgadmin`:
*  Log-in the PgAdmin application from your browser.
*  Register a new server
*  Provide `host`, `username`, `password` and `port` from 
<k8sLink kind='Secret' namespace="infra" target="keycloak-pguser-keycloak"></k8sLink> secret.

---

## 🗄️ Minio

**MinIO** is an open-source, high-performance, and scalable object storage solution designed to handle unstructured data like photos, videos, logs, backups, and other large files. It is fully compatible with the **Amazon S3 API**, enabling easy integration with tools and applications that use S3 for storage.

- **S3-Compatible Object Storage**: MinIO allows you to store and manage large amounts of data with an interface that mimics Amazon S3. It supports the same operations (e.g., `PUT`, `GET`, `DELETE`) and integrates easily with applications designed for S3.

- **High Availability & Scalability**: MinIO can be deployed in a distributed configuration, providing high availability and horizontal scalability to handle growing data needs. It is suitable for both on-premises and cloud-native environments like Kubernetes.

- **Security & Encryption**: MinIO offers advanced features like server-side encryption, access controls, and data policies to protect your data and ensure that only authorized users can access it.

MinIO is a powerful solution for cloud-native storage, offering a lightweight and easy-to-deploy alternative to traditional object storage systems, while remaining highly compatible with modern application stacks.

**Requirements**:
*  `ServiceMonitor` CRD

<k8sShell pwd="infra/minio">
helm install minio ./ --namespace=infra
</k8sShell>

To access the minio console from your browser:
*  <portForward target="minio-console" hostPort="9001" namespace="infra"></portForward>,
*  `admin` as username and the value of the secret `admin-secret-key` from
   <k8sLink kind='Secret' namespace="infra" target="minio-admin-secret"></k8sLink> as password to login.

**Start-up database**

Execute the python script:

<k8sShell>
from w3k8s_adm.copy_local_data import copy_db
from pathlib import Path
import asyncio 

# adjust db_path & k8s_ctx
task = copy_db(
  db_path=Path.home() / 'Projects' / 'py-w3nest-db' / 'startup-db', 
  k8s_ctx="minikube"
)
asyncio.run(task)

</k8sShell>
 
---

## 🔥 Redis

**Redis** is an open-source, in-memory data structure store, commonly used as a database, cache, and message broker.
It supports various data structures such as strings, hashes, lists, sets, and more, and is widely known for its 
high performance and low latency, making it a popular choice for real-time applications.

- **In-Memory Database**: Redis stores all its data in memory, making it extremely fast for both read and 
  write operations. This in-memory model allows for quick data retrieval and manipulation, which is ideal for caching, 
  session management, and leaderboards.

- **Persistence & Durability**: Although Redis operates in-memory, it can also persist data to disk for durability, 
  offering options for data snapshotting and append-only files to recover from crashes or restarts.

- **Pub/Sub Messaging**: Redis supports publish/subscribe messaging paradigms, making it useful for event-driven 
  applications, message queues, and real-time notifications.

- **High Availability & Scalability**: Redis can be configured in a clustered setup, offering high availability 
  and the ability to scale horizontally across multiple nodes to handle increasing loads.

Redis is a versatile tool, excelling in use cases where fast data retrieval, real-time processing, and message 
passing are critical. It integrates well into many different environments, from simple caching solutions to 
complex distributed systems.

<k8sShell pwd="infra/redis">
helm install redis ./ --namespace=infra
</k8sShell>

Upon completion a `redis-master` service should be available:

<service target="redis-master" namespace="infra"></service>

---

## 🛡️ Cert Manager

**Cert Manager** is an open-source Kubernetes add-on that automates the management and issuance of SSL/TLS certificates 
within Kubernetes clusters. It simplifies the process of obtaining, renewing, and managing certificates, ensuring 
secure communication for your applications and services.

- **Automated Certificate Management**: Cert Manager automates the process of acquiring, renewing, and managing 
  certificates from various certificate authorities (CAs), such as Let's Encrypt, HashiCorp Vault, and others. 
  It integrates seamlessly into Kubernetes, reducing manual intervention and ensuring certificates are always 
  up-to-date.

- **Support for Multiple Issuers**: Cert Manager supports a wide variety of certificate issuers. 
  You can configure multiple issuers to obtain certificates from different sources, allowing you to leverage 
  both public and private CAs for your services.

- **Kubernetes Native**: Cert Manager integrates directly with Kubernetes resources such as Ingress, Secrets,
   and CustomResourceDefinitions (CRDs). This means it can automatically inject certificates into your services,
   making the management of encrypted communication simple and straightforward.

- **ACME Protocol Support**: Cert Manager natively supports the ACME protocol, enabling easy integration with
   Let's Encrypt and other ACME-compatible CAs to automatically obtain and renew SSL/TLS certificates.

- **Security**: Cert Manager is an essential tool for securing your applications and services by ensuring that
   all communications are encrypted with trusted certificates. It reduces the overhead of manual certificate management
   and ensures compliance with security standards.

Cert Manager is ideal for Kubernetes environments where managing SSL/TLS certificates at scale is needed, 
particularly when securing Ingress endpoints and internal communications across services.

<k8sShell pwd="prerequisites/cert-manager">
helm install cert-manager ./ --namespace=cert-manager
</k8sShell>

---

## 📦 Static Assets

Static assets are non-dynamic resources used by web applications, such as images, CSS stylesheets, JavaScript files, 
fonts, videos, and other content that doesn't change frequently and is directly served to the client.

This chart deploys a <ext-link target="nginx">nginx container</ext-link> whose purpose is:
*  serving static assets (HTML pages, images, etc) required by the deployments on `/static` sub paths.
*  allowing switching in `maintenance` mode to serve a dedicated 'Maintenance Page' on all public end-points 
   when activated.

The `/assets` folder is used to store the static files, and the following directories are mounted:
- **Templates**: Mounted at `/etc/nginx/templates`
- **Sites**: Mounted at `/usr/share/nginx`

The assets are exposed through a ConfigMap containing a base64-encoded version of the `/assets` folder, 
sourced from the file `includes/assets.zip.b64`. 
To generate the base64-encoded version, use the following commands:

```bash
zip -r assets.zip assets/ && 
base64 assets.zip > includes/assets.zip.b64 &&
rm assets.zip
```

After updating the assets folder, re-run this command and upgrade the chart with:

```bash
helm upgrade static-assets ./ --namespace=infra
```

In addition to the assets, a ConfigMap is deployed with content from `includes/maintenance-details.txt`
which is mounted at:

`/usr/share/nginx/includes/maintenance/details.txt`.

### Installation

To install the chart, run:

<k8sShell pwd="infra/static-assets">
helm install static-assets ./ --namespace=infra
</k8sShell>

The following ingresses are deployed:


*  <ingress namespace="infra" target="static-assets-static-assets"></ingress>
   Publicly exposed as the route `/static/`. It serves the folder `sites/static-assets` from the `/assets` folder.

*  <ingress namespace="infra" target="static-assets-default-route"></ingress>
   The [defaultBackend](https://kubernetes.io/docs/concepts/services-networking/ingress/#default-backend) for 
   Kubernetes Ingresses.

*  <ingress namespace="infra" target="static-assets-maintenance"></ingress>
   It defines the route that are disabled when the cluster is set to `maintenance` mode, by setting the attribute
   `ingressClassname` of this ingress to `kong`. 
   By default, it does not have an `ingressClassname` attribute, which effectively disable it.

Here is for instance the pages served when an error occurred:

*  <cluster-link target="static/403.html">static/403</cluster-link> : unauthorized to access the resource.
*  <cluster-link target="static/404.html">static/404</cluster-link> : resource not found.

### Maintenance Mode

You can enable maintenance mode by setting the `ingressClassname` of the `maintenance` ingress to `kong`. 
This will redirect requests targeted by the ingress **static-assets-maintenance** to the `maintenance` host 
served by Nginx.

To restore these routes, simply unset the `ingressClassname` attribute.

The maintenance page can be customized by editing the ConfigMap content, ensuring that the page serves the 
appropriate file from the provided data.

**Note:** By default, the `maintenance` ingress does not have an `ingressClassname` attribute, 
which effectively disables it.

<note level="warning" title="Maintenance Mode Issue">
The ingress class `nginx` is currently set as the default in Minikube (via an addon). This setup needs to be changed. 
To disable the ingress, a different value for the `ingressClassname` (e.g., `foo`) must be used.
For more information, refer to: 
[Webhook Admission for Ingress Class](https://github.com/w3nest/cluster-static-assets/blob/main/templates/default-route.conf.template)
</note>