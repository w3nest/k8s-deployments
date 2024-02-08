{{- define "data-manager.job-spec" -}}
{{- $type_job := required "data-manager.job-spec template expects key '.typeJob' in scope" .typeJob -}}
{{- $root := required "data-manager.job-spec template expects key '.typeBackup' in scope" .root -}}
{{- $suspend := required "data-manager.job-spec template expects key '.suspend' in scope" .suspend }}
{{- $subtasks := .subtasks }}
{{- $subtask_keycloak := $subtasks | default "keycloak" | contains "keycloak" }}
{{- $subtask_s3 := $subtasks | default "s3" | contains "s3" }}
{{- $subtask_cassandra := $subtasks | default "cassandra" | contains "cassandra" }}
{{- $maintenance := list nil true | has .maintenance }}
{{- $keycloakRealmKeysRotation := .keycloakRealmKeysRotation | default "rotate" }}
{{- if not (has $type_job (list "manualBackup" "cronBackup" "manualRestore")) }}
{{- fail "data-manager.job-spec template expects key '.typeJob' to be either 'manualBackup', 'cronBackup' or 'manualRestore'" }}
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
    {{- if $root.Values.imagePullSecret }}
    imagePullSecrets:
    - name: {{ $root.Values.imagePullSecret }}
    {{- end }}
    securityContext:
      runAsUser: 10000
      runAsGroup: 10000
      fsGroup: 10000
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
          {{- if $subtasks}}
          - name: JOB_SUBTASKS
            value: {{ $subtasks }}
          {{- end }}
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
          - name: EXTERNAL_ACCOUNT_AUDIENCE
            valueFrom:
              configMapKeyRef:
                name: {{ include "data-manager.config.name" $root }}
                key: external_account_audience
          - name: EXTERNAL_ACCOUNT_IMPERSONATION_URL
            valueFrom:
              configMapKeyRef:
                name: {{ include "data-manager.config.name" $root }}
                key: external_account_impersonation_url
          - name: GOOGLE_DRIVE_ID
          {{- if (and (eq $type_job "manualRestore") ( (($root.Values.manual).restore).googleDriveId )) }}
            value: {{ $root.Values.manual.restore.googleDriveId }}
          {{- else }}
            valueFrom:
              secretKeyRef:
                name: {{ include "data-manager.secret.name" $root }}
                key: google_drive_id
          {{- end }}
          {{- if ( and (eq $type_job "manualRestore") ( (($root.Values.manual).restore).archiveName) )}}
          - name: RESTORE_ARCHIVE_NAME
            value: {{ $root.Values.manual.restore.archiveName }}
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
          {{- if $subtask_s3}}
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
          {{- if $subtask_cassandra}}
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
          {{- if $subtask_keycloak }}
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
          {{- if $subtasks }}
          - name: JOB_SUBTASKS
            value: {{ $subtasks }}
          {{- end }}
          {{- if $maintenance }}
          - name: MAINTENANCE_NAMESPACE
            value: {{ $root.Values.maintenance.namespace }}
          - name: MAINTENANCE_INGRESS_NAME
            value: {{ $root.Values.maintenance.ingress.name }}
          - name: MAINTENANCE_INGRESS_CLASS_NAME
            value: {{ $root.Values.maintenance.ingress.ingressClassName }}
          - name: MAINTENANCE_CONFIG_MAP_NAME
            value: {{ $root.Values.maintenance.configMap.name }}
          - name: MAINTENANCE_CONFIG_MAP_KEY
            value: {{ $root.Values.maintenance.configMap.key}}
          - name: MAINTENANCE_CONFIG_MAP_VALUE
            {{- if (ne $type_job "manualRestore") }}
            value: {{ $root.Values.maintenance.configMap.valueBackup | quote }}
            {{- else }}
            value: {{ $root.Values.maintenance.configMap.valueRestore | quote }}
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
          - name: EXTERNAL_ACCOUNT_AUDIENCE
            valueFrom:
              configMapKeyRef:
                name: {{ include "data-manager.config.name" $root }}
                key: external_account_audience
          - name: EXTERNAL_ACCOUNT_IMPERSONATION_URL
            valueFrom:
              configMapKeyRef:
                name: {{ include "data-manager.config.name" $root }}
                key: external_account_impersonation_url
           {{- end }}
        volumeMounts:
          - mountPath: /var/opt/data-manager
            name: work

      {{- if $subtask_s3 }}
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

      {{- if $subtask_keycloak }}
      - name: keycloak
        image: {{ printf "%s:%s" ($root.Values.keycloakImage.name | default "quay.io/keycloak/keycloak") $root.Values.keycloakImage.tag }}
        env:
          - name: PATH_WORK_DIR
            value: "/data/kc"
          {{- if $root.Values.keycloakImage.name }}
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
                name: keycloak-pguser-keycloak
          - name: KC_DB_URL_PORT
            valueFrom:
              secretKeyRef:
                key: port
                name: keycloak-pguser-keycloak
          - name: KC_DB_URL_DATABASE
            valueFrom:
              secretKeyRef:
                key: dbname
                name: keycloak-pguser-keycloak
          - name: KC_DB_USERNAME
            valueFrom:
              secretKeyRef:
                key: user
                name: keycloak-pguser-keycloak
          - name: KC_DB_PASSWORD
            valueFrom:
              secretKeyRef:
                key: password
                name: keycloak-pguser-keycloak
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
          {{- if (eq $type_job "manualRestore") }}
          {{- if (list "rotate" "reset" | has $keycloakRealmKeysRotation )}}
          - name: KEYS_ROTATION
            value: {{ $keycloakRealmKeysRotation }}
          {{- end }}
          - name: ADMIN_CLI_CLIENT_SECRET
            valueFrom:
              secretKeyRef:
                key: keycloak_admin_client_secret
                name: keycloak-admin-secret
                optional: false
          - name: INTEGRATION_TESTS_CLIENT_SECRET
            valueFrom:
              secretKeyRef:
                key: integration_tests_client_secret
                name: data-manager-secret
                optional: false
          - name: YOUWOL_PLATFORM_CLIENT_SECRET
            valueFrom:
              secretKeyRef:
                key: openid_client_secret
                name: openid-app-secret
                optional: false
          - name: WEBPM_CLIENT_SECRET
            valueFrom:
              secretKeyRef:
                key: client_secret
                name: webpm
                optional: false
          - name: YOUWOL_PLATFORM_CLIENT_REDIRECT_URIS
            value: {{ printf "\"https://%s/*\"" (include "data-manager.hosts.clusterDomain" $root) | quote }}
          {{- end }}
        command: ["/bin/bash"]
        args: ["/data/kc/kc_script.sh"]
        volumeMounts:
          - mountPath: /data
            name: work
        {{- end }}

{{- end }}
