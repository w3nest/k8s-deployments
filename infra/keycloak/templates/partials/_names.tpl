{{- define "keycloak.fullname" }}
{{- $name := .Chart.Name }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "keycloak.keycloak.name" }}
{{- printf "%s" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "keycloak.postgres.name" }}
{{- printf "%s" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "keycloak.ingress.name" }}
{{- $fullname := include "keycloak.fullname" . }}
{{- printf "%s" $fullname }}
{{- end }}

{{- define "keycloak-postgres-db-init-sql.name" }}
{{- $fullname := include "keycloak.fullname" . }}
{{- printf "%s-db-init-sql" $fullname }}
{{- end }}
