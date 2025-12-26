# Отчет о выполнении заданий по Kubernetes
---

## 1. ✅ Микросервисы

Реализовано 7 микросервисов (превышает минимальное требование в 3):

1. **Core API** - основной API-сервис на FastAPI (порт 8000, 3 реплики)
2. **Frontend** - веб-интерфейс на Streamlit (порт 8501)
3. **Job Description Service** - генерация описаний вакансий
4. **Question Generation Service** - генерация вопросов для интервью
5. **Resume Evaluation Service** - оценка резюме
6. **PostgreSQL** - база данных (версия 16)
7. **RabbitMQ** - брокер сообщений (версия 3.13-management-alpine)

Все сервисы описаны в `devops/helm/Chart.yaml` как зависимости главного chart. Каждый сервис имеет свой subchart в `devops/helm/charts/`.

---

## 2. ✅ Развертывание через Helm (Выполнил: Поляков Егор)

Все компоненты развернуты через Helm charts с иерархической структурой. Реализована модульная архитектура с главным chart и отдельными subcharts для каждого сервиса.

### Структура Helm charts:

**Главный chart** (`devops/helm/`):
- `Chart.yaml` - описание главного chart с зависимостями от 7 subcharts (core-api, frontend, job-description-service, question-generation-service, resume-evaluation-service, postgres, rabbitmq)
- `values.yaml` - глобальные настройки для всех сервисов (образы, реплики, ресурсы, секреты, автомасштабирование)
- `templates/` - общие шаблоны:
  - `configmap.yaml` - ConfigMap с несекретными настройками (порты, хосты, модели LLM)
  - `secret.yaml` - создание Secrets (если не используется Vault)
  - `hpa.yaml` - HorizontalPodAutoscaler для Core API и Frontend
  - `ingress.yaml` - Ingress для доступа извне
  - `networkpolicy-egress.yaml` - Network Policy для контроля исходящего трафика
  - `vault-externalsecret.yaml` - External Secrets для интеграции с HashiCorp Vault
  - `vault-secure.yaml` - альтернативная конфигурация Vault
  - `_helpers.tpl` - общие helper-функции

**Subcharts** (`devops/helm/charts/`):
Каждый сервис (core-api, frontend, job-description-service, question-generation-service, resume-evaluation-service, postgres, rabbitmq) имеет:
- `Chart.yaml` - описание subchart
- `values.yaml` - настройки конкретного сервиса (образ, реплики, ресурсы, probes, RBAC)
- `templates/` - шаблоны Kubernetes ресурсов:
  - `deployment.yaml` - Deployment для сервиса
  - `service.yaml` - Service для доступа к сервису
  - `rbac.yaml` - Role и RoleBinding (для сервисов с RBAC)
  - `serviceaccount.yaml` - ServiceAccount (для сервисов с RBAC)
  - `scaledobject.yaml` - KEDA ScaledObject (для worker-сервисов)
  - `_helpers.tpl` - helper-функции для конкретного сервиса

### Helper-функции (_helpers.tpl):

**В главном chart** (`devops/helm/templates/_helpers.tpl`):
- `team1-hr-assist.name` - базовое имя chart (по умолчанию из Chart.Name)
- `team1-hr-assist.fullname` - полное имя с учетом Release.Name (например, `team1-team1-hr-assist`)
- `team1-hr-assist.chart` - имя и версия chart для меток (например, `team1-hr-assist-0.1.0`)
- `team1-hr-assist.labels` - общие метки для ресурсов (helm.sh/chart, app.kubernetes.io/name, app.kubernetes.io/instance, app.kubernetes.io/version, app.kubernetes.io/managed-by)
- `team1-hr-assist.selectorLabels` - метки для селекторов (app.kubernetes.io/name, app.kubernetes.io/instance)

**В каждом subchart** (например, `devops/helm/charts/core-api/templates/_helpers.tpl`):
- `{service}.name` - имя сервиса (например, `core-api`)
- `{service}.fullname` - полное имя с учетом Release.Name (например, `team1-core-api`)
- `{service}.chart` - имя и версия chart
- `{service}.labels` - метки для ресурсов сервиса
- `{service}.selectorLabels` - метки для селекторов сервиса (включая специфичный label `app: core-api`)
- `{service}.serviceAccountName` - имя ServiceAccount (с учетом RBAC: если RBAC включен - `{Release.Name}-{service}-sa`, иначе - default)
- `{service}.secretName` - имя Secret (с учетом RBAC и глобальных настроек: если RBAC включен - `{Release.Name}-{service}-secrets`, иначе - из global.secretName или `{Release.Name}-secrets`)
- `{service}.configMapName` - имя ConfigMap (из local configMap.name или global.configMapName или `{Release.Name}-config`)
- `{service}.validateValues` - валидация обязательных значений (проверяет наличие image.repository, image.tag, replicaCount, resources; предупреждает об использовании тега `latest`)

### Использование helper-функций:

Helper-функции используются во всех шаблонах для обеспечения консистентности имен и меток. Пример использования в `deployment.yaml`:

```yaml
{{- include "core-api.validateValues" . }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "core-api.fullname" . }}
  labels:
    {{- include "core-api.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "core-api.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "core-api.selectorLabels" . | nindent 8 }}
    spec:
      {{- if or .Values.rbac.enabled (and .Values.global.rbac .Values.global.rbac.enabled) }}
      serviceAccountName: {{ include "core-api.serviceAccountName" . }}
      {{- end }}
      containers:
        - envFrom:
            - configMapRef:
                name: {{ include "core-api.configMapName" . }}
            - secretRef:
                name: {{ include "core-api.secretName" . }}
```

### Особенности реализации:

1. **Иерархическая структура**: Главный chart управляет зависимостями через `Chart.yaml`, каждый сервис изолирован в своем subchart
2. **Переиспользование кода**: Helper-функции вынесены в `_helpers.tpl` для избежания дублирования и обеспечения консистентности
3. **Гибкая настройка**: Настройки можно задавать на уровне главного chart (глобально через `global.*`) или в каждом subchart (локально через `values.yaml`)
4. **Валидация**: Helper-функции `validateValues` проверяют обязательные параметры перед развертыванием и выводят предупреждения
5. **RBAC поддержка**: Helpers автоматически генерируют правильные имена ServiceAccount и Secret в зависимости от включения RBAC (через `rbac.enabled` или `global.rbac.enabled`)
6. **Глобальные настройки**: Поддержка глобальных ConfigMap и Secret через `global.configMapName` и `global.secretName` в главном values.yaml
7. **Условная логика**: Использование `{{- if }}` для условного создания ресурсов (например, ServiceAccount только при включенном RBAC)

### Развертывание:

```bash
# Обновить зависимости (скачать/обновить subcharts)
helm dependency update devops/helm

# Развернуть
helm install team1 devops/helm --namespace team1-ns

# Или с кастомными значениями
helm install team1 devops/helm \
  --namespace team1-ns \
  --set secrets.vault.username=<username> \
  --set secrets.vault.password=<password>
```

---

## 3. ✅ CI/CD и GitOps-деплой


---

## 4. ✅ Безопасность (Secrets, RBAC)

**Secrets через Vault:**

Настроена интеграция с HashiCorp Vault через External Secrets Operator. Секреты хранятся в Vault по путям:
- `team1/hr-assist/shared` - общие секреты (OpenAI API Key)
- `team1/hr-assist/postgres` - секреты PostgreSQL
- `team1/hr-assist/rabbitmq` - секреты RabbitMQ
- `team1/hr-assist/auth` - секреты аутентификации

Конфигурация находится в `devops/helm/templates/vault-externalsecret.yaml`. Каждый сервис получает только свои секреты (принцип наименьших привилегий).

Несекретные настройки хранятся в ConfigMap (`devops/helm/templates/configmap.yaml`).

**RBAC:**

Реализована поддержка RBAC для изоляции доступа к секретам. Для каждого сервиса (core-api, frontend, postgres, rabbitmq) создаются:
- ServiceAccount (`devops/helm/charts/*/templates/serviceaccount.yaml`)
- Role с правами только на чтение конкретного Secret (`devops/helm/charts/*/templates/rbac.yaml`)
- RoleBinding для привязки ServiceAccount к Role

Включение через `rbac.enabled: true` в values.yaml соответствующего сервиса.

---

## 5. ✅ Autoscaling

Реализовано два типа автомасштабирования:

**HPA (Horizontal Pod Autoscaler)** для Core API и Frontend:
- Файл: `devops/helm/templates/hpa.yaml`
- Масштабирование на основе использования памяти
- Настройки: minReplicas: 2, maxReplicas: 5, targetMemoryUtilization: 70%
- Быстрое масштабирование вверх при превышении порога, плавное масштабирование вниз с задержкой

**KEDA** для worker-сервисов (Job Description, Question Generation, Resume Evaluation):
- Файлы: `devops/helm/charts/*/templates/scaledobject.yaml`
- Масштабирование на основе длины очереди RabbitMQ
- Использует метрики Prometheus от RabbitMQ (порт 15692)
- Настройки: minReplicaCount: 1, maxReplicaCount: 5, threshold: 10 сообщений на реплику

---

## 6. ✅ Probes (Выполнил: Поляков Егор)

Все сервисы настроены с liveness и readiness probes:

- **Core API**: HTTP GET проверки на `/health` (порт 8000) - `devops/helm/charts/core-api/values.yaml`
- **Frontend**: HTTP GET проверки на `/` (порт 8501) - `devops/helm/charts/frontend/values.yaml`
- **Worker Services**: exec проверки процесса - `devops/helm/charts/*-service/values.yaml`
- **RabbitMQ**: `rabbitmq-diagnostics ping` - `devops/helm/charts/rabbitmq/values.yaml`

Probes настроены в values.yaml каждого сервиса и применяются через templates/deployment.yaml. Liveness probe перезапускает неработающие контейнеры, readiness probe исключает неготовые поды из балансировки.

---

## 7. ✅ Интеграция RabbitMQ

Интегрирован RabbitMQ как брокер сообщений для асинхронной обработки задач. RabbitMQ развернут через Helm chart в `devops/helm/charts/rabbitmq/`.

**Конфигурация:**
- Версия: 3.13-management-alpine
- Порты: 5672 (AMQP), 15672 (Management UI), 15692 (Prometheus metrics)

**Очереди:**
- `job_description_queue` - для Job Description Service
- `question_generation_queue` - для Question Generation Service
- `resume_evaluation_queue` - для Resume Evaluation Service

**Взаимодействие между сервисами:**
```
Core API → RabbitMQ → Worker Services
```

Core API отправляет задачи в очереди RabbitMQ, worker-сервисы обрабатывают их асинхронно. Метрики RabbitMQ используются KEDA для автомасштабирования worker-сервисов на основе длины очереди.

---

## 8. ✅ Отказоустойчивость (HPA, Circuit Breaker)

Реализована отказоустойчивость через несколько механизмов:

**HPA (Horizontal Pod Autoscaler):**
- Автоматическое масштабирование при росте нагрузки
- Настроено для Core API и Frontend (`devops/helm/templates/hpa.yaml`)
- Реагирует на использование памяти

**Множественные реплики:**
- Core API: 3 реплики по умолчанию
- Worker-сервисы: масштабируются через KEDA от 1 до 5 реплик в зависимости от нагрузки
- Kubernetes Service автоматически распределяет трафик между репликами

**Health Checks:**
- Liveness probes автоматически перезапускают неработающие контейнеры
- Readiness probes исключают неготовые поды из балансировки

**Resource Limits:**
- Установлены CPU и Memory limits для всех сервисов
- Предотвращение исчерпания ресурсов кластера

**Circuit Breaker:**
Не реализован на уровне инфраструктуры Kubernetes. Может быть реализован на уровне приложения через библиотеки (`circuitbreaker`, `tenacity` для Python).

---

## 9. ⚠️ Chaos Engineering

Не реализовано. Для полного выполнения требуется настроить Chaos Mesh или Litmus для тестирования отказоустойчивости (сбои подов, сетевые проблемы, задержки).

---

## Дополнительно реализовано

**Network Policies:**
- Файл: `devops/helm/templates/networkpolicy-egress.yaml`
- Контроль исходящего трафика
- Все запросы к OpenAI идут через прокси-сервер (Squid)

**Ingress:**
- Файл: `devops/helm/templates/ingress.yaml`
- Настроен доступ к сервисам извне
- Маршрутизация: `/` → Frontend (порт 8501), `/api` → Core API (порт 8000)

---
