# Keycloak

Databases care not exposed with ingresses, they can be accessed using port-forwarding.

---

## Guest Users

<guest-users></guest-users>


---

## Export realms

A Helm chart has been defined to export Keycloak realms. It provides an automated way to back up realm configurations using Keycloak's built-in export functionality.

**Chart Components**

This chart includes:

- **A Persistent Volume Claim (PVC)** used to store the exported data.
- **A Kubernetes Job** that runs `/opt/keycloak/bin/kc.sh export` to export realms into the mounted PVC.
- **A `pvc-debug` Pod**, which remains running to allow manual access to the exported data (e.g., via `kubectl cp`).

**Usage**

*  Deploy the Chart
   <k8sShell pwd="infra/keycloak-backup">
helm upgrade keycloak-backup ./ --namespace=infra
   </k8sShell>
*  Wait for the `keycloak-backup` export job to Complete
*  Use `kubectl cp` to download the exported realms from the PVC via the `pvc-debug` pod:
   <k8sShell pwd="infra/keycloak-backup">
kubectl cp infra/pvc-debug:/export ./keycloak-exported-realms 
   <k8sShell>


---

## Setup `kcadm.sh`

To setup `kcadm.sh`, within the pod: 
*  `/opt/keycloak/bin/kcadm.sh config credentials --server $KEYCLOAK_SERVER --realm master --user $KEYCLOAK_ADMIN --password $KEYCLOAK_ADMIN_PASSWORD`
*  and e.g. `/opt/keycloak/bin/kcadm.sh get realms/youwol` 


---

## PostgreSQL Database Backup

The `keycloak-repo-host-0` pod is responsible for managing **backup and restore operations** using `pgBackRest`.

<note level="question" title="`pgBackRest`?" expandable="true">
Sure! Here's a concise description of **pgBackRest** you can include in your documentation:

---

### What is `pgBackRest`?

**pgBackRest** is a robust and reliable backup and restore solution for **PostgreSQL** databases. 
It is designed to handle large-scale, high-performance environments with features such as:

- **Full, incremental, and differential backups**
- **Compression** and **encryption** of backups
- **Parallel processing** for faster performance
- **Retention policies** to manage backup lifecycle
- **Write-Ahead Log (WAL)** archiving for point-in-time recovery
- **Stanza-based configuration** for managing multiple databases independently

It ensures **data integrity**, **consistency**, and **efficiency** during backup and restore operations, 
making it ideal for production-grade PostgreSQL deployments.
</note>

**Access the Backup Pod**

To connect to the pod via shell:

```sh
kubectl exec -it keycloak-repo-host-0 -n infra -- sh
```

Once inside the pod, the `pgbackrest` command-line tool is available for interacting with backups.


**Backup Directory**

Automated and manual backups are stored in:

```sh
/pgbackrest/repo1/backup/db
```

You can explore this directory to inspect or verify available backup archives.

**View Available Stanzas**

Run the following command to list all defined **stanzas**:

```sh
pgbackrest info
```

<note level="question" title="What is a 'stanza' in pgBackRest?" expandable="true">
A **stanza** in `pgBackRest` defines a backup configuration for a specific PostgreSQL database or cluster.

Each stanza includes:
- A unique **name** (e.g., `db`)
- The **database path**
- **Backup settings** (e.g., full/incremental, retention)
- WAL archiving configuration

The stanza allows `pgBackRest` to handle multiple backup targets independently.  
Common commands using a stanza:

- `pgbackrest --stanza=db info`: Shows backup info for the `db` stanza.
- `pgbackrest --stanza=db backup`: Triggers a backup of the associated database.
</note>

To view details of the `db` stanza:

```sh
pgbackrest --stanza=db info
```
<note level="info" title="Example output" expandable="true">
```shell
stanza: db
    status: ok
    cipher: none

    db (current)
        wal archive min/max (15): 000000010000000000000001/000000530000002E0000004D

        full backup: 20241030-160209F
            timestamp start/stop: 2024-10-30 16:02:09 / 2024-10-30 16:04:58
            wal start/stop: 000000010000000000000002 / 000000010000000000000004
            database size: 33.8MB, database backup size: 33.8MB
            repo1: backup set size: 3.9MB, backup size: 3.9MB
```
</note>


**Trigger a Manual Backup**

To initiate a **full backup** manually:

```sh
pgbackrest --stanza=db backup --type=full
```

The new backup will appear in:

```sh
/pgbackrest/repo1/backup/db
```

<note level="hint">
During the backup process, the PostgreSQL database remains fully operational, assuming that **WAL archiving** 
is properly set up.

This ensures backups are consistent and reflect all changes up to the backup's completion.
</note>
