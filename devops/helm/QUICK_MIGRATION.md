# Быстрая миграция на subchart-ы

## Минимальные шаги для обновления

```bash
# 1. Обновите зависимости
cd devops/helm
helm dependency update

# 2. Проверьте конфигурацию (замените <release-name> и <namespace> на ваши значения)
helm upgrade <release-name> . \
  --namespace <namespace> \
  --dry-run \
  --debug

# 3. Выполните обновление
helm upgrade <release-name> . \
  --namespace <namespace> \
  --wait \
  --timeout 10m

# 4. Проверьте результат
kubectl get pods -n <namespace>
helm status <release-name> -n <namespace>

# Если используете Vault, проверьте ExternalSecret
kubectl get externalsecret -n <namespace>
kubectl get secret <release-name>-secrets -n <namespace>
```

## Если что-то пошло не так

```bash
# Откат на предыдущую версию
helm rollback <release-name> -n <namespace>

# Просмотр истории
helm history <release-name> -n <namespace>
```

## Важно перед обновлением

### 1. Настройте values.yaml для работы с Vault

Если вы используете Vault (рекомендуется), настройте:

```yaml
secrets:
  useExternal: true  # Включить использование Vault
  useExisting: false
  vault:
    path: "team1/hr-assist"  # Путь к секретам в Vault

# Для subchart-ов можно оставить name пустым - секрет создается автоматически
job-description-service:
  secret:
    name: ""  # Будет использовано: <release-name>-secrets

question-generation-service:
  secret:
    name: ""

resume-evaluation-service:
  secret:
    name: ""
```

**Секреты в Vault должны иметь имена:**
- `OPENAI_API_KEY`
- `KC_CLIENT_SECRET`
- `RABBITMQ_DEFAULT_PASS`
- `POSTGRES_PASSWORD`

### 2. Если используете существующий секрет (без Vault)

```yaml
secrets:
  useExternal: false
  useExisting: true
  existingSecretName: "hr-assist-secrets"

# Обновите для всех трех subchart-ов:
job-description-service:
  secret:
    name: "hr-assist-secrets"
```

**Примечание:** Если оставить `name: ""` (пустое значение), будет использовано значение по умолчанию: `<release-name>-secrets`

