{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "cert-manager-webhook-ovh.fullname" -}}
{{- printf "%s-%s" .Release.Name "webhook-ovh" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "cert-manager-webhook-ovh.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{ include "cert-manager-webhook-ovh.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}


{{- define "cert-manager-webhook-ovh.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: cert-manager-webhook-ovh
{{- end }}

{{- define "cert-manager-webhook-ovh.selfSignedIssuer" -}}
{{ printf "%s-selfsign" (include "cert-manager-webhook-ovh.fullname" .) }}
{{- end -}}

{{- define "cert-manager-webhook-ovh.rootCAIssuer" -}}
{{ printf "%s-ca" (include "cert-manager-webhook-ovh.fullname" .) }}
{{- end -}}

{{- define "cert-manager-webhook-ovh.rootCACertificate" -}}
{{ printf "%s-ca" (include "cert-manager-webhook-ovh.fullname" .) }}
{{- end -}}

{{- define "cert-manager-webhook-ovh.servingCertificate" -}}
{{ printf "%s-tls" (include "cert-manager-webhook-ovh.fullname" .) }}
{{- end -}}

{{- define "cert-manager-webhook-ovh.groupName" }}{{ .Release.Name }}{{- end }}

{{- define "cert-manager-webhook-ovh.image" }}
{{- printf "baarde/cert-manager-webhook-ovh:%s" .Chart.AppVersion }}
{{- end }}
