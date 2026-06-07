# RingAlert — Data Profile Report
Generated: 2026-06-07 17:22

---

## 1. Dataset Overview

| Metric | Value |
|--------|-------|
| Total transactions | 5,000 |
| Unique sender accounts | 300 |
| Date range | 2026-01-01 → 2026-03-30 |
| Columns | transaction_id, sender_account, receiver_account, amount, timestamp, device_id, hour, day_of_week, date, week, edge_key, in_suspect_range, late_night, sender_tx_seq, hours_since_last |
| Null rows dropped | 0 |

---

## 2. Amount Distribution

| Stat | Value |
|------|-------|
| Min | $10.30 |
| Max | $14,770.58 |
| Mean | $2,193.55 |
| Median | $1,901.73 |
| Std Dev | $1,624.87 |
| In $400–$900 range | 1,152 txns (23.0%) |

**→ Agent 3 significance:** 23.0% of all transactions fall in the $400–$900 suspect range.
A naive range-filter would flag too many. Agents must combine range + timing + graph pattern.

---

## 3. Temporal Patterns

| Metric | Value |
|--------|-------|
| Late-night txns (2–4 AM) | 1,241 (24.8%) |
| Peak hour (all txns) | Hour 3 |
| Most active day of week | Fri |

**Hour distribution (top 6):**
```
hour
3     522
2     499
21    225
4     220
16    199
17    191
```

**→ Agent 3 significance:** Late-night 2–4 AM window has 24.8% of transactions.
Cross this with $400–$900 range and near-regular intervals to isolate the fraud ring.

---

## 4. Account-Level Statistics

| Metric | Value |
|--------|-------|
| Total unique accounts | 300 |
| Avg transactions per account | 16.7 |
| Max transactions (single account) | 82 |
| Accounts with >20 txns | 35 |
| Accounts with >50% late-night txns | 12 |
| Accounts with >50% in suspect range | 13 |

---

## 5. Fraud Signal Inventory

These are the signals your agents should hunt for (in priority order):

### Signal A — Shared Device Fingerprints ⚠️ HIGHEST PRIORITY
Found 282 device(s) shared across multiple accounts:
```json
{
  "DEV-57e0b": [
    "ACC-N0149",
    "ACC-N0263",
    "ACC-N0016",
    "ACC-N0111",
    "ACC-N0061",
    "ACC-N0168"
  ],
  "DEV-1dcc8": [
    "ACC-N0102",
    "ACC-N0003",
    "ACC-N0154",
    "ACC-N0223",
    "ACC-N0097",
    "ACC-N0184"
  ],
  "DEV-a27eb": [
    "ACC-N0100",
    "ACC-N0010",
    "ACC-N0025",
    "ACC-N0060",
    "ACC-N0087",
    "ACC-N0110"
  ],
  "DEV-3c28d": [
    "ACC-N0064",
    "ACC-N0075",
    "ACC-N0129",
    "ACC-N0237",
    "ACC-N0094",
    "ACC-N0118"
  ],
  "DEV-cc147": [
    "ACC-N0106",
    "ACC-N0263",
    "ACC-N0021",
    "ACC-N0024",
    "ACC-N0112",
    "ACC-N0012"
  ]
}
```
**→ Agent 2 action:** Flag all accounts sharing a device ID as a candidate ring cluster.

### Signal B — Accounts Opened in Same Window ⚠️ HIGH PRIORITY
Found 59 cluster(s) of accounts with first-transaction within 12 days of each other.
Largest cluster size: 286 accounts.
**→ Agent 2 action:** Any cluster ≥ 5 accounts with same-window open dates = ring candidate.

### Signal C — Late-Night + Suspect Range Accounts ⚠️ HIGH PRIORITY
9 accounts have >50% of transactions both in 2–4 AM window AND $400–$900 range:
```
['ACC-R0001', 'ACC-R0002', 'ACC-R0003', 'ACC-R0004', 'ACC-R0005', 'ACC-R0006', 'ACC-R0007', 'ACC-R0008', 'ACC-R0009']
```
**→ Agent 3 action:** These are your strongest single-account fraud signals.

### Signal D — Circular Pairs (A→B and B→A both exist) ⚠️ HIGH PRIORITY
202 circular pairs detected (account A sent to B AND B sent to A).
**→ Agent 3 action:** Circular pairs that also share device fingerprints = near-certain ring members.

### Signal E — Near-Regular Transaction Intervals ⚠️ MEDIUM PRIORITY
0 accounts transact at near-regular intervals (CV < 25%):
```
[]
```
**→ Agent 3 action:** Near-regular + late-night = automated/coordinated behaviour.

---

## 6. Distractor Account Warning

The dataset contains accounts with legitimate anomalies designed to fool naive strategies:
- Large single transfers (≥ $5,000) — NOT fraud
- Late-night transactions alone — NOT fraud
- High transaction frequency alone — NOT fraud
- Round number amounts — NOT fraud

**Precision penalty:** Flagging everything above a threshold will catch distractors.
Judges score against the answer key — false positives hurt.

**→ Agent 3 must use COMBINED signals:** amount range + timing + circular graph pattern + shared device.
No single signal is sufficient.

---

## 7. Graph Structure Summary

| Metric | Value |
|--------|-------|
| Unique directed edges (A→B pairs) | 4,092 |
| Circular pairs (A→B + B→A) | 202 |
| Max repeat transactions on one edge | 82 |
| Top edge (most transactions) | ACC-R0002→ACC-R0003 |

---

## 8. Agent Design Recommendations (from this data)

### Agent 1 — DataIngestor
- Normalise column names (done by cleaner)
- Parse timestamps with `pd.to_datetime(infer_datetime_format=True)`
- Engineer: `hour`, `late_night`, `in_suspect_range`, `edge_key`
- Store to Cognee as flat transaction list + account entity list

### Agent 2 — GraphMapper
- Build directed graph from `edge_key` counts
- Add device fingerprint shared-accounts as a "hard cluster" signal
- Score each edge: `late_night_pct × suspect_range_pct × frequency`
- Flag any device shared across ≥ 3 accounts as a candidate ring cluster
- Store enriched graph + suspicion scores to Cognee

### Agent 3 — PatternDetector
- DFS cycle detection on high-suspicion edges only (pruned graph)
- Combine: circular flow + shared device + same-window open date
- Near-regular interval check for automated behaviour
- Flag rings, NOT individual accounts — output ring objects with evidence

### Agent 4 — RiskScorer (PyMC)
- Features per ring: num_accounts, num_loops, total_exposure, late_night_pct, device_shared
- Bayesian model: P(fraud | features) with Beta prior (base rate ~3%)
- Output: probability + 90% CI + evidence list
- Generate downloadable narrative PDF per ring

### Agent 5 — CaseBriefWriter
- Read ring + score + evidence from Cognee
- Prompt: 3 sentences — what happened, why suspicious, recommended action
- Surface in UI right panel
- Include account IDs, risk %, confidence interval

---

## 9. Key Numbers for Your Step 0 Brief

- Dataset: 5,000 transactions, 300 accounts
- Date range: 2026-01-01 → 2026-03-30
- Target: 12 fraud ring accounts across 6 circular loops
- Total ring exposure: ~$430,000
- Ring detection window: 2–4 AM, $400–$900 amounts, near-regular 8–14 hr intervals
- Distractor accounts: 15 (designed to fool threshold-only strategies)

---

*Generated by RingAlert data cleaning pipeline · June 7, 2026*
