# RuckCoin White Paper

**A fair-launch, mineable coin for sending value and issuing assets.  
Built to serve veterans in the open, not through a hidden premine.**

Version 1.0 · 14 August 2026  
Ticker: **RUCK** · Network: independent (not Ravencoin, not Bitcoin)

This paper is written for a regular reader first. Technical notes are marked as such. If a sentence uses a jargon word, the [glossary](#16-glossary) at the end explains it.

---

## 0. Read this first

**RuckCoin is not a public network yet.**

A working test chain exists on one local computer. Blocks have been mined, coins have been sent, and a test asset has been issued. That test wallet belongs to the builders. Those test coins will **not** be the public supply.

When RuckCoin opens to the public, it will start again at **height 0** (the first block). Nobody gets a head start. There is no premine, no ICO, no founder allocation, and nothing to buy from the project.

Until that public start is announced on this site and in the source repository, **do not send money to anyone promising RUCK.** There is no official sale.

---

## 1. In one page

RuckCoin is a cryptocurrency you **mine**, not buy from us.

It is a code fork of [Ravencoin](https://github.com/RavenProject/Ravencoin), which itself comes from Bitcoin. A code fork means we copied the software and started a **new, separate network**. It is not a split of the Ravencoin chain. Ravencoin coins (RVN) and RuckCoin coins (RUCK) are different. They do not mix.

What you can do with it, once it is public:

1. **Hold and send RUCK** — the native coin, created only by mining blocks.
2. **Issue assets** — named tokens on the same chain (a ticket, a membership, a share of a project, a unique item). Issuing an asset burns a fixed amount of RUCK so names stay scarce.
3. **Message and vote** (same tools Ravencoin already has) — optional extras for people who issue assets.

What you cannot do, by design:

- You cannot get coins from a premine or a team wallet at genesis.
- You cannot stake. There are no masternodes.
- You cannot send RUCK to a Ravencoin `R…` address, or RVN to a RuckCoin `K…` address. They are different formats on purpose.

**Why “Ruck.”** A ruck is the pack you carry. The project’s social aim is to support veterans — with a published donation address and open books *after* launch, not with a hidden stash of coins minted at the start. That support is a **promise we will be judged on**, not a rule baked into every block.

**Money rules (frozen):**

| Rule | Value |
| --- | --- |
| Ticker | RUCK |
| How new coins appear | Proof-of-work mining only |
| Block time | about 1 minute |
| Block reward | 5,000 RUCK |
| Halving | every 2,100,000 blocks (~4 years) |
| Max supply | 21 billion RUCK |
| Year-1 issuance if on schedule | about 2.6 billion RUCK |
| Premine / ICO / team cut | none |
| Address style | starts with **K** |
| Mining algorithm | KAWPOW (after a short X16Rv2 genesis) |
| Assets | on from block 1 |

---

## 2. Why this exists

Most new coins start with a story and a sale. Someone mints a large pile, keeps a cut, and asks the public to buy the rest.

RuckCoin starts the other way around, the same way Bitcoin and Ravencoin did:

- The software is open source.
- Coins come out of the ground when someone spends electricity and hardware to find the next block.
- The first people who have coins are the people who mined them, after the public start.

We forked Ravencoin instead of writing a chain from scratch because Ravencoin already solved the hard part we want: **a Bitcoin-style ledger that understands assets**. Bitcoin is cash. Ravencoin is cash plus “who owns this named thing.” RuckCoin keeps that, on its own network, with its own name, ports, and addresses, and with a public commitment to veterans that is social and auditable — not a protocol backdoor.

If we had put a veterans tax or a team wallet into genesis, you would have to trust us forever. We refused that. Veterans support, if it is real, will be a published address, public inflows, and (optionally) public burns of a stated share of *those* inflows. You will be able to check the chain.

---

## 3. What RuckCoin is, and what it is not

### It is

- A **peer-to-peer** network. You run software. You do not need a company account.
- **Proof of work.** Miners compete to add the next block. The network follows the chain with the most work.
- **UTXO-based**, like Bitcoin. Your wallet holds unspent outputs, not an account balance inside a smart contract.
- **Asset-aware.** The node itself knows about named assets. You cannot accidentally destroy an asset by spending the coin the way you can on some “tokens bolted onto Bitcoin” systems.
- **Fair issuance.** 21 billion RUCK, released on a known schedule, no founder pile.

### It is not

- A Ravencoin clone that talks to Ravencoin peers. Magic bytes are `RUCK`. Ports are 8867 (P2P) and 8866 (RPC). The networks cannot confuse each other.
- An Ethereum-style smart-contract platform. You do not write Solidity. You issue assets with built-in rules.
- A security offering, a share of a company, or an investment contract from the project. This paper describes software and a public network plan. It is not a prospectus.
- Live on the public internet as of this version. See section 12.

### Veterans, said plainly

The protocol does **not**:

- mint coins for a veterans fund at genesis,
- skim a percent of every block,
- or lock a master key that we control.

The project **will**, after public launch:

- publish one donation address,
- say what that address is for,
- and if we later burn part of what that address receives, publish the transaction id.

If we fail at that, you will be able to see it. That is the point.

---

## 4. How a coin is created

Imagine a notebook that many people keep a copy of. Every minute or so, someone is allowed to add a new page. That page is a **block**. It contains:

- transfers people broadcast (Alice pays Bob 25 RUCK),
- asset actions (issue `TICKET`, send 1 `TICKET`),
- and a special first line — the **coinbase** — that creates 5,000 new RUCK for the miner who found the page.

To be allowed to add the page, a miner must solve a hard puzzle (proof of work). The puzzle is designed so that, on average, someone in the world finds an answer about once a minute. If miners join and the answers start coming too fast, the puzzle gets harder. If they leave, it gets easier. That adjustment is automatic.

**KAWPOW** is the puzzle RuckCoin uses after genesis. It is the same family Ravencoin uses today. It is meant to be mined with ordinary GPUs, not to hand the chain to a single chip design on day one. The very first block (genesis) is identified with X16Rv2; every block after that is KAWPOW.

You do not need to mine to *use* RuckCoin. You only need to mine if you want new coins to come into existence in your wallet, or if you want to help secure the network.

There is no “generate” button that prints coins without work. If a website offers you RUCK for a card payment before public launch, it is not us.

---

## 5. Supply and money rules

These numbers are **frozen**. Changing them after people mine would break trust and, in most cases, split the chain.

### Emission

- Block 1 through 2,099,999: **5,000 RUCK** per block.
- Then the reward halves, and halves again every 2,100,000 blocks.
- If blocks stay near one minute, a halving is about every four years.
- The curve stops at **21,000,000,000 RUCK**.

If the chain stays on schedule, the first year creates about **2.6 billion** RUCK. That is a lot of units on purpose: fees and asset burns can stay in whole numbers that feel usable, the same reason Ravencoin picked a large supply.

### Burns (coins that go away)

Some actions cost RUCK that is sent to an **unspendable burn address**. Nobody, including us, can spend those outputs. That is how asset names stay costly to squat.

| Action | RUCK burned |
| --- | ---: |
| Issue a new asset name | 500 |
| Reissue, sub-asset, or message channel | 100 |
| Unique asset | 5 |
| Qualifier | 1,000 |
| Restricted asset | 1,500 |
| Tag | 0.1 |

There is **no extra scheduled supply burn** in the protocol. We will not “surprise burn” the money supply from a privileged key.

Optional later: a published foundation address may burn 25–50% of *its own incoming donations* once a quarter, with a public transaction id. That only affects coins people chose to send there.

### What this means in a kitchen-table sentence

New RUCK is created only when a block is mined. Some RUCK is destroyed when people create assets. Nobody is allocated coins at the start.

---

## 6. Addresses, and why they start with K

A RuckCoin **payment address** is a short string that starts with **`K`**.

Example shape (do not send to this; it is a format example):

`KEPRbPbSLRbS3r6VaaXxH1MizfB9b97cc7`

Ravencoin addresses start with **`R`**. We changed the version byte on purpose so a tired person, or a confused exchange, is less likely to mix the two.

**Never:**

- send Ravencoin (RVN) to a `K…` address,
- send RuckCoin (RUCK) to an `R…` address,
- type an address from memory if you can copy it,
- trust an address a stranger DMs you.

Script (pay-to-script) addresses on RuckCoin start with **`k`**.

The unofficial BIP44 coin type is **1776**. That only matters to wallet developers who derive keys from a seed.

**Signed messages** still use the inherited Ravencoin message magic so we did not silently break a compatibility detail inside the software. Everyday users can ignore this.

---

## 7. Assets: named things on the same chain

RUCK is the native coin. An **asset** is a name you create on the chain, with a quantity you choose.

Examples of what an asset *can* represent. The chain does not enforce the real-world meaning. The issuer does, and the law in your country still applies.

- A ticket: `SHOW/SEAT-14A`
- A membership: `VFW_POST_12`
- A unique item: `ART/MONA` (only one exists)
- A share of a small project, where that is legal
- An in-game item that can leave the game

### Why not just use Ethereum tokens?

On Ethereum, a token is a contract. Contracts can have the same display name. Users have to check a long hash. A buggy contract can freeze or mint.

On RuckCoin (as on Ravencoin):

- **Names are unique.** The first valid issue of `NAME` owns that name.
- The **node understands** the asset. Wallets can refuse to destroy it by accident.
- Rules are the protocol’s rules, not a one-off program.

### Kinds of assets (plain language)

| Kind | What it is | Typical burn |
| --- | --- | ---: |
| Main asset | `NAME` — a fungible token | 500 RUCK |
| Sub-asset | `NAME/CHILD` | 100 |
| Unique | `NAME#ITEM` — only one | 5 |
| Message channel | talk to holders | 100 |
| Qualifier / restricted / tags | extra rules for who can hold | 1,000 / 1,500 / 0.1 |

You can attach IPFS metadata (a document or image hash) if you want the asset to point at a file. That file lives off-chain; the hash is on-chain.

### Rewards and votes

If you issued `LEMONADE`, you can later send RUCK to every current holder in proportion, in one command. You can also issue vote tokens 1:1 to holders. These features already exist in the Ravencoin lineage. RuckCoin keeps them.

---

## 8. How this relates to Bitcoin and Ravencoin

```
Bitcoin (2009)
    └── code lineage
         └── Ravencoin (2018) — assets, 1-minute blocks, fair POW
              └── RuckCoin (2026) — new network, new name, new addresses
```

We owe the Bitcoin and Ravencoin developers the usual debt: the UTXO model, the asset layer, KAWPOW, messaging, restricted assets. RuckCoin is **not** a Ravencoin sidechain and **not** an airdrop to RVN holders.

What we changed to make it a separate coin:

- Network magic: `RUCK` (`0x52 0x55 0x43 0x4b`)
- Ports: 8867 / 8866
- Data directory: `Ruck` on Windows, `.ruck` on Linux
- Address version 45 → `K…`
- New genesis time, nonce, and hash
- Ravencoin DNS seeds, fixed seeds, and checkpoints removed
- Assets, messaging, restricted assets, and KAWPOW active from the start
- Display name, ticker, Qt id, payment URI `ruck:`

What we did **not** change, because changing them would invent a new science project:

- The UTXO and script model
- The asset consensus rules we inherited
- The idea of fair proof-of-work issuance

---

## 9. Security, in ordinary words

**Your coins are the keys in your wallet.** If someone has the seed or the `wallet.dat` and the password, they have the coins. We cannot reverse a payment.

**The chain is as honest as its work.** After public launch, a thief who wants to rewrite history must out-mine the honest network. On day one, with few miners, that is easier than it will be later. That is true of every new proof-of-work coin. Treat early blocks as a new, thin wall — not as Bitcoin.

**Do not announce a public network from one home PC.** A single node is a test. A public coin needs published binaries, more than one seed, and a start time people can verify.

**RPC passwords on the test node are for localhost only.** They are not a production secret.

---

## 10. What we refuse to put in the protocol

These are not coming later as a “surprise upgrade”:

- Premine or instamine for founders
- ICO, private sale, or “strategic allocation”
- Masternodes
- Staking
- A built-in veterans tax on every block
- A hidden genesis wallet
- A scheduled supply burn from a privileged key
- A DEX inside the base protocol

A DEX *listing*, much later, would be a normal market thing other people (or we, with our own cash) might do. It is not required to launch. Launch costs no treasury. Coins do not exist until they are mined.

---

## 11. How you will use it (when public)

**Run a node.** The programs are still built as `ravend` / `raven-cli` / `raven-qt` because that is the upstream build system. The wrappers are `ruckd` and `ruck-cli`. Config file: `ruck.conf` (an old `raven.conf` in the same folder still works).

**Wallet.** On the test machine, Linux Qt did not show a window under WSLg. A small local page is the working view today. A real public wallet (desktop, then whatever people actually use) is a launch requirement, not a nice-to-have.

**Mine.** GPU miners that speak KAWPOW / stratum can point at a RuckCoin node the same way they point at Ravencoin, once the public ports and a pool or solo path are published. Test mining already worked on the local node.

**Issue an asset.** When the public chain is up, `issue NAME 1000` (and the GUI equivalent) burns 500 RUCK and creates the name.

Exact command lists belong in the repository docs, not in this paper, so we do not freeze typos here.

---

## 12. Public launch rule

The current test chain has a known genesis:

- Time: 1786665600 (14 August 2026, 00:00:00 UTC)
- Nonce: 17493341
- Hash: `000000862510f4b80dc2ecd874b5603917424b9289d26d14e0f63e70e9cc9a50`

That chain was used to prove mining, sends, and assets. The builder wallet on that chain holds mined test coins. **Those coins are not a premine of the public coin. They will not carry over.**

Public launch means:

1. A published **height-0** start (new genesis clock, or a clearly documented reuse of this genesis *only if* the test wallet is emptied and the chain is reset so no prior spendable coin exists).
2. Tagged source and binaries.
3. This website and the GitHub repository stating the same start time.
4. At least the seed story we commit to that day (one honest seed is better than five fake ones; more seeds only if the coin actually has miners).

If we ever skip the reset and call the test wallet “the public chain,” treat that as a broken promise. This paragraph exists so you can hold us to it.

---

## 13. Timeline (summary)

Full dates and exit criteria live in [timeline.md](timeline.md) and on the website.

| Phase | Name | Status |
| --- | --- | --- |
| 0 | Private test chain | Done (August 2026) |
| 1 | Public record (this site, this paper) | Now |
| 2 | Wallet people can actually use + local explorer | Next |
| 3 | Public launch day (height 0) | After phase 2 |
| 4 | Seeds, public explorer, miner docs | Only if people show up |
| 5 | Optional markets (DEX) | Later, only with a real reason |

We will not invent a listing date or a price. Those are not ours to promise.

---

## 14. Technical appendix

For implementers. Ordinary readers can skip this.

| Item | Value |
| --- | --- |
| Source | https://github.com/madeagle100/RuckCoin |
| Upstream | Ravencoin Core (Bitcoin lineage), master as of August 2026 |
| P2P magic | `0x52 0x55 0x43 0x4b` (“RUCK”) |
| P2P port | 8867 |
| RPC port | 8866 |
| Pubkey address version | 45 (`K`) |
| Script address version | 107 (`k`) |
| BIP44 coin type | 1776 (unofficial) |
| Genesis algorithm identity | X16Rv2 |
| Ongoing PoW | KAWPOW |
| Block interval target | 60 seconds |
| Subsidy | 5,000 * COIN, halving interval 2,100,000 |
| Max money | 21,000,000,000 * COIN |
| Payment URI | `ruck:` |
| Default datadir | `%APPDATA%\Ruck` / `~/.ruck` |
| Default conf | `ruck.conf` (fallback `raven.conf`) |
| Default pid | `ruckd.pid` |
| Client user agent | `/RuckCoin:…/` |

**Burn addresses (unspendable):**

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

Note: confirm burn addresses against `src/chainparams.cpp` and `doc/LAUNCH_SPEC.md` before relying on this table in production tooling. If they ever disagree, the running consensus code wins.

---

## 15. Risks (said without marketing)

- **New networks die.** Most never get a second miner.
- **Early hash rate is low.** Reorgs and attacks are cheaper at the start.
- **Software has bugs.** This is a fork of a large C++ codebase. We have already had to fix build and mining-edge issues on the test node.
- **No liquidity.** There is no official market. If someone offers you a price, that is them, not the protocol.
- **Legal.** Issuing an asset that is a security, a gambling chip, or a fraud in your country is still illegal. The chain will not save you.
- **Veterans outcome is social.** If we do not publish the address and the flows, we failed a promise, not a consensus rule.

---

## 16. Glossary

**Asset** — A named token on the RuckCoin chain, separate from RUCK itself.

**Block** — A page of transactions plus the proof-of-work that lets it hang off the previous page.

**Burn** — Sending coins to an address that can never spend them.

**Coinbase** — The first transaction in a block; this is how new RUCK is created.

**Consensus** — The rules every honest node uses to decide which chain is valid.

**Fork (code)** — Copying software and running a new network. Not the same as a chain split.

**Genesis** — Block 0, the first block. Everything hangs off it.

**Halving** — Cutting the block reward in half after a fixed number of blocks.

**Height** — How many blocks after genesis. Height 337 means 337 blocks on top of genesis.

**KAWPOW** — The mining puzzle used after genesis.

**Node** — A computer running the RuckCoin software and keeping a copy of the chain.

**Premine** — Coins created for insiders before the public can mine. RuckCoin does not have this on the public start.

**Proof of work** — A hard puzzle whose answer is easy to check. Used to decide who writes the next block.

**RPC** — The local command interface a wallet or miner uses to talk to your node.

**Seed node** — A published computer new peers can dial to find the rest of the network.

**UTXO** — An unspent output. Your “balance” is the sum of UTXOs your keys can spend.

---

## 17. References

1. S. Nakamoto, *Bitcoin: A Peer-to-Peer Electronic Cash System*, https://bitcoin.org/bitcoin.pdf
2. B. Fenton, T. Black, *Ravencoin* white paper (2018), included in this repository under `whitepaper/README.md`
3. Raven Project, Ravencoin source, https://github.com/RavenProject/Ravencoin
4. RuckCoin source, https://github.com/madeagle100/RuckCoin
5. RuckCoin launch spec, `doc/LAUNCH_SPEC.md`
6. T. Black, J. Weight, *X16R* algorithm paper
7. Ravencoin KAWPOW documentation (Raven Project)

---

*RuckCoin is free and open source under the MIT license, as inherited from Bitcoin and Ravencoin. This paper describes a project and a network plan. It is not an offer to sell coins.*
