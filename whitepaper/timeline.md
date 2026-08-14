# RuckCoin timeline

Last updated: 14 August 2026

This is the working calendar. Dates after Phase 1 are **windows**, not press-release promises. A phase is done only when its exit check is true.

The public website shows the same phases as a march route.

---

## How to read this

- **Now** means it is finished or in progress.
- **Next** means that is what we build after the current phase.
- **If** means we will not spend time on it until the condition is real (miners, users, a reason to trade).

We will not publish a token price, an exchange listing date, or a “guaranteed” hash rate.

---

## Phase 0 — Private test chain

**When:** 14 August 2026  
**Status:** Done

**What we did**

- Forked current Ravencoin Core into an independent network.
- New magic (`RUCK`), ports (8867 / 8866), `K` addresses, burn addresses, genesis.
- Built and ran a node on Ubuntu in WSL.
- Mined blocks with KAWPOW (local GPU + stratum path).
- Sent RUCK and issued a test asset (`TEST_RUCK`).
- Rebranded what people see (`ruck.conf`, `ruckd` / `ruck-cli`, RuckCoin strings) without changing consensus.

**Exit check:** A local node can mine, send, and issue an asset. Met.

**What this is not:** A public launch. The test wallet holds mined coins. Those coins do not become the public supply.

---

## Phase 1 — Public record

**When:** 14–18 August 2026  
**Status:** In progress (this document and the website)

**What we ship**

- Public-facing website that a non-technical person can read.
- This white paper (v1.0) and this timeline.
- Honest status: private test, nothing to buy.

**Exit check:** Anyone can open the site, read the paper, and see the same frozen parameters as `doc/LAUNCH_SPEC.md`.

---

## Phase 2 — A wallet people can actually use

**When:** late August – mid September 2026  
**Status:** Next

Linux Qt did not appear on the Windows desktop. The current local page only shows balances.

**What we ship**

- A local wallet UI that can show a receive address, send RUCK, and handle assets.
- A desktop shortcut that starts the node and opens that UI.
- A simple local explorer (height, txid, `K` address).
- Written miner notes for the one-node setup (already partly working).

**Exit check:** A person who is not us can receive, send, and issue an asset on the test node without using raw RPC.

---

## Phase 3 — Public launch day (height 0)

**When:** target window September – October 2026, only after Phase 2  
**Status:** Not started

**What we ship**

- A published start time (UTC).
- A chain that begins at height 0 with **no spendable premine**.
- Tagged source + binaries (at least Linux; Windows if the wallet is ready).
- The website and GitHub showing the same genesis hash.
- One honest public seed if we are willing to keep it up; more only if needed.

**Exit check:** A stranger can download software, mine or receive a first coin, and verify genesis against this site.

**Hard rule:** If we skip the reset and call the test wallet the public coin, we have broken the white paper.

---

## Phase 4 — Only if people actually show up

**When:** after Phase 3, if there is real hash rate or real users  
**Status:** If

**What we ship**

- 2–3 seed nodes (small VPS, port 8867 open). Hostnames go into `vSeeds`.
- A public explorer.
- Clear GPU / stratum instructions that do not assume our living room.
- A published veterans donation address and a one-page “how we will report inflows.”

**Exit check:** A new peer can find the network without knowing our home IP.

---

## Phase 5 — Markets (optional, later)

**When:** only after Phase 4 has a reason  
**Status:** If, and not required

There is no official DEX, CEX, or liquidity plan required to exist.

If people want to trade RUCK against something else, that can be:

- a community-run atomic swap or wrapped pair, or
- a pool someone funds with **their own** cash (the white paper’s optional $5k–$15k line).

The project will not pretend a market is part of consensus.

**Exit check:** None. Skip forever if there is no reason.

---

## What is deliberately not on the calendar

- Masternodes, staking, an ICO date
- A built-in veterans tax
- “Listing on Binance by Q4”
- A second coin, an NFT marketplace, or a mobile app before a working desktop wallet

---

## One-line calendar

| Dates | Phase |
| --- | --- |
| 14 Aug 2026 | Test chain works |
| 14–18 Aug 2026 | Website + white paper |
| late Aug – mid Sep 2026 | Wallet + local explorer |
| Sep – Oct 2026 | Public height-0 launch, if wallet is ready |
| After launch, if used | Seeds, public explorer, veterans address |
| Later, if needed | Optional market liquidity |

If a date slips, we slip the date. We do not quietly change the money rules to look busy.
