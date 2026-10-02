{{- define "fleetops.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "fleetops.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "fleetops.labels" -}}
app.kubernetes.io/name: {{ include "fleetops.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "fleetops.selectorLabels" -}}
app.kubernetes.io/name: {{ include "fleetops.name" . }}-{{ .component }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "fleetops.databaseUrl" -}}
{{- printf "postgresql://%s:%s@%s-db:5432/%s" (.Values.database.user | urlquery) (.Values.database.password | urlquery) (include "fleetops.fullname" .) (.Values.database.name | urlquery) -}}
{{- end -}}
