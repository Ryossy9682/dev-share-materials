param(
    [ValidateSet('minimal','patterns')][string]$Project = 'patterns',
    [ValidateSet('phase1','phase2')][string]$Phase = 'phase1'
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$files = @('raw_orders.csv')
if ($Project -eq 'patterns') { $files += @('raw_customers.csv', 'raw_events.csv') }
foreach ($file in $files) {
    Copy-Item (Join-Path $root "fixtures\$Phase\$file") (Join-Path $root "projects\$Project\seeds\$file")
}
Write-Host "CSVを$Phaseへ切り替えました。クラウドのデータはまだ変更されていません。"
