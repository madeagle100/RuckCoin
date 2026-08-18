# RuckCoin public AI handoff

Last updated: 2026-08-18 by OpenAI Codex.

This is a sanitized, tracked handoff for developers and future AI assistants. It contains no wallet secrets, RPC credentials, private addresses, home IPs, or operator contact details. The operator may keep a separate ignored local state file; never copy private values from it into GitHub.

## Current state

- RuckCoin is a native mineable UTXO chain, not an ERC-20/BEP-20 token.
- The running chain is a **public test**. Keep its existing blocks, wallets, and test RUCK available for continued testing with strangers and exchange engineers.
- The public-test chain is not approved for production custody, trading, deposits, or withdrawals. Its balances must not become production balances.
- Current public-test identity and integration constants live in `contrib/exchange/network-manifest.json`.
- Consensus truth remains `src/chainparams.cpp`; documentation must be corrected if it disagrees with running code.
- One best-effort test seed exists. Multiple independent seeds and a public explorer are still production blockers.
- The build emits `ravend` and `raven-cli`; public `ruckd` and `ruck-cli` wrappers exist.

## Exchange-readiness work added

- `doc/EXCHANGE_INTEGRATION.md`: RPC, deposits, withdrawals, confirmations, reorgs, upgrades, supply, test coins, and production cutover.
- `doc/EXCHANGE_RELEASE_CHECKLIST.md`: evidence-based public-test and production gates.
- `contrib/exchange/network-manifest.json`: machine-readable public-test parameters.
- `contrib/exchange/validate_node.py`: rejects node/manifest identity mismatches; `--require-production` must fail today.
- `contrib/exchange/supply.py`: exact subsidy schedule plus live UTXO/burn-based circulating upper bound.
- `SECURITY.md`: private vulnerability and exchange-emergency route.

## Validation commands

```sh
python3 -m unittest contrib/exchange/test_supply.py
python3 -m json.tool contrib/exchange/network-manifest.json
python3 contrib/exchange/supply.py --offline --height 337 --human
python3 contrib/exchange/validate_node.py --cli ./contrib/ruck-cli --datadir ~/.ruck
python3 contrib/exchange/validate_node.py --require-production --cli ./contrib/ruck-cli --datadir ~/.ruck
```

The first four commands should pass when run in the appropriate environment. The last command should fail until a reviewed production manifest explicitly sets `production_listing_ready` to true.

## Do not do

- Do not delete, reset, move, or publish the operator's test datadir or wallet.
- Do not put credentials, private keys, wallet addresses tied to the operator, or personal contact details in tracked files.
- Do not change consensus/network identity while the public test is running without a written migration plan.
- Do not call the existing test tag or website ZIPs reproducible production binaries.
- Do not claim a public explorer, redundant seed network, legal opinion, signed release, or distribution audit exists until evidence is linked.
- Do not simply toggle the public-test manifest to production. Create a reviewed final release, publish its immutable identity, and start from clean data so test UTXOs cannot carry over.

## Remaining production blockers

1. Decide and freeze the final production chain identity and cutover plan.
2. Security/code review and deterministic Linux builds with independent matching hashes.
3. Signed production tag, binaries, checksums, and build attestations.
4. Three or more independently operated seeds and a public indexed explorer/API.
5. Clean-chain deposit/withdrawal/reorg/backup/restore integration tests.
6. Snapshot-based miner/holder concentration report and final circulating-supply evidence.
7. Logo package, final white paper/site review, and a qualified lawyer's jurisdiction-specific opinion.

## Authorship and scope

The exchange-readiness package in this change was prepared by OpenAI Codex for the RuckCoin operator. Review it as engineering documentation and tooling, not as an exchange approval, security audit, or legal opinion.
