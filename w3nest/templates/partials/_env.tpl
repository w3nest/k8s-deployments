{{- define "w3nest.env.spec" -}}
{{- $version := include "w3nest.lookup.clusterVersion" . }}
{{- if eq $version "v1"}}
{{- include "w3nest.env-v1.spec" . }}
{{- else if eq $version "deprecated"}}
{{- include "w3nest.env-deprecated.spec" . }}
{{- else }}
{{ fail (printf "Unknown clusterVersion '%s'" $version )  }}
{{- end}}
{{- end }}
