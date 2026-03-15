param(
    [string]$ApiHost = "127.0.0.1",
    [int]$Port = 8000,
    [string]$EnvFile = ".env.test",
    [switch]$NoReload
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) {
    Write-Host "[INFO] $msg" -ForegroundColor Cyan
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    throw ".venv python not found: $pythonExe"
}

$envPath = Join-Path $projectRoot $EnvFile
if (-not (Test-Path $envPath)) {
    Write-Info "Env file not found: $envPath (will still try to start with defaults)"
}

$env:XJ_ENV_FILE = $EnvFile

$uvicornArgs = @(
    "-m",
    "uvicorn",
    "app.main:app",
    "--host",
    $ApiHost,
    "--port",
    "$Port"
)

if (-not $NoReload) {
    $uvicornArgs += "--reload"
}

Write-Info "Project root: $projectRoot"
Write-Info "Using env file: $EnvFile"
Write-Info "Starting backend: http://$ApiHost`:$Port"

Push-Location $projectRoot
try {
    & $pythonExe @uvicornArgs
} finally {
    Pop-Location
}
