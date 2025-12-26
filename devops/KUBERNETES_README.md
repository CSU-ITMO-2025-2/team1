# Kubernetes-инфраструктура проекта HR Assistant

## Что это

Проект HR Assistant развернут в Kubernetes. Это система для автоматизации HR-процессов с использованием ИИ.

## Архитектура

У нас 7 микросервисов:

1. **Core API** - основной API (FastAPI, порт 8000)
2. **Frontend** - веб-интерфейс (Streamlit, порт 8501)
3. **Job Description Service** - генерация описаний вакансий
4. **Question Generation Service** - генерация вопросов для интервью
5. **Resume Evaluation Service** - оценка резюме
6. **PostgreSQL** - база данных
7. **RabbitMQ** - брокер сообщений для очередей

Все развернуто через Helm charts.

## Микросервисы

### Core API
- FastAPI сервис
- 3 реплики по умолчанию
- Ресурсы: CPU 200m-250m, Memory 512Mi

### Frontend
- Streamlit приложение
- 1 реплика (масштабируется через HPA)
- Ресурсы: CPU 100m, Memory 256Mi

### Worker-сервисы (Job Description, Question Generation, Resume Evaluation)
- Обрабатывают задачи из очередей RabbitMQ
- Масштабируются через KEDA в зависимости от длины очереди
- Ресурсы: CPU 10m-100m, Memory 150Mi-300Mi

### PostgreSQL
- Версия 16
- База данных: hr_assist

### RabbitMQ
- Версия 3.13-management-alpine
- Порты: 5672 (AMQP), 15672 (UI), 15692 (метрики)

## Развертывание через Helm

Все компоненты упакованы в Helm charts. Структура:

```
devops/helm/
├── Chart.yaml              # Главный chart
├── values.yaml             # Настройки
├── templates/              # Общие шаблоны
│   ├── hpa.yaml           # Автомасштабирование
│   ├── ingress.yaml       # Доступ извне
│   ├── secret.yaml        # Секреты
│   └── ...
└── charts/                 # Subcharts для каждого сервиса
    ├── core-api/
    ├── frontend/
    └── ...
```

### Как развернуть

```bash
# Обновить зависимости
helm dependency update devops/helm

# Развернуть
helm install hr-assist devops/helm \
  --namespace hr-assist \
  --create-namespace \
  --set secrets.vault.username=<username> \
  --set secrets.vault.password=<password>
```

## Безопасность

### Секреты через Vault

Используем HashiCorp Vault для хранения секретов. Интеграция через External Secrets Operator.

Секреты разделены по назначению:
- `team1/hr-assist/shared` - общие (OpenAI API Key)
- `team1/hr-assist/postgres` - для PostgreSQL
- `team1/hr-assist/rabbitmq` - для RabbitMQ
- `team1/hr-assist/auth` - для аутентификации

Каждый сервис получает только свои секреты (принцип наименьших привилегий).

### RBAC

Можно включить RBAC для изоляции доступа к секретам. При включении для каждого сервиса создается:
- ServiceAccount
- Role с правами только на свой Secret
- RoleBinding

Включение: `rbac.enabled: true` в values.yaml

### ConfigMap

Несекретные настройки (модели, порты, хосты) хранятся в ConfigMap.

## Автомасштабирование

Используем два типа автомасштабирования:

### HPA (для Core API и Frontend)

Масштабирование на основе использования памяти:

```yaml
minReplicas: 2
maxReplicas: 5
targetMemoryUtilization: 70%  # Масштабируем при 70% памяти
```

- Масштабирование вверх: быстрое, при превышении порога
- Масштабирование вниз: плавное, с задержкой 5 минут

### KEDA (для worker-сервисов)

Масштабирование на основе длины очереди RabbitMQ:

```yaml
minReplicaCount: 1
maxReplicaCount: 5
threshold: "10"  # 1 реплика на 10 сообщений в очереди
```

KEDA смотрит на метрики RabbitMQ (порт 15692) и автоматически создает/удаляет реплики в зависимости от количества задач в очереди.

## Health Checks (Probes)

Все сервисы имеют liveness и readiness probes:

- **Liveness** - проверяет, жив ли контейнер. Если нет - перезапускает.
- **Readiness** - проверяет, готов ли принимать трафик. Если нет - убирает из балансировки.

### Core API и Frontend
Используют HTTP проверки на `/health` или `/`.

### Worker-сервисы
Используют exec проверки (проверка процесса).

### RabbitMQ
Использует `rabbitmq-diagnostics ping` для проверки.

## RabbitMQ

RabbitMQ используется для асинхронной обработки задач:

```
Core API → RabbitMQ → Worker Services
```

### Очереди

- `job_description_queue` - для генерации описаний вакансий
- `question_generation_queue` - для генерации вопросов
- `resume_evaluation_queue` - для оценки резюме

### Метрики

RabbitMQ отдает метрики Prometheus на порту 15692. KEDA использует метрику `rabbitmq_queue_messages_ready` для определения длины очереди и масштабирования.

## Отказоустойчивость

### Высокая доступность

- Core API: 3 реплики
- Frontend: масштабируется через HPA
- Worker-сервисы: масштабируются через KEDA (1-5 реплик)

Kubernetes автоматически распределяет трафик между репликами.

### Автомасштабирование

- HPA реагирует на рост нагрузки по памяти
- KEDA реагирует на появление задач в очереди
- Автоматическое масштабирование вниз при снижении нагрузки

### Health Checks

Probes автоматически перезапускают неработающие контейнеры и исключают неготовые из балансировки.

### Лимиты ресурсов

Установлены CPU и Memory limits для предотвращения исчерпания ресурсов кластера.

## Сетевая безопасность

### Network Policies

Настроена политика для контроля исходящего трафика. Все запросы к OpenAI идут через прокси-сервер (Squid).

### Ingress

Настроен Ingress для доступа к сервисам:
- `/` → Frontend (порт 8501)
- `/api` → Core API (порт 8000)

## Как развернуть

### Требования

- Kubernetes 1.24+
- Helm 3.0+
- External Secrets Operator (для Vault)
- KEDA (для автомасштабирования worker-сервисов)
- Ingress Controller (например, NGINX)

### Настройка

Отредактируйте `devops/helm/values.yaml`:

```yaml
secrets:
  useExternal: true
  vault:
    server: "https://vault.kubepractice.ru"
    path: "team1/hr-assist"
    username: "<username>"
    password: "<password>"

autoscaling:
  coreApi:
    enabled: true
    minReplicas: 2
    maxReplicas: 5

ingress:
  enabled: true
  host: "hr-assist.example.com"
```

### Команды

```bash
# Создать namespace
kubectl create namespace hr-assist

# Развернуть
helm install hr-assist devops/helm \
  --namespace hr-assist \
  --set secrets.vault.username=<username> \
  --set secrets.vault.password=<password>

# Проверить
kubectl get pods -n hr-assist
kubectl get hpa -n hr-assist
kubectl get scaledobject -n hr-assist

# Обновить
helm upgrade hr-assist devops/helm --namespace hr-assist

# Удалить
helm uninstall hr-assist --namespace hr-assist
```

## Мониторинг

### Метрики

- RabbitMQ: Prometheus метрики на порту 15692 (используются KEDA)
- Kubernetes: CPU и Memory метрики (используются HPA)

Рекомендуется настроить Prometheus и Grafana для визуализации.

## Что реализовано

✅ **Микросервисы** - 7 сервисов  
✅ **Helm** - все развернуто через Helm charts  
✅ **Безопасность** - Vault, RBAC, Network Policies  
✅ **Автомасштабирование** - HPA и KEDA  
✅ **Probes** - health checks для всех сервисов  
✅ **RabbitMQ** - интеграция и масштабирование на основе очередей  
✅ **Отказоустойчивость** - множественные реплики, автомасштабирование, health checks  


## Итого

Проект развернут в Kubernetes с использованием современных практик:
- Модульная архитектура
- Безопасное управление секретами
- Автоматическое масштабирование
- Высокая отказоустойчивость
- Интеграция с RabbitMQ

Для полного соответствия всем требованиям можно дополнительно настроить CI/CD и Chaos Engineering тесты.
