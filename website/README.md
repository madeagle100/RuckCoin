# RuckCoin public site

Static pages. No build step.

## Open locally

From this folder:

```
python -m http.server 8765
```

Then visit http://127.0.0.1:8765/

## Pages

| File | What it is |
| --- | --- |
| `index.html` | Home |
| `run.html` | Start — Windows / Linux / Mac (which file to get) |
| `learn.html` | Plain-language walkthrough |
| `paper.html` | White paper |
| `timeline.html` | March route |
| `veterans.html` | Fund policy and (later) the public address |
| `wallet.html` | Wallet (same zip on every OS) |
| `mine.html` | GPU mining on your node, your K address |
| `downloads/ruckcoin-wallet.zip` | Wallet zip |
| `downloads/ruckcoin-linux-x86_64.zip` | Linux node (Ubuntu 24.04 x86_64) |
| `downloads/SHA256SUMS.txt` | SHA-256 of the zips |
| `spec.html` | Frozen numbers |
| `faq.html` | Short answers |

Canonical long text also lives in:

- `../whitepaper/ruckcoin-whitepaper.md`
- `../whitepaper/timeline.md`
- `../doc/LAUNCH_SPEC.md`

## Publish

Point GitHub Pages (or any static host) at this `website/` folder. Do not call the network public until Phase 3 on the timeline.
