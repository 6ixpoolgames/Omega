param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $LakeArgs
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")
$leanDir = Join-Path $repoRoot "formal\lean"
$elanBin = Join-Path $env:USERPROFILE ".elan\bin"
$lakeFromElan = Join-Path $elanBin "lake.exe"
$toolchainFile = Join-Path $leanDir "lean-toolchain"
$lakeFromInstalledToolchain = $null

if (Test-Path -LiteralPath $toolchainFile) {
    $toolchainName = (Get-Content -Path $toolchainFile -TotalCount 1).Trim()
    $toolchainDirName = $toolchainName.Replace("/", "--").Replace(":", "---")
    $toolchainBin = Join-Path $env:USERPROFILE ".elan\toolchains\$toolchainDirName\bin"
    $candidateLake = Join-Path $toolchainBin "lake.exe"
    if (Test-Path -LiteralPath $candidateLake) {
        $lakeFromInstalledToolchain = $candidateLake
        $env:PATH = "$toolchainBin;$env:PATH"
    }
}

if ($lakeFromInstalledToolchain) {
    $lakePath = $lakeFromInstalledToolchain
} else {
    $lake = Get-Command lake.exe -ErrorAction SilentlyContinue
    if ($lake) {
        $lakePath = $lake.Source
    } elseif (Test-Path -LiteralPath $lakeFromElan) {
        $lakePath = $lakeFromElan
        $env:PATH = "$elanBin;$env:PATH"
    } else {
        throw "lake.exe not found. Install Elan and ensure $elanBin exists."
    }
}

Push-Location $leanDir
try {
    & $lakePath @LakeArgs
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
