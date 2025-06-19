


# ScyllaDB

<note level="warning">
Increase `aio-max-nr` in minikube.
<k8sShell pwd="prerequisites/cert-manager">
minikube ssh -- "echo 1048576 | sudo tee /proc/sys/fs/aio-max-nr"
minikube ssh -- "cat /proc/sys/fs/aio-max-nr" 
</k8sShell>
</note>
Install scylla-operator:

<k8sShell pwd="operators/scylla-operator">
helm install scylla-operator ./ --namespace=scylla-operator
</k8sShell>

Then, scylla-manager:

<k8sShell pwd="operators/scylla-manager">
helm install scylla-manager ./ --namespace=scylla-manager
</k8sShell>

<note level="warning">
It can take a couple of minutes for everything to get green.
</note>

Finally:

<k8sShell pwd="infra/scylla-db">
helm install scylla-db ./ --namespace=infra
</k8sShell>

---

# WebPM

<k8sShell pwd="webpm">
helm install webpm ./ --namespace=webpm
</k8sShell>

For now, it is required to be able to run the restore step.
