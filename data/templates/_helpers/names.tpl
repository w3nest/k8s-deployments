{{- define "data-manager.fullname" }}
{{- $name := .Chart.Name }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}{{- end }}

{{- define "data-manager.maintenance-switcher.name" }}
{{- $name :=  "maintenance-switcher" }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}


{{- define "data-manager.cronjob-backup.name" }}
{{- $name :=  "backup" }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "data-manager.cronjob-backup.job.name" }}
{{- $name :=  "cronjob-backup" }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "data-manager.job-backup.name" }}
{{- $name :=  "backup" }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "data-manager.job-restore.name" }}
{{- $name :=  "restore" }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "data-manager.secret.name" }}
{{- $name :=  "secret" }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "data-manager.config.name" }}
{{- $name :=  "config" }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
