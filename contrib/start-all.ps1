# Start the local test node, wait until it answers, then open the wallet.
$ErrorActionPreference = "Continue"
$root = Split-Path $PSScriptRoot -Parent
$starter = Join-Path $PSScriptRoot "test-node.ps1"
Write-Host "Starting the RuckCoin node..."
& $starter start
$cli = "/root/src/ruckcoin/src/raven-cli -datadir=/home/ruck/.ruck getblockcount"
$up = $false
for ($i = 1; $i -le 30; $i++) {
    wsl.exe -d Ubuntu-24.04 -u root -- bash -lc $cli 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { $up = $true; break }
    Write-Host "  waiting $i..."
    Start-Sleep -Seconds 2
}
if (-not $up) {
    Write-Host "The node did not answer. Use '4 Node Status' and try again."
    exit 1
}
Write-Host "Node is up. Opening the wallet..."
Start-Process "http://127.0.0.1:8870/"
Set-Location (Join-Path $root "wallet")
python .\ruck-wallet.py
