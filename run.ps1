param(
    [int]$Port = 8005
)

$ErrorActionPreference = "Stop"

function Find-Python {
    $knownPaths = @(
        (Join-Path $PSScriptRoot ".python313\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe")
    )

    foreach ($path in $knownPaths) {
        if (Test-Path $path) {
            & $path --version *> $null
            if ($LASTEXITCODE -eq 0) {
                return $path
            }
        }
    }

    $commands = @("python", "py")
    foreach ($command in $commands) {
        $candidate = Get-Command $command -ErrorAction SilentlyContinue
        if ($candidate) {
            try {
                & $candidate.Source --version *> $null
                if ($LASTEXITCODE -eq 0) {
                    return $candidate.Source
                }
            }
            catch {
                continue
            }
        }
    }

    throw "Python is not installed or is not on PATH. Install Python 3.13 or newer, then run this script again."
}

Push-Location $PSScriptRoot
try {
    $python = Find-Python
    $venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

    if (-not (Test-Path $venvPython)) {
        & $python -m venv (Join-Path $PSScriptRoot ".venv")
    }

    & $venvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & $venvPython -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & $venvPython manage.py migrate
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    & $venvPython manage.py runserver "127.0.0.1:$Port"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    Pop-Location
}
