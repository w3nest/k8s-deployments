{{- define "static-assets.fullname" }}
{{- $name := .Chart.Name }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}{{- end }}

{{- define "static-assets.service-default-route.name" }}
{{- $name :=  "default-route" }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "static-assets.service-maintenance.name" }}
{{- $name :=  "maintenance" }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "static-assets.service-static-assets.name" }}
{{- $name :=  "static-assets" }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "static-assets.includes-maintenance-configmap.name" }}
{{- printf "%s-%s" (include "static-assets.service-maintenance.name" .) "includes" }}
{{- end }}

{{- define "static-assets.assets-zip-configmap.name" }}
{{- printf "%s-%s" .Release.Name "assets-zip" | trunc 63 | trimSuffix "-" }}
{{- end }}