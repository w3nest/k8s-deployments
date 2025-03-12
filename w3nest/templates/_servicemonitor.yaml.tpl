{{- define "w3nest.serviceMonitor" -}}
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ include "w3nest.fullname" . }}
spec:
  endpoints:
    - honorLabels: true
      path: /
      port: monitor
      scheme: http
  jobLabel: {{ include "w3nest.fullname" . }}
  namespaceSelector:
    matchNames:
      - {{ .Release.Namespace }}
  selector:
    matchLabels:
{{- include "w3nest.selectorLabels" . | nindent 6 }}
{{- end }}
