param(
    [switch]$SkipInstall,
    [int]$Port = 8501
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

function Load-DotEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        return
    }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
            return
        }
        $pair = $line.Split("=", 2)
        $key = $pair[0].Trim()
        $value = $pair[1].Trim().Trim("'`"")
        if ($key -and -not [string]::IsNullOrWhiteSpace($value)) {
            Set-Item -Path "Env:$key" -Value $value
        }
    }
}

Load-DotEnv -Path ".env"

$hfModel = if ($env:HF_MODEL) { $env:HF_MODEL } else { "HuggingFaceTB/SmolLM2-1.7B-Instruct" }
Write-Host "Starting AI Support Intelligence Dashboard..."
Write-Host "Model Profile: $hfModel"

function Get-FreePort {
    param([int]$PreferredPort)

    for ($candidate = $PreferredPort; $candidate -lt ($PreferredPort + 20); $candidate++) {
        $listener = $null
        try {
            $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $candidate)
            $listener.Start()
            $listener.Stop()
            return $candidate
        } catch {
            if ($listener) {
                try { $listener.Stop() } catch {}
            }
            continue
        }
    }

    return $PreferredPort
}

Write-Host "Starting Streamlit..."
$pythonExe = "python"
if (Test-Path ".\\.venv\\Scripts\\python.exe") {
    $pythonExe = ".\\.venv\\Scripts\\python.exe"
}

if (-not $SkipInstall) {
    Write-Host "Installing dependencies..."
    & $pythonExe -m pip install -r requirements.txt
}

$finalPort = Get-FreePort -PreferredPort $Port
if ($finalPort -ne $Port) {
    Write-Host "Port $Port is busy. Using available port $finalPort."
}

& $pythonExe -m streamlit run app.py --server.port $finalPort
