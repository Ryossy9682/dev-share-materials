$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    & py -3.13 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.13の仮想環境作成に失敗しました。' }
    & .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw '依存関係のインストールに失敗しました。' }
} finally { Pop-Location }
