# Exchange release checklist

This is the go/no-go checklist for a native RUCK exchange integration. The current public-test chain is intentionally preserved for testing, but it does **not** pass the production gates below.

## Current public-test phase

- [x] Source is public.
- [x] Test tag `test-2026-08-15` and test download checksums exist.
- [x] Public-test genesis and network parameters are machine-readable.
- [x] Deposit, withdrawal, confirmation, reorganization, and upgrade guidance is documented.
- [x] Node identity validator and supply calculator exist.
- [x] Test seed is published for best-effort stranger testing.
- [ ] Multiple independent public-test peers are continuously reachable.
- [ ] A public indexed block explorer/API is continuously reachable.
- [ ] Linux artifacts are independently reproducible byte-for-byte.

Do not delete or reset the operator's current public-test blocks, wallet, or test coins during this phase.

## Production release gate

- [ ] Freeze production consensus parameters and publish a new production manifest.
- [ ] Ensure the production chain identity cannot accept or reconnect to public-test history.
- [ ] Start production from a clean datadir; prove that no public-test balance carries over.
- [ ] Complete code review and security review of consensus, wallet, P2P, RPC, and dependencies.
- [ ] Create a signed annotated release tag from the reviewed commit.
- [ ] Publish source archives and deterministic build instructions.
- [ ] Have at least two independent builders reproduce identical Linux artifact hashes.
- [ ] Publish `ruckd`/`ruck-cli` artifacts (or explicitly document the reviewed upstream binary names).
- [ ] Publish SHA-256 checksums and signatures over the checksum file.
- [ ] Operate at least three seeds across independent operators/providers/regions.
- [ ] Operate a public explorer/API and monitor it from outside the operator network.
- [ ] Run deposit/withdraw/reorg/backup/restore tests on a clean exchange test environment.
- [ ] Publish the final confirmation policy and emergency pause contacts.
- [ ] Publish a supply snapshot generated at a named height.
- [ ] Publish miner and rich-list concentration methodology and snapshot.
- [ ] Publish logo assets, website, white paper, and jurisdiction-specific legal opinion.
- [ ] Obtain written exchange acceptance of the final genesis, decimals, ticker, and chain type.

## Required release evidence

Archive the following together for each exchange candidate:

- source tag, commit ID, tag signature, build instructions, compiler/dependency versions;
- artifact filenames, sizes, SHA-256 values, and builder attestations;
- final `network-manifest.json` and successful `validate_node.py --require-production` output;
- public seed and explorer health checks;
- `supply.py` JSON output at the submitted snapshot height;
- upgrade/reorg procedure, security-report route, and test transaction IDs;
- legal opinion supplied by a qualified lawyer—not generated or represented as legal advice by project software or an AI.

No checkbox should be marked complete without a link or immutable artifact proving it.
