RuckCoin node — Linux x86_64
============================

These programs were built on Ubuntu 24.04. They are dynamically linked.
On another distro, build from source if they will not start.

  chmod +x ravend raven-cli ruckd ruck-cli
  mkdir -p ~/.ruck
  cp ruck.conf.example ~/.ruck/ruck.conf
  # edit rpcpassword in that file
  ./ruckd -daemon
  ./ruck-cli getblockcount

P2P port 8867. RPC port 8866 (localhost only).
Public network is not open. Do not set addnode until the official site
prints a host.

Windows users: unzip this folder next to the wallet folder and use
Start RuckCoin.bat (needs WSL). There is no ravend.exe in this zip.

Checksums: website/downloads/SHA256SUMS.txt
Source: https://github.com/madeagle100/RuckCoin
