# Minikube In `ubuntu@54.39.16.218`

## Installation


### **1. Update Your System**
First, make sure your system is up to date:

<k8sShell>
sudo apt update && sudo apt upgrade -y
</k8sShell>

---

### **2. Install Required Dependencies**
Minikube requires `conntrack`, `curl`, and `virtualization tools`:

<k8sShell>
sudo apt install -y curl conntrack
</k8sShell>

Check if your system supports virtualization (for `KVM` or `VirtualBox`):

<k8sShell>
egrep -q 'vmx|svm' /proc/cpuinfo && echo "Virtualization supported" || echo "No virtualization support"
</k8sShell>
If **virtualization is not supported**, Minikube will use the `--driver=none` mode (bare metal).

---

### **3. Install Minikube**
Download and install the latest Minikube binary:

<k8sShell>
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
</k8sShell>

Verify the installation:

<k8sShell>
minikube version
</k8sShell>

---

### **4. Install kubectl (Kubernetes CLI)**

You'll need `kubectl` to interact with Minikube:

<k8sShell>
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl
</k8sShell>

Verify:

<k8sShell>
kubectl version --client
</k8sShell>

---

### **5. Install Docker**

<k8sShell>
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
</k8sShell>

### **6. Install Addons**

<k8sShell>
minikube addons enable metrics-server
minikube addons enable dashboard
minikube addons enable ingress
<k8sShell>


## Start Minikube

<k8sShell>
minikube start --driver=docker
</k8sShell>

Check Minikube Status:

<k8sShell>
minikube status
</k8sShell>

Verify Your Kubernetes Cluster

<k8sShell>
kubectl get nodes
</k8sShell>

### Minikube Dashboard

<k8sShell>
minikube dashboard
</k8sShell>

The port forward from the local PC (**adjust the `46401` port**):

<k8sShell>
ssh -L 8001:127.0.0.1:46401 ubuntu@54.39.16.218
</k8sShell>

Visit [the dashboard](http://127.0.0.1:8001/api/v1/namespaces/kubernetes-dashboard/services/http:kubernetes-dashboard:/proxy/).

### Connect to remote K8s cluster

Find out connection info:

<k8sShell>
kubectl cluster-info
Kubernetes control plane is running at https://192.168.49.2:8443
CoreDNS is running at https://192.168.49.2:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
</k8sShell>

And SSH to it from local PC:

<k8sShell>
ssh -L 8443:192.168.49.2:8443 ubuntu@54.39.16.218 -N
</k8sShell>

<note level="warning" title="Unauthenticated">
From local PC:

<k8sShell>
curl -k https://127.0.0.1:8443
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {},
  "status": "Failure",
  "message": "forbidden: User \"system:anonymous\" cannot get path \"/\"",
  "reason": "Forbidden",
  "details": {},
  "code": 403
}%  
</k8sShell>

As well:

<k8sShell>
kubectl get nodes                                   
error: You must be logged in to the server (Unauthorized)
</k8sShell>
</note>

#### Setup k8s config file

**Copy minikube credentials**

Create a `.minikube-ovh` folder, and copy minikube certificates:

<k8sShell>
scp -r ubuntu@54.39.16.218:~/.minikube/profiles ~/.minikube-ovh 
</k8sShell>

**Edit `.kube/config` to add cluster**

Add a new `cluster`, `context` & `user` in `.kube/config`:


<k8sShell>
apiVersion: v1
clusters:
- cluster:
    insecure-skip-tls-verify: true
    # certificate-authority: /home/greinisch/.minikube-ovh/ca.crt
    # server : https://k8s.w3nest.org
    server: https://127.0.0.1:8443
  name: minikube-ovh
contexts:
- context:
    cluster: minikube-ovh
    namespace: default
    user: minikube-ovh
  name: minikube-ovh
current-context: minikube-ovh
kind: Config
preferences: {}
users:
- name: minikube-ovh
  user:
    client-certificate: /home/greinisch/.minikube-ovh/profiles/minikube/client.crt
    client-key: /home/greinisch/.minikube-ovh/profiles/minikube/client.key
</k8sShell>

Finally:

<k8sShell>
kubectl config use-context minikube-ovh                    
Switched to context "minikube-ovh".
➜  .minikube-ovh kubectl get nodes                                              
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   43m   v1.32.0
</k8sShell>



## Setup nginx server

<note level="warning" title="`use-forwarded-headers`">

Set `use-forwarded-headers` for the `ingress-nginx-controller` config maps:

```
{
	"hsts": "false",
	"use-forwarded-headers": "true"
}
```
</note>

### Register hosts

Within OVH:

*  Acquire the domain `w3nest.org` 
*  Register the A records for `w3nest.org` & `tooling.w3nest.org` pointing to `minikube ip`.

### Configurations

In `/etc/nginx/sites-available/` add the following nginx server configuration files.


<note level="abstract" title="**w3nest.org**" expandable="true">
`sudo nano /etc/nginx/sites-available/w3nest.org` with

<k8sShell>
server {
    listen 80;
    server_name w3nest.org www.w3nest.org;

    location /.well-known/acme-challenge/ { # Allow Certbot renewals
        root /var/www/html;
    }

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name w3nest.org www.w3nest.org;

    ssl_certificate /etc/letsencrypt/live/w3nest.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/w3nest.org/privkey.pem;

    location / {
        proxy_pass http://192.168.49.2;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Port 443;
   }
}
</k8sShell>
</note>

<note level="abstract" title="**tooling.w3nest.org**" expandable="true">
`sudo nano /etc/nginx/sites-available/tooling.w3nest.org` with:

<k8sShell>
server {
    listen 80;
    server_name tooling.w3nest.org www.tooling.w3nest.org;

    location /.well-known/acme-challenge/ { # Allow Certbot renewals
        root /var/www/html;
    }

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tooling.w3nest.org www.tooling.w3nest.org;

    ssl_certificate /etc/letsencrypt/live/tooling.w3nest.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tooling.w3nest.org/privkey.pem;

    location / {
        proxy_pass http://192.168.49.2;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Port 443;
   }
}
</k8sShell>
</note>

Then create a sym-link in `/etc/nginx/sites-enabled/`:

<k8sShell>
sudo ln -s /etc/nginx/sites-available/w3nest.org /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/tooling.w3nest.org /etc/nginx/sites-enabled/
</k8sShell>


### Create SSL certificates

If not available, install `certbot`:

<k8sShell>
sudo apt update 
sudo apt install certbot python3-certbot-nginx
</k8sShell>

Generate the certificates:

<k8sShell>
sudo certbot --nginx -d w3nest.org
sudo certbot --nginx -d tooling.w3nest.org
</k8sShell>

<note level="abstract" title="ex. output" expandable="true">

```bash
Requesting a certificate for w3nest.org

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/w3nest.org/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/w3nest.org/privkey.pem
This certificate expires on 2025-06-30.
These files will be updated when the certificate renews.
Certbot has set up a scheduled task to automatically renew this certificate in the background.

Deploying certificate
Successfully deployed certificate for w3nest.org to /etc/nginx/sites-enabled/w3nest.org
Congratulations! You have successfully enabled HTTPS on https://w3nest.org

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
 * Donating to EFF:                    https://eff.org/donate-le
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

```
</note>


### Start nginx server

Make sure everything is OK:

<k8sShell>
sudo nginx -t
sudo nginx -T
</k8sShell>

Start the server:

<k8sShell>
sudo systemctl start nginx
sudo systemctl enable nginx
</k8sShell>

<note level="hint" title="nginx commands" expandable="true">
```bash
sudo systemctl stop nginx
sudo systemctl reload nginx
sudo tail -f /var/log/nginx/access.log
```
</note>

### Troubles Shooting

**308 redirects loop**

```bash
curl -I  https://w3nest.org/auth --resolve w3nest.org:443:192.168.49.2  # => OK
curl -I  https://w3nest.org/auth # 308 redirect loop
```

Likely missing the `use-forwarded-headers` in nginx-controller config map (see above).



## Setup GitHub

A SSH key has been generated in the server (at `~/.ssh/server_gh_sshkey`), and registered in github.


### Step 1: Start the SSH Agent

If the SSH agent isn't running, you can start it manually. Run the following command:

<k8sShell>
eval "$(ssh-agent -s)"
</k8sShell>

This command will start the SSH agent and set the necessary environment variables.

### Step 2: Add Your SSH Key to the Agent
Once the SSH agent is running, you can add your private key to it:

<k8sShell>
ssh-add ~/.ssh/server_gh_sshkey
</k8sShell>

Replace `server_gh_sshkey` with the actual name of your private key file.

### Step 3: Verify the Key is Added
Now you can verify that the key is correctly loaded into the SSH agent:

<k8sShell>
ssh-add -l
</k8sShell>

It should show your SSH key fingerprint if everything is set up correctly.


Configure SSH to use the right key when connecting to GitHub by editing the `~/.ssh/config` file.

Open or create the `~/.ssh/config` file:

<k8sShell>
nano ~/.ssh/config
</k8sShell>

Add this configuration to tell SSH to use the server_gh_sshkey private key for GitHub:

<k8sShell>
Host github.com
  User git
  HostName github.com
  IdentityFile ~/.ssh/server_gh_sshkey
  IdentitiesOnly yes
</k8sShell>

### Step 4: Test SSH Authentication with GitHub

Once your key is loaded, test the SSH connection to GitHub:

<k8sShell>
ssh -T git@github.com
</k8sShell>

You should see a message like:

```
Hi <your-github-username>! You've successfully authenticated, but GitHub does not provide shell access.
```

And be able to use github w/ `w3nest` repo, e.g.:

<k8sShell>
git clone git@github.com:w3nest/py-w3nest.git
</k8sShell>
