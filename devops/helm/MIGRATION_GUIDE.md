# Гайд по миграции на subchart-ы для LLM сервисов

Этот гайд описывает процесс обновления уже развернутого Kubernetes кластера после разделения Helm конфигураций на subchart-ы.

## Предварительные требования

- Установленный `helm` (версия 3.x)
- Доступ к Kubernetes кластеру
- Текущий релиз должен быть развернут через Helm

## Шаг 1: Проверка текущего состояния

Сначала проверьте текущий релиз:

```bash
# Проверьте список релизов
helm list -n <namespace>

# Проверьте текущие deployment-ы
kubectl get deployments -n <namespace>

# Проверьте текущие значения
helm get values <release-name> -n <namespace>
```

## Шаг 2: Обновление зависимостей Helm

Перед обновлением релиза необходимо обновить зависимости:

```bash
# Перейдите в директорию с Helm чартом
cd devops/helm

# Обновите зависимости (это создаст Chart.lock и загрузит subchart-ы)
helm dependency update

# Проверьте, что зависимости обновлены корректно
helm dependency list
```

Вы должны увидеть три зависимости:
- `job-description-service`
- `question-generation-service`
- `resume-evaluation-service`

## Шаг 3: Проверка конфигурации

Проверьте, что ваши значения в `values.yaml` корректны:

```bash
# Просмотрите текущие значения релиза
helm get values <release-name> -n <namespace> > current-values.yaml

# Сравните с новым values.yaml
# Убедитесь, что секции для subchart-ов настроены правильно
```

### Важные моменты:

1. **Имена секретов**: Убедитесь, что в секциях subchart-ов указаны правильные имена:
   
   **Если вы используете Vault через ExternalSecret** (рекомендуется):
   
   ```yaml
   secrets:
     useExternal: true  # Включить использование Vault
     useExisting: false
     vault:
       path: "team1/hr-assist"  # Путь к секретам в Vault
   
   # Для subchart-ов можно оставить name пустым - секрет создается автоматически
   job-description-service:
     secret:
       name: ""  # Будет использовано: <release-name>-secrets (создается ExternalSecret)
   ```
   
   ExternalSecret автоматически создаст секрет с именем `<release-name>-secrets` из Vault.
   Секреты в Vault должны иметь имена: `OPENAI_API_KEY`, `KC_CLIENT_SECRET`, `RABBITMQ_DEFAULT_PASS`, `POSTGRES_PASSWORD`
   
   **Если вы используете существующий секрет** (без Vault):
   
   ```yaml
   secrets:
     useExternal: false
     useExisting: true
     existingSecretName: "hr-assist-secrets"  # ваше имя секрета
   
   # Обновите секции subchart-ов:
   job-description-service:
     secret:
       name: "hr-assist-secrets"  # используйте то же имя, что и в secrets.existingSecretName
   ```
   
   Если оставить `name: ""` (пустое значение), будет использовано значение по умолчанию: `<release-name>-secrets`

2. **Имена ConfigMap**: Аналогично для ConfigMap:
   ```yaml
   job-description-service:
     configMap:
       name: ""  # Если пусто, будет использовано: <release-name>-config
   ```
   
   Обычно ConfigMap генерируется автоматически, поэтому можно оставить пустым.

### Пример полной настройки values.yaml для миграции с Vault:

```yaml
# ... остальные настройки ...

secrets:
  useExternal: true  # Использование Vault через ExternalSecret
  useExisting: false
  vault:
    path: "team1/hr-assist"  # Путь к секретам в Vault

# LLM сервисы
job-description-service:
  image:
    repository: erofeevdma/aith-team1-job-description-service
    tag: latest
    pullPolicy: Always
  replicaCount: 1
  configMap:
    name: ""  # Автоматически: <release-name>-config
  secret:
    name: ""  # Автоматически: <release-name>-secrets (создается ExternalSecret из Vault)

question-generation-service:
  image:
    repository: erofeevdma/aith-team1-question-generation-service
    tag: latest
    pullPolicy: Always
  replicaCount: 1
  configMap:
    name: ""
  secret:
    name: ""  # Автоматически: <release-name>-secrets

resume-evaluation-service:
  image:
    repository: erofeevdma/aith-team1-resume-evaluation-service
    tag: latest
    pullPolicy: Always
  replicaCount: 1
  configMap:
    name: ""
  secret:
    name: ""  # Автоматически: <release-name>-secrets
```

### Пример настройки values.yaml без Vault (существующий секрет):

```yaml
secrets:
  useExternal: false
  useExisting: true
  existingSecretName: "hr-assist-secrets"

# LLM сервисы
job-description-service:
  secret:
    name: "hr-assist-secrets"  # Используем существующий секрет
```

## Шаг 4: Dry-run проверка

Перед реальным обновлением выполните dry-run для проверки:

```bash
# Выполните dry-run с текущими значениями
helm upgrade <release-name> . \
  --namespace <namespace> \
  --dry-run \
  --debug

# Или с файлом значений
helm upgrade <release-name> . \
  --namespace <namespace> \
  --values values.yaml \
  --dry-run \
  --debug
```

Проверьте вывод на наличие ошибок. Убедитесь, что:
- Все deployment-ы LLM сервисов будут созданы через subchart-ы
- Имена ресурсов корректны
- Нет конфликтов с существующими ресурсами

## Шаг 5: Обновление релиза

### Вариант A: Обновление без простоя (рекомендуется)

```bash
# Обновите релиз
helm upgrade <release-name> . \
  --namespace <namespace> \
  --wait \
  --timeout 10m

# Или с файлом значений
helm upgrade <release-name> . \
  --namespace <namespace> \
  --values values.yaml \
  --wait \
  --timeout 10m
```

### Вариант B: Обновление с проверкой истории

```bash
# Проверьте историю релиза
helm history <release-name> -n <namespace>

# Выполните обновление
helm upgrade <release-name> . \
  --namespace <namespace> \
  --wait \
  --timeout 10m

# Если что-то пошло не так, можно откатиться
helm rollback <release-name> <revision-number> -n <namespace>
```

## Шаг 6: Проверка после обновления

После обновления проверьте состояние:

```bash
# Проверьте статус релиза
helm status <release-name> -n <namespace>

# Проверьте deployment-ы
kubectl get deployments -n <namespace>

# Проверьте поды
kubectl get pods -n <namespace>

# Если используете Vault, проверьте ExternalSecret
kubectl get externalsecret -n <namespace>
kubectl get secretstore -n <namespace>
kubectl describe externalsecret <release-name>-secrets -n <namespace>

# Проверьте, что секрет создан из Vault
kubectl get secret <release-name>-secrets -n <namespace>

# Проверьте логи подов LLM сервисов
kubectl logs -n <namespace> -l app=job-descr-worker --tail=50
kubectl logs -n <namespace> -l app=question-worker --tail=50
kubectl logs -n <namespace> -l app=resume-worker --tail=50
```

## Шаг 7: Очистка старых ресурсов (если необходимо)

Если старые deployment-ы не были автоматически удалены (что маловероятно), их можно удалить вручную:

```bash
# Проверьте, есть ли старые deployment-ы
kubectl get deployments -n <namespace> | grep -E "(job-descr-worker|question-worker|resume-worker)"

# Если они все еще существуют и не управляются Helm, удалите их
# ВНИМАНИЕ: Убедитесь, что новые deployment-ы работают корректно!
kubectl delete deployment <release-name>-job-descr-worker -n <namespace>
kubectl delete deployment <release-name>-question-worker -n <namespace>
kubectl delete deployment <release-name>-resume-worker -n <namespace>
```

## Возможные проблемы и решения

### Проблема 1: Ошибка "dependencies not updated"

**Решение:**
```bash
cd devops/helm
helm dependency update
```

### Проблема 2: Конфликт имен ресурсов

Если Helm пытается создать ресурсы с теми же именами, это нормально - он обновит существующие.

### Проблема 3: Поды не запускаются

**Проверьте:**
1. Имена ConfigMap и Secret:
   ```bash
   kubectl get configmap -n <namespace>
   kubectl get secret -n <namespace>
   ```

2. Если используете Vault, проверьте ExternalSecret:
   ```bash
   kubectl get externalsecret -n <namespace>
   kubectl describe externalsecret <release-name>-secrets -n <namespace>
   
   # Проверьте статус синхронизации
   kubectl get externalsecret <release-name>-secrets -n <namespace> -o yaml | grep -A 5 status
   ```

3. Обновите values.yaml, указав правильные имена:
   ```yaml
   # Для Vault:
   secrets:
     useExternal: true
     vault:
       path: "team1/hr-assist"
   
   # Для существующего секрета:
   job-description-service:
     configMap:
       name: "<release-name>-config"
     secret:
       name: "hr-assist-secrets"  # или ваше имя
   ```

### Проблема 3.1: ExternalSecret не синхронизирует секреты из Vault

**Проверьте:**
1. Убедитесь, что External Secrets Operator установлен:
   ```bash
   kubectl get pods -n external-secrets-system
   ```

2. Проверьте SecretStore:
   ```bash
   kubectl get secretstore -n <namespace>
   kubectl describe secretstore <release-name>-vault-store -n <namespace>
   ```

3. Проверьте логи External Secrets Operator:
   ```bash
   kubectl logs -n external-secrets-system -l app.kubernetes.io/name=external-secrets --tail=100
   ```

4. Убедитесь, что секреты существуют в Vault по пути `team1/hr-assist`:
   - `OPENAI_API_KEY`
   - `KC_CLIENT_SECRET`
   - `RABBITMQ_DEFAULT_PASS`
   - `POSTGRES_PASSWORD`

5. Проверьте учетные данные для доступа к Vault:
   ```bash
   kubectl get secret vault-credentials -n <namespace>
   ```

### Проблема 4: Subchart-ы не применяются

**Решение:**
1. Убедитесь, что зависимости обновлены:
   ```bash
   helm dependency update
   helm dependency list
   ```

2. Проверьте Chart.yaml на наличие зависимостей

3. Пересоздайте Chart.lock:
   ```bash
   rm Chart.lock
   helm dependency update
   ```

## Откат изменений

Если что-то пошло не так, можно откатиться:

```bash
# Посмотрите историю релиза
helm history <release-name> -n <namespace>

# Откатитесь на предыдущую версию
helm rollback <release-name> <previous-revision> -n <namespace>

# Или откатитесь на последнюю версию
helm rollback <release-name> -n <namespace>
```

## Проверка структуры после миграции

После успешной миграции структура должна быть следующей:

```bash
# Deployment-ы должны быть созданы через subchart-ы
kubectl get deployments -n <namespace>

# Должны быть видны:
# - <release-name>-core-api
# - <release-name>-frontend
# - <release-name>-job-descr-worker (из subchart)
# - <release-name>-question-worker (из subchart)
# - <release-name>-resume-worker (из subchart)
```

## Дополнительные команды для отладки

```bash
# Просмотр манифестов, которые будут применены
helm template <release-name> . -n <namespace>

# Просмотр значений subchart-ов
helm get values <release-name> -n <namespace> -a

# Проверка зависимостей
helm dependency list

# Просмотр информации о релизе
helm get manifest <release-name> -n <namespace>
```

## Пример полного процесса

```bash
# 1. Перейдите в директорию Helm чарта
cd devops/helm

# 2. Обновите зависимости
helm dependency update

# 3. Проверьте конфигурацию
cat values.yaml

# 4. Выполните dry-run
helm upgrade team1-hr-assist . \
  --namespace default \
  --dry-run \
  --debug

# 5. Выполните обновление
helm upgrade team1-hr-assist . \
  --namespace default \
  --wait \
  --timeout 10m

# 6. Проверьте результат
helm status team1-hr-assist -n default
kubectl get pods -n default
```

## Примечания

- При обновлении Helm автоматически обновит существующие deployment-ы
- Поды будут пересозданы с новыми конфигурациями
- ConfigMap и Secret останутся без изменений (если имена не изменились)
- Рекомендуется выполнять обновление в нерабочее время или с использованием стратегии blue-green

