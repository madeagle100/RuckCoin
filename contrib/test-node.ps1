# Control the single local RuckCoin test node in Ubuntu WSL.
param(
    [Parameter(Position = 0)]
    [ValidateSet("start", "stop", "status", "address", "mine")]
    [string]$Command = "status"
)

$wsl = @("-d", "Ubuntu-24.04", "-u", "root", "--")
$cli = "/root/src/ruckcoin/src/raven-cli -datadir=/root/.ruck"
$d = "/root/src/ruckcoin/src/ravend -datadir=/root/.ruck"

switch ($Command) {
    "start" {
        wsl @wsl bash -lc "pgrep -x ravend >/dev/null && echo already running || ($d && echo started)"
    }
    "stop" {
        wsl @wsl bash -lc "$cli stop 2>/dev/null || pkill ravend; echo stopped"
    }
    "status" {
        wsl @wsl bash -lc "pgrep -a ravend || echo DOWN; echo; $cli getblockchaininfo 2>/dev/null | head -12"
    }
    "address" {
        wsl @wsl bash -lc "$cli getnewaddress"
    }
    "mine" {
        Start-Process python -ArgumentList "$PSScriptRoot\..\miners\ravencoin-stratum-proxy\stratum-converter.py","54325","127.0.0.1","ruck","ruckdev","8866","true" -WindowStyle Minimized
        Start-Sleep 2
        $exe = Join-Path $PSScriptRoot "..\miners\kawpowminer\kawpowminer-windows-1.2.4\kawpowminer.exe"
        Start-Process -FilePath $exe -ArgumentList "-P","stratum+tcp://KEPRbPbSLRbS3r6VaaXxH1MizfB9b97cc7.rig1@127.0.0.1:54325"
    }
}
