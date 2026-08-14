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
| `learn.html` | Plain-language walkthrough |
| `paper.html` | White paper v1.0 |
| `timeline.html` | March route |
| `spec.html` | Frozen numbers |
| `faq.html` | Short answers |

Canonical long text also lives in:

- `../whitepaper/ruckcoin-whitepaper.md`
- `../whitepaper/timeline.md`
- `../doc/LAUNCH_SPEC.md`

## Publish

Point GitHub Pages (or any static host) at this `website/` folder. Do not call the network public until Phase 3 on the timeline.
