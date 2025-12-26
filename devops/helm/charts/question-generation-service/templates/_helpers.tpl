{{/*
Expand the name of the chart.
*/}}
{{- define "question-generation-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "question-generation-service.fullname" -}}
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
{{- define "question-generation-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "question-generation-service.labels" -}}
helm.sh/chart: {{ include "question-generation-service.chart" . }}
{{ include "question-generation-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "question-generation-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "question-generation-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: question-worker
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "question-generation-service.serviceAccountName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-workers-sa" .Release.Name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the secret to use
*/}}
{{- define "question-generation-service.secretName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-workers-secrets" .Release.Name }}
{{- else }}
{{- .Values.secret.name | default .Values.global.secretName | default (printf "%s-secrets" .Release.Name) }}
{{- end }}
{{- end }}

{{/*
Create the name of the config map to use
*/}}
{{- define "question-generation-service.configMapName" -}}
{{- .Values.configMap.name | default .Values.global.configMapName | default (printf "%s-config" .Release.Name) }}
{{- end }}

{{/*
Create the deployment name (short name for worker)
*/}}
{{- define "question-generation-service.deploymentName" -}}
{{- printf "%s-question-worker" .Release.Name }}
{{- end }}

{{/*
Validate required values
*/}}
{{- define "question-generation-service.validateValues" -}}
{{- if not .Values.image.repository }}
{{- fail "question-generation-service: image.repository is required" }}
{{- end }}
{{- if not .Values.image.tag }}
{{- fail "question-generation-service: image.tag is required" }}
{{- end }}
{{- if eq .Values.image.tag "latest" }}
{{- printf "\nWARNING: question-generation-service: Using 'latest' tag for image is not recommended for production\n" }}
{{- end }}
{{- if not .Values.replicaCount }}
{{- fail "question-generation-service: replicaCount is required" }}
{{- end }}
{{- if not .Values.resources }}
{{- fail "question-generation-service: resources are required" }}
{{- end }}
{{- if and .Values.autoscaling.enabled (not .Values.autoscaling.queueName) }}
{{- fail "question-generation-service: autoscaling.queueName is required when autoscaling is enabled" }}
{{- end }}
{{- end }}

