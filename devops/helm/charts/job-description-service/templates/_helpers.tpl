{{- define "job-description-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "job-description-service.fullname" -}}
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

{{- define "job-description-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "job-description-service.labels" -}}
helm.sh/chart: {{ include "job-description-service.chart" . }}
{{ include "job-description-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "job-description-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "job-description-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: job-descr-worker
{{- end }}

{{- define "job-description-service.serviceAccountName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-workers-sa" .Release.Name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "job-description-service.secretName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-workers-secrets" .Release.Name }}
{{- else }}
{{- .Values.secret.name | default .Values.global.secretName | default (printf "%s-secrets" .Release.Name) }}
{{- end }}
{{- end }}

{{- define "job-description-service.configMapName" -}}
{{- .Values.configMap.name | default .Values.global.configMapName | default (printf "%s-config" .Release.Name) }}
{{- end }}

{{- define "job-description-service.deploymentName" -}}
{{- printf "%s-job-descr-worker" .Release.Name }}
{{- end }}

{{- define "job-description-service.validateValues" -}}
{{- if not .Values.image.repository }}
{{- fail "job-description-service: image.repository is required" }}
{{- end }}
{{- if not .Values.image.tag }}
{{- fail "job-description-service: image.tag is required" }}
{{- end }}
{{- if eq .Values.image.tag "latest" }}
{{- printf "\nWARNING: job-description-service: Using 'latest' tag for image is not recommended for production\n" }}
{{- end }}
{{- if not .Values.replicaCount }}
{{- fail "job-description-service: replicaCount is required" }}
{{- end }}
{{- if not .Values.resources }}
{{- fail "job-description-service: resources are required" }}
{{- end }}
{{- if and .Values.autoscaling.enabled (not .Values.autoscaling.queueName) }}
{{- fail "job-description-service: autoscaling.queueName is required when autoscaling is enabled" }}
{{- end }}
{{- end }}

