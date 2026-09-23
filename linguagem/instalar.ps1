$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

$Python = Get-Command py -ErrorAction SilentlyContinue
if (-not $Python) {
    $Python = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $Python) {
    throw "Hzhon precisa do Python 3.10 ou mais recente. Instale Python e tente novamente."
}

$Launcher = Join-Path $env:USERPROFILE "hzhon.cmd"
@"
@echo off
py "$Root\hzhon_cli.py" %*
"@ | Set-Content -Encoding ASCII $Launcher

Write-Host "Hzhon instalada em $Launcher"
Write-Host "Abra um novo terminal e execute: hzhon --help"