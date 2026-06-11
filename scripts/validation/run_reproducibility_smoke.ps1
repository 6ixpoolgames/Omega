param(
    [string] $OutRoot = ".tmp\reproducibility_smoke",
    [switch] $SkipPytest
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")

if ([System.IO.Path]::IsPathRooted($OutRoot)) {
    $resolvedOutRoot = $OutRoot
} else {
    $resolvedOutRoot = Join-Path $repoRoot $OutRoot
}

$runId = Get-Date -Format "yyyyMMdd_HHmmss"
$runRoot = Join-Path $resolvedOutRoot $runId
$x3Out = Join-Path $runRoot "registry_first_x3"
$auditOut = Join-Path $runRoot "registry_first_x3_audit"
$pytestBaseTemp = Join-Path $runRoot "pytest_tmp"
$pytestCache = Join-Path $runRoot "pytest_cache"

New-Item -ItemType Directory -Force -Path $runRoot | Out-Null
New-Item -ItemType Directory -Force -Path $pytestBaseTemp | Out-Null
New-Item -ItemType Directory -Force -Path $pytestCache | Out-Null

$python = Get-Command python -ErrorAction SilentlyContinue
$py = Get-Command py -ErrorAction SilentlyContinue
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

if ($python) {
    $pythonCommand = @($python.Source)
} elseif ($py) {
    $pythonCommand = @($py.Source, "-3")
} elseif (Test-Path -LiteralPath $venvPython) {
    $pythonCommand = @($venvPython)
} else {
    throw "No Python interpreter found. Install Python, add it to PATH, or create .venv\Scripts\python.exe."
}

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $Command
    )

    $args = @()
    if ($Command.Length -gt 1) {
        $args = @($Command[1..($Command.Length - 1)])
    }
    $output = & $Command[0] @args 2>&1
    if ($LASTEXITCODE -ne 0) {
        $message = ($output | Out-String).Trim()
        throw "Command failed: $($Command -join ' ')`n$message"
    }
    return $output
}

function Invoke-JsonCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $Command
    )

    $output = Invoke-CheckedCommand $Command
    return ($output | Out-String | ConvertFrom-Json)
}

function Assert-Equal {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name,
        [Parameter(Mandatory = $true)]
        $Actual,
        [Parameter(Mandatory = $true)]
        $Expected
    )

    if ("$Actual" -ne "$Expected") {
        throw "$Name expected '$Expected' but got '$Actual'"
    }
}

Push-Location $repoRoot
try {
    $probe = Invoke-JsonCommand @(
        $pythonCommand
        "-m",
        "omega.stochastic_distinction_channel.registry_first_x3_probe",
        "--out",
        $x3Out
    )

    $audit = Invoke-JsonCommand @(
        $pythonCommand
        "-m",
        "omega.stochastic_distinction_channel.registry_first_adversarial_audit",
        "--source",
        $x3Out,
        "--out",
        $auditOut
    )

    $carrier = Import-Csv -LiteralPath (Join-Path $x3Out "carrier_manifest.csv")

    Assert-Equal -Name "carrier_id" -Actual $probe.carrier_id -Expected "X3"
    Assert-Equal -Name "state_count" -Actual $carrier[0].state_count -Expected "8"
    Assert-Equal -Name "channel_count" -Actual $probe.channel_count -Expected "15"
    Assert-Equal -Name "registered_rows" -Actual $probe.registered_rows -Expected "120"
    Assert-Equal -Name "gap_rows" -Actual $probe.gap_rows -Expected "120"
    Assert-Equal -Name "cascade_evidence_status" -Actual $probe.cascade_evidence_status -Expected "path_rows_retained"
    Assert-Equal -Name "probe_overall_status" -Actual $probe.overall_status -Expected "registry_first_theorem_transfer_ready"
    Assert-Equal -Name "audit_overall_status" -Actual $audit.overall_status -Expected "PASS"
    Assert-Equal -Name "audit_rows" -Actual $audit.audit_rows -Expected "105"
    Assert-Equal -Name "audit_failure_count" -Actual $audit.failure_count -Expected "0"

    if (-not $SkipPytest) {
        Invoke-CheckedCommand @(
            $pythonCommand
            "-m",
            "pytest",
            "tests\test_stochastic_registry_first_x3_probe.py",
            "--basetemp",
            $pytestBaseTemp,
            "-o",
            "cache_dir=$pytestCache"
        ) | Write-Output
    }

    [pscustomobject]@{
        status = "PASS"
        run_root = $runRoot
        x3_output = $x3Out
        audit_output = $auditOut
        carrier_id = $probe.carrier_id
        state_count = [int] $carrier[0].state_count
        channel_count = [int] $probe.channel_count
        registered_rows = [int] $probe.registered_rows
        provenance_gap_rows = [int] $probe.gap_rows
        audit_rows = [int] $audit.audit_rows
        audit_failure_count = [int] $audit.failure_count
        focused_pytest = if ($SkipPytest) { "skipped" } else { "passed" }
    } | ConvertTo-Json -Depth 3
} finally {
    Pop-Location
}
