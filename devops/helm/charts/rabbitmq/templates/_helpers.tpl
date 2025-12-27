{{- define "rabbitmq.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "rabbitmq.fullname" -}}
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

{{- define "rabbitmq.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "rabbitmq.labels" -}}
helm.sh/chart: {{ include "rabbitmq.chart" . }}
{{ include "rabbitmq.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "rabbitmq.selectorLabels" -}}
app.kubernetes.io/name: {{ include "rabbitmq.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: rabbitmq
{{- end }}

{{- define "rabbitmq.serviceAccountName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-rabbitmq-sa" .Release.Name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "rabbitmq.secretName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-rabbitmq-secrets" .Release.Name }}
{{- else }}
{{- .Values.secret.name | default .Values.global.secretName | default (printf "%s-secrets" .Release.Name) }}
{{- end }}
{{- end }}

{{- define "rabbitmq.configMapName" -}}
{{- .Values.configMap.name | default .Values.global.configMapName | default (printf "%s-config" .Release.Name) }}
{{- end }}

{{- define "rabbitmq.validateValues" -}}
{{- if not .Values.image }}
{{- fail "rabbitmq: image is required" }}
{{- end }}
{{- if not .Values.port }}
{{- fail "rabbitmq: port is required" }}
{{- end }}
{{- if not .Values.uiPort }}
{{- fail "rabbitmq: uiPort is required" }}
{{- end }}
{{- if not .Values.replicaCount }}
{{- fail "rabbitmq: replicaCount is required" }}
{{- end }}
{{- if not .Values.resources }}
{{- fail "rabbitmq: resources are required" }}
{{- end }}
{{- end }}

