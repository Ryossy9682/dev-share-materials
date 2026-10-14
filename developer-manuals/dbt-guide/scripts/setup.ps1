$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    & py -3.12 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.12の仮想環境を作成できませんでした。' }
    & .\.venv\Scripts\python.exe -m pip install -r requirements-offline.txt
    if ($LASTEXITCODE -ne 0) { throw '依存関係のインストールに失敗しました。' }
    if (!(Test-Path '.\profiles\profiles.yml')) {
        Copy-Item '.\profiles\profiles.yml.example' '.\profiles\profiles.yml'
    }
} finally { Pop-Location }
