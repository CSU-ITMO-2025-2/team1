# Проверка Circuit Breaker в Istio

Write-Host "=== Проверка Circuit Breaker ===" -ForegroundColor Green

$namespace = "team1-ns"
$appLabel = "app=core-api"

Write-Host "`n1. Проверка подов..." -ForegroundColor Yellow
$pods = kubectl get pods -n $namespace -l $appLabel -o jsonpath='{.items[*].metadata.name}' 2>&1
if ($pods) {
    $podArray = $pods -split ' '
    foreach ($pod in $podArray) {
        Write-Host "`n  Pod: $pod" -ForegroundColor Cyan
        
        # Проверка контейнеров
        $containers = kubectl get pod $pod -n $namespace -o jsonpath='{.spec.containers[*].name}' 2>&1
        $ready = kubectl get pod $pod -n $namespace -o jsonpath='{.status.containerStatuses[*].ready}' 2>&1
        Write-Host "    Контейнеры: $containers" -ForegroundColor White
        Write-Host "    Ready: $ready" -ForegroundColor White
        
        if ($containers -match "istio-proxy") {
            Write-Host "    ✓ Istio sidecar найден" -ForegroundColor Green
        } else {
            Write-Host "    ✗ Istio sidecar ОТСУТСТВУЕТ!" -ForegroundColor Red
        }
        
        # Проверка аннотации
        $annotation = kubectl get pod $pod -n $namespace -o jsonpath='{.metadata.annotations.sidecar\.istio\.io/inject}' 2>&1
        Write-Host "    Аннотация sidecar.istio.io/inject: $annotation" -ForegroundColor White
        
        # Проверка меток namespace (если есть доступ)
        $nsLabel = kubectl get namespace $namespace -o jsonpath='{.metadata.labels.istio-injection}' 2>&1
        if ($nsLabel) {
            Write-Host "    Метка namespace istio-injection: $nsLabel" -ForegroundColor White
        }
    }
} else {
    Write-Host "✗ Поды не найдены" -ForegroundColor Red
}

Write-Host "`n2. Проверка DestinationRule..." -ForegroundColor Yellow
$dr = kubectl get destinationrule -n $namespace -o name 2>&1
if ($dr -match "destinationrule") {
    Write-Host "✓ DestinationRule найден" -ForegroundColor Green
    Write-Host "  $dr" -ForegroundColor White
} else {
    Write-Host "✗ DestinationRule не найден или нет прав на просмотр" -ForegroundColor Red
    Write-Host "  Попробуйте с правами администратора:" -ForegroundColor Yellow
    Write-Host "  kubectl get destinationrule -n $namespace --as=system:admin" -ForegroundColor Cyan
}

Write-Host "`n3. Проверка метрик Envoy (если sidecar есть)..." -ForegroundColor Yellow
$podWithSidecar = kubectl get pods -n $namespace -l $appLabel -o jsonpath='{.items[?(@.spec.containers[*].name=="istio-proxy")].metadata.name}' 2>&1
if ($podWithSidecar) {
    Write-Host "  Pod с sidecar: $podWithSidecar" -ForegroundColor Cyan
    Write-Host "  Проверка метрик circuit breaker..." -ForegroundColor White
    $circuitMetrics = kubectl exec -n $namespace $podWithSidecar -c istio-proxy -- curl -s localhost:15000/stats 2>&1 | Select-String -Pattern "circuit|outlier" | Select-Object -First 5
    if ($circuitMetrics) {
        Write-Host "  ✓ Метрики найдены:" -ForegroundColor Green
        $circuitMetrics | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
    } else {
        Write-Host "  ⚠ Метрики не найдены или sidecar не отвечает" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ Нет подов с sidecar для проверки метрик" -ForegroundColor Yellow
}

Write-Host "`n=== Резюме ===" -ForegroundColor Green
Write-Host "Для работы Circuit Breaker необходимо:" -ForegroundColor Yellow
Write-Host "1. ✓ DestinationRule создан (проверьте выше)" -ForegroundColor White
Write-Host "2. ✗ Istio sidecar должен быть в подах (2/2 READY)" -ForegroundColor White
Write-Host "3. ⚠ Если sidecar отсутствует:" -ForegroundColor Yellow
Write-Host "   - Проверьте, что Istio установлен в кластере" -ForegroundColor White
Write-Host "   - Проверьте, что Istio webhook работает" -ForegroundColor White
Write-Host "   - Пересоздайте поды после добавления аннотации" -ForegroundColor White
Write-Host "   - Выполните: kubectl rollout restart deployment -n $namespace" -ForegroundColor Cyan

