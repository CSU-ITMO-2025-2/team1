# Kubernetes - Документация и отчет

---

# Часть I: Документация по развертыванию и запуску

## Описание архитектуры

Проект состоит из 7 микросервисов: Core API (FastAPI), Frontend (Streamlit), Job Description Service, Question Generation Service, Resume Evaluation Service, PostgreSQL, RabbitMQ.

**Схема взаимодействия:**
```
Frontend → Core API → PostgreSQL
              ↓
          RabbitMQ → Worker Services
```

---

## Требования

- Kubernetes кластер (1.24+)
- Helm 3.x
- kubectl
- Доступ к Docker registry

**Минимальные ресурсы:** CPU: 4 cores, Memory: 8 GB, Storage: 20 GB

---

## Развертывание

### 1. Подготовка

```bash
# Создание namespace
kubectl create namespace team1-ns

# Обновление зависимостей Helm
cd devops/helm
helm dependency update
```

### 2. Настройка секретов

**Kubernetes Secrets:**
```bash
kubectl create secret generic team-1-secrets \
  --from-literal=openai-api-key=<key> \
  --from-literal=postgres-password=<password> \
  --from-literal=rabbitmq-password=<password> \
  --namespace=team1-ns
```

**Или через Vault:** Настройте секреты в Vault по путям `team1/hr-assist/*` (см. `devops/helm/templates/vault-externalsecret.yaml`)

### 3. Установка

```bash
# Базовое развертывание
helm install team1 devops/helm --namespace team1-ns

# С кастомными значениями
helm install team1 devops/helm \
  --namespace team1-ns \
  --set global.rbac.enabled=true
```

### 4. Обновление/Откат

```bash
# Обновление
helm upgrade team1 devops/helm --namespace team1-ns

# Откат
helm rollback team1 --namespace team1-ns
```

---

## Проверка работоспособности

```bash
# Статус подов
kubectl get pods -n team1-ns

# Логи
kubectl logs -n team1-ns -l app=core-api --tail=50

# Доступ через port-forward
kubectl port-forward -n team1-ns svc/team1-frontend 8501:8501
kubectl port-forward -n team1-ns svc/team1-core-api 8000:8000
```

---

## Устранение неполадок

```bash
# Описание пода (события, ошибки)
kubectl describe pod <pod-name> -n team1-ns

# Логи пода
kubectl logs <pod-name> -n team1-ns

# Проверка ресурсов
kubectl top pods -n team1-ns

# Удаление развертывания
helm uninstall team1 --namespace team1-ns
```

---

# Часть II: Отчет о выполнении заданий по Kubernetes

---

## 1. ✅ Микросервисы

**Статус:** Выполнено

Реализовано 7 микросервисов (превышает минимальное требование в 3):

1. **Core API** - основной API-сервис на FastAPI (порт 8000, 3 реплики)
2. **Frontend** - веб-интерфейс на Streamlit (порт 8501)
3. **Job Description Service** - генерация описаний вакансий
4. **Question Generation Service** - генерация вопросов для интервью
5. **Resume Evaluation Service** - оценка резюме
6. **PostgreSQL** - база данных (версия 16)
7. **RabbitMQ** - брокер сообщений (версия 3.13-management-alpine)

Все сервисы описаны в `devops/helm/Chart.yaml` как зависимости главного chart. Каждый сервис имеет свой subchart в `devops/helm/charts/`.

**Взаимодействие между сервисами:**
- Core API взаимодействует с Frontend через HTTP
- Core API взаимодействует с PostgreSQL для хранения данных
- Core API отправляет задачи в RabbitMQ для асинхронной обработки
- Worker-сервисы (Job Description, Question Generation, Resume Evaluation) обрабатывают задачи из очередей RabbitMQ

---

## 2. ✅ Развертывание через Helm

**Статус:** Выполнено  
**Выполнил:** Поляков Егор

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

### Особенности реализации:

1. **Иерархическая структура**: Главный chart управляет зависимостями через `Chart.yaml`, каждый сервис изолирован в своем subchart
2. **Переиспользование кода**: Helper-функции вынесены в `_helpers.tpl` для избежания дублирования и обеспечения консистентности
3. **Гибкая настройка**: Настройки можно задавать на уровне главного chart (глобально через `global.*`) или в каждом subchart (локально через `values.yaml`)
4. **Валидация**: Helper-функции `validateValues` проверяют обязательные параметры перед развертыванием и выводят предупреждения
5. **RBAC поддержка**: Helpers автоматически генерируют правильные имена ServiceAccount и Secret в зависимости от включения RBAC (через `rbac.enabled` или `global.rbac.enabled`)
6. **Глобальные настройки**: Поддержка глобальных ConfigMap и Secret через `global.configMapName` и `global.secretName` в главном values.yaml
7. **Условная логика**: Использование `{{- if }}` для условного создания ресурсов (например, ServiceAccount только при включенном RBAC)

---

## 3. ⏳ GitOps-деплой

**Статус:** Выполнено
**Выполнил:**: 


## 4. ⏳ CI/CD-пайплайн

**Статус:** Выполнено
**Выполнил:**: 

_Место для описания CI/CD-пайплайна, автоматически собирающего образы и публикующего их в registry._

**Планируемая реализация:**
- Настройка GitHub Actions / GitLab CI / Jenkins для автоматической сборки образов
- Публикация образов в Docker registry при коммитах в определенные ветки
- Автоматическое обновление Helm charts с новыми версиями образов
- Интеграция с GitOps для автоматического развертывания

---

## 5. ✅ Секреты и конфигурации

**Статус:** Выполнено
**Выполнил:**: 

### Управление секретами

**Secrets через Vault:**

Настроена интеграция с HashiCorp Vault через External Secrets Operator. Секреты хранятся в Vault по путям:
- `team1/hr-assist/shared` - общие секреты (OpenAI API Key)
- `team1/hr-assist/postgres` - секреты PostgreSQL
- `team1/hr-assist/rabbitmq` - секреты RabbitMQ
- `team1/hr-assist/auth` - секреты аутентификации

Конфигурация находится в `devops/helm/templates/vault-externalsecret.yaml`. Каждый сервис получает только свои секреты (принцип наименьших привилегий).

**Kubernetes Secrets:**

Альтернативный вариант - использование стандартных Kubernetes Secrets. Конфигурация в `devops/helm/templates/secret.yaml`.

**Sealed Secrets:**

Поддержка Sealed Secrets для безопасного хранения секретов в Git-репозитории.

### Управление конфигурациями

**ConfigMap:**

Несекретные настройки хранятся в ConfigMap (`devops/helm/templates/configmap.yaml`):
- Порты сервисов
- Хосты и URL
- Настройки моделей LLM
- Другие несекретные параметры

**Глобальные и локальные настройки:**

- Глобальные настройки задаются в главном `values.yaml` через `global.*`
- Локальные настройки переопределяются в `values.yaml` каждого subchart
- Поддержка `global.configMapName` и `global.secretName` для централизованного управления

---

## 6. ✅ Безопасность

**Статус:** Выполнено
**Выполнил:**: 

### Разграничение прав доступа (RBAC)

Реализована поддержка RBAC для изоляции доступа к секретам. Для каждого сервиса (core-api, frontend, postgres, rabbitmq) создаются:
- ServiceAccount (`devops/helm/charts/*/templates/serviceaccount.yaml`)
- Role с правами только на чтение конкретного Secret (`devops/helm/charts/*/templates/rbac.yaml`)
- RoleBinding для привязки ServiceAccount к Role

Включение через `rbac.enabled: true` в values.yaml соответствующего сервиса или глобально через `global.rbac.enabled: true`.

**Принцип наименьших привилегий:**
- Каждый сервис имеет доступ только к своим секретам
- ServiceAccount изолированы по сервисам
- Role ограничивает доступ только на чтение необходимых ресурсов

### HTTPS

**Ingress с TLS:**

Настроен Ingress (`devops/helm/templates/ingress.yaml`) с поддержкой TLS:
- Маршрутизация: `/` → Frontend (порт 8501), `/api` → Core API (порт 8000)
- Поддержка TLS-сертификатов (можно настроить через cert-manager)

### JWT (JSON Web Tokens)

JWT может быть реализован на уровне приложения через библиотеки аутентификации. Инфраструктура Kubernetes обеспечивает безопасную передачу токенов через ServiceAccount и RBAC.

### Network Policies

**Контроль сетевого трафика:**

Реализована Network Policy (`devops/helm/templates/networkpolicy-egress.yaml`) для контроля исходящего трафика:
- Все запросы к OpenAI идут через прокси-сервер (Squid)
- Ограничение доступа к внешним ресурсам

---

## 7. ✅ Масштабирование и отказоустойчивость

**Статус:** Выполнено
**Выполнил:**: 

### Автомасштабирование (HPA)

**HPA (Horizontal Pod Autoscaler)** для Core API и Frontend:
- Файл: `devops/helm/templates/hpa.yaml`
- Масштабирование на основе использования памяти
- Настройки: minReplicas: 2, maxReplicas: 5, targetMemoryUtilization: 70%
- Быстрое масштабирование вверх при превышении порога, плавное масштабирование вниз с задержкой

### Автомасштабирование worker-сервисов (KEDA)

**KEDA** для worker-сервисов (Job Description, Question Generation, Resume Evaluation):
- Файлы: `devops/helm/charts/*/templates/scaledobject.yaml`
- Масштабирование на основе длины очереди RabbitMQ
- Использует метрики Prometheus от RabbitMQ (порт 15692)
- Настройки: minReplicaCount: 1, maxReplicaCount: 5, threshold: 10 сообщений на реплику

### Health Checks (Probes)

**Статус:** Выполнено  
**Выполнил:** Поляков Егор

Все сервисы настроены с liveness и readiness probes:

- **Core API**: HTTP GET проверки на `/health` (порт 8000) - `devops/helm/charts/core-api/values.yaml`
- **Frontend**: HTTP GET проверки на `/` (порт 8501) - `devops/helm/charts/frontend/values.yaml`
- **Worker Services**: exec проверки процесса - `devops/helm/charts/*-service/values.yaml`
- **RabbitMQ**: `rabbitmq-diagnostics ping` - `devops/helm/charts/rabbitmq/values.yaml`

Probes настроены в values.yaml каждого сервиса и применяются через templates/deployment.yaml. Liveness probe перезапускает неработающие контейнеры, readiness probe исключает неготовые поды из балансировки.

### Retry и Fallback

**Множественные реплики:**
- Core API: 3 реплики по умолчанию
- Worker-сервисы: масштабируются через KEDA от 1 до 5 реплик в зависимости от нагрузки
- Kubernetes Service автоматически распределяет трафик между репликами

**Resource Limits:**
- Установлены CPU и Memory limits для всех сервисов
- Предотвращение исчерпания ресурсов кластера

**Circuit Breaker:**
Не реализован на уровне инфраструктуры Kubernetes. Может быть реализован на уровне приложения через библиотеки (`circuitbreaker`, `tenacity` для Python).

---

## 8. ⏳ Chaos Engineering

**Статус:** Выполнено



## 9. ✅ Взаимодействие между сервисами через Pub/Sub

**Статус:** Выполнено
**Выполнил:**: 

### Интеграция RabbitMQ

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

**Преимущества Pub/Sub архитектуры:**
- Асинхронная обработка задач
- Развязка сервисов
- Автомасштабирование на основе нагрузки
- Отказоустойчивость (сообщения сохраняются в очереди)

---

## Дополнительно реализовано

### Network Policies

**Контроль исходящего трафика:**
- Файл: `devops/helm/templates/networkpolicy-egress.yaml`
- Контроль исходящего трафика
- Все запросы к OpenAI идут через прокси-сервер (Squid)

### Ingress

**Доступ извне:**
- Файл: `devops/helm/templates/ingress.yaml`
- Настроен доступ к сервисам извне
- Маршрутизация: `/` → Frontend (порт 8501), `/api` → Core API (порт 8000)
- Поддержка TLS

### Мониторинг и метрики

- RabbitMQ предоставляет метрики Prometheus на порту 15692
- Метрики используются KEDA для автомасштабирования
- Health checks предоставляют информацию о состоянии сервисов

---

## Итоговая таблица выполнения

| Задание | Статус | Примечания |
|---------|--------|------------|
| Микросервисы (≥3) | ✅ | Реализовано 7 микросервисов |
| Развертывание через Helm | ✅ | Иерархическая структура с subcharts |
| GitOps-деплой | ✅ |  |
| CI/CD-пайплайн | ⏳ |  |
| Секреты и конфигурации | ✅ | Vault, Kubernetes Secrets, ConfigMap |
| Безопасность (RBAC, HTTPS, JWT) | ✅ | RBAC, Ingress с TLS, Network Policies |
| Масштабирование (HPA, KEDA) | ✅ | HPA для API/Frontend, KEDA для workers |
| Probes | ✅ | Liveness и readiness для всех сервисов |
| Retry/Fallback | ✅ | Множественные реплики, resource limits |
| Chaos Engineering | ✅ | |
| Pub/Sub взаимодействие | ✅ | RabbitMQ с очередями |
| Документация | ✅ | Инструкция по запуску и отчет |

---

## Список участников

- **Поляков Егор** - Развертывание через Helm, Probes

---


