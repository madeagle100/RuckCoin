#!/bin/sh
# Start the wallet. Start a node first (./ruckd from the Linux pack).
cd "$(dirname "$0")"
echo "Opening the RuckCoin wallet at http://127.0.0.1:8870/"
echo "Leave this terminal open."
python3 ruck-wallet.py
