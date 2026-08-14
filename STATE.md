# RuckCoin — project state

Last updated: 14 August 2026  
Repo: https://github.com/madeagle100/RuckCoin  
This file is the handoff. Read it before changing the chain, the site, or the wallet.

---

## What this is

RuckCoin (ticker **RUCK**) is an independent mineable coin. It is a **code fork** of Ravencoin (Bitcoin lineage), **not** a Ravencoin chain split and **not** an airdrop to RVN holders.

- Coins are created only by proof-of-work mining.
- No premine, no ICO, no team allocation, no masternodes, no staking.
- Named **assets** work on the same chain (inherited from Ravencoin).
- Addresses start with **K**. Ravencoin starts with **R**. They do not mix.
- You do **not** need cash to launch. A DEX pool is optional and later.

Nobody “owns” the notebook. Each node keeps a copy. Copies stay aligned by the same rules and the most-work chain. A website or wallet anyone else builds cannot move coins without keys. The official front door is this repo + the site we published.

---

## Where we are

| Phase | Name | Status |
| --- | --- | --- |
| 0 | Private test chain | **Done** |
| 1 | Public record (site, paper, timeline) | **Done** |
| 2 | Wallet people can use + explorer + one-click start | **Done** |
| 3 | Public launch at height 0 | **Not started** |
| 4 | Extra seeds / public explorer / GPU docs | Only if people show up |
| 5 | Markets | Optional, later |

**This test chain is not the public coin.** The builder wallet holds mined test RUCK. Those coins must **not** carry over. Public launch is a fresh **height 0** with no spendable premine. Skipping that reset breaks the white paper.

---

## Frozen chain identity

Do not change these after people start mining the **public** chain. Source of truth: `doc/LAUNCH_SPEC.md` and `src/chainparams.cpp`. If they disagree, running consensus code wins.

| Item | Value |
| --- | --- |
| Name / ticker | RuckCoin / RUCK |
| Magic | `RUCK` (`0x52 0x55 0x43 0x4b`) |
| P2P / RPC | 8867 / 8866 |
| Address / script | version 45 → `K` / version 107 → `k` |
| BIP44 (unofficial) | 1776 |
| PoW | Genesis identity X16Rv2; **KAWPOW** after that |
| Block time | ~60 seconds |
| Subsidy | 5,000 RUCK |
| Halving | every 2,100,000 blocks (~4 years) |
| Max supply | 21,000,000,000 |
| Assets | on from block 1 |
| Datadir | `%APPDATA%\Ruck` (Windows), `~/.ruck` (Linux) |
| Config / pid | `ruck.conf` (fallback `raven.conf`) / `ruckd.pid` |
| URI / user agent | `ruck:` / `/RuckCoin:…/` |
| Test genesis time | `1786665600` (14 Aug 2026 00:00:00 UTC) |
| Test genesis nonce | `17493341` |
| Test genesis hash | `000000862510f4b80dc2ecd874b5603917424b9289d26d14e0f63e70e9cc9a50` |

Burn amounts: issue 500, reissue/sub/channel 100, unique 5, qualifier 1000, restricted 1500, tag 0.1. Addresses are in `doc/LAUNCH_SPEC.md`.

---

## Live private test node (this PC)

One node. Not a public network. Do **not** put RPC passwords, the test miner address, or wallet balances on the public site.

| Piece | Where |
| --- | --- |
| Windows product tree | `C:\Users\270de\ruckcoin` (git `master`) |
| WSL build / running binary | Ubuntu-24.04: `/root/src/ruckcoin/src/ravend` |
| Datadir (wallet + blocks) | `/home/ruck/.ruck` |
| Config | `/home/ruck/.ruck/ruck.conf` (copied from `raven.conf`) |
| P2P / RPC | `127.0.0.1:8867` / `127.0.0.1:8866` |
| Last verified height | **337** (grew if mining continued) |
| Last verified spendable | ~1.18M RUCK + ~500k immature (test coins only) |
| Test assets issued | `TEST_RUCK`, `TEST_RUCK!`, later `PHASE226206` |
| Miner / funded address (test only) | `KEPRbPbSLRbS3r6VaaXxH1MizfB9b97cc7` |
| Wallet UI | http://127.0.0.1:8870/ |
| Public site (local) | http://127.0.0.1:8765/ |
| Qt | Built as `/opt/ruck/raven-qt`; **does not show** a usable window on this desktop (WSLg). Do not rely on it. |

RPC is localhost only. Do not publish credentials. Do not copy `/home/ruck/.ruck` onto the Desktop or OneDrive (keys).

Two source trees existed during the work: Windows `C:\Users\270de\ruckcoin` is the product repo. WSL `/root/src/ruckcoin` is the compiled node (started from an earlier commit, with rebrand files copied in for rebuilds). After consensus-sensitive edits, copy to WSL and rebuild `ravend` / `raven-cli` there.

---

## What we built (in order)

### Independent chain (Phase 0)

- Forked current Ravencoin Core; new magic, ports, datadir, `K` addresses, new burn addresses, new genesis.
- Ubuntu 24.04 / WSL2 build: Berkeley DB 4.8, Boost 1.83 connection fix, lockedpool include fix.
- GBT needed `-bypassdownload` when solo.
- Stratum: kralverde proxy + kawpowminer CUDA. Proxy patched for address version **45** and BIP34 `OP_1` at height 1.
- Easy DGW + fast GPU can hit `time-too-old` if blocks come faster than one per minute.
- Smoke: send 25 RUCK, issue `TEST_RUCK`.
- User-facing rebrand **without** touching consensus: `ruck.conf` + `raven.conf` fallback, `ruckd.pid`, help/RPC/Qt strings, `ruckd` / `ruck-cli` wrappers. Did **not** change genesis, magic, ports, rewards, address version, or signed-message magic (`Raven Signed Message:\n`).
- Binaries still named `ravend` / `raven-cli` / `raven-qt` (upstream build system).

### Public record (Phase 1)

- Site in `website/` — field-manual look, honest “private test, nothing to buy.”
- Pages: home, how it works, white paper, timeline, veterans, wallet download, look-up, spec, FAQ.
- White paper v1.1: `whitepaper/ruckcoin-whitepaper.md` and `website/paper.html`.
- Timeline: `whitepaper/timeline.md` and `website/timeline.html`.
- Public site does **not** list RPC passwords, WSL paths, test balances, or the miner address.

### Veterans policy (option A)

- **Not** a protocol tax. **Not** a cut of fees or of the 5,000 block reward.
- **Not** locked until a price or “the coin grows.”
- At **public** launch: one address on `website/veterans.html`.
- Official wallet: optional donate, **off** unless the user turns it on.
- Outflows get a public txid on that page.
- Until the address is printed there, there is **no** official fund. Do not send to collectors.

### Wallet (Phase 2)

- Local app: `wallet/ruck-wallet.py` + `wallet/static/` on **127.0.0.1:8870** only.
- Talks to the local node. Never phones home. No Google font CDN.
- First-timer copy: address as a mailbox, K vs R, sends have no undo.
- Tabs: Home, Receive, Send, Activity, Look up, Assets (create + send), Mine (optional, explained first), Settings.
- Offline switch: `setnetworkactive false` so the **node** also stops talking to peers. Address and last-known balance still work; new incoming payments and a send the other person can see wait until online.
- Settings store in `%APPDATA%\Ruck\wallet-ui.json` (or `~/.ruck/wallet-ui.json`).
- Download zip: `website/downloads/ruckcoin-wallet.zip`.
- Needs Python 3 and a running node. Not a full air-gapped PSBT signer.

### Explorer

- Wallet **Look up** tab and `website/explore.html` (calls the wallet API).
- Accepts block height, 64-char id (tx or block), or `K` address.
- Verified: height 337, genesis → block 0, funded K address.

### One-click start

- Desktop: `RuckCoin\0 Start RuckCoin.bat` → `contrib/start-all.ps1` (start node, wait, open wallet).
- Also `wallet/Start RuckCoin.bat` in the zip.

### Desktop folder

`C:\Users\270de\OneDrive\Desktop\RuckCoin` (junction from `C:\Users\270de\Desktop\RuckCoin`).

| Item | Role |
| --- | --- |
| `START HERE.txt` | Map |
| `0 Start RuckCoin.bat` | Node + wallet |
| `1 Open Website.bat` | Site on :8765 |
| `2 Open Wallet.bat` | Wallet on :8870 |
| `3` / `4` / `6` | Node start / status / stop |
| `5 Mine RuckCoin.bat` | GPU miner via `contrib/test-node.ps1 mine` |
| `website` / `papers` / `source` | Junctions into the repo |

Old loose desktop bats live in `old-shortcuts\`.

---

## How the network works (decided, for later readers)

- Every user who wants to participate runs **their own** node. They do not mine on this home PC.
- The live node here is the **private test** copy, not the world’s mining server.
- **Seeds** are optional receptionists so strangers can find the first peer. Not required for friends-only. Not required today. Two or three VPS later only if the coin is public and the first door must stay up.
- Compatible third-party wallets/sites can exist. Phishing sites can too. Official = this genesis + this repo + links we publish. Never ask for seed words.

---

## What we will not do

- Call the test wallet the public chain.
- Premine, ICO, masternodes, staking, built-in veterans tax, lock-the-fund-until-price.
- Promise a listing, a price, or “three servers required.”
- Put the live `wallet.dat` / `.ruck` datadir on OneDrive.

---

## Next (Phase 3 — only when we want strangers)

1. Publish a UTC start time.
2. New height-0 genesis (or a documented reset so **no** prior spendable test coin exists).
3. Tag source + binaries (at least Linux).
4. Site + GitHub show the same genesis hash.
5. Print the veterans address on `website/veterans.html`.
6. One honest public seed **if** we will keep it up. More only if people come.

Until then: keep one local test node. Mine, send, look up, and issue on this machine only.

---

## Important files

| Path | What |
| --- | --- |
| `doc/LAUNCH_SPEC.md` | Frozen identity and burns |
| `whitepaper/ruckcoin-whitepaper.md` | Paper v1.1 |
| `whitepaper/timeline.md` | March route |
| `website/` | Public site |
| `wallet/` | Official local wallet |
| `contrib/test-node.ps1` | start / stop / status / mine |
| `contrib/start-all.ps1` | One-click node + wallet |
| `contrib/ruckd`, `contrib/ruck-cli` | Wrappers |
| `src/chainparams.cpp` | Consensus / genesis |
| `src/util.cpp` | `ruck.conf` + `raven.conf` fallback |

---

## Git note

Product work lives on `master` in `C:\Users\270de\ruckcoin`. Untracked leftovers (not required): `contrib/build-qt.sh`, `run-build.sh`, `watch-build.sh`, desktop screenshots.
