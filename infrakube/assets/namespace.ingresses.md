# **Ingresses**

## **What is a Kubernetes Ingress?**

A **Kubernetes Ingress** is an API object that manages external access to Services within a cluster, typically for 
HTTP and HTTPS traffic. Ingress allows you to define rules for routing traffic from outside the Kubernetes cluster to 
specific Services within it, using a variety of routing techniques such as host-based, path-based, and TLS termination.

In simple terms, Ingress acts as a smart gateway that directs external traffic to the appropriate internal Service in 
the cluster, offering more flexible and efficient traffic management compared to other exposure methods like 
`NodePort` or `LoadBalancer`.

---

## **Why Use Ingress?**

Ingress provides several benefits that make it the preferred method for exposing applications in Kubernetes:

- **Efficient External Access**: Ingress allows you to route multiple Services through a single external IP, avoiding
  the need for multiple `LoadBalancer` Services.
- **Advanced Routing**: Supports complex traffic-routing rules based on URL paths or hostnames, allowing better 
  organization and flexibility when deploying multiple services or microservices.
- **TLS Termination**: Ingress simplifies SSL/TLS management by handling certificate termination, offloading this task 
  from individual applications.
- **Cost-Effective**: By using one Ingress Controller and a single IP address, it reduces the costs associated with 
  provisioning multiple cloud load balancers.

---

## **Types of Kubernetes Ingress**

There are different types of Ingress, depending on how you configure the routing rules and traffic management. 
These include:

1. **Simple Ingress**: Directs traffic to a single backend Service. Useful when you have a single application to expose.
2. **Host-Based Ingress**: Routes traffic based on the requested hostname (e.g., `api.example.com`, `app.example.com`).
   This allows hosting multiple services on different subdomains or domains.
3. **Path-Based Ingress**: Routes traffic to different Services based on URL paths (e.g., `example.com/api` to one 
   Service, and `example.com/app` to another).
4. **TLS Ingress**: Supports secure HTTPS connections by terminating TLS at the Ingress Controller, providing encrypted 
   traffic without requiring each Service to manage its own SSL certificates.

---

## **Key Components of an Ingress**

1. **Ingress Resource**: The API object that defines routing rules (e.g., paths, hosts) for handling external requests.
2. **Ingress Controller**: A component that watches for changes to the Ingress resources and implements the routing
   rules. Popular Ingress Controllers include **NGINX**, **Traefik**, and **HAProxy**.
3. **Backend Services**: The Services that receive traffic from the Ingress resource based on defined routing rules.
4. **TLS Certificates**: Optional, used for securing HTTP traffic by supporting HTTPS and handling SSL/TLS termination 
   at the Ingress level.

---

## **Examples of Ingress Definition**

Here’s a simple example of an Ingress resource that routes traffic to two different services based on the URL path:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
  tls:
  - hosts:
    - example.com
    secretName: example-tls
```

In this example:
- Traffic to `example.com/api` is directed to `api-service`.
- Traffic to `example.com/web` is directed to `web-service`.
- TLS is enabled for secure communication.

---

## **Best Practices**

- **Use TLS**: Always configure TLS for secure traffic to ensure data privacy, especially for public-facing applications.
- **Keep Rules Simple**: While Ingress allows complex routing rules, keeping them simple makes it easier to 
  maintain and debug.
- **Monitor Ingress Performance**: Keep track of traffic patterns and performance using monitoring tools 
  (e.g., Prometheus, Grafana) to ensure your Ingress Controller is not overwhelmed.
- **Restrict Access**: Use Ingress annotations or policies to limit external access where necessary, avoiding exposure
  of sensitive internal Services.

---

## **Common Use Cases**

- **Hosting Multiple Services**: Ingress is ideal for scenarios where multiple microservices need to be hosted behind 
  a single IP, such as separating traffic to APIs, frontends, and admin interfaces.
- **Handling SSL/TLS Certificates**: Simplifies the management of certificates across multiple applications by 
  centralizing TLS termination.
- **Path-Based Routing**: Useful in monolithic applications or applications with different modules (e.g., an e-commerce
  site where `/shop` points to one Service and `/admin` to another).

---

## **Additional Resources**

- [Kubernetes Ingress Documentation](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Kubernetes Ingress Best Practices](https://kubernetes.io/blog/2020/07/21/ingress-controller-best-practices/)

---

## **Summary**

Kubernetes Ingress provides a powerful, flexible, and cost-effective way to manage external access to applications 
running in a cluster. With features like advanced routing, TLS termination, and support for multiple virtual hosts,
Ingress simplifies how services are exposed to the internet. When combined with best practices and proper monitoring, 
Ingress becomes a crucial part of managing network traffic in any Kubernetes environment.