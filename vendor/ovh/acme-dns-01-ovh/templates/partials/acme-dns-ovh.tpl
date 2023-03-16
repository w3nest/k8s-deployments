{{- define "acme-dns-ovh.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{ include "acme-dns-ovh.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}


{{- define "acme-dns-ovh.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: issuer
{{- end }}


{{- define "acme-dns-ovh.ovhCredentialsSecret.name" -}}
{{- if kindIs "string" .Values.ovh.applicationSecret }}
{{- printf "%s-credentials" .Release.Name }}
{{- else }}
{{- required "ovh.applicationSecret.existingSecret must provide a name" .Values.ovh.applicationSecret.name }}
{{- end }}
{{- end }}

{{- define "acme-dns-ovh.ovhCredentialsSecret.key" -}}
{{- if kindIs "string" .Values.ovh.applicationSecret }}applicationSecret{{ else }}
{{- required "ovh.applicationSecret.existingSecret must provide a key" .Values.ovh.applicationSecret.key }}
{{- end }}
{{- end }}

{{- define "acme-dns-ovh.privateKeySecretRef" -}}
{{- if .Values.acme.accountShared }}{{ .Values.acme.accountEmail | replace "@" "_"}}
{{- else }}{{ .Release.Name }}
{{- end }}
{{- end }}
