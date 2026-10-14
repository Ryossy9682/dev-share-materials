param([string]$ConfigPath = (Join-Path (Split-Path $PSScriptRoot -Parent) 'deploy.config.json'))
$ErrorActionPreference = 'Stop'
$cfg = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
$required = 'projectId','region','serviceName','runtimeServiceAccount','cpu','memory','concurrency','minInstances','maxInstances','timeoutSeconds'
foreach ($name in $required) {
    if ($null -eq $cfg.$name -or [string]::IsNullOrWhiteSpace([string]$cfg.$name)) { throw "設定が未入力です: $name" }
    if ([string]$cfg.$name -match 'YOUR_') { throw "設定例を実際の値に変更してください: $name" }
}
if ([int]$cfg.concurrency -lt 1 -or [int]$cfg.concurrency -gt 1000) { throw 'concurrencyは1～1000です。' }
if ([int]$cfg.minInstances -lt 0 -or [int]$cfg.maxInstances -lt 1 -or [int]$cfg.minInstances -gt [int]$cfg.maxInstances) { throw 'インスタンス数の設定が不正です。' }
if ([int]$cfg.timeoutSeconds -lt 1 -or [int]$cfg.timeoutSeconds -gt 3600) { throw 'timeoutSecondsは1～3600です。' }
$root = Split-Path $PSScriptRoot -Parent
Write-Host "配置先: $($cfg.projectId) / $($cfg.region) / $($cfg.serviceName)"
Push-Location $root
try {
    $deployArgs = @('run','deploy',[string]$cfg.serviceName,'--project',[string]$cfg.projectId,
        '--region',[string]$cfg.region,'--source','.', '--function','hello','--base-image','python313',
        '--service-account',[string]$cfg.runtimeServiceAccount,'--no-allow-unauthenticated',
        '--invoker-iam-check','--cpu-throttling','--cpu',[string]$cfg.cpu,'--memory',[string]$cfg.memory,
        '--concurrency',[string]$cfg.concurrency,'--min',[string]$cfg.minInstances,
        '--max',[string]$cfg.maxInstances,'--timeout',[string]$cfg.timeoutSeconds)
    & gcloud @deployArgs
    if ($LASTEXITCODE -ne 0) { throw 'デプロイに失敗しました。Cloud BuildとCloud Runのログを確認してください。' }
} finally { Pop-Location }
