{{- define "w3nest.service" -}}
apiVersion: v1
kind: Service

metadata:
  name: {{ include "w3nest.fullname" . }}
  labels:
    {{- include "w3nest.labels" . | nindent 4 }}

spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: http
      protocol: TCP
      name: http
    - port: 8001
      targetPort: 8001
      protocol: TCP
      name: monitor
  selector:
    {{- include "w3nest.selectorLabels" . | nindent 4 }}
{{- end}}
