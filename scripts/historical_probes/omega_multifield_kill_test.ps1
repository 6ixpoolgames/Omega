param(
    [int]$MaxMs = 45000
)

$ErrorActionPreference = "Stop"
$StartedAt = Get-Date
$OutDir = Join-Path (Get-Location) "omega_multifield_results"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function Assert-NotTimedOut {
    $elapsed = ((Get-Date) - $StartedAt).TotalMilliseconds
    if ($elapsed -gt $MaxMs) {
        throw "timeout: exceeded ${MaxMs}ms"
    }
}

function New-Rng([uint32]$Seed) {
    $rng = [System.Random]::new([int]($Seed -band 0x7fffffff))
    return {
        return $rng.NextDouble()
    }.GetNewClosure()
}

function Get-Normal($Rand) {
    $u = 0.0
    $v = 0.0
    while ($u -eq 0.0) { $u = & $Rand }
    while ($v -eq 0.0) { $v = & $Rand }
    return [Math]::Sqrt(-2.0 * [Math]::Log($u)) * [Math]::Cos(2.0 * [Math]::PI * $v)
}

function Clamp([double]$X, [double]$Lo, [double]$Hi) {
    return [Math]::Max($Lo, [Math]::Min($Hi, $X))
}

function Get-Preferred([string]$Type, $Rand, [bool]$NearEnrichment) {
    if ($Type -eq "T") { return 1.15 + 0.1 * (Get-Normal $Rand) }
    if ($NearEnrichment) { return -0.35 + 0.5 * (Get-Normal $Rand) }
    return -1.1 + 0.75 * (Get-Normal $Rand)
}

function Get-Basin([double]$X) {
    if ($X -lt -0.45) { return "L" }
    if ($X -gt 0.55) { return "R" }
    return "M"
}

function Get-LocalDrift([double]$X, [string]$Type) {
    if ($Type -eq "T") {
        return -0.11 * ($X - 1.15) - 0.02 * [Math]::Pow($X - 1.15, 3)
    }
    return -0.035 * ($X + 0.9) + 0.018 * [Math]::Sin(2.2 * $X)
}

function New-TrajectoryPair($Regime, [string]$Condition, [int]$Horizon, $Rand) {
    $noise = if ($Condition -eq "perturbed") { 0.09 } else { 0.065 }
    $perturbKick = if ($Condition -eq "perturbed") { 0.025 } else { 0.0 }
    $xA = Get-Preferred $Regime.TypeA $Rand $Regime.NearEnrichment
    $xB = Get-Preferred $Regime.TypeB $Rand $Regime.NearEnrichment
    $a = New-Object System.Collections.Generic.List[double]
    $b = New-Object System.Collections.Generic.List[double]
    $a.Add($xA)
    $b.Add($xB)
    $viable = ([Math]::Abs($xA) -lt 3.0 -and [Math]::Abs($xB) -lt 3.0)
    $cost = 0.0

    for ($t = 0; $t -lt $Horizon; $t++) {
        $cA = 0.0
        $cB = 0.0
        if ($Condition -eq "coupled" -or $Condition -eq "perturbed") {
            $delta = $xB - $xA
            $sign = if ($Regime.Coupling -eq "attractive") { 1.0 } else { -1.0 }
            $cA = $sign * $Regime.Alpha * 0.045 * $delta
            $cB = -$sign * $Regime.Alpha * 0.045 * $delta
        }

        $dxA = (Get-LocalDrift $xA $Regime.TypeA) + $cA + $noise * (Get-Normal $Rand) + $perturbKick * [Math]::Sin(0.17 * $t + 1.3)
        $dxB = (Get-LocalDrift $xB $Regime.TypeB) + $cB + $noise * (Get-Normal $Rand) + $perturbKick * [Math]::Cos(0.13 * $t + 0.7)
        $xA += $dxA
        $xB += $dxB
        $cost += [Math]::Abs($dxA) + [Math]::Abs($dxB)

        if ([Math]::Abs($xA) -gt 3.0 -or [Math]::Abs($xB) -gt 3.0 -or $cost -gt 0.2 * $Horizon) {
            $viable = $false
        }

        $xA = Clamp $xA -3.5 3.5
        $xB = Clamp $xB -3.5 3.5
        $a.Add($xA)
        $b.Add($xB)
    }

    return [pscustomobject]@{ A = $a.ToArray(); B = $b.ToArray(); Viable = $viable }
}

function New-Trajectories($Regime, [string]$Condition, [int]$Horizon, [int]$Count, [int]$SeedOffset) {
    $rand = New-Rng ([uint32]($Regime.Seed + $SeedOffset))
    $items = New-Object System.Collections.Generic.List[object]
    for ($i = 0; $i -lt $Count; $i++) {
        if (($i % 25) -eq 0) { Assert-NotTimedOut }
        $items.Add((New-TrajectoryPair $Regime $Condition $Horizon $rand))
    }
    return $items.ToArray()
}

function New-ShuffledPairs($Independent, [int]$Seed) {
    $rand = New-Rng ([uint32]$Seed)
    $bParts = @($Independent | ForEach-Object { [pscustomobject]@{ B = $_.B; ViableB = $_.Viable } })
    for ($i = $bParts.Count - 1; $i -gt 0; $i--) {
        $j = [int][Math]::Floor((& $rand) * ($i + 1))
        $tmp = $bParts[$i]
        $bParts[$i] = $bParts[$j]
        $bParts[$j] = $tmp
    }
    $out = New-Object System.Collections.Generic.List[object]
    for ($i = 0; $i -lt $Independent.Count; $i++) {
        $out.Add([pscustomobject]@{
            A = $Independent[$i].A
            B = $bParts[$i].B
            Viable = ($Independent[$i].Viable -and $bParts[$i].ViableB)
        })
    }
    return $out.ToArray()
}

function Get-SampleIndexes([int]$Length, [int]$Parts = 12) {
    $idx = New-Object System.Collections.Generic.List[int]
    for ($i = 0; $i -lt $Parts; $i++) {
        $idx.Add([int][Math]::Round(($i * ($Length - 1)) / ($Parts - 1)))
    }
    return $idx.ToArray()
}

function QBin([double]$X, [double]$Width) {
    return [string][int][Math]::Round($X / $Width)
}

function Get-KappaKey($Tau, [string]$Kappa) {
    $idx = Get-SampleIndexes $Tau.A.Count 12
    $parts = New-Object System.Collections.Generic.List[string]
    foreach ($i in $idx) {
        if ($Kappa -eq "center_of_mass") {
            $parts.Add((QBin (($Tau.A[$i] + $Tau.B[$i]) / 2.0) 0.32))
        } elseif ($Kappa -eq "relative_distance") {
            $parts.Add((QBin ([Math]::Abs($Tau.A[$i] - $Tau.B[$i])) 0.25))
        } else {
            $parts.Add("$(Get-Basin $Tau.A[$i])$(Get-Basin $Tau.B[$i])")
        }
    }
    return ($parts -join ".")
}

function Log2([double]$X) {
    return [Math]::Log($X) / [Math]::Log(2.0)
}

function Get-Metrics($Trajectories, [string]$Kappa) {
    $counts = @{}
    $viableCount = 0
    foreach ($tau in $Trajectories) {
        if ($tau.Viable) {
            $viableCount++
            $key = Get-KappaKey $tau $Kappa
            if (-not $counts.ContainsKey($key)) { $counts[$key] = 0 }
            $counts[$key]++
        }
    }
    if ($viableCount -eq 0) {
        return [pscustomobject]@{ RBits = 0.0; RNorm = 0.0; HMacroBits = 0.0; MacroClasses = 0; Viability = 0.0 }
    }
    $r = 0.0
    $hMacro = 0.0
    foreach ($count in $counts.Values) {
        $p = $count / $viableCount
        $r += $p * (Log2 $count)
        $hMacro -= $p * (Log2 $p)
    }
    $rNorm = if ($viableCount -gt 1) { $r / (Log2 $viableCount) } else { 0.0 }
    return [pscustomobject]@{
        RBits = $r
        RNorm = $rNorm
        HMacroBits = $hMacro
        MacroClasses = $counts.Count
        Viability = $viableCount / $Trajectories.Count
    }
}

function Round4([double]$X) {
    return [Math]::Round($X, 4)
}

$Regimes = @(
    [pscustomobject]@{ Id = "FT_attractive_alpha_0.3"; Label = "(F,T) attractive"; TypeA = "F"; TypeB = "T"; Coupling = "attractive"; Alpha = 0.3; Seed = 1101; NearEnrichment = $false },
    [pscustomobject]@{ Id = "FF_repulsive_alpha_0.3"; Label = "(F,F) repulsive"; TypeA = "F"; TypeB = "F"; Coupling = "repulsive"; Alpha = 0.3; Seed = 2202; NearEnrichment = $false },
    [pscustomobject]@{ Id = "near_enrichment_repulsive_alpha_0.3"; Label = "near-enrichment repulsive"; TypeA = "F"; TypeB = "T"; Coupling = "repulsive"; Alpha = 0.3; Seed = 3303; NearEnrichment = $true }
)

$Horizons = @(20, 40)
$SampleCounts = @(25, 75)
$Kappas = @("center_of_mass", "relative_distance", "joint_basin")
$Rows = New-Object System.Collections.Generic.List[object]

foreach ($regime in $Regimes) {
    foreach ($horizon in $Horizons) {
        foreach ($sampleCount in $SampleCounts) {
            Assert-NotTimedOut
            $coupled = New-Trajectories $regime "coupled" $horizon $sampleCount (10 + $horizon + $sampleCount)
            $independent = New-Trajectories $regime "independent" $horizon $sampleCount (20 + $horizon + $sampleCount)
            $shuffled = New-ShuffledPairs $independent ($regime.Seed + 999 + $horizon + $sampleCount)
            $perturbed = New-Trajectories $regime "perturbed" $horizon $sampleCount (30 + $horizon + $sampleCount)

            foreach ($kappa in $Kappas) {
                $mc = Get-Metrics $coupled $kappa
                $mi = Get-Metrics $independent $kappa
                $ms = Get-Metrics $shuffled $kappa
                $mp = Get-Metrics $perturbed $kappa
                $deltaS = $mc.RBits - $ms.RBits
                $deltaI = $mc.RBits - $mi.RBits
                $retention = if ($mc.RBits -gt 0.000000001) { $mp.RBits / $mc.RBits } else { 0.0 }
                $Rows.Add([pscustomobject]@{
                    regime = $regime.Label
                    regime_id = $regime.Id
                    coupling_type = $regime.Coupling
                    alpha = $regime.Alpha
                    kappa = $kappa
                    horizon = $horizon
                    sample_count = $sampleCount
                    R_coupled = Round4 $mc.RBits
                    R_independent = Round4 $mi.RBits
                    R_shuffled = Round4 $ms.RBits
                    R_perturbed = Round4 $mp.RBits
                    Rn_coupled = Round4 $mc.RNorm
                    Rn_shuffled = Round4 $ms.RNorm
                    Hmacro_coupled = Round4 $mc.HMacroBits
                    Hmacro_shuffled = Round4 $ms.HMacroBits
                    Delta_R_coupled_minus_shuffled = Round4 $deltaS
                    Delta_R_coupled_minus_independent = Round4 $deltaI
                    viability_coupled = Round4 $mc.Viability
                    viability_independent = Round4 $mi.Viability
                    viability_shuffled = Round4 $ms.Viability
                    viability_perturbed = Round4 $mp.Viability
                    perturbation_retention = Round4 $retention
                    macro_classes_coupled = $mc.MacroClasses
                    macro_classes_shuffled = $ms.MacroClasses
                })
            }
        }
    }
}

$Summaries = New-Object System.Collections.Generic.List[object]
foreach ($regime in $Regimes) {
    foreach ($kappa in $Kappas) {
        $subset = @($Rows | Where-Object { $_.regime_id -eq $regime.Id -and $_.kappa -eq $kappa })
        $meanDelta = ($subset | Measure-Object -Property Delta_R_coupled_minus_shuffled -Average).Average
        $meanViability = ($subset | Measure-Object -Property viability_coupled -Average).Average
        $meanRetention = ($subset | Measure-Object -Property perturbation_retention -Average).Average
        $positives = @($subset | Where-Object { $_.Delta_R_coupled_minus_shuffled -gt 0 }).Count
        $status = "fail"
        $reason = "coupled realization robustness did not beat shuffled null consistently"
        if ($positives -ge 3 -and $meanDelta -gt 0 -and $meanViability -ge 0.8 -and $meanRetention -ge 0.7) {
            $status = "pass"
            $reason = "coupled beats shuffled in most horizon/sample checks with viability retained"
        } elseif ($positives -ge 2 -and $meanDelta -gt 0 -and $meanViability -ge 0.8) {
            $status = "weak"
            $reason = "partial positive signal, but not robust across all checks"
        }
        $Summaries.Add([pscustomobject]@{
            regime = $regime.Label
            kappa = $kappa
            status = $status
            mean_delta_R = Round4 $meanDelta
            mean_viability_coupled = Round4 $meanViability
            mean_perturbation_retention = Round4 $meanRetention
            reason = $reason
        })
    }
}

$CsvPath = Join-Path $OutDir "omega_multifield_kill_test_results.csv"
$SummaryPath = Join-Path $OutDir "omega_multifield_kill_test_summary.md"
$Rows | Export-Csv -NoTypeInformation -Path $CsvPath

$summaryText = @()
$summaryText += "# Omega Multifield Compact Kill-Test Summary"
$summaryText += ""
$summaryText += "Runtime cap: ${MaxMs}ms"
$summaryText += "Rows: $($Rows.Count)"
$summaryText += ""
$summaryText += "Estimator: ``R_bits = E_gamma[log2(|fiber_gamma|)]`` over viable observed trajectories, weighted by viable trajectory counts. This estimates aggregate realization-fiber support, not macro-class entropy. ``Hmacro_*`` is reported separately."
$summaryText += ""
$summaryText += "Important limitation: this is a standalone toy simulator because no prior multifield code was present in the workspace."
$summaryText += ""
$summaryText += "## Summary"
$summaryText += ""
$summaryText += ($Summaries | ConvertTo-Csv -NoTypeInformation | ForEach-Object { $_ })
$summaryText += ""
$summaryText += "## Main Results"
$summaryText += ""
$summaryText += ($Rows | ConvertTo-Csv -NoTypeInformation | ForEach-Object { $_ })
$summaryText -join "`n" | Set-Content -Path $SummaryPath -Encoding UTF8

[pscustomobject]@{
    csvPath = $CsvPath
    summaryPath = $SummaryPath
    summaries = $Summaries
} | ConvertTo-Json -Depth 5
