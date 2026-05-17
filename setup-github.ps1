# EasyLearn — conectar este proyecto con GitHub (una sola vez).
# Ejecutar en PowerShell desde la carpeta del proyecto:
#   .\setup-github.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

$RepoName = "easy-learn-design-system"
$GhExe = "$env:TEMP\gh-cli\bin\gh.exe"

if (-not (Test-Path $GhExe)) {
    Write-Host "Descargando GitHub CLI..."
    $ghZip = "$env:TEMP\gh-cli.zip"
    $ghDir = "$env:TEMP\gh-cli"
    Invoke-WebRequest -Uri "https://github.com/cli/cli/releases/download/v2.92.0/gh_2.92.0_windows_amd64.zip" -OutFile $ghZip -UseBasicParsing
    Expand-Archive -Path $ghZip -DestinationPath $ghDir -Force
}

& $GhExe auth status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Inicia sesion en GitHub (se abrira el navegador)..."
    & $GhExe auth login -h github.com -p https -w
}

$owner = (& $GhExe api user -q .login).Trim()
$remoteUrl = "https://github.com/$owner/$RepoName.git"

Write-Host ""
Write-Host "Cuenta: $owner"
Write-Host "Repositorio: $RepoName"
Write-Host ""

if (git remote get-url origin 2>$null) {
    git remote set-url origin $remoteUrl
} else {
    git remote add origin $remoteUrl
}

$exists = & $GhExe repo view "$owner/$RepoName" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creando repositorio en GitHub..."
    & $GhExe repo create $RepoName --public --source=. --remote=origin --description "EasyLearn — design system y portales Django (estudiante, docente, administrador)"
} else {
    Write-Host "El repositorio ya existe en GitHub."
}

Write-Host "Subiendo rama main..."
git push -u origin main

Write-Host ""
Write-Host "Listo: https://github.com/$owner/$RepoName"
