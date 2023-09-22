{{- define "data-manager.backup-job-spec" -}}
{{- $type_job := required "data-manager.backup-job-spec template expects key '.typeJob' in scope" .typeJob -}}
{{- $root := required "data-manager.backup-job-spec template expects key '.typeBackup' in scope" .root -}}
{{- $suspend := dig "suspend" true . }}
{{- $subtasks := $root.Values.jobs.subtasks | default "cassandra:keycloak:s3" }}
{{- if not (has $type_job (list "manualBackup" "cronBackup" "manualRestore")) }}
{{- fail "data-manager.backup-job-spec template expects key '.typeJob' to be either 'manualBackup', 'cronBackup' or 'manualRestore'" }}
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
          - setup
        env:
          - name: JOB_UUID
            valueFrom:
              fieldRef:
                fieldPath: metadata.labels['controller-uid']
          - name: JOB_SUBTASKS
            value: {{ $subtasks }}
          - name: OIDC_ISSUER
            valueFrom:
              configMapKeyRef:
                name: {{ include "data-manager.config.name" $root }}
                key: oidc_issuer
          - name: OIDC_CLIENT_ID
            valueFrom:
              configMapKeyRef:
                name: {{ include "data-manager.config.name" $root }}
                key: oidc_client_id
          - name: OIDC_CLIENT_SECRET
            valueFrom:
              secretKeyRef:
                name: {{ include "data-manager.secret.name" $root }}
                key: oidc_client_secret
          - name: GOOGLE_DRIVE_ID
          {{- if (and (eq $type_job "manualRestore") ( $root.Values.jobs.manualJobs.restore.googleDriveId )) }}
            value: {{ $root.Values.jobs.manualJobs.restore.googleDriveId }}
          {{- else }}
            valueFrom:
              secretKeyRef:
                name: {{ include "data-manager.secret.name" $root }}
                key: google_drive_id
          {{- end }}
          {{- if ( and (eq $type_job "manualRestore") ($root.Values.jobs.manualJobs.restore.archiveName) )}}
          - name: RESTORE_ARCHIVE_NAME
            value: {{ $root.Values.jobs.manualJobs.restore.archiveName }}
          {{- end }}
          - name: KEYCLOAK_SCRIPT
          {{- if (eq $type_job "manualRestore")}}
            value: import
          {{- else }}
            value: export
          {{- end }}
        volumeMounts:
          - mountPath: /var/opt/data-manager
            name: work
    containers:
      - name: main
        image: "registry.gitlab.com/youwol/platform/cluster-data-manager:{{ $root.Chart.AppVersion }}"
        args:
          - {{ eq $type_job "manualRestore" | ternary "restore" "backup" }}
        env:
          - name: JOB_UUID
            valueFrom:
               fieldRef:
                 fieldPath: metadata.labels['controller-uid']
          {{- if contains "s3" $subtasks}}
          - name: S3_BUCKETS
            valueFrom:
              configMapKeyRef:
                name: {{ include "data-manager.config.name" $root }}
                key: s3_buckets
          - name: MINIO_LOCAL_ACCESS_KEY
            value: root
          - name: MINIO_LOCAL_SECRET_KEY
            valueFrom:
              secretKeyRef:
                name: {{ include "data-manager.secret.name" $root }}
                key: minio_local_secret_key
          - name: S3_HOST
            valueFrom:
              configMapKeyRef:
                name: {{ include "data-manager.config.name" $root }}
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
          {{- end }}
          {{- if contains "cassandra" $subtasks}}
          - name: CQL_HOST
            valueFrom:
              configMapKeyRef:
                name: {{ include "data-manager.config.name" $root }}
                key: cql_host
          - name: CQL_KEYSPACES
            valueFrom:
              configMapKeyRef:
                name: {{ include "data-manager.config.name" $root }}
                key: cql_keyspaces
          - name: CQL_TABLES
            valueFrom:
              configMapKeyRef:
                name: {{ include "data-manager.config.name" $root }}
                key: cql_tables
          {{- end }}
          {{- if contains "keycloak" $subtasks }}
          - name: KEYCLOAK_BASE_URL
            value: {{ printf "https://%s/auth" (include "data-manager.hosts.clusterDomain" $root ) | quote }}
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
          {{- end }}
          - name: JOB_SUBTASKS
            value: {{ $subtasks }}
          {{- if ($root.Values.jobs.maintenance)}}
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
            {{- if (ne $type_job "manualRestore") }}
            value: {{ $root.Values.jobs.maintenance.configMap.valueBackup | quote }}
            {{- else }}
            value: {{ $root.Values.jobs.maintenance.configMap.valueRestore | quote }}
            {{- end }}
          {{- else }}
          - name: MAINTENANCE_ENABLE
            value: "no"
          {{- end }}
          {{- if (ne $type_job "manualRestore") }}
          - name: TYPE_BACKUP
            value: {{ eq $type_job "cronBackup" | ternary "cron" "manual" }}
          - name: GOOGLE_DRIVE_ID
            valueFrom:
              secretKeyRef:
                name: {{ include "data-manager.secret.name" $root }}
                key: google_drive_id
          - name: OIDC_ISSUER
            valueFrom:
              configMapKeyRef:
                name: {{ include "data-manager.config.name" $root }}
                key: oidc_issuer
          - name: OIDC_CLIENT_ID
            valueFrom:
              configMapKeyRef:
                name: {{ include "data-manager.config.name" $root }}
                key: oidc_client_id
          - name: OIDC_CLIENT_SECRET
            valueFrom:
              secretKeyRef:
                name: {{ include "data-manager.secret.name" $root }}
                key: oidc_client_secret
          {{- end }}
        volumeMounts:
          - mountPath: /var/opt/data-manager
            name: work

      {{- if contains "s3" $subtasks}}
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
                name: {{ include "data-manager.secret.name" $root }}
                key: minio_local_secret_key
        volumeMounts:
          - mountPath: /data
            name: work
      {{- end }}

      {{- if contains "keycloak" $subtasks }}
      - name: keycloak
        image: {{ printf "%s:%s" ($root.Values.jobs.keycloakImage.name | default "quay.io/keycloak/keycloak") $root.Values.jobs.keycloakImage.tag }}
        env:
          - name: PATH_WORK_DIR
            value: "/data/kc"
          {{- if $root.Values.jobs.keycloakImage.name }}
          - name: KEYCLOAK_IMAGE_OPTIMIZED
            value: "1"
          {{- end }}
          - name: PATH_KEYCLOAK_COMMON_SCRIPT
            value: "/data/kc/kc_common.sh"
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
            value: {{ include "data-manager.hosts.clusterDomain" $root }}
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

{{- end }}
