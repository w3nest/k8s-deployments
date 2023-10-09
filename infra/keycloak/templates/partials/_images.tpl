{{- define "keycloak.image" -}}
{{ $defaultName := "quay.io/keycloak/keycloak" }}
{{- if .Values.keycloakImage }}
{{- $name := .Values.keycloakImage.name | default $defaultName }}
{{- if eq (.Values.keycloakImage.appVersionAsTag) false }}
{{- $name }}
{{- else -}}
{{- printf "%s:%s" $name .Chart.AppVersion }}
{{- end -}}
{{- else -}}
{{- printf "%s:%s" $defaultName .Chart.AppVersion }}
{{- end -}}
{{- end -}}
