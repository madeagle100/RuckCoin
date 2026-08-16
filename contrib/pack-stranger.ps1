# Build stranger-facing zips + SHA256SUMS into website/downloads.
# Linux ravend/raven-cli are stripped copies from WSL /tmp/ruck-rel/linux
# or from -LinuxBinDir.
param(
    [string]$LinuxBinDir = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$deskSite = "\OneDrive\Desktop\RuckCoin\website"
if (Test-Path (Join-Path $root "website\index.html")) {
    $site = Join-Path $root "website"
} elseif (Test-Path (Join-Path $deskSite "index.html")) {
    $site = $deskSite
} else {
    throw "website/ not found"
}
$out = Join-Path $site "downloads"
New-Item -ItemType Directory -Force -Path $out | Out-Null

$stage = Join-Path $env:TEMP "ruck-pack"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $stage | Out-Null

# --- wallet zip (no WSL paths, no __pycache__) ---
$wdir = Join-Path $stage "ruckcoin-wallet"
New-Item -ItemType Directory -Force -Path (Join-Path $wdir "static") | Out-Null
Copy-Item (Join-Path $root "wallet\ruck-wallet.py") $wdir
Copy-Item (Join-Path $root "wallet\Open Wallet.bat") $wdir
Copy-Item (Join-Path $root "wallet\Start RuckCoin.bat") $wdir
Copy-Item (Join-Path $root "wallet\start-ruckcoin.sh") $wdir
Copy-Item (Join-Path $root "wallet\README.txt") $wdir
Copy-Item (Join-Path $root "wallet\static\*") (Join-Path $wdir "static")
Copy-Item (Join-Path $root "contrib\start-node.ps1") $wdir
Copy-Item (Join-Path $root "contrib\ruck.conf.example") $wdir
Add-Type -AssemblyName System.IO.Compression.FileSystem
function Zip-Dir($from, $to) {
    $tmp = Join-Path $env:TEMP ([IO.Path]::GetFileName($to))
    if (Test-Path $tmp) { Remove-Item $tmp -Force }
    [IO.Compression.ZipFile]::CreateFromDirectory($from, $tmp, [IO.Compression.CompressionLevel]::Optimal, $true)
    Copy-Item $tmp $to -Force
}
$walletZip = Join-Path $out "ruckcoin-wallet.zip"
Zip-Dir $wdir $walletZip

# --- linux node zip ---
if (-not $LinuxBinDir) {
    $unc = "\\wsl$\Ubuntu-24.04\tmp\ruck-rel\linux"
    if (Test-Path (Join-Path $unc "ravend")) { $LinuxBinDir = $unc }
}
if (-not $LinuxBinDir -or -not (Test-Path (Join-Path $LinuxBinDir "ravend"))) {
    Write-Warning "No stripped Linux ravend found. Linux zip will be skipped. Run strip first."
    $linuxZip = $null
} else {
    $ldir = Join-Path $stage "ruckcoin-linux-x86_64"
    New-Item -ItemType Directory -Force -Path $ldir | Out-Null
    Copy-Item (Join-Path $LinuxBinDir "ravend") $ldir
    Copy-Item (Join-Path $LinuxBinDir "raven-cli") $ldir
    Copy-Item (Join-Path $root "contrib\ruck.conf.example") $ldir
    Copy-Item (Join-Path $root "contrib\pack-linux\ruckd") $ldir
    Copy-Item (Join-Path $root "contrib\pack-linux\ruck-cli") $ldir
    Copy-Item (Join-Path $root "contrib\pack-linux\README.txt") $ldir
    $linuxZip = Join-Path $out "ruckcoin-linux-x86_64.zip"
    Zip-Dir $ldir $linuxZip
}

# --- checksums ---
$sumFile = Join-Path $out "SHA256SUMS.txt"
$lines = @()
$lines += "# RuckCoin downloads. Verify with: Get-FileHash -Algorithm SHA256 <file>"
$lines += "# Official: this site and https://github.com/madeagle100/RuckCoin"
$lines += "# Public network is not open. These are practice binaries."
$lines += ""
Get-ChildItem $out -File | Where-Object { $_.Name -ne "SHA256SUMS.txt" -and $_.Extension -ne ".md" } | Sort-Object Name | ForEach-Object {
    $h = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower()
    $lines += "$h  $($_.Name)"
}
$lines | Set-Content -Path $sumFile -Encoding ascii
Write-Host "Wrote:"
Get-ChildItem $out | Format-Table Name, Length
Get-Content $sumFile
