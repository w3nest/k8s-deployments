{{- define "w3nest.notes" -}}
{{- $name := .Release.Name}}
{{- $ins := .Release.IsInstall}}
{{- $up := .Release.IsUpgrade}}
{{- $rev := .Release.Revision}}
{{- $v := .Values.global.appVersion}}
{{- $ns := .Release.Namespace}}
{{- $fullname := include "w3nest.fullname" .}}
{{- $fqdn := printf "%s.%s.svc.cluster.local" $fullname $ns}}
🚀 {{ .Chart.Name }}-{{ .Chart.Version }} ({{ include "w3nest.notes.selfNameVersion" . }})

    🛠️  Use configMaps and secrets for {{ join ", " .Values.env}}.
    📡  Service FQDN is '{{ $fqdn }}'.
    🔗  To port forward to this service:  'kubectl --namespace {{ $ns }} port-forward svc/{{ $fullname }} 8080:80'.
    {{if default .Values.ingressEnabled false -}}
    {{- $fullName := include "w3nest.fullname" . -}}
    {{- $path := .Values.ingressPath | default (printf "/api/%s" $fullName) -}}
    {{- $platformDomain := include "w3nest.lookup.clusterDomain" . -}}
    {{- $uri := printf "https://%s%s" $platformDomain $path -}}
    🌍  Public-facing endpoint: '{{ $uri }}'.
    {{- end}}
    {{- end }}

{{- define "w3nest.notes.selfNameVersion"}}
{{- range .Chart.Dependencies }}
{{- with fromJson (toJson .) }}
{{- if eq .name "w3nest"}}
{{- printf "%s-%s" .name .version }}
{{- end }}
{{- end }}
{{- end}}
{{- end}}
