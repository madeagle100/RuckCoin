# RuckCoin launch spec (draft)

Draft launch identity. The values below currently identify the disposable public-test chain. Keep that test chain available for testing, but publish and verify a final production manifest before a real launch. Do not change production consensus values after people start mining the production chain.

## Do you need your own cash?

**No. You do not need to put money in to launch RuckCoin.**

This is a mineable proof-of-work coin, like Ravencoin:

- Coins are created when someone mines a block.
- There is no premine, no ICO, and no team allocation.
- Nodes, the wallet, and mining do not require a DEX pool.

The “$5k–$15k of your own cash” line in the plan is **optional and later**. It only applies if, after the chain is alive and people want to *trade* RUCK on a DEX, you personally want to seed a wrapped-RUCK / USDT (or ETH) pool. That cash would be yours, because a fair-mined coin has no unsold tokens sitting around to dump into liquidity.

| When | Cash needed |
| --- | --- |
| Launch the chain, wallets, seeds, explorer, GPU mining | **$0** (plus whatever you already pay for VPS, if any) |
| First DEX trading pair, if you ever want one | Optional **$5k–$15k** of *your* money, after launch |
| Protocol asset burns | Automatic, paid by whoever issues an asset |

Skip the DEX until there is a real reason. Launch does not depend on it.

## Chain identity

| Item | Value |
| --- | --- |
| Name | RuckCoin |
| Ticker | RUCK |
| Algorithm | Genesis X16Rv2; KAWPOW from 1 second after genesis |
| Block time | 1 minute |
| Block reward | 5,000 RUCK |
| Halving | every 2,100,000 blocks (~4 years) |
| Max supply | 21,000,000,000 RUCK |
| Premine | none |
| P2P port | 8867 |
| RPC port | 8866 |
| Magic | `RUCK` (`0x52 0x55 0x43 0x4b`) |
| Address prefix | **`K`** (version 45). Not compatible with Ravencoin `R` addresses. |
| Script prefix | `k` (version 107) |
| BIP44 coin type | 1776 (unofficial) |
| Genesis time | 1786665600 (2026-08-14 00:00:00 UTC) |
| Genesis nonce | 17493341 |
| Genesis hash | `000000862510f4b80dc2ecd874b5603917424b9289d26d14e0f63e70e9cc9a50` |
| Data directory | `%APPDATA%\Ruck` (Windows), `~/.ruck` (Linux) |

**Never send Ravencoin (RVN) to a `K…` address, and never send RUCK to an `R…` Ravencoin address.**

## Economics (frozen)

- Year-1 emission if blocks stay on schedule: about 2.6 billion RUCK.
- Liquidity at launch: none. There is no RUCK until it is mined.
- Consensus burns (automatic, when someone uses assets):

  | Action | Burn |
  | --- | --- |
  | Issue asset | 500 RUCK |
  | Reissue / sub-asset / channel | 100 |
  | Unique | 5 |
  | Qualifier | 1000 |
  | Sub-qualifier | 100 |
  | Restricted | 1500 |
  | Tag | 0.1 |

- Extra scheduled “supply burns”: none.
- Optional later: a published foundation address may burn 25–50% of *its own inflows* once per quarter, with a txid. That is not consensus and is not required for launch.

## Burn addresses (unspendable)

| Use | Address |
| --- | --- |
| Issue asset | `KVUdNCN27k6K9nQZMoP3oH4Lu9G5RZK3Ui` |
| Reissue | `KLXEKc36VJzFDAHp1iknodm8fGCDLtjLk9` |
| Sub-asset | `KN2d83sgWNUBVoMie4M3gfprPgjMJqkKkH` |
| Unique | `KTLtFJXxuCAmavuF6nm7TVZpD54TLEN8mV` |
| Message channel | `KDuMvtTY8nGY9sTttYYaGN82xk7nhGbL13` |
| Qualifier | `KLQhZi9xxvK4rRCj912NG2jTLavFcnMRZS` |
| Sub-qualifier | `KWEwQoGRqEvYH4cAXmom9rCaEXpZiffVES` |
| Restricted | `KRQiWua21ciB6af8jNjdWMm777qA4HoYmy` |
| Tag | `KQaccmhNwTjCZxn3DPAPjzMXQ1TKxN7bgx` |
| Global burn | `KAf8usFDdmMQJ1yoxnvo9AFnDkKeA1bYi1` |

## Not in the protocol

No masternodes, no built-in veterans payout, no staking, no scheduled supply burn, no DEX, no premine.

Veterans support is **option A** (social, not consensus):

- One published address at public launch, listed on `website/veterans.html`.
- Official wallet may offer an optional donation (off by default).
- No fee tax, no block-reward skim, no lock until a price or “the coin grows.”
- Outflows to real aid get a public txid. Until the address is on the site, there is no official fund.

## Network posture

**One home seed for the public test.** Strangers connect with `addnode=seed.ruckcoin.org:8867`. RPC stays on localhost with a password you choose — never publish RPC user/password.

When you add more seeds later: 2–3 VPS, open 8867, put hostnames in `vSeeds`, rebuild. A single home PC will go down.

## Security (ported from 2Miners Ravencoin 4.6.1.1-hf1)

- KAWPOW header `nHeight` must equal the block's real chain height (`bad-blk-height`). Enforced from the first KAWPOW block. Ravencoin's 4,487,775 checkpoint is **not** used.
- Asset and restricted-asset DBs wipe on `-reindex-chainstate` as well as full `-reindex`.
- Client version **4.6.1.1**. Existing honest test blocks already set `nHeight` correctly; no new genesis required for this patch.

## Still TODO before a production announcement

Public site, paper, timeline, wallet UI, local explorer: done. Stranger packs: wallet zip (all OS) + Linux node zip + Start/Mine pages. Preserve the current test blocks, wallets, and coins while testing continues. Still needed for launch day: a final production identity that cannot reconnect to test history, a clean production datadir, tagged GitHub Release, reproducible binaries, public explorer, multiple independent seeds, and the final public policy addresses. See [EXCHANGE_RELEASE_CHECKLIST.md](EXCHANGE_RELEASE_CHECKLIST.md).
