# Minikube Install & Setup

## Installation

Minikube was installed by following this guide:
*  [Installing Minikube on Ubuntu 20.04 LTS](https://medium.com/@areesmoon/installing-minikube-on-ubuntu-20-04-lts-focal-fossa-b10fad9d0511)


<note level="abstract" expandable="true" title="install" mode="stateful">
To install **Minikube** on Ubuntu 24.04, follow these steps:

---

### **1. Update Your System**
First, make sure your system is up to date:
```bash
sudo apt update && sudo apt upgrade -y
```

---

### **2. Install Required Dependencies**
Minikube requires `conntrack`, `curl`, and `virtualization tools`:
```bash
sudo apt install -y curl conntrack
```

Check if your system supports virtualization (for `KVM` or `VirtualBox`):
```bash
egrep -q 'vmx|svm' /proc/cpuinfo && echo "Virtualization supported" || echo "No virtualization support"
```
If **virtualization is not supported**, Minikube will use the `--driver=none` mode (bare metal).

---

### **3. Install Minikube**
Download and install the latest Minikube binary:
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

Verify the installation:
```bash
minikube version
```
.---


### **4. Install kubectl (Kubernetes CLI)**
You'll need `kubectl` to interact with Minikube:
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl
```

Verify:
```bash
kubectl version --client
```

---


### **5. Start Minikube**
If you have virtualization support (KVM or VirtualBox), use:
```bash
minikube start --driver=kvm2
```
Otherwise, for **bare metal (no VM)**, use:
```bash
minikube start --driver=none
```
⚠️ **Note**: When using `--driver=none`, Minikube runs directly on your server. You need to run it as **root**:
```bash
sudo minikube start --driver=none
```

---

### **6. Check Minikube Status**
```bash
minikube status
```

---

### **7. Enable the Minikube Ingress Controller (Optional)**
If you plan to use **Ingress (NGINX)** for routing:
```bash
minikube addons enable ingress
```

---

### **8. Verify Your Kubernetes Cluster**
```bash
kubectl get nodes
```
If Minikube is running, you should see:
```
NAME       STATUS   ROLES    AGE   VERSION
minikube   Ready    master   1m    v1.29.0
```

---

### **9. Set Minikube IP (If Needed for External Access)**
To get the Minikube IP:
```bash
minikube ip
```
If you want Minikube to listen on your server's **public IPv4** (e.g., `54.39.16.218`), you may need to:
```bash
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination $(minikube ip):80
sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination $(minikube ip):443
```

---

### **That's It! 🎉**
You now have **Minikube running on your Ubuntu server**. Let me know if you need help! 🚀
</note>
---

### Start

<k8sShell>
 minikube start 
</k8sShell>

Minikube **automatically selects the best driver** (if none is specified), in my case `docker`. 
You can force it adding `--driver=docker`.

<note level="info" title='Outputs' expandable="true">
This is the output I have:

```
(3.12) ➜  keycloak git:(nevado-tres-cruces) ✗ minikube start
😄  minikube v1.34.0 sur Ubuntu 22.04
✨  Choix automatique du pilote docker
📌  Utilisation du pilote Docker avec le privilège root
👍  Démarrage du nœud "minikube" primary control-plane dans le cluster "minikube"
🚜  Extraction de l'image de base v0.0.45...
🔥  Création de docker container (CPU=2, Memory=7900Mo) ...
🐳  Préparation de Kubernetes v1.31.0 sur Docker 27.2.0...
▪ Génération des certificats et des clés
▪ Démarrage du plan de contrôle ...
▪ Configuration des règles RBAC ...
🔗  Configuration de bridge CNI (Container Networking Interface)...
🔎  Vérification des composants Kubernetes...
▪ Utilisation de l'image gcr.io/k8s-minikube/storage-provisioner:v5
🌟  Modules activés: storage-provisioner, default-storageclass

❗  /usr/local/bin/kubectl est la version 1.25.0, qui peut comporter des incompatibilités avec Kubernetes 1.31.0.
▪ Vous voulez kubectl v1.31.0? Essayez 'minikube kubectl -- get pods -A'
🏄  Terminé ! kubectl est maintenant configuré pour utiliser "minikube" cluster et espace de noms "default" par défaut.
```
</note>

<note level="warning" title="multi-nodes & PV/PVC" expandable="true">
For multi-nodes minikube setup, there is a challenge regarding PV & PVC to be shared across nodes.

See:
* [Mounting Volume for Two Nodes in Minikube](https://stackoverflow.com/questions/70878064/mounting-volume-for-two-nodes-in-minikube)
* [Minikube Multi-Node Cluster with Shared NFS Mount PV](https://techexpertise.medium.com/minikube-multi-node-k8s-cluster-with-shared-nfs-mount-pv-cb3105f9a2c7)

maybe to look at:
minikube addons enable storage-provisioner
</note>

---

### Enabling Minikube addons

<k8sShell>
minikube addons enable metrics-server
minikube addons enable dashboard
minikube addons enable ingress
</k8sShell>

<note level="warning">
Ingress takes a while to verify.
</note>

The enabled addons are:  
*  `dashboard`
*  `default-storageclass`
*  `ingress`
*  `metrics-server`
*  `storage-provisioner`.

<note level="hint" icon="fas fa-external-link-alt" title="Links" expandable="true">
*  [IngressMinikube](https://kubernetes.io/docs/tasks/access-application-cluster/ingress-minikube/)
</note>


---

### Minikube Dashboard

<k8sShell>
minikube dashboard
</k8sShell>

After a little while, the K8s dashboard will open.

<note level="hint" icon="fas fa-external-link-alt" title="Links" expandable="true">
[minikube-dashboard](https://medium.com/@areesmoon/setting-up-minikube-and-accessing-minikube-dashboard-09b42fa25fb6)
</note>

---

### Ingress Configuration

#### Local Minikube

To access services exposed via Ingress, add entries in `/etc/hosts`.

1️⃣ First, get the Minikube IP:
```sh
minikube ip
```
Example output:
```sh
192.168.49.2
```

2️⃣ Then, register the domain names in `/etc/hosts`:
```plaintext
192.168.49.2 w3nest.minikube
192.168.49.2 tooling.w3nest.minikube
```
These domains are **local-only** and work only on your PC.

#### Remote Minikube

TBC 


## **Using Local Docker Images in Minikube**  

1. **Configure Docker to Use Minikube’s Environment**  
   Run the following command to set up your Docker environment so that images are built within Minikube’s context:  
   ```sh
   eval $(minikube docker-env)
   ```

2. **Build the Backend Image**  
   From the `py-w3nest` directory, build the Docker image and tag it appropriately:  
   ```sh
   docker build -f images/backends/Dockerfile -t backends -t backends:0.1.13-wip .
   ```

3. **Disable Image Pulling in Helm Configuration**  
   Ensure that the `imagePullPolicy` is set to `Never` in `k8s-deployments/w3nest.values.yaml` for all `w3nest` 
   sub-charts to allow Kubernetes to use the locally built image without trying to pull it from a remote registry.


## Configuring Self Signed Certificate

You can generate a self-signed SSL certificate for your local `w3nest.minikube` domain to use with HTTPS. 
Here's how to create and configure a self-signed certificate for `w3nest.minikube` on your local machine:

### Step 1: Generate a Self-Signed Certificate

1. **Open a terminal** and create a directory to store the certificate files (optional):

   ```bash
   mkdir -p ~/certs/w3nest.minikube
   cd ~/certs/w3nest.minikube
   ```

2. **Generate the certificate** and private key for `w3nest.minikube` using OpenSSL:

   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout w3nest.minikube.key \
       -out w3nest.minikube.crt \
       -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=w3nest.minikube"
   ```

3. Add `w3nest.minikube` to the certificate's Subject Alternative Names (SAN) if needed:

   ```bash
   openssl req -new -key w3nest.minikube.key -out w3nest.minikube.csr \
       -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=w3nest.minikube"
   
   openssl x509 -req -in w3nest.minikube.csr -signkey w3nest.minikube.key \
       -out w3nest.minikube.crt -days 365 \
       -extfile <(printf "subjectAltName=DNS:w3nest.minikube")
   ```

This will generate:
- `w3nest.minikube.key`: The private key for the certificate.
- `w3nest.minikube.crt`: The self-signed certificate.

### Step 2: Configure Minikube to Use the Self-Signed Certificate

1. **Copy the certificate files** to a location where Minikube can access them.

2. **Create a Kubernetes secret** in the same namespace as your `Ingress` resource. This secret will hold the certificate and key:

   ```bash
   kubectl create secret tls w3nest-minikube-tls \
       --cert=w3nest.minikube.crt \
       --key=w3nest.minikube.key \
       --namespace=default  # or the namespace of your Ingress resource
   ```

### Step 3: Configure the Ingress to Use the Self-Signed Certificate

Edit your Ingress configuration to use the newly created TLS secret.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: w3nest-ingress
  namespace: default  # or your Ingress namespace
spec:
  rules:
    - host: w3nest.minikube
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web  # your service name
                port:
                  number: 8080
  tls:
    - hosts:
        - w3nest.minikube
      secretName: w3nest-minikube-tls
```

### Step 4: Add `w3nest.minikube` to Your Local Trust Store

For your browser or application to trust this self-signed certificate, add `w3nest.minikube.crt` to the trusted certificates on your machine.

- **On Linux**:
  ```bash
  sudo cp w3nest.minikube.crt /usr/local/share/ca-certificates/
  sudo update-ca-certificates
  ```

- **On macOS**:
  Double-click the `.crt` file and add it to the Keychain Access as a trusted certificate.

- **On Windows**:
  Open the certificate file, then install it in the “Trusted Root Certification Authorities” store.

### Step 5: Test HTTPS Access

You should now be able to access `https://w3nest.minikube` in your browser or application without SSL verification errors.
