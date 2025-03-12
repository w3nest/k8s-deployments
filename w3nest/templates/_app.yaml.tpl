{{- define "w3nest.app" -}}
{{ include "w3nest.deployment" . }}
---
{{ include "w3nest.service" . }}
---
{{ include "w3nest.serviceAccount" . }}
---
{{ include "w3nest.ingress" .}}
---
{{ include "w3nest.serviceMonitor" . }}
{{- end }}
