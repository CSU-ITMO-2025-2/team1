{{- define "frontend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "frontend.fullname" -}}
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

{{- define "frontend.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "frontend.labels" -}}
helm.sh/chart: {{ include "frontend.chart" . }}
{{ include "frontend.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "frontend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: frontend
{{- end }}

{{- define "frontend.serviceAccountName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-frontend-sa" .Release.Name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "frontend.secretName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-frontend-secrets" .Release.Name }}
{{- else }}
{{- .Values.secret.name | default .Values.global.secretName | default (printf "%s-secrets" .Release.Name) }}
{{- end }}
{{- end }}

{{- define "frontend.configMapName" -}}
{{- .Values.configMap.name | default .Values.global.configMapName | default (printf "%s-config" .Release.Name) }}
{{- end }}

{{- define "frontend.validateValues" -}}
{{- if not .Values.image.repository }}
{{- fail "frontend: image.repository is required" }}
{{- end }}
{{- if not .Values.image.tag }}
{{- fail "frontend: image.tag is required" }}
{{- end }}
{{- if eq .Values.image.tag "latest" }}
{{- printf "\nWARNING: frontend: Using 'latest' tag for image is not recommended for production\n" }}
{{- end }}
{{- if not .Values.replicaCount }}
{{- fail "frontend: replicaCount is required" }}
{{- end }}
{{- if not .Values.resources }}
{{- fail "frontend: resources are required" }}
{{- end }}
{{- end }}

