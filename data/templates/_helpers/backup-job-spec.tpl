{{- define "cluster-data-manager.backup-job-spec" -}}
{{- $type_job := required "cluster-data-manager.backup-job-spec template expects key '.typeJob' in scope" .typeJob -}}
{{- $root := required "cluster-data-manager.backup-job-spec template expects key '.typeBackup' in scope" .root -}}
{{- $suspend := dig "suspend" true . }}
{{- if not (has $type_job (list "manualBackup" "cronBackup" "manualRestore")) }}
{{- fail "cluster-data-manager.backup-job-spec template expects key '.typeJob' to be either 'manualBackup', 'cronBackup' or 'manualRestore'" }}
{{- end }}
suspend: {{ $suspend }}
parallelism: 1
template:
  spec:
    volumes:
      - name: work
        ephemeral:
          volumeClaimTemplate:
            spec:
              accessModes:
                - ReadWriteOnce
              resources:
                requests:
                  storage: 30Gi
    restartPolicy: Never
    imagePullSecrets:
    - name: gitlab-docker
    securityContext:
      runAsUser: 1000
      runAsGroup: 1000
      fsGroup: 1000
    initContainers:
      - name: setup
        image: "registry.gitlab.com/youwol/platform/cluster-data-manager:{{ $root.Chart.AppVersion }}"
        args:
          - {{ternary "setup_restore" "setup_backup" (eq $type_job  "manualRestore") }}
        env:
          {{- if (eq $type_job "manualRestore") }}
          - name: RESTORE_ARCHIVE_NAME
            value: {{ required "job restore expects value '.manual.restore.archiveName'" $root.Values.jobs.manualJobs.restore.archiveName }}
          {{- end }}
          - name: JOB_UUID
            valueFrom:
              fieldRef:
                fieldPath: metadata.labels['controller-uid']
          - name: GOOGLE_DRIVE_ID
            valueFrom:
              secretKeyRef:
                name: data-manager-secret
                key: google_drive_id
          - name: OIDC_ISSUER
            valueFrom:
              configMapKeyRef:
                name: data-manager-config
                key: oidc_issuer
          - name: OIDC_CLIENT_ID
            valueFrom:
              configMapKeyRef:
                name: data-manager-config
                key: oidc_client_id
          - name: OIDC_CLIENT_SECRET
            valueFrom:
              secretKeyRef:
                name: data-manager-secret
                key: oidc_client_secret
        volumeMounts:
          - mountPath: /var/opt/data-manager
            name: work
    containers:
      - name: main
        image: "registry.gitlab.com/youwol/platform/cluster-data-manager:{{ $root.Chart.AppVersion }}"
        args:
          - {{ ternary "restore" "backup" (eq $type_job "manualRestore") }}
        env:
          - name: JOB_UUID
            valueFrom:
               fieldRef:
                 fieldPath: metadata.labels['controller-uid']
          - name: S3_BUCKETS
            valueFrom:
              configMapKeyRef:
                name: data-manager-config
                key: s3_buckets
          - name: MINIO_LOCAL_ACCESS_KEY
            value: root
          - name: MINIO_LOCAL_SECRET_KEY
            valueFrom:
              secretKeyRef:
                name: data-manager-secret
                key: minio_local_secret_key
          - name: S3_HOST
            valueFrom:
              configMapKeyRef:
                name: data-manager-config
                key: s3_host
          - name: S3_TLS
            value: "no"
          - name: S3_ACCESS_KEY
            value: admin # From cluster
          - name: S3_SECRET_KEY
            valueFrom:
              secretKeyRef:
                name: minio-admin-secret
                key: admin-secret-key
          - name: CQL_HOST
            value: scylla-db-client.infra.svc.cluster.local # TODO: from template
          - name: CQL_KEYSPACES
            valueFrom:
              configMapKeyRef:
                name: data-manager-config
                key: cql_keyspaces
          - name: CQL_TABLES
            valueFrom:
              configMapKeyRef:
                name: data-manager-config
                key: cql_tables

          {{- if (eq $type_job "manualRestore") }}
          - name: RESTORE_OVERWRITE
            value: {{ $root.Values.jobs.manualJobs.restore.overwrite | quote | default "no" }}
          {{- else }}
          - name: TYPE_BACKUP
            value: {{ ternary "cron" "manual" (eq $type_job "cronBackup") }}
          - name: GOOGLE_DRIVE_ID
            valueFrom:
              secretKeyRef:
                name: data-manager-secret
                key: google_drive_id
          - name: OIDC_ISSUER
            valueFrom:
              configMapKeyRef:
                name: data-manager-config
                key: oidc_issuer
          - name: OIDC_CLIENT_ID
            valueFrom:
              configMapKeyRef:
                name: data-manager-config
                key: oidc_client_id
          - name: OIDC_CLIENT_SECRET
            valueFrom:
              secretKeyRef:
                name: data-manager-secret
                key: oidc_client_secret
          - name: KEYCLOAK_BASE_URL
            value: "https://platform.youwol.com/auth"
          - name: KEYCLOAK_USERNAME
            valueFrom:
              secretKeyRef:
                key: username
                name: keycloak-initial-admin
                optional: false
          - name: KEYCLOAK_PASSWORD
            valueFrom:
              secretKeyRef:
                key: password
                name: keycloak-initial-admin
                optional: false
          - name: MAINTENANCE_NAMESPACE
            value: {{ $root.Values.jobs.maintenance.namespace }}
          - name: MAINTENANCE_INGRESS_NAME
            value: {{ $root.Values.jobs.maintenance.ingress.name }}
          - name: MAINTENANCE_INGRESS_CLASS_NAME
            value: {{ $root.Values.jobs.maintenance.ingress.ingressClassName }}
          - name: MAINTENANCE_CONFIG_MAP_NAME
            value: {{ $root.Values.jobs.maintenance.configMap.name }}
          - name: MAINTENANCE_CONFIG_MAP_KEY
            value: {{ $root.Values.jobs.maintenance.configMap.key}}
          - name: MAINTENANCE_CONFIG_MAP_VALUE
            value: {{ $root.Values.jobs.maintenance.configMap.value | quote }}
          {{- end }}
        volumeMounts:
          - mountPath: /var/opt/data-manager
            name: work
      - name: minio
        image: quay.io/minio/minio:latest
        args:
          - minio
          - server
          - /data/minio
        env:
          - name: MINIO_ROOT_USER
            value: root
          - name: MINIO_ROOT_PASSWORD
            valueFrom:
              secretKeyRef:
                name: data-manager-secret
                key: minio_local_secret_key
        volumeMounts:
          - mountPath: /data
            name: work
      - name: keycloak
        image: quay.io/keycloak/keycloak:19.0.3
        env:
          - name: PATH_WORK_DIR
            value: "/data/kc"
          - name: PATH_KEYCLOAK_STATUS_FILE
            value: "/data/kc/kc_status"
          - name: KC_CACHE_STACK
            value: kubernetes
          - name: KC_CACHE
            value: ispn
          - name: KC_FEATURES
            value: token-exchange
          - name: KC_PROXY
            value: edge
          - name: KC_HTTP_RELATIVE_PATH
            value: /auth
          - name: KC_DB
            value: postgres
          - name: KC_DB_URL_HOST
            valueFrom:
              secretKeyRef:
                key: host
                name: keycloak-db-pguser-keycloak-db
          - name: KC_DB_URL_PORT
            valueFrom:
              secretKeyRef:
                key: port
                name: keycloak-db-pguser-keycloak-db
          - name: KC_DB_URL_DATABASE
            valueFrom:
              secretKeyRef:
                key: dbname
                name: keycloak-db-pguser-keycloak-db
          - name: KC_DB_USERNAME
            valueFrom:
              secretKeyRef:
                key: user
                name: keycloak-db-pguser-keycloak-db
          - name: KC_DB_PASSWORD
            valueFrom:
              secretKeyRef:
                key: password
                name: keycloak-db-pguser-keycloak-db
          - name: KEYCLOAK_ADMIN
            valueFrom:
              secretKeyRef:
                key: username
                name: keycloak-initial-admin
                optional: false
          - name: KEYCLOAK_ADMIN_PASSWORD
            valueFrom:
              secretKeyRef:
                key: password
                name: keycloak-initial-admin
                optional: false
          - name: jgroups.dns.query
            value: keycloak-discovery.infra
          - name: KC_HOSTNAME
            value: platform.youwol.com
          - name: KC_HTTP_ENABLED
            value: "true"
          - name: KC_HOSTNAME_STRICT_HTTPS
            value: "false"
        command: ["/bin/bash"]
        args: ["/data/kc/kc_script.sh"]
        volumeMounts:
          - mountPath: /data
            name: work

{{- end }}
