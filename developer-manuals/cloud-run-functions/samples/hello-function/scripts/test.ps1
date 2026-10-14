$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    if (!(Test-Path '.\.venv\Scripts\python.exe')) { throw '先にsetup.ps1を実行してください。' }
    & .\.venv\Scripts\python.exe -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'テストに失敗しました。' }
} finally { Pop-Location }
