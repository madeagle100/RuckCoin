#!/bin/bash
set -euo pipefail
CLI="/root/src/ruckcoin/src/raven-cli -datadir=/home/ruck/.ruck"

echo "=== send test ==="
DEST=$($CLI getnewaddress dest)
echo "dest=$DEST"
TXID=$($CLI sendtoaddress "$DEST" 25)
echo "txid=$TXID"
$CLI gettransaction "$TXID"

echo
echo "=== asset issue ==="
# name qty units reissuable has_ipfs
$CLI issue TEST_RUCK 1000 "" "" 2 false false
echo
echo "=== listmyassets ==="
$CLI listmyassets
echo
echo "=== listunspent dest ==="
$CLI listunspent 0 9999999 "[\"$DEST\"]"
echo
echo "=== wallet ==="
$CLI getwalletinfo
echo
echo "=== height ==="
$CLI getblockcount
