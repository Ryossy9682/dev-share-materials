param([ValidateRange(1024,65535)][int]$Port = 8080)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    if (!(Test-Path '.\.venv\Scripts\functions-framework.exe')) { throw '先にsetup.ps1を実行してください。' }
    & .\.venv\Scripts\functions-framework.exe --target hello --host 127.0.0.1 --port $Port
    if ($LASTEXITCODE -ne 0) { throw 'ローカルサーバーが異常終了しました。' }
} finally { Pop-Location }
