{{/* vim: set filetype=mustache: */}}
{{- define  "lib-configuration.force-update"}}
{{- $root := required "lib-configuration.force-update expects entry '.root' in scope dictonnary" .root}}
{{- $kind := required "lib-configuration.force-update expects entry '.kind' in scope dictonnary" .kind}}
{{- $name := required "lib-configuration.force-update expects entry '.name' in scope dictonnary" .name}}
{{- $ns := .namespace | default $root.Release.Namespace}}
{{- $marker := ""}}
{{- $debug := ""}}
{{- $currentMarker := ""}}
{{- $globalPolicy := get $root.Values "forceUpdatePolicy"}}
{{- $objectsPolicies := $root.Values.forceUpdatePolicies | default (dict)}}
{{- $policy :=  get $objectsPolicies $name | default $globalPolicy | default "install"}}
{{- $currentObject := lookup "v1" $kind $ns $name}}
{{- $currentMarker = get ($currentObject.metadata).annotations "w3nest/force-update-marker" }}
{{- if eq $policy "force"}}
{{- $marker = default uuidv4 }}
{{- $debug = "force new marker"}}
{{- else if eq $policy "install"}}
{{- if $currentMarker}}
{{- $marker =  $currentMarker }}
{{- $debug = "using current marker" }}
{{- else }}
{{- $marker = default uuidv4}}
{{- $debug = "install new marker" }}
{{- end}}
{{- else if eq $policy "keep"}}
{{- $marker = $currentMarker}}
{{- end}}
{{- if $marker }}
w3nest/force-update-marker: {{ $marker | quote }} # {{ $debug }}
{{- else}}
# No marker defined for force-update
{{- end}}
{{- end}}
