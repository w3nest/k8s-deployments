{{/*{{- "platform.int.youwol.com" }}*/}}
{{- define  "data-manager.hosts.clusterDomain" }}
{{- (lookup "v1" "ConfigMap" "apps" "cluster-config").data.clusterDomain }}
{{- end }}

{{- define  "data-manager.hosts.cql" }}
{{- "scylla-db-client.infra.svc.cluster.local" }}
{{- end }}

{{/*{{- "minio.infra.svc.cluster.local" }}*/}}
{{- define "data-manager.hosts.s3"}}
{{- (lookup "v1" "ConfigMap" "apps" "env-config").data.minio_host }}
{{- end }}
