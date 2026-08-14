# Control the single local RuckCoin test node in Ubuntu WSL.
param(
    [Parameter(Position = 0)]
    [ValidateSet("start", "stop", "status", "address")]
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
}
