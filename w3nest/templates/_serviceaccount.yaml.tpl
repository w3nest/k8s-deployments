{{- define "w3nest.serviceAccount" -}}
apiVersion: v1
kind: ServiceAccount

metadata:
  name: {{ include "w3nest.fullname" . }}
  labels:
{{- include "w3nest.labels" . | nindent 4 }}

imagePullSecrets:
- name: gitlab-docker
{{- end}}
