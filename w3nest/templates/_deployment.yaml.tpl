{{- define "w3nest.deployment" -}}
{{ $probeSecret := randAlphaNum 16 | quote }}
apiVersion: apps/v1
kind: Deployment

metadata:
  name: {{ include "w3nest.fullname" . }}
  labels:
    {{- include "w3nest.labels" . | nindent 4 }}
  annotations:
    {{- include "w3nest.forceUpdate" . | nindent 4 }}
spec:
  replicas: {{ include "w3nest.deployment.replicas" . }}
  selector:
    matchLabels:
      {{- include "w3nest.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "w3nest.selectorLabels" . | nindent 8 }}
    spec:
      serviceAccountName: {{ include "w3nest.fullname" . }}
      {{- if .Values.tempVolume }}
      volumes:
        - name: temp
          emptyDir:
            medium: Memory
      {{- end }}
      containers:
        - name: {{ .Chart.Name }}
          {{- include "w3nest.image.spec" . | indent 10 }}
          args:
            {{- include "w3nest.image.args" . | indent 12 }}
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          securityContext:
            readOnlyRootFilesystem: true
            runAsNonRoot: true
            runAsUser: 10000
            runAsGroup: 10000
          readinessProbe:
            httpGet:
              port: 8080
              path: /observability/readiness
          livenessProbe:
            httpGet:
              port: 8080
              path: /observability/liveness
          startupProbe:
            httpGet:
              port: 8080
              path: /observability/startup
          env:
            {{- include "w3nest.env.spec" . | nindent 12 }}
          {{- include "w3nest.deployment.resources" . | indent 10 }}
          {{- if .Values.tempVolume }}
          volumeMounts:
            - mountPath: /tmp
              name: temp
          {{- end }}

{{- end -}}
