# TechFreedom catalogue data

This directory is the canonical static data source for the assessment and alternatives experience.

- `tools.json` contains the mainstream tools being assessed.
- `alternatives.json` contains curated alternatives.
- `archetypes.json` contains example technology stacks.

## Alternative links

Every value in an alternative's `alternativeTo` array must be an exact `slug` from `tools.json`. Do not add shorthand or phantom products here. If the mainstream tool does not yet exist in `tools.json`, add and score that tool first.

## Risk scoring

Each product is scored from **1 (minimal risk)** to **5 (critical risk)** on five lenses. `total` must equal the sum of the five lens scores.

| Lens | 1 — minimal | 2 — low | 3 — moderate | 4 — high | 5 — critical |
| --- | --- | --- | --- | --- | --- |
| Jurisdiction | UK/EU or similarly strong privacy jurisdiction; clear residency | Strong privacy regime with minor jurisdiction questions | US company with meaningful EU hosting/configuration | US company; primarily US data; CLOUD Act exposure | US data/no meaningful residency; serious legal conflict/exposure |
| Continuity | Open export, open formats, self-hostable/easy to switch | Good export and several alternatives | Export possible but switching needs planning | Difficult/incomplete export; few alternatives | No meaningful export or realistic exit |
| Surveillance | Open/privacy-first; no tracking or harvesting | Minimal tracking; no sale of data; transparent policy | Product analytics/tracking with some controls | Extensive tracking or reuse for ads/AI | Surveillance is central to the business model |
| Lock-in | Open standards, full portability, easy exit | Mostly open; migration practical | Mixed/proprietary workflows create switching cost | Deep proprietary integration/formats | No practical portability |
| Cost exposure | Free/open source or highly stable/competitive | Affordable and predictable | Mid-range/limited free tier/meaningful increases possible | Expensive per-seat or repeated increases | Monopoly-like pricing/captive users |

Scores are about **risk**, not product quality. Self-hosting can reduce jurisdiction, surveillance and lock-in risk while increasing operational effort; that trade-off belongs in `tradeoffs`, not by artificially lowering every score.

## Review discipline

`lastReviewed` is the month in which the entry's factual claims and scores were substantively checked. Prefer primary sources for company location, hosting/data residency, licensing, self-hosting and pricing.

Run:

```bash
python server/validate-data.py
```

before committing catalogue changes.
