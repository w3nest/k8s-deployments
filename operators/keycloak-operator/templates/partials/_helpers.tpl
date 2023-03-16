{{- define "keycloakOperator.name" }}
{{- "keycloak-operator" }}
{{- end }}

{{- define "keycloakOperator.labels" }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- include "keycloakOperator.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}


{{- define "keycloakOperator.selectorLabels" }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "keycloakOperator.keycloakImage" }}
{{- printf "quay.io/keycloak/keycloak:%s" .Chart.AppVersion | quote }}
{{- end }}

{{- define  "keycloakOperator.operatorImage" }}
{{- printf "quay.io/keycloak/keycloak-operator:%s" .Chart.AppVersion | quote }}
{{- end }}
