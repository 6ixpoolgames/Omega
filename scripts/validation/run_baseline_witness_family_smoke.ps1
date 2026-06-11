param(
    [string] $OutRoot = ".tmp\baseline_witness_family_smoke",
    [int] $MaxNuisanceBits = 5,
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
$pytestBaseTemp = Join-Path $runRoot "pytest_tmp"
$pytestCache = Join-Path $runRoot "pytest_cache"

New-Item -ItemType Directory -Force -Path $runRoot | Out-Null
New-Item -ItemType Directory -Force -Path $pytestBaseTemp | Out-Null
New-Item -ItemType Directory -Force -Path $pytestCache | Out-Null

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$python = Get-Command python -ErrorAction SilentlyContinue
$py = Get-Command py -ErrorAction SilentlyContinue

if (Test-Path -LiteralPath $venvPython) {
    $pythonCommand = @($venvPython)
} elseif ($python) {
    $pythonCommand = @($python.Source)
} elseif ($py) {
    $pythonCommand = @($py.Source, "-3")
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

$familyTests = @(
    "tests\test_chain_evidence_class_soundness_family.py",
    "tests\test_coarse_bisimulation_consequence_profile_family.py",
    "tests\test_compression_score_merge_soundness_family.py",
    "tests\test_entropy_recovery_profile_family.py",
    "tests\test_frontier_morphology_loss_profile_family.py",
    "tests\test_marginal_success_joint_success_family.py",
    "tests\test_mutual_information_declared_recovery_family.py",
    "tests\test_observation_rank_declared_recovery_family.py",
    "tests\test_optimized_success_declared_recovery_family.py",
    "tests\test_reachability_declared_recovery_family.py"
)

Push-Location $repoRoot
try {
    $summaryOutput = Invoke-CheckedCommand @(
        $pythonCommand
        "-m"
        "omega.baseline_witnesses.family_smoke"
        "--max-nuisance-bits"
        "$MaxNuisanceBits"
    )
    $summary = ($summaryOutput | Out-String | ConvertFrom-Json)

    if ($summary.status -ne "PASS") {
        throw "Family smoke failed: $($summaryOutput | Out-String)"
    }

    if (-not $SkipPytest) {
        $pytestCommand = @($pythonCommand)
        $pytestCommand += @("-m", "pytest")
        $pytestCommand += $familyTests
        $pytestCommand += @("-q", "--basetemp", $pytestBaseTemp, "-o", "cache_dir=$pytestCache")
        Invoke-CheckedCommand $pytestCommand | Write-Output
    }

    [pscustomobject]@{
        status = "PASS"
        run_root = $runRoot
        max_nuisance_bits = $summary.max_nuisance_bits
        family_count = $summary.family_count
        case_count = $summary.case_count
        aggregate_check = "passed"
        focused_pytest = if ($SkipPytest) { "skipped" } else { "passed" }
        families = $summary.families
        not_claimed = $summary.not_claimed
    } | ConvertTo-Json -Depth 6
} finally {
    Pop-Location
}
