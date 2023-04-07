{{- define "cluster-data-manager.backup-job-spec" -}}
{{- $type_backup := required "cluster-data-manager.backup-job-spec template expects key '.typeBackup' in scope" .typeBackup -}}
{{- $root := required "cluster-data-manager.backup-job-spec template expects key '.typeBackup' in scope" .root -}}
apiVersion: batch/v1
kind: Job
metadata:
  name: backup-manual
spec:
  suspend: false
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

      restartPolicy: OnFailure
      imagePullSecrets:
      - name: gitlab-docker
      initContainers:
        - name: setup
          image: "registry.gitlab.com/youwol/platform/cluster-data-manager:{{ $root.Chart.AppVersion }}"
          args:
            - setup_backup
          env:
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
            - mountPath: /var/tmp/app
              name: work
      containers:
        - name: main
          image: "registry.gitlab.com/youwol/platform/cluster-data-manager:{{ $root.Chart.AppVersion }}"
          args:
            - backup
          env:
            - name: JOB_UUID
              valueFrom:
                 fieldRef:
                   fieldPath: metadata.labels['controller-uid']
            - name: TYPE_BACKUP
              value: {{ $type_backup }}
            - name: GOOGLE_DRIVE_ID
              valueFrom:
                secretKeyRef:
                  name: data-manager-secret
                  key: google_drive_id
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
            - name: SCYLLA_HOST
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
            - mountPath: /var/tmp/app
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
{{- end }}
