# RuckCoin

RuckCoin is a mineable, asset-capable cryptocurrency forked from [Ravencoin](https://github.com/RavenProject/Ravencoin) (Bitcoin code lineage). It is intended to support veterans through governance and on-chain utility.

This tree is based on Ravencoin Core 4.6.1.0 (`master` as of early 2026-08), plus the 2Miners **4.6.1.1-hf1** KAWPOW `nHeight` check and asset-DB wipe on `-reindex-chainstate`. Ravencoin mainnet checkpoints are not used. It is **not** a Ravencoin chain split.

Public site (white paper, timeline, FAQ): [website/](website/). Long form: [whitepaper/ruckcoin-whitepaper.md](whitepaper/ruckcoin-whitepaper.md). Launch identity: [doc/LAUNCH_SPEC.md](doc/LAUNCH_SPEC.md). Exchange engineers should start with [doc/EXCHANGE_INTEGRATION.md](doc/EXCHANGE_INTEGRATION.md). Future developers and AI assistants should read the sanitized [doc/STATE.md](doc/STATE.md). **You do not need to put cash in to launch** — this is a mineable chain.

The current network is a disposable public test with one best-effort seed. It is not production listing-ready, and its test balances must not carry into a future production launch. Extra independent seeds and a public explorer are production blockers. From PowerShell: `contrib/test-node.ps1 status`

## Coin parameters

| Parameter | Value |
| --- | --- |
| Name | RuckCoin |
| Ticker | RUCK |
| Algorithm | KAWPOW (X16R genesis identity) |
| Block time | 1 minute |
| Block reward | 5,000 RUCK |
| Halving | every 2,100,000 blocks (~4 years) |
| Supply | 21 billion |
| Address prefix | `K` (not Ravencoin `R`) |
| P2P port | 8867 |
| RPC port | 8866 |
| Data directory | `%APPDATA%\Ruck` (Windows), `~/.ruck` (Linux) |
| Assets | enabled from block 1 |

RuckCoin keeps Ravencoin's asset (token) layer, so you can issue and transfer assets on this chain.

## What changed from Ravencoin

- New network magic (`RUCK`) so this node will not talk to Ravencoin peers
- New ports, data directory, and BIP44 coin type (`1776`)
- New genesis timestamp and coinbase message
- Ravencoin DNS seeds, fixed seeds, and checkpoints removed
- Asset / messaging / restricted-asset / KAWPOW activation start at genesis
- Display name, ticker, Qt app id, and payment URI scheme (`ruck:`)

The build system still produces `ravend`, `raven-cli`, and `raven-qt`. Use the `ruckd` / `ruck-cli` wrappers (they call those binaries). Config is `ruck.conf` in the data directory; a leftover `raven.conf` is still read if `ruck.conf` is missing.

## Source

- Product repo: https://github.com/madeagle100/RuckCoin
- Upstream Ravencoin: https://github.com/RavenProject/Ravencoin
- GitHub fork of upstream: https://github.com/madeagle100/Ravencoin

## Build

See [INSTALL.md](INSTALL.md) and the files in [doc](doc). Typical Unix flow:

```sh
./autogen.sh
./configure
make
```

Windows users typically use the depends build or the documented MSVC / MinGW path from Ravencoin.

## License

Released under the MIT license. See [COPYING](COPYING).

RuckCoin is built on the work of the Bitcoin and Ravencoin developers.
