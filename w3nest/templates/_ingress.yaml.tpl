{{- define "w3nest.ingress" -}}
{{- if default .Values.ingressEnabled false }}
{{- $fullName := include "w3nest.fullname" . -}}
{{- $path := .Values.ingressPath | default (printf "/api/%s" $fullName) -}}
{{- $platformDomain := include "w3nest.lookup.clusterDomain" . -}}
{{- $platformDomainOrigin := include "w3nest.lookup.clusterDomainOrigin" . -}}
apiVersion: networking.k8s.io/v1
kind: Ingress

metadata:
  name: {{ $fullName }}
  labels:
    {{- include "w3nest.labels" . | nindent 4 }}
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-youwol

spec:
  ingressClassName: nginx
  tls:
    - hosts:
      - {{ $platformDomain }} # taken from {{ $platformDomainOrigin }}
      secretName: platform-tls
  rules:
    - host: {{ $platformDomain }} # taken from {{ $platformDomainOrigin }}
      http:
        paths:
          - path: {{ $path }}
            pathType: Prefix
            backend:
              service:
                name: {{ $fullName }}
                port:
                  number: 80
{{- end}}
{{- end}}
