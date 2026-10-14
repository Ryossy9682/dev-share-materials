param([string]$ConfigPath = (Join-Path (Split-Path $PSScriptRoot -Parent) 'deploy.config.json'))
$ErrorActionPreference = 'Stop'
$cfg = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
if ([string]::IsNullOrWhiteSpace($cfg.projectId) -or $cfg.projectId -match 'YOUR_') { throw 'projectIdを設定してください。' }
$serviceUrl = & gcloud run services describe $cfg.serviceName --project $cfg.projectId --region $cfg.region --format='value(status.url)'
if ($LASTEXITCODE -ne 0 -or !$serviceUrl) { throw 'サービスURLを取得できませんでした。' }
$token = & gcloud auth print-identity-token
if ($LASTEXITCODE -ne 0 -or !$token) { throw '開発用IDトークンを取得できませんでした。' }
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "$serviceUrl/?name=Developer" -Headers $headers
