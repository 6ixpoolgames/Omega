param(
    [string] $OutRoot = ".tmp\baseline_witness_smoke",
    [string] $RetainedRoot = "results\baseline_witnesses",
    [switch] $SkipPytest
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")

if ([System.IO.Path]::IsPathRooted($OutRoot)) {
    $resolvedOutRoot = $OutRoot
} else {
    $resolvedOutRoot = Join-Path $repoRoot $OutRoot
}

if ([System.IO.Path]::IsPathRooted($RetainedRoot)) {
    $resolvedRetainedRoot = $RetainedRoot
} else {
    $resolvedRetainedRoot = Join-Path $repoRoot $RetainedRoot
}

$runId = Get-Date -Format "yyyyMMdd_HHmmss"
$runRoot = Join-Path $resolvedOutRoot $runId
$witnessOutRoot = Join-Path $runRoot "witnesses"
$pytestBaseTemp = Join-Path $runRoot "pytest_tmp"
$pytestCache = Join-Path $runRoot "pytest_cache"

New-Item -ItemType Directory -Force -Path $witnessOutRoot | Out-Null
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

$witnesses = @(
    [pscustomobject]@{
        id = "same_reachability_different_recovery_v0"
        module = "omega.baseline_witnesses.same_reachability_different_recovery"
        expected_status = "same_reachability_different_declared_recovery"
        retained_summary = "20260611_same_reachability_different_recovery_v0\witness_summary.json"
        test = "tests\test_same_reachability_different_recovery.py"
    },
    [pscustomobject]@{
        id = "same_entropy_different_recovery_profile_v0"
        module = "omega.baseline_witnesses.same_entropy_different_recovery_profile"
        expected_status = "same_entropy_different_recovery_profile"
        retained_summary = "20260611_same_entropy_different_recovery_profile_v0\witness_summary.json"
        test = "tests\test_same_entropy_different_recovery_profile.py"
    },
    [pscustomobject]@{
        id = "same_frontier_morphology_different_loss_profile_v0"
        module = "omega.baseline_witnesses.same_frontier_morphology_different_loss_profile"
        expected_status = "same_frontier_morphology_different_declared_loss_profile"
        retained_summary = "20260611_same_frontier_morphology_different_loss_profile_v0\witness_summary.json"
        test = "tests\test_same_frontier_morphology_different_loss_profile.py"
    },
    [pscustomobject]@{
        id = "same_mutual_information_different_declared_recovery_v0"
        module = "omega.baseline_witnesses.same_mutual_information_different_declared_recovery"
        expected_status = "same_mutual_information_different_declared_recovery"
        retained_summary = "20260611_same_mutual_information_different_declared_recovery_v0\witness_summary.json"
        test = "tests\test_same_mutual_information_different_declared_recovery.py"
    },
    [pscustomobject]@{
        id = "same_optimized_success_different_declared_recovery_v0"
        module = "omega.baseline_witnesses.same_optimized_success_different_declared_recovery"
        expected_status = "same_optimized_success_different_declared_recovery"
        retained_summary = "20260611_same_optimized_success_different_declared_recovery_v0\witness_summary.json"
        test = "tests\test_same_optimized_success_different_declared_recovery.py"
    },
    [pscustomobject]@{
        id = "same_marginal_success_different_joint_success_v0"
        module = "omega.baseline_witnesses.same_marginal_success_different_joint_success"
        expected_status = "same_marginal_success_different_joint_success"
        retained_summary = "20260611_same_marginal_success_different_joint_success_v0\witness_summary.json"
        test = "tests\test_same_marginal_success_different_joint_success.py"
    },
    [pscustomobject]@{
        id = "same_compression_score_different_merge_soundness_v0"
        module = "omega.baseline_witnesses.same_compression_score_different_merge_soundness"
        expected_status = "same_compression_score_different_merge_soundness"
        retained_summary = "20260611_same_compression_score_different_merge_soundness_v0\witness_summary.json"
        test = "tests\test_same_compression_score_different_merge_soundness.py"
    },
    [pscustomobject]@{
        id = "same_chain_evidence_different_class_soundness_v0"
        module = "omega.baseline_witnesses.same_chain_evidence_different_class_soundness"
        expected_status = "same_chain_evidence_different_class_soundness"
        retained_summary = "20260611_same_chain_evidence_different_class_soundness_v0\witness_summary.json"
        test = "tests\test_same_chain_evidence_different_class_soundness.py"
    },
    [pscustomobject]@{
        id = "same_coarse_bisimulation_different_consequence_profile_v0"
        module = "omega.baseline_witnesses.same_coarse_bisimulation_different_consequence_profile"
        expected_status = "same_coarse_bisimulation_different_consequence_profile"
        retained_summary = "20260611_same_coarse_bisimulation_different_consequence_profile_v0\witness_summary.json"
        test = "tests\test_same_coarse_bisimulation_different_consequence_profile.py"
    }
)

Push-Location $repoRoot
try {
    $results = @()

    foreach ($spec in $witnesses) {
        $outDir = Join-Path $witnessOutRoot $spec.id
        $retainedPath = Join-Path $resolvedRetainedRoot $spec.retained_summary
        if (-not (Test-Path -LiteralPath $retainedPath)) {
            throw "Retained witness summary missing: $retainedPath"
        }

        $result = Invoke-JsonCommand @(
            $pythonCommand
            "-m"
            $spec.module
            "--out"
            $outDir
        )

        $retained = Get-Content -LiteralPath $retainedPath -Raw | ConvertFrom-Json
        $generatedSummaryPath = Join-Path $outDir "witness_summary.json"
        $generated = Get-Content -LiteralPath $generatedSummaryPath -Raw | ConvertFrom-Json

        Assert-Equal -Name "$($spec.id).witness_id" -Actual $result.witness_id -Expected $spec.id
        Assert-Equal -Name "$($spec.id).witness_status" -Actual $result.witness_status -Expected $spec.expected_status
        Assert-Equal -Name "$($spec.id).retained_witness_id" -Actual $retained.witness_id -Expected $spec.id
        Assert-Equal -Name "$($spec.id).retained_witness_status" -Actual $retained.witness_status -Expected $spec.expected_status
        Assert-Equal -Name "$($spec.id).generated_summary_digest" -Actual $generated.summary_digest -Expected $result.summary_digest
        Assert-Equal -Name "$($spec.id).retained_summary_digest" -Actual $result.summary_digest -Expected $retained.summary_digest

        $results += [pscustomobject]@{
            witness_id = $spec.id
            witness_status = $result.witness_status
            summary_digest = $result.summary_digest
            output = $outDir
        }
    }

    if (-not $SkipPytest) {
        $pytestCommand = @($pythonCommand)
        $pytestCommand += @("-m", "pytest")
        $pytestCommand += @($witnesses | ForEach-Object { $_.test })
        $pytestCommand += @("-q", "--basetemp", $pytestBaseTemp, "-o", "cache_dir=$pytestCache")
        Invoke-CheckedCommand $pytestCommand | Write-Output
    }

    [pscustomobject]@{
        status = "PASS"
        run_root = $runRoot
        witness_count = $witnesses.Count
        witness_outputs = $witnessOutRoot
        retained_digest_check = "passed"
        focused_pytest = if ($SkipPytest) { "skipped" } else { "passed" }
        witnesses = $results
    } | ConvertTo-Json -Depth 5
} finally {
    Pop-Location
}
