param(
    [switch]$SkipMinikubeStart
)

$ErrorActionPreference = "Stop"
$repoRoot = $PSScriptRoot

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & $Name @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Name $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
    }
}

foreach ($command in @("docker", "minikube", "helm")) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "$command was not found on PATH. Install it and reopen PowerShell."
    }
}

Push-Location $repoRoot
try {
    Invoke-CheckedCommand -Name "docker" -Arguments @("info", "--format", "{{.ServerVersion}}")

    if (-not $SkipMinikubeStart) {
        Invoke-CheckedCommand -Name "minikube" -Arguments @(
            "start", "--driver=docker", "--cpus=2", "--memory=3072",
            "--kubernetes-version=v1.35.1"
        )
    }

    $images = @(
        @{ Name = "fleetops-api"; Dockerfile = "Dockerfile.api" }
    )

    foreach ($image in $images) {
        $tag = "$($image.Name):local"
        Invoke-CheckedCommand -Name "docker" -Arguments @(
            "build", "-t", $tag, "-f", $image.Dockerfile, "."
        )
        Invoke-CheckedCommand -Name "minikube" -Arguments @("image", "load", $tag)
    }

    Invoke-CheckedCommand -Name "helm" -Arguments @(
        "upgrade", "--install", "fleetops", ".\helm\fleetops",
        "--namespace", "fleetops", "--create-namespace", "--wait", "--timeout", "3m"
    )
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "FleetOps is deployed. Open the web app with:"
Write-Host "  minikube service fleetops-web -n fleetops"
Write-Host ""
Write-Host "To check pods:"
Write-Host "  minikube kubectl -- get pods -n fleetops"
