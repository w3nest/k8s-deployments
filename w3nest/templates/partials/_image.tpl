{{- define "w3nest.image.spec" -}}
{{- $repository := .Values.global.repository | default "backends" }} # Use default local image name if not set
{{- $tag := .Values.imageTag | default .Values.global.appVersion }}
image: {{ printf "%s:%s" $repository $tag | quote -}}
{{- if .Values.global.imagePullPolicy }}
# Specified image policy
imagePullPolicy: {{ .Values.global.imagePullPolicy }} # Explicitly specified image policy
{{- else }}
{{- if hasSuffix "-wip" .Values.global.appVersion }}
imagePullPolicy: Always # Always pull image since AppVersion end with "-wip"
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "w3nest.image.notes" -}}
{{- $tag := .Values.imageTag | default .Values.global.appVersion }}
{{- $repository := .Values.global.repository | default "backends" }} # Use default local image name if not set
{{- $url := printf "%s:%s"  $repository $tag | quote }}
{{- $descExplicitPullPolicy := printf "using explicit pull policy '%s'" .Values.global.imagePullPolicy }}
{{- $descPullPolicyWip := "using pull policy 'Always' since AppVersion end with '-wip'" }}
{{- $descDefaultPolicy := (eq $tag "latest") | ternary "'Always' since tag is 'latest'" "'IfNotPresent'"}}
{{- $descUnspecifiedPolicy := printf "without specifying pull policy (will default to %s)" $descDefaultPolicy}}
    🖼️  Image will be pulled from {{ $url }},{{ if .Values.global.imagePullPolicy }} {{ $descExplicitPullPolicy }}.
{{- else -}}{{ if hasSuffix "-wip" .Values.global.appVersion }} {{$descPullPolicyWip}}.
{{- else }} {{$descUnspecifiedPolicy}}.{{- end -}}
{{- end -}}
{{- end -}}

{{- define "w3nest.image.args" -}}
{{- $args := .Values.containerArgs | default (list .Chart.Name) -}}
{{- range $args }}
- {{ . }}
{{- end }}
{{- end -}}
