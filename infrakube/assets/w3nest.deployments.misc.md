

# Misc


## IntelliJ

Pugins:
* `Remote File System` to connect to minio
*  In `Big Data Tools` -> Minio -> aborded
*  In `services` connect to the k8s cluster
*  In `databases`, add `postgress` data source, in settings.kubernetes:
    *  cluster: `minikube`
    *  namespace: `infra`
    *  pod: `keycloak-00-xxx`
    *  host & container port: `5432`
    *  login & pwd: use secret `keycloak-pguser-keycloak` with `user` & `password`
    *  in schemas, select all `keycloak`
    *  In `databases.postgres@localhost` look at `keycloak.public.tables`


Evolution

*  there is one chart per backend + webpm, only one gathering all of them would be more effective
*  taiga for me : use dockercompose and deploy locally + backups on google drive (folder 'backup')
*  `helm-lib/lib-backend` is useless (only 1 usage, also related to first point).



## Questions 

*  `docdb` &  `storage`
*  reference `tbd_test_openid`
*  How to include 'Create account' on login page
*  Running data-manager in local thoughts
*  Publish final `py-youwol` package

## Data Manager in local

Main issue: move backup data in cluster in some ways.


## Generate certificate

Yes, you can generate a self-signed SSL certificate for your local `w3nest.minikube` domain to use with HTTPS. 
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

## Global certificate

*  using `opennssl s_server ...` allow to test a certifcate from a browser 

```
pip install certbot
pip install certibot-dns-godaddy
```

2 ways to verify certificate:
-  via DNS
-  via HTTP (simpler but only good for a simple site)

But only DNS allows wildcard e.g. '*.w3nest.org'. -> Always use DNS for w3nest

Protocole ACME, 2 URL proposed by certbot:
*  stagging (Test) -> will generate certificate but not usable (or config browser to allow using the staging certificate)
   Détails pour environment staging de Let’s Encrypt : https://letsencrypt.org/docs/staging-environment/
*  prod (Real)

On my computer, certificates for letsencrypt is in `/etc/ssl/certs`, they are called `ISRG_Root*`.

We can add manually certificates in my browser (to test, but just one shot, not trusted).
see `pem` links for `bogus` & `pretend` in https://letsencrypt.org/docs/staging-environment/.

They define authorities that will be required to be installed in the browser to test the certificates emitted
by certbot when using `stagging` environment.

```
certbot --logs-dir ./certbot/logs --config-dir ./certbot/config --work-dir ./certbot/lib certonly 
--authenticator dns-godaddy --dns-godaddy-credentials ./certbot/godaddy.credentials.prod.ini 
--domains 'w3nest.org,*.w3nest.org' --dry-run (or --stagging)
```

