# RuckCoin exchange integration guide

> **Public-test package — not approved for deposits, withdrawals, trading, or a production listing.**
>
> The current chain and its test RUCK remain available so exchange engineers and strangers can test. Test balances have no promised value and will not carry into a future production launch.

This document describes native RUCK integration. RUCK is a mineable UTXO coin with a Ravencoin/Bitcoin code lineage; it is not an ERC-20/BEP-20 token and does not have a token contract address.

The machine-readable source of the values below is [`contrib/exchange/network-manifest.json`](../contrib/exchange/network-manifest.json). Validate a node against it before integration:

```sh
python3 contrib/exchange/validate_node.py --cli ./contrib/ruck-cli --datadir ~/.ruck
```

Adding `--require-production` deliberately fails on the current public-test manifest. A real listing must not bypass that gate.

## Network identity

| Item | Current public-test value |
| --- | --- |
| Name / ticker | RuckCoin / RUCK |
| Accounting model | UTXO |
| Decimals | 8 (1 RUCK = 100,000,000 ruckoshi) |
| P2P / RPC | 8867 / 8866 |
| Message start | `52 55 43 4b` (`RUCK`) |
| Public-test seed | `seed.ruckcoin.org:8867` (single, non-SLA seed) |
| Address versions | P2PKH 45 (`K…`), P2SH 107 (`k…`), WIF 128 |
| BIP44 | 1776, unofficial |
| URI | `ruck:` |
| Genesis hash | `000000862510f4b80dc2ecd874b5603917424b9289d26d14e0f63e70e9cc9a50` |
| Genesis merkle root | `2f92ddefe4842df446b6dc736ce3f3d837c0b3ebeb01a330b7d34172aa4b7e24` |
| Genesis time / nonce / bits | 1786665600 / 17493341 / `1e00ffff` |
| Block target | approximately 60 seconds |
| Initial subsidy | 5,000 RUCK |
| Halving interval | 2,100,000 blocks |
| Coinbase maturity | 100 blocks |

The genesis coinbase is not spendable and is excluded from issued-supply calculations. Subsidy supply starts at height 1.

## Node configuration

Use a dedicated wallet and host. Bind RPC only to a private interface, use strong unique credentials, firewall it, and never expose RPC to the internet.

```ini
server=1
listen=1
txindex=1
addressindex=1
port=8867
rpcport=8866
rpcbind=127.0.0.1
rpcallowip=127.0.0.1
rpcuser=EXCHANGE_UNIQUE_USER
rpcpassword=EXCHANGE_LONG_RANDOM_SECRET
addnode=seed.ruckcoin.org:8867
```

The build currently emits upstream executable names `ravend` and `raven-cli`; `contrib/ruckd` and `contrib/ruck-cli` are RuckCoin wrappers. An exchange must pin a reviewed source commit and verify release checksums rather than downloading an unversioned website file.

## Deposit workflow

Generate a unique address per customer/account:

```sh
ruck-cli getnewaddress "deposit-customer-123"
ruck-cli validateaddress "K..."
```

Scan incrementally and persist the last processed block hash:

```sh
ruck-cli listsinceblock "LAST_PROCESSED_BLOCK_HASH" 1 true
ruck-cli gettransaction "TXID"
ruck-cli getblock "BLOCK_HASH"
```

Process both the `transactions` and `removed` arrays returned by `listsinceblock`. Credit only ordinary RUCK outputs assigned to the exchange; do not mistake the chain's named-asset fields for base RUCK. Make all credits idempotent by `(txid, vout)`.

For the present network, use **at least 61 confirmations** for ordinary deposits and at least 101 confirmations before treating newly mined coinbase outputs as spendable. This is a starting policy, not an assurance. Pause credits when the node is behind, warnings are non-empty, fewer than four peers are connected, the public seed is the only peer, or competing tips/reorganizations are observed.

## Withdrawal workflow

Validate the destination and reject non-RuckCoin address versions:

```sh
ruck-cli validateaddress "K..."
ruck-cli sendtoaddress "K..." 12.34567890 "withdrawal-id-456"
ruck-cli gettransaction "RETURNED_TXID"
```

Use exact decimal handling—never binary floating point—and cap amounts at eight decimal places. Production systems should construct, review, sign, and broadcast withdrawals using an offline/hot-wallet policy rather than exposing an unlocked wallet to a web application. Keep hot-wallet funds limited, require human approval above a threshold, reconcile every output and fee, and suspend broadcasting under the same health conditions used for deposits.

## Reorganizations and upgrades

The current code limits automatic deep-reorganization acceptance using a 60-block depth, four-peer minimum, and 12-hour tip-age rule. Those controls do not make a one-seed/low-peer network safe: some checks depend on peer count and tip freshness. The exchange policy must therefore be stricter than consensus policy.

- Keep a rolling record of credited `(block hash, height, txid, vout)` entries.
- Reverse or freeze credits found in `listsinceblock.removed`.
- Stop deposits and withdrawals on any unexpected reorganization, peer isolation, header lag, or node warning.
- Resume only after manual review and a stable observation window.
- Treat consensus releases as coordinated maintenance: stop wallets, back up, verify signed/tagged source and checksums, stage on a test node, then resume.
- RuckCoin maintainers must publish incompatible-upgrade height/timing and rollback guidance before activation.

## Supply and distribution

Run the checked-in calculator against an indexed node:

```sh
python3 contrib/exchange/supply.py --cli ./contrib/ruck-cli --datadir ~/.ruck
```

It reports maximum subsidy emission, the live UTXO total, balances at known consensus burn addresses, and `UTXO total - known burns` as a **circulating upper bound**. That upper bound still includes immature, locked, and lost coins. It is not a claim that every reported coin is liquid.

There was no protocol premine, ICO, staking allocation, or genesis team wallet. Coins are obtained through proof-of-work or transfers. A credible production listing still needs an independently reproducible miner/holder concentration report at a named snapshot height. The current project does not claim one.

## Public-test integration coins

The operator may provide disposable test RUCK for integration testing. Request them through the Security/Integration category at <https://ruckcoin.org/report.html>; never post exchange credentials or private keys. Record the test genesis hash and never merge the test wallet/database with a future production environment.

## Production cutover requirements

Before a real listing, all parties must receive a production integration package with:

1. a final, signed source tag and immutable SHA-256 checksums;
2. independently reproducible Linux binaries and documented build provenance;
3. a final production manifest and genesis identity that cannot reconnect to this test history;
4. at least three independently operated public nodes/seeds and a public explorer/API;
5. a clean production datadir/wallet, with no test UTXOs credited;
6. current RPC compatibility tests, supply snapshot, miner/holder distribution snapshot, upgrade/reorg policy, and security contact;
7. project logo/website/white paper plus legal counsel's jurisdiction-specific opinion.

The future production identity has not been finalized. Do not relabel the existing public-test manifest as production. Publish a replacement manifest, rebuild from its tagged source, and require a clean data directory so test coins cannot carry over.

## Support and security

Technical integration questions and private vulnerability reports start at <https://ruckcoin.org/report.html>. Mark the category clearly. See [`SECURITY.md`](../SECURITY.md). Do not use a public GitHub issue for an unpatched vulnerability.
