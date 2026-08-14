#!/bin/bash
set -euo pipefail
D=/root/.ruck
BIN=/root/src/ruckcoin/src
CONF=$D/raven.conf

mkdir -p "$D"
grep -q '^bypassdownload=' "$CONF" 2>/dev/null || echo 'bypassdownload=1' >> "$CONF"
if ! grep -q '^server=1' "$CONF"; then
  cat >> "$CONF" << 'EOF'
server=1
listen=1
daemon=1
txindex=1
addressindex=1
assetindex=1
port=8867
rpcport=8866
rpcuser=ruck
rpcpassword=ruckdev
rpcallowip=127.0.0.1
rpcbind=127.0.0.1
bypassdownload=1
EOF
fi

if ! pgrep -x ravend >/dev/null; then
  "$BIN/ravend" -datadir="$D"
  sleep 3
else
  "$BIN/raven-cli" -datadir="$D" stop || true
  sleep 3
  "$BIN/ravend" -datadir="$D"
  sleep 3
fi

"$BIN/raven-cli" -datadir="$D" getblocktemplate '{"rules":["segwit"]}' | head -c 400
echo
