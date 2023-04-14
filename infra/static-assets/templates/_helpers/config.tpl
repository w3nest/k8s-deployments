
{{- define  "static-assets.platform-host" }}
{{- $clusterConfig := (lookup "v1" "ConfigMap" "apps" "cluster-config") }}
{{- if $clusterConfig }}
{{- $clusterConfig.data.clusterDomain }}
{{- else}}
{{- required "configmap «cluster-config» not found and no platformHost defined" .Values.platformHost }}
{{- end }}
{{- end }}


{{- define  "static-assets.repo.branch" }}
{{- default .Chart.AppVersion .Values.repo.ref }}
{{- end }}


{{- define "static-assets.ingress-maintenance.ingressClass" -}}
{{- $maintenance := .Values.maintenance | default dict }}
{{- $disabledIngressClass := $maintenance.disableIngressClass | default "disabled" }}
{{- if ($maintenance.enable | default false) }}
{{- printf "kong"}}
{{- else }}
{{- printf $disabledIngressClass }}
{{- end }}
{{- end }}
