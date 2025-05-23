{{- define "w3nest.env-v1.spec" -}}
{{ if default .Values.env false -}}
{{- include "w3nest.env-v1.forwardedAllowIps" . -}}
{{- include "w3nest.env-v1.w3nestOrigin" . -}}
{{- include "w3nest.env-v1.openidBaseUrl" . -}}
{{- include "w3nest.env-v1.openidClient" . -}}
{{- include "w3nest.env-v1.keycloakAdmin" . -}}
{{- include "w3nest.env-v1.redis" . -}}
{{- include "w3nest.env-v1.minio" . -}}
{{- end -}}
{{- end -}}

{{- define "w3nest.env-v1.forwardedAllowIps" -}}
{{ if has "forwardedAllowIps" .Values.env  -}}
# Environment variables for openidBaseUrl
- name: FORWARDED_ALLOW_IPS
  value: "*"
{{ end -}}
{{- end -}}

{{- define "w3nest.env-v1.w3nestOrigin" -}}
{{ if has "w3nestOrigin" .Values.env  -}}
# Environment variables for W3NEST origin
- name: W3NEST_ORIGIN
  valueFrom:
    configMapKeyRef:
      name: cluster-config
      key: clusterOrigin
{{ end -}}
{{- end -}}

{{- define "w3nest.env-v1.openidBaseUrl" -}}
{{ if has "openidBaseUrl" .Values.env  -}}
# Environment variables for openidBaseUrl
- name: OPENID_BASE_URL
  valueFrom:
    configMapKeyRef:
      name: env-config
      key: openid_base_url
{{ end -}}
{{- end -}}

{{- define "w3nest.env-v1.openidClient" -}}
{{ if has "openidClient" .Values.env -}}
# Environment variables for openidClient
{{ if not (has "openidBaseUrl" .Values.env) -}}
- name: OPENID_BASE_URL
  valueFrom:
    configMapKeyRef:
      name: env-config
      key: openid_base_url
{{ end -}}
- name: OPENID_CLIENT_ID
  valueFrom:
    configMapKeyRef:
      name: env-config
      key: openid_client_id
- name: OPENID_CLIENT_SECRET
  valueFrom:
    secretKeyRef:
      name: openid-app-secret
      key: openid_client_secret
{{ end -}}
{{- end -}}

{{- define "w3nest.env-v1.redis" -}}
{{ if has "redis" .Values.env -}}
# Environment variables for redis
- name: REDIS_HOST
  valueFrom:
    configMapKeyRef:
      name: env-config
      key: redis_host
- name: REDIS_USERNAME
  valueFrom:
    configMapKeyRef:
      name: env-config
      key: redis_username
- name: REDIS_PASSWORD
  valueFrom:
    secretKeyRef:
      name: redis-app-secret
      key: redis_password
{{ end -}}
{{- end -}}

{{- define "w3nest.env-v1.minio" -}}
{{ if has "minio" .Values.env -}}
# Environment variables for minio
- name: MINIO_HOST
  valueFrom:
    configMapKeyRef:
      name: env-config
      key: minio_host
- name: MINIO_ACCESS_KEY
  valueFrom:
    configMapKeyRef:
      name: env-config
      key: minio_access_key
- name: MINIO_ACCESS_SECRET
  valueFrom:
    secretKeyRef:
      name: minio-app-secret
      key: app-secret-key
{{ end -}}
{{- end -}}

{{- define "w3nest.env-v1.keycloakAdmin" -}}
{{ if has "keycloakAdmin" .Values.env -}}
# Environment variables for keycloakAdmin
- name: KEYCLOAK_ADMIN_CLIENT_ID
  valueFrom:
    configMapKeyRef:
      name: env-config
      key: keycloak_admin_client_id
- name: KEYCLOAK_ADMIN_CLIENT_SECRET
  valueFrom:
    secretKeyRef:
      name: keycloak-admin-secret
      key: keycloak_admin_client_secret
- name: KEYCLOAK_ADMIN_BASE_URL
  valueFrom:
    configMapKeyRef:
      name: env-config
      key: keycloak_admin_base_url
{{ end -}}
{{- end -}}
