# Start a RuckCoin node on THIS computer, then (optionally) the wallet.
# Looks next to this script, in a sibling linux pack, or on PATH.
# Does not use the private test-node WSL paths.
param(
    [ValidateSet("start", "stop", "status")]
    [string]$Command = "start",
    [switch]$NoWallet
)

$ErrorActionPreference = "Continue"
$here = $PSScriptRoot
$dataDir = Join-Path $env:APPDATA "Ruck"
$conf = Join-Path $dataDir "ruck.conf"

function Find-WinDaemon {
    $names = @("ravend.exe", "ruckd.exe")
    $dirs = @(
        $here,
        (Join-Path $here "node"),
        (Join-Path $here "..\node"),
        (Join-Path $here "..\..\ruckcoin-windows-x64")
    )
    foreach ($d in $dirs) {
        foreach ($n in $names) {
            $p = Join-Path $d $n
            if (Test-Path $p) { return (Resolve-Path $p).Path }
        }
    }
    foreach ($n in $names) {
        $cmd = Get-Command $n -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    return $null
}

function Find-LinuxDaemon {
    $names = @("ravend", "ruckd")
    $dirs = @(
        $here,
        (Join-Path $here "node"),
        (Join-Path $here "..\ruckcoin-linux-x86_64"),
        (Join-Path $here "..\..\ruckcoin-linux-x86_64")
    )
    Get-ChildItem (Join-Path $here "..") -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "ruckcoin-linux*" } |
        ForEach-Object { $dirs += $_.FullName }
    foreach ($d in $dirs) {
        foreach ($n in $names) {
            $p = Join-Path $d $n
            if (Test-Path $p) { return (Resolve-Path $p).Path }
        }
    }
    return $null
}

function Ensure-Conf {
    if (Test-Path $conf) { return }
    New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $bytes = New-Object byte[] 18
    $rng.GetBytes($bytes)
    $pass = [Convert]::ToBase64String($bytes).TrimEnd("=") -replace "[^A-Za-z0-9]", "x"
    @"
server=1
listen=1
txindex=1
addressindex=1
assetindex=1
port=8867
rpcport=8866
rpcuser=ruck
rpcpassword=$pass
rpcallowip=127.0.0.1
rpcbind=127.0.0.1
miningrequirespeers=0
addnode=seed.ruckcoin.org:8867
"@ | Set-Content -Path $conf -Encoding ascii
    Write-Host "Created $conf with a new RPC password. The wallet will read it."
}

function Read-Rpc {
    $user = "ruck"
    $pass = ""
    if (Test-Path $conf) {
        Get-Content $conf | ForEach-Object {
            if ($_ -match '^\s*rpcuser=(.+)$') { $user = $Matches[1].Trim() }
            if ($_ -match '^\s*rpcpassword=(.+)$') { $pass = $Matches[1].Trim() }
        }
    }
    return @{ User = $user; Password = $pass }
}

function Sync-WalletCfg {
    $rpc = Read-Rpc
    $ui = Join-Path $dataDir "wallet-ui.json"
    $obj = @{
        host = "127.0.0.1"
        port = 8866
        user = $rpc.User
        password = $rpc.Password
        receive_address = ""
        veterans_address = ""
    }
    if (Test-Path $ui) {
        try {
            $old = Get-Content $ui -Raw | ConvertFrom-Json
            if ($old.receive_address) { $obj.receive_address = $old.receive_address }
            if ($old.veterans_address) { $obj.veterans_address = $old.veterans_address }
        } catch {}
    }
    ($obj | ConvertTo-Json) | Set-Content -Path $ui -Encoding utf8
}

function Get-WslPath([string]$winPath) {
    $out = & wsl.exe wslpath -a $winPath 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $out) { return $null }
    return ($out | Select-Object -Last 1).Trim()
}

switch ($Command) {
    "stop" {
        $cli = Join-Path $here "raven-cli.exe"
        if (Test-Path $cli) {
            & $cli -datadir=$dataDir stop
        } else {
            Write-Host "No raven-cli.exe here. If the node is in WSL: wsl pkill ravend"
        }
        break
    }
    "status" {
        $cli = Join-Path $here "raven-cli.exe"
        if (Test-Path $cli) {
            & $cli -datadir=$dataDir getblockchaininfo
        } else {
            Write-Host "No Windows node binary in this folder."
        }
        break
    }
    default {
        Ensure-Conf
        Sync-WalletCfg
        $win = Find-WinDaemon
        $linux = Find-LinuxDaemon
        if ($win) {
            Write-Host "Starting Windows node: $win"
            Start-Process -FilePath $win -ArgumentList "-datadir=`"$dataDir`"" -WindowStyle Minimized
        } elseif ($linux -and (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
            $wslBin = Get-WslPath $linux
            if (-not $wslBin) {
                Write-Host "Found a Linux node file but WSL could not see it: $linux"
                exit 1
            }
            Write-Host "Starting Linux node in WSL: $linux"
            Write-Host "(No ravend.exe in this folder yet. WSL runs the Linux build.)"
            $wslConf = Get-WslPath $conf
            $copyConf = ""
            if ($wslConf) {
                $copyConf = "if [ ! -f `$HOME/.ruck/ruck.conf ] && [ -f `"$wslConf`" ]; then cp `"$wslConf`" `$HOME/.ruck/ruck.conf; fi;"
            }
            $start = "mkdir -p `$HOME/.ruck; $copyConf pgrep -x ravend >/dev/null && echo already running || `"$wslBin`" -daemon -datadir=`$HOME/.ruck"
            wsl.exe -e bash -lc $start
        } else {
            Write-Host ""
            Write-Host "No node program found on this computer."
            Write-Host "Windows: put ravend.exe in this folder (when the Windows node pack is published),"
            Write-Host "         or install WSL, unzip ruckcoin-linux-x86_64 next to the wallet, and run this again."
            Write-Host "Linux:   run ./ruckd from the linux pack."
            Write-Host "macOS:   build from source (see the Start page)."
            Write-Host ""
            Write-Host "Opening the wallet anyway. It will wait until a node is running."
        }
        if (-not $NoWallet) {
            $wallet = Join-Path $here "ruck-wallet.py"
            if (-not (Test-Path $wallet)) { $wallet = Join-Path $here "..\wallet\ruck-wallet.py" }
            if (Test-Path $wallet) {
                Start-Process "http://127.0.0.1:8870/"
                Set-Location (Split-Path $wallet)
                python (Split-Path $wallet -Leaf)
            }
        }
    }
}
