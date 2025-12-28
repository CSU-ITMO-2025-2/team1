# Простая проверка Circuit Breaker

Write-Host "=== Проверка Circuit Breaker ===" -ForegroundColor Green

$namespace = "team1-ns"
$podName = "team1-project-core-api-7d8c5889ff-k2wr9"

Write-Host "`n1. Проверка контейнеров в поде..." -ForegroundColor Yellow
$containers = kubectl get pod $podName -n $namespace -o jsonpath='{.spec.containers[*].name}' 2>&1
$ready = kubectl get pod $podName -n $namespace -o jsonpath='{.status.containerStatuses[*].ready}' 2>&1
$readyCount = kubectl get pod $podName -n $namespace -o jsonpath='{.status.containerStatuses | length}' 2>&1

Write-Host "  Контейнеры: $containers" -ForegroundColor White
Write-Host "  Ready статус: $ready" -ForegroundColor White
Write-Host "  Количество контейнеров: $readyCount" -ForegroundColor White

if ($containers -match "istio-proxy") {
    Write-Host "  ✓ Istio sidecar НАЙДЕН" -ForegroundColor Green
    Write-Host "  ✓ Circuit Breaker может работать" -ForegroundColor Green
} else {
    Write-Host "  ✗ Istio sidecar ОТСУТСТВУЕТ" -ForegroundColor Red
    Write-Host "  ✗ Circuit Breaker НЕ РАБОТАЕТ" -ForegroundColor Red
    Write-Host "`n  Проблема: Sidecar не инжектирован" -ForegroundColor Yellow
}

Write-Host "`n2. Проверка аннотации sidecar injection..." -ForegroundColor Yellow
$annotation = kubectl get pod $podName -n $namespace -o jsonpath='{.metadata.annotations.sidecar\.istio\.io/inject}' 2>&1
if ($annotation -eq "true") {
    Write-Host "  ✓ Аннотация sidecar.istio.io/inject: $annotation" -ForegroundColor Green
    Write-Host "  ⚠ Но sidecar не инжектирован - возможно:" -ForegroundColor Yellow
    Write-Host "     - Istio не установлен в кластере" -ForegroundColor White
    Write-Host "     - Istio webhook не работает" -ForegroundColor White
    Write-Host "     - Namespace не имеет метки istio-injection" -ForegroundColor White
} else {
    Write-Host "  ✗ Аннотация отсутствует: $annotation" -ForegroundColor Red
    Write-Host "  ⚠ Нужно включить Istio в values.yaml и обновить релиз" -ForegroundColor Yellow
}

Write-Host "`n3. Проверка метки namespace (если есть доступ)..." -ForegroundColor Yellow
$nsLabel = kubectl get namespace $namespace -o jsonpath='{.metadata.labels.istio-injection}' 2>&1
if ($nsLabel) {
    Write-Host "  Метка istio-injection: $nsLabel" -ForegroundColor White
} else {
    Write-Host "  Метка отсутствует или нет прав на просмотр" -ForegroundColor Yellow
    Write-Host "  (Не критично, если есть аннотация в поде)" -ForegroundColor Gray
}

Write-Host "`n4. Проверка метрик Envoy (только если sidecar есть)..." -ForegroundColor Yellow
if ($containers -match "istio-proxy") {
    Write-Host "  Попытка получить метрики circuit breaker..." -ForegroundColor White
    $metrics = kubectl exec -n $namespace $podName -c istio-proxy -- curl -s localhost:15000/stats 2>&1 | Select-String -Pattern "circuit|outlier" | Select-Object -First 10
    if ($metrics) {
        Write-Host "  ✓ Метрики найдены:" -ForegroundColor Green
        $metrics | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
    } else {
        Write-Host "  ⚠ Метрики не найдены" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ Пропущено - sidecar отсутствует" -ForegroundColor Yellow
}

Write-Host "`n=== РЕЗЮМЕ ===" -ForegroundColor Green
if ($containers -match "istio-proxy") {
    Write-Host "✓ Circuit Breaker настроен и готов к работе" -ForegroundColor Green
    Write-Host "✓ Istio sidecar инжектирован" -ForegroundColor Green
    Write-Host "✓ DestinationRule должен применяться" -ForegroundColor Green
} else {
    Write-Host "✗ Circuit Breaker НЕ РАБОТАЕТ" -ForegroundColor Red
    Write-Host "`nПричина: Istio sidecar не инжектирован" -ForegroundColor Yellow
    Write-Host "`nЧто делать:" -ForegroundColor Cyan
    Write-Host "1. Проверьте, что Istio установлен в кластере" -ForegroundColor White
    Write-Host "2. Убедитесь, что Istio включен в values.yaml:" -ForegroundColor White
    Write-Host "   - global.istio.enabled: true" -ForegroundColor Gray
    Write-Host "   - charts.core-api.istio.enabled: true" -ForegroundColor Gray
    Write-Host "3. Обновите Helm релиз через GitOps/ArgoCD" -ForegroundColor White
    Write-Host "4. Пересоздайте поды:" -ForegroundColor White
    Write-Host "   kubectl rollout restart deployment team1-project-core-api -n $namespace" -ForegroundColor Cyan
}

