{{/*
Expand the name of the chart.
*/}}
{{- define "resume-evaluation-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "resume-evaluation-service.fullname" -}}
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
{{- define "resume-evaluation-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "resume-evaluation-service.labels" -}}
helm.sh/chart: {{ include "resume-evaluation-service.chart" . }}
{{ include "resume-evaluation-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "resume-evaluation-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "resume-evaluation-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: resume-worker
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "resume-evaluation-service.serviceAccountName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-workers-sa" .Release.Name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the secret to use
*/}}
{{- define "resume-evaluation-service.secretName" -}}
{{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
{{- printf "%s-workers-secrets" .Release.Name }}
{{- else }}
{{- .Values.secret.name | default .Values.global.secretName | default (printf "%s-secrets" .Release.Name) }}
{{- end }}
{{- end }}

{{/*
Create the name of the config map to use
*/}}
{{- define "resume-evaluation-service.configMapName" -}}
{{- .Values.configMap.name | default .Values.global.configMapName | default (printf "%s-config" .Release.Name) }}
{{- end }}

{{/*
Create the deployment name (short name for worker)
*/}}
{{- define "resume-evaluation-service.deploymentName" -}}
{{- printf "%s-resume-worker" .Release.Name }}
{{- end }}

