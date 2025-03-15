{{- define "lib-configuration.config-map"}}
{{- $name := required "lib-configuration.config-map template expects key '.name' in scope" .name}}
{{- $root := required "lib-configuration.config-map template expects key '.root' in scope" .root}}
{{- $values := required "lib-configuration.config-map template expects key '.values' in scope" .values}}
{{- $checksum := print .values | sha256sum}}
{{- $forceUpdateArgs := dict "root" $root "name" $name "kind" "ConfigMap" }}
apiVersion: v1
kind: ConfigMap

metadata:
  name: {{ $name }}
  namespace: {{ $root.Release.Namespace }}
  annotations:
    w3nest/checksum: {{ $checksum}}
    {{- include "lib-configuration.force-update" $forceUpdateArgs | indent 4}}

data:
  {{- $values | nindent 2}}

{{- end}}

{{- define  "lib-configuration.duplicate-config-map" }}
{{- $root := required "lib-configuration.duplicate-config-map template expects key '.root' in scope" .root}}
{{- $name := required "lib-configuration.duplicate-config-map template expects key '.name' in scope" .name}}
{{- $namespace := required "lib-configuration.duplicate-config-map template expects key '.namespace' in scope" .namespace}}
{{- $original := lookup "v1" "ConfigMap" $namespace $name }}
apiVersion: v1
kind: ConfigMap

metadata:
  name: {{ $name }}
  namespace: {{ $root.Release.Namespace }}
  annotations:
    youwol.com/duplicate-of: configmap/{{ $namespace }}.{{ $name }}
    {{- if hasKey $original.metadata.annotations "w3nest/checksum" }}
    w3nest/checksum: {{ get $original.metadata.annotations "w3nest/checksum" }}
    {{- end}}
    {{- if hasKey $original.metadata.annotations "w3nest/force-update-marker" }}
    w3nest/force-update-marker: {{get $original.metadata.annotations "w3nest/force-update-marker"}}
    {{- end}}
data:
  {{- $original.data | toYaml | nindent 2}}

{{- end}}
