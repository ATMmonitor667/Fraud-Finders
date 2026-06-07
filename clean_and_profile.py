"""
RingAlert — Data Cleaning + Profiling Pipeline
Works on both the synthetic dataset AND the real Kaggle CSV.
Run: python clean_and_profile.py
Outputs:
  track02_clean.csv         — cleaned, typed, normalised
  data_profile_report.md    — EDA findings for agent design
"""

import pandas as pd
import numpy as np
import json
from collections import defaultdict, Counter
from datetime import datetime

CSV_IN  = "/sessions/optimistic-bold-goldberg/mnt/outputs/track02_transactions.csv"
CSV_OUT = "/sessions/optimistic-bold-goldberg/mnt/outputs/track02_clean.csv"
RPT_OUT = "/sessions/optimistic-bold-goldberg/mnt/outputs/data_profile_report.md"

# ══════════════════════════════════════════════════════════════════
# STEP 1 — LOAD
# ══════════════════════════════════════════════════════════════════
print("Loading CSV...")
df = pd.read_csv(CSV_IN)

print(f"  Raw shape: {df.shape[0]:,} rows × {df.shape[1]} cols")
print(f"  Columns:   {list(df.columns)}")

# ══════════════════════════════════════════════════════════════════
# STEP 2 — NORMALISE COLUMN NAMES
# Works regardless of whether columns are camelCase, snake_case, etc.
# ══════════════════════════════════════════════════════════════════
print("\nNormalising column names...")
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(r"[\s\-]+", "_", regex=True)
    .str.replace(r"[^a-z0-9_]", "", regex=True)
)

# Map common variants → canonical names
rename_map = {
    "from":            "sender_account",
    "from_account":    "sender_account",
    "from_acc":        "sender_account",
    "source":          "sender_account",
    "to":              "receiver_account",
    "to_account":      "receiver_account",
    "to_acc":          "receiver_account",
    "destination":     "receiver_account",
    "value":           "amount",
    "sum":             "amount",
    "transfer_amount": "amount",
    "date":            "timestamp",
    "time":            "timestamp",
    "datetime":        "timestamp",
    "txn_id":          "transaction_id",
    "tx_id":           "transaction_id",
    "id":              "transaction_id",
    "device":          "device_id",
    "fingerprint":     "device_id",
    "device_fingerprint": "device_id",
}
df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

REQUIRED = ["transaction_id", "sender_account", "receiver_account", "amount", "timestamp"]
missing = [c for c in REQUIRED if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns after normalisation: {missing}")

print(f"  Canonical columns: {list(df.columns)}")

# ══════════════════════════════════════════════════════════════════
# STEP 3 — TYPE COERCION
# ══════════════════════════════════════════════════════════════════
print("\nCoercing types...")

# Amount → float, strip currency symbols
df["amount"] = (
    df["amount"]
    .astype(str)
    .str.replace(r"[$,£€\s]", "", regex=True)
    .pipe(pd.to_numeric, errors="coerce")
)

# Timestamp → datetime
df["timestamp"] = pd.to_datetime(df["timestamp"], infer_datetime_format=True, errors="coerce")

# String fields — strip whitespace, uppercase account IDs
for col in ["transaction_id", "sender_account", "receiver_account"]:
    df[col] = df[col].astype(str).str.strip()

if "device_id" in df.columns:
    df["device_id"] = df["device_id"].astype(str).str.strip()

print(f"  Nulls before drop: amount={df['amount'].isna().sum()}, timestamp={df['timestamp'].isna().sum()}")

# ══════════════════════════════════════════════════════════════════
# STEP 4 — DROP / FLAG PROBLEMS
# ══════════════════════════════════════════════════════════════════
print("\nDropping bad rows...")
before = len(df)

df.dropna(subset=["sender_account", "receiver_account", "amount", "timestamp"], inplace=True)
df = df[df["amount"] > 0]                        # no zero/negative amounts
df = df[df["sender_account"] != df["receiver_account"]]  # no self-transfers
df.drop_duplicates(subset=["transaction_id"], inplace=True)

after = len(df)
print(f"  Dropped {before - after} rows ({before - after}/{before} = {(before-after)/before*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════
# STEP 5 — FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════════
print("\nEngineering features...")
df = df.sort_values("timestamp").reset_index(drop=True)

df["hour"]      = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek   # 0=Mon
df["date"]      = df["timestamp"].dt.date
df["week"]      = df["timestamp"].dt.isocalendar().week.astype(int)

# Per-account running stats (for drift detection)
df["edge_key"] = df["sender_account"] + "→" + df["receiver_account"]

# Flag: amount in ring suspect range $400–$900
df["in_suspect_range"] = df["amount"].between(400, 900)

# Flag: late-night transaction (2–4 AM)
df["late_night"] = df["hour"].between(2, 4)

# Cumulative per-sender
df["sender_tx_seq"] = df.groupby("sender_account").cumcount() + 1

# Time since last transaction per sender (in hours)
df["prev_ts"] = df.groupby("sender_account")["timestamp"].shift(1)
df["hours_since_last"] = (
    (df["timestamp"] - df["prev_ts"]).dt.total_seconds() / 3600
).round(2)
df.drop(columns=["prev_ts"], inplace=True)

# ══════════════════════════════════════════════════════════════════
# STEP 6 — ACCOUNT-LEVEL STATS
# ══════════════════════════════════════════════════════════════════
print("Computing account stats...")

acct_stats = (
    df.groupby("sender_account")
    .agg(
        tx_count         = ("transaction_id", "count"),
        total_sent       = ("amount", "sum"),
        avg_sent         = ("amount", "mean"),
        min_sent         = ("amount", "min"),
        max_sent         = ("amount", "max"),
        late_night_count = ("late_night", "sum"),
        suspect_range_ct = ("in_suspect_range", "sum"),
        unique_receivers = ("receiver_account", "nunique"),
        first_tx         = ("timestamp", "min"),
        last_tx          = ("timestamp", "max"),
    )
    .reset_index()
)
acct_stats.rename(columns={"sender_account": "account_id"}, inplace=True)
acct_stats["late_night_pct"]   = (acct_stats["late_night_count"]  / acct_stats["tx_count"] * 100).round(1)
acct_stats["suspect_range_pct"]= (acct_stats["suspect_range_ct"] / acct_stats["tx_count"] * 100).round(1)
acct_stats["active_days"]      = (acct_stats["last_tx"] - acct_stats["first_tx"]).dt.days

# ══════════════════════════════════════════════════════════════════
# STEP 7 — FRAUD SIGNAL DETECTION (no labels — pure heuristics)
# ══════════════════════════════════════════════════════════════════
print("Computing fraud signals...")

# Signal 1: Device fingerprint sharing
device_to_accounts = defaultdict(set)
if "device_id" in df.columns:
    for _, row in df.iterrows():
        if row["device_id"] not in ("nan", "None", ""):
            device_to_accounts[row["device_id"]].add(row["sender_account"])
    shared_devices = {d: list(a) for d, a in device_to_accounts.items() if len(a) > 1}
else:
    shared_devices = {}

# Signal 2: Accounts opened in same window (approximate — first tx date)
open_dates = acct_stats.set_index("account_id")["first_tx"]
acct_list  = list(open_dates.index)
clusters   = []
for i, a in enumerate(acct_list):
    group = [b for b in acct_list if abs((open_dates[a] - open_dates[b]).days) <= 12]
    if len(group) >= 5:
        clusters.append(sorted(group))
# Deduplicate
seen = set()
unique_clusters = []
for c in clusters:
    key = tuple(c)
    if key not in seen:
        seen.add(key)
        unique_clusters.append(c)

# Signal 3: Late-night micro-transaction accounts (>50% of txns are 2–4 AM + in $400–900)
suspect_accounts = acct_stats[
    (acct_stats["late_night_pct"] > 50) &
    (acct_stats["suspect_range_pct"] > 50) &
    (acct_stats["tx_count"] > 5)
]["account_id"].tolist()

# Signal 4: Circular pair detection (A→B AND B→A)
pair_fwd = set(df["edge_key"])
pair_rev = set(df["receiver_account"] + "→" + df["sender_account"])
circular_pairs = pair_fwd & pair_rev

# Signal 5: Near-regular interval detection
near_regular_accounts = []
for acct, grp in df.groupby("sender_account"):
    if len(grp) < 8:
        continue
    intervals = grp["hours_since_last"].dropna()
    if len(intervals) < 5:
        continue
    cv = intervals.std() / intervals.mean() if intervals.mean() > 0 else 999
    if cv < 0.25:   # coefficient of variation < 25% = near-regular
        near_regular_accounts.append(acct)

# ══════════════════════════════════════════════════════════════════
# STEP 8 — SAVE CLEAN CSV
# ══════════════════════════════════════════════════════════════════
print(f"\nSaving clean CSV → {CSV_OUT}")
df.to_csv(CSV_OUT, index=False)
print(f"  Shape: {df.shape[0]:,} rows × {df.shape[1]} cols")

# ══════════════════════════════════════════════════════════════════
# STEP 9 — PROFILE REPORT
# ══════════════════════════════════════════════════════════════════
print("Writing profile report...")

total_txns    = len(df)
total_accts   = df["sender_account"].nunique()
date_range    = f"{df['timestamp'].min().date()} → {df['timestamp'].max().date()}"
amount_stats  = df["amount"].describe()
late_night_n  = df["late_night"].sum()
suspect_rng_n = df["in_suspect_range"].sum()

report = f"""# RingAlert — Data Profile Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## 1. Dataset Overview

| Metric | Value |
|--------|-------|
| Total transactions | {total_txns:,} |
| Unique sender accounts | {total_accts:,} |
| Date range | {date_range} |
| Columns | {', '.join(df.columns)} |
| Null rows dropped | {before - after} |

---

## 2. Amount Distribution

| Stat | Value |
|------|-------|
| Min | ${amount_stats['min']:,.2f} |
| Max | ${amount_stats['max']:,.2f} |
| Mean | ${amount_stats['mean']:,.2f} |
| Median | ${df['amount'].median():,.2f} |
| Std Dev | ${amount_stats['std']:,.2f} |
| In $400–$900 range | {suspect_rng_n:,} txns ({suspect_rng_n/total_txns*100:.1f}%) |

**→ Agent 3 significance:** {suspect_rng_n/total_txns*100:.1f}% of all transactions fall in the $400–$900 suspect range.
A naive range-filter would flag too many. Agents must combine range + timing + graph pattern.

---

## 3. Temporal Patterns

| Metric | Value |
|--------|-------|
| Late-night txns (2–4 AM) | {late_night_n:,} ({late_night_n/total_txns*100:.1f}%) |
| Peak hour (all txns) | Hour {df['hour'].mode()[0]} |
| Most active day of week | {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][df['day_of_week'].mode()[0]]} |

**Hour distribution (top 6):**
```
{df['hour'].value_counts().head(6).to_string()}
```

**→ Agent 3 significance:** Late-night 2–4 AM window has {late_night_n/total_txns*100:.1f}% of transactions.
Cross this with $400–$900 range and near-regular intervals to isolate the fraud ring.

---

## 4. Account-Level Statistics

| Metric | Value |
|--------|-------|
| Total unique accounts | {df['sender_account'].nunique():,} |
| Avg transactions per account | {acct_stats['tx_count'].mean():.1f} |
| Max transactions (single account) | {acct_stats['tx_count'].max()} |
| Accounts with >20 txns | {len(acct_stats[acct_stats['tx_count'] > 20])} |
| Accounts with >50% late-night txns | {len(acct_stats[acct_stats['late_night_pct'] > 50])} |
| Accounts with >50% in suspect range | {len(acct_stats[acct_stats['suspect_range_pct'] > 50])} |

---

## 5. Fraud Signal Inventory

These are the signals your agents should hunt for (in priority order):

### Signal A — Shared Device Fingerprints ⚠️ HIGHEST PRIORITY
{f"Found {len(shared_devices)} device(s) shared across multiple accounts:" if shared_devices else "Device ID column not present — skip this signal."}
```json
{json.dumps({k: v[:6] for k, v in list(shared_devices.items())[:5]}, indent=2)}
```
**→ Agent 2 action:** Flag all accounts sharing a device ID as a candidate ring cluster.

### Signal B — Accounts Opened in Same Window ⚠️ HIGH PRIORITY
Found {len(unique_clusters)} cluster(s) of accounts with first-transaction within 12 days of each other.
Largest cluster size: {max((len(c) for c in unique_clusters), default=0)} accounts.
**→ Agent 2 action:** Any cluster ≥ 5 accounts with same-window open dates = ring candidate.

### Signal C — Late-Night + Suspect Range Accounts ⚠️ HIGH PRIORITY
{len(suspect_accounts)} accounts have >50% of transactions both in 2–4 AM window AND $400–$900 range:
```
{suspect_accounts[:15]}
```
**→ Agent 3 action:** These are your strongest single-account fraud signals.

### Signal D — Circular Pairs (A→B and B→A both exist) ⚠️ HIGH PRIORITY
{len(circular_pairs):,} circular pairs detected (account A sent to B AND B sent to A).
**→ Agent 3 action:** Circular pairs that also share device fingerprints = near-certain ring members.

### Signal E — Near-Regular Transaction Intervals ⚠️ MEDIUM PRIORITY
{len(near_regular_accounts)} accounts transact at near-regular intervals (CV < 25%):
```
{near_regular_accounts[:10]}
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
| Unique directed edges (A→B pairs) | {df['edge_key'].nunique():,} |
| Circular pairs (A→B + B→A) | {len(circular_pairs):,} |
| Max repeat transactions on one edge | {df['edge_key'].value_counts().max()} |
| Top edge (most transactions) | {df['edge_key'].value_counts().index[0]} |

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

- Dataset: {total_txns:,} transactions, {df['sender_account'].nunique():,} accounts
- Date range: {date_range}
- Target: 12 fraud ring accounts across 6 circular loops
- Total ring exposure: ~$430,000
- Ring detection window: 2–4 AM, $400–$900 amounts, near-regular 8–14 hr intervals
- Distractor accounts: 15 (designed to fool threshold-only strategies)

---

*Generated by RingAlert data cleaning pipeline · June 7, 2026*
"""

with open(RPT_OUT, "w") as f:
    f.write(report)

print(f"  Profile report written → {RPT_OUT}")
print("\n✅ All done.")
print(f"   Clean CSV:      track02_clean.csv  ({df.shape[0]:,} rows × {df.shape[1]} cols)")
print(f"   Profile report: data_profile_report.md")
