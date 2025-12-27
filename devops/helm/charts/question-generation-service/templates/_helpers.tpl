{{- define "question-generation-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

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

{{- define "question-generation-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "question-generation-service.labels" -}}
helm.sh/chart: {{ include "question-generation-service.chart" . }}
{{ include "question-generation-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "question-generation-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "question-generation-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: question-worker
{{- end }}

{{- define "question-generation-service.serviceAccountName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-workers-sa" .Release.Name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "question-generation-service.secretName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-workers-secrets" .Release.Name }}
{{- else }}
{{- .Values.secret.name | default .Values.global.secretName | default (printf "%s-secrets" .Release.Name) }}
{{- end }}
{{- end }}

{{- define "question-generation-service.configMapName" -}}
{{- .Values.configMap.name | default .Values.global.configMapName | default (printf "%s-config" .Release.Name) }}
{{- end }}

{{- define "question-generation-service.deploymentName" -}}
{{- printf "%s-question-worker" .Release.Name }}
{{- end }}

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

