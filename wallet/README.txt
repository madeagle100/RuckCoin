RuckCoin wallet
===============

This zip is the official local wallet. Same files on Windows, Linux, and Mac.
It talks only to a RuckCoin node on THIS computer. It does not phone home.

The public network is not open yet. These programs are for practice.

What you still need
-------------------
A node (the program that keeps the chain). That file depends on your computer:

  Windows  Wallet: this zip. Node: not a .exe yet. Use the Linux node zip
           inside Windows Subsystem for Linux (WSL), or build from source.
  Linux    This zip + ruckcoin-linux-x86_64.zip (Ubuntu 24.04, 64-bit).
  macOS    This zip + build the node from source. No Mac binary yet.

Full picture: website/run.html or the Start page on the site.

Windows
-------
1. Install Python 3 from python.org. Tick "Add python.exe to PATH".
2. Keep every file in this folder together.
3. If a node is already running:  Open Wallet.bat
4. To try starting a node + wallet:  Start RuckCoin.bat
   Put the unzipped Linux node folder next to this folder if you use WSL.

Linux
-----
1. Start the node from the Linux pack:  ./ruckd -daemon
2. In this folder:  python3 ruck-wallet.py
3. Open http://127.0.0.1:8870/

macOS
-----
1. Build ravend from the GitHub source, then run it.
2. python3 ruck-wallet.py
3. Open http://127.0.0.1:8870/

If the wallet cannot connect
----------------------------
Open Settings. Host 127.0.0.1, port 8866, same user and password as
your ruck.conf. Do not use an example password from a web page.

Safety
------
- Addresses start with K. Ravencoin starts with R. Do not mix them.
- Never type an address from memory.
- This program only listens on 127.0.0.1.
- Official files: this project’s site and github.com/madeagle100/RuckCoin.
  A different genesis hash is a different coin.
