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
| `report.html` | Issue / suggestion box (inbox key in `js/report-key.js`, not an email address) |
| `downloads/` | Wallet zip, Linux node zip, SHA256SUMS |

Canonical long text also lives in:

- `../whitepaper/ruckcoin-whitepaper.md`
- `../whitepaper/timeline.md`
- `../doc/LAUNCH_SPEC.md`

## Publish

Live site: **https://ruckcoin.org/** (GitHub Pages).  
Test seed: `addnode=seed.ruckcoin.org:8867`

DNS at the registrar (this is the part you add; GitHub cannot do it):

| Type | Name | Value | Proxy |
| --- | --- | --- | --- |
| A | `@` | `185.199.108.153` | off |
| A | `@` | `185.199.109.153` | off |
| A | `@` | `185.199.110.153` | off |
| A | `@` | `185.199.111.153` | off |
| CNAME | `www` | `madeagle100.github.io` | off |
| A | `seed` | your current home IP | off |

Do not orange-cloud / proxy `seed`. P2P on 8867 will break.
