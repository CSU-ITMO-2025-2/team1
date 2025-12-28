{{- define "postgres.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "postgres.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "postgres.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "postgres.labels" -}}
helm.sh/chart: {{ include "postgres.chart" . }}
{{ include "postgres.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "postgres.selectorLabels" -}}
app.kubernetes.io/name: {{ include "postgres.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: postgres
{{- end }}

{{- define "postgres.serviceAccountName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-postgres-sa" .Release.Name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "postgres.secretName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-postgres-secrets" .Release.Name }}
{{- else }}
{{- .Values.secret.name | default .Values.global.secretName | default (printf "%s-secrets" .Release.Name) }}
{{- end }}
{{- end }}

{{- define "postgres.configMapName" -}}
{{- .Values.configMap.name | default .Values.global.configMapName | default (printf "%s-config" .Release.Name) }}
{{- end }}

{{- define "postgres.validateValues" -}}
{{- if not .Values.image }}
{{- fail "postgres: image is required" }}
{{- end }}
{{- if not .Values.username }}
{{- fail "postgres: username is required" }}
{{- end }}
{{- if not .Values.db }}
{{- fail "postgres: db (database name) is required" }}
{{- end }}
{{- if not .Values.port }}
{{- fail "postgres: port is required" }}
{{- end }}
{{- if not .Values.replicaCount }}
{{- fail "postgres: replicaCount is required" }}
{{- end }}
{{- if not .Values.resources }}
{{- fail "postgres: resources are required" }}
{{- end }}
{{- end }}

