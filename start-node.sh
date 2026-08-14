#!/bin/bash
set -u
LOG=/root/ruckcoin-build.log
D=/home/ruck/.ruck
BIN=/root/src/ruckcoin/src

exec > >(tee -a "$LOG") 2>&1

echo
echo "==== STARTING RUCKCOIN NODE $(date) ===="

mkdir -p "$D"
if [ ! -f "$D/ruck.conf" ]; then
  if [ -f "$D/raven.conf" ]; then
    cp "$D/raven.conf" "$D/ruck.conf"
  else
    cat > "$D/ruck.conf" << 'EOF'
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
printtoconsole=0
bypassdownload=1
EOF
  fi
fi

echo "config: $D/ruck.conf"
if pgrep -x ravend >/dev/null; then
  echo "ravend already running"
else
  "$BIN/ravend" -datadir="$D"
  echo "ravend launched"
fi

echo "waiting for RPC..."
ok=0
for i in $(seq 1 40); do
  if "$BIN/raven-cli" -datadir="$D" getblockchaininfo > /tmp/ruck-info.json 2>/tmp/ruck-err.txt; then
    echo "RPC is up"
    cat /tmp/ruck-info.json
    ok=1
    break
  fi
  err=$(tr -d '\n' < /tmp/ruck-err.txt)
  echo "  wait $i: $err"
  sleep 2
done

if [ "$ok" != 1 ]; then
  echo "RPC failed to come up"
  tail -40 "$D/debug.log" || true
  exit 1
fi

echo
echo "==== getnetworkinfo ===="
"$BIN/raven-cli" -datadir="$D" getnetworkinfo

echo
echo "==== wallet ===="
if ! "$BIN/raven-cli" -datadir="$D" getwalletinfo >/tmp/ruck-wallet.json 2>/tmp/ruck-err.txt; then
  echo "creating wallet..."
  "$BIN/raven-cli" -datadir="$D" createwallet "" || true
  "$BIN/raven-cli" -datadir="$D" getwalletinfo || true
else
  cat /tmp/ruck-wallet.json
fi

ADDR=$("$BIN/raven-cli" -datadir="$D" getnewaddress "miner" 2>/dev/null || true)
echo "miner address: ${ADDR:-none}"

if [ -n "${ADDR:-}" ]; then
  echo
  echo "==== trying one CPU block (100k tries) ===="
  "$BIN/raven-cli" -datadir="$D" generatetoaddress 1 "$ADDR" 100000 || echo "no block this round (KAWPOW is slow on CPU)"
fi

echo
echo "==== chain ===="
"$BIN/raven-cli" -datadir="$D" getblockchaininfo
echo
echo "==== DONE $(date) ===="
