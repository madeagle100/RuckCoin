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
| `run.html` | Start — Windows / Linux / Mac |
| `wallet.html` | Wallet |
| `mine.html` | Mine |
| `learn.html` | How it works (hub to paper, timeline, spec, look-up) |
| `books.html` | Open books hub (veterans, locks, votes) |
| `veterans.html` | Veterans fund |
| `locks.html` | Ops and listing locks |
| `votes.html` | Holder votes |
| `paper.html` | White paper |
| `timeline.html` | Calendar |
| `spec.html` | Frozen numbers |
| `explore.html` | Local look-up |
| `faq.html` | Short answers |
| `downloads/` | Wallet zip, Linux node zip, SHA256SUMS |

Canonical long text also lives in:

- `../whitepaper/ruckcoin-whitepaper.md`
- `../whitepaper/timeline.md`
- `../doc/LAUNCH_SPEC.md`

## Publish

Point GitHub Pages (or any static host) at this `website/` folder. Do not call the network public until Phase 3 on the timeline.
