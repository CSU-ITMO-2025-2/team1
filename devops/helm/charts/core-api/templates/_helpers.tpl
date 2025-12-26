{{/*
Expand the name of the chart.
*/}}
{{- define "core-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "core-api.fullname" -}}
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

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "core-api.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "core-api.labels" -}}
helm.sh/chart: {{ include "core-api.chart" . }}
{{ include "core-api.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "core-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "core-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: core-api
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "core-api.serviceAccountName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-core-api-sa" .Release.Name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the secret to use
*/}}
{{- define "core-api.secretName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-core-api-secrets" .Release.Name }}
{{- else }}
{{- .Values.secret.name | default .Values.global.secretName | default (printf "%s-secrets" .Release.Name) }}
{{- end }}
{{- end }}

{{/*
Create the name of the config map to use
*/}}
{{- define "core-api.configMapName" -}}
{{- .Values.configMap.name | default .Values.global.configMapName | default (printf "%s-config" .Release.Name) }}
{{- end }}

{{/*
Validate required values
*/}}
{{- define "core-api.validateValues" -}}
{{- if not .Values.image.repository }}
{{- fail "core-api: image.repository is required" }}
{{- end }}
{{- if not .Values.image.tag }}
{{- fail "core-api: image.tag is required" }}
{{- end }}
{{- if eq .Values.image.tag "latest" }}
{{- printf "\nWARNING: core-api: Using 'latest' tag for image is not recommended for production\n" }}
{{- end }}
{{- if not .Values.replicaCount }}
{{- fail "core-api: replicaCount is required" }}
{{- end }}
{{- if not .Values.resources }}
{{- fail "core-api: resources are required" }}
{{- end }}
{{- end }}

