# Services Account

## What is a Kubernetes Service Account?

A **Kubernetes Service Account** is an identity that pods use to authenticate and communicate with the Kubernetes API. 
Unlike user accounts meant for humans, Service Accounts are designed for applications, automation tasks, or processes 
running inside pods. 
They allow pods to interact securely with cluster resources based on predefined roles and permissions.

---

## Why Use a Service Account?

- **Pod API Access**: Service Accounts enable pods to authenticate and perform actions on Kubernetes resources 
  (like querying pods, accessing secrets, or modifying services).
- **Fine-Grained Permissions**: Service Accounts work with **Role-Based Access Control (RBAC)** to enforce granular 
  permissions, ensuring that pods only have access to resources they need, improving security.
- **Separation of Concerns**: Different applications or microservices running in different pods may need specific 
  permissions, and Service Accounts provide the mechanism to isolate their access to resources.
- **Automation**: Applications, CI/CD pipelines, or monitoring tools running inside pods can interact programmatically 
  with the Kubernetes API through Service Accounts.

---

## Types of Kubernetes Service Accounts

1. **Default Service Account**:
    - Every namespace has a **default Service Account** automatically created when the namespace is created.
    - Pods that do not explicitly specify a Service Account are automatically associated with the default Service
      Account of their namespace.

2. **Custom Service Accounts**:
    - You can create Service Accounts with specific roles and permissions tailored to a particular workload or 
      application.
    - Custom Service Accounts are used when you need to restrict or expand the pod’s access to the API beyond the 
      default account's permissions.

---

## Key Components of a Service Account

1. **ServiceAccount Resource**:
    - Defines the Service Account within a specific namespace. A pod can be associated with a Service Account,
      giving it the identity and permissions to interact with the Kubernetes API.

2. **Secret**:
    - A Service Account is linked to a **token** that Kubernetes stores as a **Secret**. This token allows the pod 
      to authenticate with the Kubernetes API. The token is usually mounted as a file inside the pod 
      (e.g., at `/var/run/secrets/kubernetes.io/serviceaccount/token`).

3. **RBAC (Roles and RoleBindings)**:
    - Kubernetes uses **Roles** and **RoleBindings** to assign specific permissions to a Service Account. 
      A Role defines what actions can be performed, while a RoleBinding assigns that role to the Service Account.

---

## Examples of Service Account Definition

1. **Creating a Service Account**:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: custom-sa
  namespace: my-namespace
```

2. **Using the Service Account in a Pod**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app-pod
spec:
  serviceAccountName: custom-sa
  containers:
  - name: my-container
    image: my-app-image
```

3. **Granting Permissions with RBAC**:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: my-namespace
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-reader-binding
  namespace: my-namespace
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: pod-reader
subjects:
- kind: ServiceAccount
  name: custom-sa
  namespace: my-namespace
```

---

## Best Practices

- **Principle of Least Privilege**: Assign Service Accounts the minimum permissions they need to perform their tasks. 
  Avoid giving broad access to resources or the API unless necessary.
- **Use Custom Service Accounts**: For each application or service, use custom Service Accounts with tailored 
  permissions rather than relying on the default Service Account.
- **Secure Token Access**: Ensure the token associated with the Service Account is handled securely and is only
  available to the pods that need it.
- **Namespace Isolation**: Keep Service Accounts scoped to specific namespaces and avoid using cross-namespace 
  Service Account bindings unless required.
- **Rotate Tokens**: Ensure token rotation mechanisms are in place for long-running workloads to reduce security risks.

---

## Common Use Cases

- **CI/CD Pipelines**: Using Service Accounts to automate the deployment of applications, interact with Kubernetes 
  resources, or update configurations from inside a CI/CD pod.
- **Monitoring and Logging**: Granting monitoring tools like Prometheus or Grafana access to query the 
  Kubernetes API for metrics and logs.
- **Application Access to Secrets**: Pods that need access to sensitive information (like API keys) can retrieve 
  Secrets stored in the cluster by being associated with a Service Account with the appropriate access rights.

---

## Additional Resources

- [Kubernetes Service Accounts Documentation](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/)
- [Role-Based Access Control (RBAC) in Kubernetes](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

---

## Summary

A **Service Account** in Kubernetes provides an identity for pods to authenticate with the API server and interact with 
cluster resources. It works closely with RBAC to assign fine-grained permissions, enhancing security and control over 
what a pod can access. Using custom Service Accounts is recommended for securing workloads, allowing you to assign the 
minimal required permissions.
They play a key role in automation, monitoring, and securing inter-service communication in modern Kubernetes 
environments.