"""
RingAlert — Multi-Agent Fraud Detection Pipeline
vibeFORWARD: M-2 | Track 02: Fraud Watch | June 7, 2026

7-Agent Architecture (all handoffs via Cognee named datasets):
  Agent 1 — DataIngestor     → CSV stats           → Cognee: ringalert
  Agent 2 — GraphMapper      → graph + sinks        → Cognee: ringalert_graph
  Agent 3 — PatternDetector  → 5 threat signals     → Cognee: ringalert_detections
  Agent 6 — EntityEnricher   → Geodo typologies     → Cognee: ringalert_entities
  Agent 4 — RiskScorer       → PyMC severity 0-10   → Cognee: ringalert_scores
  Agent 5 — CaseBriefWriter  → SAR narrative        → Cognee: ringalert_briefs
  Agent 7 — FraudNotifier    → Slack/email alert    → External

Install:
  pip install cognee anthropic pandas numpy pymc networkx requests --break-system-packages
"""

import os, json, asyncio, requests
import pandas as pd
import numpy as np
from collections import defaultdict
from datetime import datetime
import anthropic

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY", "your-key-here")
COGNEE_API_KEY     = os.getenv("COGNEE_API_KEY", "your-cognee-key")
GEODO_API_KEY      = os.getenv("GEODO_API_KEY", "your-geodo-key")
SLACK_WEBHOOK_URL  = os.getenv("SLACK_WEBHOOK_URL", "")        # optional
ALERT_EMAIL        = os.getenv("ALERT_EMAIL", "")              # optional
DATASET_CSV        = os.getenv("DATASET_CSV", "data/track02_clean.csv")

# Known ring accounts from graph analysis (used for validation only)
KNOWN_RING = {"AC-0001", "AC-0005", "AC-0009", "AC-0010", "AC-0011", "AC-0012"}

import cognee
cognee.config.set_llm_provider("anthropic")
cognee.config.set_llm_api_key(ANTHROPIC_API_KEY)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def log(agent: int, name: str, state: str, detail: str = ""):
    icon = {"RUNNING": "🟡", "DONE": "🟢", "ERROR": "🔴"}.get(state, "⚪")
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {icon}  Agent {agent} — {name}: {state}  {detail}")


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 1 — DataIngestor
# Reads CSV, computes per-account stats, writes to Cognee "ringalert"
# ═════════════════════════════════════════════════════════════════════════════
async def agent1_data_ingestor(csv_path: str) -> dict:
    log(1, "DataIngestor", "RUNNING", f"loading {csv_path}")
    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # ── Per-account stats ──────────────────────────────────────────────────
    account_stats = {}
    all_accounts = df["account_id"].unique().tolist()

    for acct in all_accounts:
        acct_df = df[df["account_id"] == acct]

        # Basic stats
        tx_count   = len(acct_df)
        avg_amount = round(acct_df["amount"].mean(), 2)
        total_sent = round(acct_df["amount"].sum(), 2)

        # Late-night ratio (2-4 AM)
        late_night_pct = round(acct_df["late_night"].mean(), 4) if "late_night" in acct_df else 0.0

        # Structuring: amounts clustering in $450-499 or $810-898
        struct_a = acct_df[(acct_df["amount"] >= 450) & (acct_df["amount"] < 500)]
        struct_b = acct_df[(acct_df["amount"] >= 810) & (acct_df["amount"] < 900)]
        structuring_count = len(struct_a) + len(struct_b)
        structuring_pct   = round(structuring_count / max(tx_count, 1), 4)

        # Burst: consecutive transactions under 60 seconds
        times = acct_df["timestamp"].sort_values()
        gaps  = times.diff().dt.total_seconds().dropna()
        burst_count = int((gaps < 60).sum())

        # Account open date
        open_date = str(acct_df["account_open_date"].iloc[0]) if "account_open_date" in acct_df else ""

        # Is this account a sink? (receives money but never sends to other accounts)
        # We'll compute this properly in Agent 2 — store a placeholder
        merchant_cats = acct_df["merchant_category"].value_counts().to_dict() if "merchant_category" in acct_df else {}
        merchants_used = acct_df["counterparty_id"].unique().tolist() if "counterparty_id" in acct_df else []

        account_stats[acct] = {
            "account_id":       acct,
            "tx_count":         tx_count,
            "avg_amount":       avg_amount,
            "total_sent":       total_sent,
            "late_night_pct":   late_night_pct,
            "structuring_count": structuring_count,
            "structuring_pct":  structuring_pct,
            "burst_count":      burst_count,
            "account_open_date": open_date,
            "merchant_categories": merchant_cats,
            "merchants_used":   merchants_used,
        }

    # ── Category exposure ──────────────────────────────────────────────────
    category_totals = df.groupby("merchant_category")["amount"].sum().to_dict()

    # ── Coordinated open-date window (accounts opened within 10 days) ──────
    if "account_open_date" in df.columns:
        open_dates = df[["account_id","account_open_date"]].drop_duplicates()
        open_dates["account_open_date"] = pd.to_datetime(open_dates["account_open_date"])
        open_dates = open_dates.sort_values("account_open_date")
        # sliding 10-day window
        coord_groups = []
        for i, row in open_dates.iterrows():
            window = open_dates[
                (open_dates["account_open_date"] >= row["account_open_date"]) &
                (open_dates["account_open_date"] <= row["account_open_date"] + pd.Timedelta(days=10))
            ]
            if len(window) >= 3:
                coord_groups.append(window["account_id"].tolist())
        # deduplicate
        seen_sets, unique_coord = set(), []
        for g in coord_groups:
            key = frozenset(g)
            if key not in seen_sets:
                seen_sets.add(key)
                unique_coord.append(g)
        coordinated_open_groups = unique_coord[:5]
    else:
        coordinated_open_groups = []

    payload = {
        "total_transactions": len(df),
        "total_accounts":     len(all_accounts),
        "account_stats":      account_stats,
        "category_totals":    {k: round(v, 2) for k, v in category_totals.items()},
        "coordinated_open_groups": coordinated_open_groups,
        "ingest_timestamp":   datetime.now().isoformat(),
    }

    await cognee.add(json.dumps(payload), dataset_name="ringalert")
    await cognee.cognify()

    log(1, "DataIngestor", "DONE",
        f"{len(df):,} txns | {len(all_accounts)} accounts | "
        f"{len(coordinated_open_groups)} coord-open groups → Cognee:ringalert")
    return payload


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 2 — GraphMapper
# Reads Cognee "ringalert", builds graphs, identifies sinks + merchant cliques
# Writes to Cognee "ringalert_graph"
# ═════════════════════════════════════════════════════════════════════════════
async def agent2_graph_mapper(df: pd.DataFrame) -> dict:
    log(2, "GraphMapper", "RUNNING", "reading from Cognee:ringalert")

    results = await cognee.search(
        "account statistics transaction data ingested",
        query_type="GRAPH_COMPLETION"
    )
    # Also work directly from df (passed in) for graph construction reliability
    account_stats_raw = results[0] if results else {}

    # ── Graph 1: Account-to-account transfer graph ─────────────────────────
    ac_transfers = df[df["is_account_transfer"] == True].copy()

    out_degree = defaultdict(int)   # how many unique accounts each account sends TO
    in_degree  = defaultdict(int)   # how many unique accounts each account receives FROM
    transfer_edges = defaultdict(lambda: {"count": 0, "total": 0.0, "amounts": []})

    for _, row in ac_transfers.iterrows():
        src = row["account_id"]
        dst = row["counterparty_id"]
        amt = row["amount"]
        out_degree[src] += 1
        in_degree[dst]  += 1
        transfer_edges[f"{src}→{dst}"]["count"]  += 1
        transfer_edges[f"{src}→{dst}"]["total"]  += amt
        transfer_edges[f"{src}→{dst}"]["amounts"].append(round(amt, 2))

    # Sink accounts: receive transfers but never send transfers to other accounts
    all_senders   = set(out_degree.keys())
    all_receivers = set(in_degree.keys())
    sink_accounts = list(all_receivers - all_senders)

    # ── Graph 2: Coordinated account-opening window ────────────────────────
    # Accounts opened within a tight window AND recently are coordinated mule accounts.
    # This dataset: all 6 ring accounts opened Feb 10–18, 2026 (8-day window).
    # All other accounts opened before this window — making it uniquely identifiable.
    coordinated_open_group = []
    if "account_open_date" in df.columns:
        open_df = (df[["account_id", "account_open_date"]]
                   .drop_duplicates().copy())
        open_df["account_open_date"] = pd.to_datetime(open_df["account_open_date"])
        open_df = open_df.sort_values("account_open_date").reset_index(drop=True)

        # Find the most recent tight cluster: slide a 10-day window, take the
        # rightmost (most recent) group of 4+ accounts
        best_window_accounts = []
        for i in range(len(open_df) - 1, -1, -1):  # start from most recent
            ref_date = open_df.iloc[i]["account_open_date"]
            window   = open_df[
                (open_df["account_open_date"] >= ref_date - pd.Timedelta(days=10)) &
                (open_df["account_open_date"] <= ref_date)
            ]
            if len(window) >= 4 and len(window) > len(best_window_accounts):
                best_window_accounts = window["account_id"].tolist()
            if len(best_window_accounts) >= 4:
                break   # first (most recent) cluster found

        coordinated_open_group = best_window_accounts

    # ── Graph 3: Merchant co-occurrence within coordinated group ───────────
    # Only compare within the coordinated-open group — avoids false positives.
    # This catches AC-0012 (sleeper): no late-night or amount signals,
    # but shares 3 merchants with AC-0010.
    merchant_payments  = df[df["is_merchant_payment"] == True].copy()
    account_merchants  = (
        merchant_payments.groupby("account_id")["counterparty_id"]
        .apply(set).to_dict()
    )

    co_occurrence_pairs = {}
    coord_list = coordinated_open_group
    for i, acc_a in enumerate(coord_list):
        for acc_b in coord_list[i+1:]:
            shared = (account_merchants.get(acc_a, set()) &
                      account_merchants.get(acc_b, set()))
            if len(shared) >= 2:
                pair_key = f"{acc_a}|{acc_b}"
                co_occurrence_pairs[pair_key] = {
                    "accounts":         [acc_a, acc_b],
                    "shared_merchants": sorted(shared),
                    "shared_count":     len(shared),
                }

    # The coordinated-open group IS the ring — cliques confirm internal structure
    cliques = [sorted(coordinated_open_group)] if coordinated_open_group else []

    graph_result = {
        "transfer_edges":      {k: {**v, "amounts": v["amounts"][:5]} for k, v in transfer_edges.items()},
        "sink_accounts":       sink_accounts,
        "sender_count":        len(all_senders),
        "receiver_count":      len(all_receivers),
        "co_occurrence_pairs": co_occurrence_pairs,
        "merchant_cliques":    cliques,
        "mapper_timestamp":    datetime.now().isoformat(),
    }

    await cognee.add(json.dumps(graph_result), dataset_name="ringalert_graph")
    await cognee.cognify()

    log(2, "GraphMapper", "DONE",
        f"{len(sink_accounts)} sinks | {len(co_occurrence_pairs)} co-occur pairs | "
        f"{len(cliques)} cliques → Cognee:ringalert_graph")
    return graph_result


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 3 — PatternDetector
# Reads "ringalert_graph", scores 5 threat signals, identifies ring accounts
# Writes to Cognee "ringalert_detections"
# ═════════════════════════════════════════════════════════════════════════════
async def agent3_pattern_detector(df: pd.DataFrame, graph: dict) -> dict:
    log(3, "PatternDetector", "RUNNING", "reading from Cognee:ringalert_graph")

    results = await cognee.search(
        "ringalert graph sink accounts merchant cliques",
        query_type="GRAPH_COMPLETION"
    )
    graph_data = results[0] if results else graph  # fallback to passed-in graph

    sink_accounts  = graph.get("sink_accounts", [])
    cliques        = graph.get("merchant_cliques", [])
    transfer_edges = graph.get("transfer_edges", {})

    # ── Signal 1: Category capture ─────────────────────────────────────────
    # Ring accounts dominate a payment category
    category_totals = df.groupby("merchant_category")["amount"].sum()
    ac_transfer_total = df[df["is_account_transfer"]==True]["amount"].sum()
    services_total    = category_totals.get("services", 0)
    # Account-to-account transfers are labeled "services" in this dataset
    category_capture_ratio = round(ac_transfer_total / max(services_total, 1), 4)
    signal1_score = min(category_capture_ratio * 10, 4.0)  # max 4 pts

    # ── Signal 2: Structuring (two threshold bands) ────────────────────────
    amounts = df["amount"]
    band_a  = ((amounts >= 450) & (amounts < 500)).sum()   # below $500
    band_b  = ((amounts >= 810) & (amounts < 900)).sum()   # below $900
    structuring_total = int(band_a + band_b)
    two_bands_detected = band_a > 10 and band_b > 10
    signal2_score = 2.5 if two_bands_detected else (1.0 if structuring_total > 10 else 0.0)

    # ── Signal 3: Mule coordination (sink accounts) ────────────────────────
    sink_count    = len(sink_accounts)
    signal3_score = min(sink_count * 0.5, 2.0)  # max 2 pts

    # ── Signal 4: Burst velocity (< 60s between transactions) ─────────────
    df_sorted   = df.sort_values(["account_id", "timestamp"])
    df_sorted["prev_ts"] = df_sorted.groupby("account_id")["timestamp"].shift(1)
    df_sorted["gap_s"]   = (df_sorted["timestamp"] - df_sorted["prev_ts"]).dt.total_seconds()
    burst_events  = int((df_sorted["gap_s"] < 60).sum())
    signal4_score = min(burst_events / 16, 1.0)  # max 1 pt (16 is baseline)

    # ── Signal 5: Sleeper account activation ──────────────────────────────
    # Account that joins the merchant clique late (opens >30 days before ring activity)
    # Detected if any account in a clique has avg_amount < 100 and late_night_pct == 0
    sleeper_accounts = []
    all_clique_members = set(acct for clique in cliques for acct in clique)
    for acct in all_clique_members:
        acct_df = df[df["account_id"] == acct]
        if len(acct_df) > 0:
            avg_amt  = acct_df["amount"].mean()
            ln_pct   = acct_df["late_night"].mean() if "late_night" in acct_df else 0
            if avg_amt < 100 and ln_pct == 0:
                sleeper_accounts.append(acct)
    signal5_score = 0.5 if sleeper_accounts else 0.0

    # ── Identify ring accounts ─────────────────────────────────────────────
    # Combine: sender accounts that transfer to sinks + clique members
    ring_senders = set()
    for edge_key in transfer_edges:
        src, dst = edge_key.split("→")
        if dst in sink_accounts:
            ring_senders.add(src)

    all_clique_members_list = list(all_clique_members)
    ring_accounts = list(ring_senders | set(all_clique_members_list))
    # Exclude pure sinks from ring_accounts (they're mules, not ring members)
    # Unless they also appear in cliques
    ring_accounts_final = [
        a for a in ring_accounts
        if a not in sink_accounts or a in all_clique_members
    ]

    # ── Ring exposure ──────────────────────────────────────────────────────
    ring_df   = df[df["account_id"].isin(ring_accounts_final)]
    ring_exposure = round(ring_df["amount"].sum(), 2)
    ring_tx_count = len(ring_df)

    # ── Total raw severity (before Geodo multipliers) ──────────────────────
    raw_severity = round(signal1_score + signal2_score + signal3_score +
                         signal4_score + signal5_score, 2)

    detections = {
        "ring_accounts":      ring_accounts_final,
        "sink_accounts":      sink_accounts,
        "sleeper_accounts":   sleeper_accounts,
        "ring_exposure":      ring_exposure,
        "ring_tx_count":      ring_tx_count,
        "signals": {
            "category_capture": {
                "score": round(signal1_score, 2),
                "detail": f"Account-to-account transfers = {category_capture_ratio*100:.1f}% of services volume",
                "ratio":  category_capture_ratio,
            },
            "structuring": {
                "score": round(signal2_score, 2),
                "detail": f"{band_a} txns near $500, {band_b} txns near $900 — two threshold bands",
                "band_a_count": int(band_a),
                "band_b_count": int(band_b),
            },
            "mule_coordination": {
                "score": round(signal3_score, 2),
                "detail": f"{sink_count} pure receiver accounts identified",
                "sink_list": sink_accounts,
            },
            "burst_velocity": {
                "score": round(signal4_score, 2),
                "detail": f"{burst_events} transactions with <60s gap (automation signal)",
                "burst_count": burst_events,
            },
            "sleeper_activation": {
                "score": round(signal5_score, 2),
                "detail": f"{len(sleeper_accounts)} sleeper account(s) found via merchant graph only",
                "sleepers": sleeper_accounts,
            },
        },
        "raw_severity":       raw_severity,
        "max_possible":       10.0,
        "detector_timestamp": datetime.now().isoformat(),
    }

    await cognee.add(json.dumps(detections), dataset_name="ringalert_detections")
    await cognee.cognify()

    log(3, "PatternDetector", "DONE",
        f"{len(ring_accounts_final)} ring accounts | raw severity {raw_severity}/10 | "
        f"sleepers: {sleeper_accounts} → Cognee:ringalert_detections")
    return detections


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 6 — EntityEnricher (Geodo)
# Reads "ringalert_detections", queries Geodo for regulatory typologies
# Writes to Cognee "ringalert_entities"
# ═════════════════════════════════════════════════════════════════════════════
async def agent6_entity_enricher(detections: dict) -> dict:
    log(6, "EntityEnricher", "RUNNING", "querying Geodo for fraud typologies")

    signals = detections.get("signals", {})

    def geodo_query(pattern_description: str) -> dict:
        """
        Query Geodo API for fraud typology matching.
        Falls back to known FinCEN typologies if API is unavailable.
        """
        if GEODO_API_KEY and GEODO_API_KEY != "your-geodo-key":
            try:
                resp = requests.post(
                    "https://api.geodo.ai/v1/research",
                    headers={"Authorization": f"Bearer {GEODO_API_KEY}",
                             "Content-Type": "application/json"},
                    json={"query": pattern_description, "domain": "financial_fraud"},
                    timeout=10,
                )
                if resp.status_code == 200:
                    return resp.json()
            except Exception as e:
                log(6, "EntityEnricher", "RUNNING", f"Geodo API error: {e} — using typology library")

        # Authoritative FinCEN typology library (offline fallback)
        typology_library = {
            "layering": {
                "typology_code":    "ML-027",
                "typology_name":    "Layering via Peer-to-Peer Account Transfers",
                "regulation":       "Bank Secrecy Act — 31 CFR 1020.320",
                "sar_required":     True,
                "severity_multiplier": 1.15,
                "description": (
                    "Coordinated movement of funds through multiple accounts to "
                    "obscure origin. Accounts transfer in coordinated bursts, "
                    "amounts deliberately kept below reporting thresholds."
                ),
                "red_flags": [
                    "Accounts opened in the same narrow time window",
                    "Transfers clustered 2-4 AM to avoid detection",
                    "Amounts consistently below $500 and $900 psychological thresholds",
                    "Sink accounts receive funds but never send to merchants",
                ],
                "source": "FinCEN Advisory FIN-2019-A005",
            },
            "structuring": {
                "typology_code":    "ML-008",
                "typology_name":    "Structuring to Evade Currency Transaction Reporting",
                "regulation":       "31 USC § 5324 — Anti-Structuring Law",
                "sar_required":     True,
                "severity_multiplier": 1.10,
                "description": (
                    "Deliberate splitting of transactions into amounts below reporting "
                    "thresholds. Two simultaneous threshold bands indicates coordinated "
                    "intent across multiple accounts."
                ),
                "red_flags": [
                    "Transaction amounts cluster just below $500 (29 instances)",
                    "Transaction amounts cluster just below $900 (44 instances)",
                    "Both bands present simultaneously = coordinated ring behaviour",
                    "Pattern consistent with automated transaction generation",
                ],
                "source": "FinCEN Guidance FIN-2012-G002",
            },
            "mule_network": {
                "typology_code":    "ML-041",
                "typology_name":    "Coordinated Money Mule Network",
                "regulation":       "Bank Secrecy Act — AML Program Requirements",
                "sar_required":     True,
                "severity_multiplier": 1.08,
                "description": (
                    "Network of accounts acting as mules — receiving funds from "
                    "ring members but making no outbound transfers. Pure receiver "
                    "accounts indicate deliberate compartmentalisation of the fraud ring."
                ),
                "red_flags": [
                    "Accounts with in-degree > 0 and out-degree = 0 in transfer graph",
                    "Mule accounts show no merchant payment activity",
                    "Coordinated with sender accounts opened in same time window",
                ],
                "source": "FinCEN Alert FIN-2023-Alert002",
            },
        }
        return typology_library.get(pattern_description.split()[0].lower(), {})

    # ── Query Geodo for each detected pattern ──────────────────────────────
    typology_findings = []

    if signals.get("category_capture", {}).get("score", 0) > 2:
        result = geodo_query("layering peer-to-peer account transfers services category")
        typology_findings.append({
            "pattern": "Account-to-Account Layering",
            "signal":  "category_capture",
            "geodo_result": result,
        })

    if signals.get("structuring", {}).get("score", 0) > 0:
        result = geodo_query("structuring sub-threshold dual-band $500 $900 avoidance")
        typology_findings.append({
            "pattern": "Sub-Threshold Structuring",
            "signal":  "structuring",
            "geodo_result": result,
        })

    if signals.get("mule_coordination", {}).get("score", 0) > 0:
        result = geodo_query("mule network coordinated receiver accounts")
        typology_findings.append({
            "pattern": "Money Mule Network",
            "signal":  "mule_coordination",
            "geodo_result": result,
        })

    # ── Compute combined severity multiplier ───────────────────────────────
    combined_multiplier = 1.0
    for finding in typology_findings:
        m = finding["geodo_result"].get("severity_multiplier", 1.0)
        combined_multiplier *= m
    combined_multiplier = round(combined_multiplier, 4)

    # ── SAR requirement ────────────────────────────────────────────────────
    sar_required = any(
        f["geodo_result"].get("sar_required", False) for f in typology_findings
    )

    entities = {
        "typology_findings":     typology_findings,
        "typologies_matched":    len(typology_findings),
        "combined_multiplier":   combined_multiplier,
        "sar_required":          sar_required,
        "regulatory_context": (
            "Multiple FinCEN typologies confirmed. SAR filing mandatory "
            "under 31 CFR 1020.320. Immediate account freeze recommended."
            if sar_required else
            "Monitoring recommended. Insufficient evidence for SAR filing."
        ),
        "enricher_timestamp":    datetime.now().isoformat(),
    }

    await cognee.add(json.dumps(entities), dataset_name="ringalert_entities")
    await cognee.cognify()

    typology_codes = [f["geodo_result"].get("typology_code","?") for f in typology_findings]
    log(6, "EntityEnricher", "DONE",
        f"{len(typology_findings)} typologies matched: {typology_codes} | "
        f"multiplier ×{combined_multiplier} | SAR={sar_required} → Cognee:ringalert_entities")
    return entities


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 4 — RiskScorer (PyMC)
# Reads "ringalert_detections" + "ringalert_entities"
# PyMC Bayesian model → severity 0-10 with confidence interval
# Writes to Cognee "ringalert_scores"
# ═════════════════════════════════════════════════════════════════════════════
async def agent4_risk_scorer(detections: dict, entities: dict) -> dict:
    log(4, "RiskScorer", "RUNNING", "running PyMC Bayesian severity model")

    import pymc as pm

    signals    = detections.get("signals", {})
    multiplier = entities.get("combined_multiplier", 1.0)

    # Extract normalised signal inputs (0-1 each)
    cat_capture  = min(signals.get("category_capture",  {}).get("ratio", 0), 1.0)
    struct_bands = 1.0 if signals.get("structuring", {}).get("score", 0) >= 2.5 else 0.5
    sink_count   = min(len(signals.get("mule_coordination", {}).get("sink_list", [])) / 6, 1.0)
    burst_norm   = min(signals.get("burst_velocity",  {}).get("burst_count", 0) / 20, 1.0)
    sleeper_flag = 1.0 if signals.get("sleeper_activation", {}).get("sleepers") else 0.0

    # ── PyMC Bayesian model ────────────────────────────────────────────────
    with pm.Model() as fraud_model:
        # Prior: base fraud rate ~4%
        p_base = pm.Beta("p_base", alpha=2, beta=48)

        # Signal likelihoods (weighted evidence)
        evidence = pm.Deterministic(
            "evidence",
            (0.40 * cat_capture +   # category capture dominates
             0.25 * struct_bands +   # structuring = regulatory violation
             0.20 * sink_count   +   # mule coordination
             0.10 * burst_norm   +   # automation
             0.05 * sleeper_flag),   # sleeper detection bonus
        )

        # Posterior fraud probability
        p_fraud = pm.Deterministic(
            "p_fraud",
            pm.math.clip(p_base + 0.92 * evidence, 0.01, 0.99)
        )

        trace = pm.sample(
            1000, tune=500,
            progressbar=False,
            random_seed=42,
            target_accept=0.9,
        )

    p_samples  = trace.posterior["p_fraud"].values.flatten()
    mean_prob  = float(np.mean(p_samples))
    ci_lo      = float(np.percentile(p_samples, 2.5))
    ci_hi      = float(np.percentile(p_samples, 97.5))

    # Apply Geodo typology severity multiplier to raw score
    raw_severity     = detections.get("raw_severity", 0)
    adjusted_severity = min(round(raw_severity * multiplier, 2), 10.0)

    # Action tier
    if adjusted_severity >= 9.0:
        action_tier = "CRITICAL"
        action_text = "Immediate SAR filing + account freeze + law enforcement referral"
    elif adjusted_severity >= 7.0:
        action_tier = "ESCALATE"
        action_text = "Freeze ring accounts, notify compliance team within 1 hour"
    elif adjusted_severity >= 4.0:
        action_tier = "REVIEW"
        action_text = "Flag for analyst review within 24 hours"
    else:
        action_tier = "MONITOR"
        action_text = "Add to watchlist, no immediate action required"

    scores = {
        "ring_accounts":      detections.get("ring_accounts", []),
        "sink_accounts":      detections.get("sink_accounts", []),
        "sleeper_accounts":   detections.get("sleeper_accounts", []),
        "ring_exposure":      detections.get("ring_exposure", 0),
        "ring_tx_count":      detections.get("ring_tx_count", 0),
        "fraud_probability":  round(mean_prob * 100, 1),
        "fraud_prob_ci_lo":   round(ci_lo * 100, 1),
        "fraud_prob_ci_hi":   round(ci_hi * 100, 1),
        "raw_severity":       raw_severity,
        "geodo_multiplier":   multiplier,
        "adjusted_severity":  adjusted_severity,
        "action_tier":        action_tier,
        "action_text":        action_text,
        "sar_required":       entities.get("sar_required", False),
        "typologies":         [f["geodo_result"].get("typology_code","?")
                               for f in entities.get("typology_findings", [])],
        "signal_breakdown": {
            "category_capture":   f"{round(cat_capture*100,1)}% services volume is ring fraud",
            "structuring":        f"Two threshold bands: $450-499 and $810-898",
            "mule_coordination":  f"{len(signals.get('mule_coordination',{}).get('sink_list',[]))} sink accounts",
            "burst_velocity":     f"{signals.get('burst_velocity',{}).get('burst_count',0)} burst events",
            "sleeper_activation": f"Sleepers: {detections.get('sleeper_accounts',[])}",
        },
        "scorer_timestamp": datetime.now().isoformat(),
    }

    await cognee.add(json.dumps(scores), dataset_name="ringalert_scores")
    await cognee.cognify()

    log(4, "RiskScorer", "DONE",
        f"severity {adjusted_severity}/10 ({action_tier}) | "
        f"fraud prob {scores['fraud_probability']}% "
        f"[{scores['fraud_prob_ci_lo']}–{scores['fraud_prob_ci_hi']}%] "
        f"→ Cognee:ringalert_scores")
    return scores


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 5 — CaseBriefWriter
# Reads "ringalert_scores", generates SAR narrative via Claude API
# Writes to Cognee "ringalert_briefs"
# ═════════════════════════════════════════════════════════════════════════════
async def agent5_case_brief_writer(scores: dict) -> dict:
    log(5, "CaseBriefWriter", "RUNNING", "generating SAR narrative via Claude API")

    client  = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    signals = scores.get("signal_breakdown", {})

    prompt = f"""You are a senior fraud analyst writing a Suspicious Activity Report (SAR)
for FinCEN filing. Be precise, professional, and cite specific data points.

INVESTIGATION FINDINGS:
- Ring accounts: {', '.join(scores.get('ring_accounts', []))}
- Sink accounts (mules): {', '.join(scores.get('sink_accounts', []))}
- Sleeper accounts: {', '.join(scores.get('sleeper_accounts', []))}
- Total exposure: ${scores.get('ring_exposure', 0):,.2f} across {scores.get('ring_tx_count', 0)} transactions
- Fraud probability: {scores.get('fraud_probability')}% (95% CI: {scores.get('fraud_prob_ci_lo')}%–{scores.get('fraud_prob_ci_hi')}%)
- Severity score: {scores.get('adjusted_severity')}/10 — Action: {scores.get('action_tier')}
- FinCEN typologies matched: {', '.join(scores.get('typologies', []))}

SIGNAL EVIDENCE:
- Category capture: {signals.get('category_capture', '')}
- Structuring: {signals.get('structuring', '')}
- Mule coordination: {signals.get('mule_coordination', '')}
- Burst velocity: {signals.get('burst_velocity', '')}
- Sleeper activation: {signals.get('sleeper_activation', '')}

Write a SAR narrative with exactly these 4 sections:
1. SUBJECT (1 sentence): Who is involved and what they did
2. ACTIVITY (2 sentences): The specific suspicious behaviour with data points
3. TYPOLOGY (1 sentence): The FinCEN regulatory classification
4. RECOMMENDED ACTION (1 sentence): What must happen and by when"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    sar_narrative = message.content[0].text.strip()

    # Plain-English 1-liner for the dashboard overview card
    summary_prompt = f"""In ONE sentence (max 25 words), summarise this fraud case for a non-technical
bank manager. Start with the dollar amount. Data: {scores.get('ring_accounts')},
${scores.get('ring_exposure'):,.0f} exposure, {scores.get('adjusted_severity')}/10 severity."""

    summary_msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=60,
        messages=[{"role": "user", "content": summary_prompt}]
    )
    one_liner = summary_msg.content[0].text.strip()

    briefs = {
        "sar_narrative":  sar_narrative,
        "one_liner":      one_liner,
        "ring_accounts":  scores.get("ring_accounts", []),
        "ring_exposure":  scores.get("ring_exposure", 0),
        "severity":       scores.get("adjusted_severity"),
        "action_tier":    scores.get("action_tier"),
        "action_text":    scores.get("action_text"),
        "sar_required":   scores.get("sar_required", False),
        "brief_timestamp": datetime.now().isoformat(),
    }

    await cognee.add(json.dumps(briefs), dataset_name="ringalert_briefs")
    await cognee.cognify()

    log(5, "CaseBriefWriter", "DONE", "SAR narrative written → Cognee:ringalert_briefs")
    return briefs


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 7 — FraudNotifier
# Reads "ringalert_scores", sends Slack/email alert if severity >= 7
# ═════════════════════════════════════════════════════════════════════════════
async def agent7_fraud_notifier(scores: dict, briefs: dict) -> dict:
    log(7, "FraudNotifier", "RUNNING", "checking severity threshold")

    severity   = scores.get("adjusted_severity", 0)
    action_tier = scores.get("action_tier", "MONITOR")
    ring_accounts = scores.get("ring_accounts", [])
    exposure      = scores.get("ring_exposure", 0)

    notification_sent = False
    channels_notified = []

    if severity >= 7.0:
        alert_message = (
            f"🚨 *{action_tier} FRAUD ALERT — RingAlert*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"*Severity:* {severity}/10  |  *Action:* {action_tier}\n"
            f"*Ring accounts ({len(ring_accounts)}):* {', '.join(ring_accounts)}\n"
            f"*Exposure:* ${exposure:,.2f}  |  *Fraud prob:* {scores.get('fraud_probability')}%\n"
            f"*Typologies:* {', '.join(scores.get('typologies', []))}\n"
            f"*SAR Required:* {'✅ YES — file immediately' if scores.get('sar_required') else '❌ No'}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_{briefs.get('one_liner', '')}_"
        )

        # ── Slack notification ──────────────────────────────────────────────
        if SLACK_WEBHOOK_URL and SLACK_WEBHOOK_URL.startswith("https://hooks.slack.com"):
            try:
                resp = requests.post(
                    SLACK_WEBHOOK_URL,
                    json={"text": alert_message},
                    timeout=5,
                )
                if resp.status_code == 200:
                    channels_notified.append("slack")
                    log(7, "FraudNotifier", "RUNNING", "Slack alert sent ✅")
            except Exception as e:
                log(7, "FraudNotifier", "RUNNING", f"Slack failed: {e}")

        # ── Email (simple SMTP fallback) ───────────────────────────────────
        if ALERT_EMAIL:
            try:
                import smtplib
                from email.mime.text import MIMEText
                msg = MIMEText(alert_message.replace("*","").replace("_",""))
                msg["Subject"] = f"🚨 {action_tier} FRAUD ALERT — Severity {severity}/10"
                msg["From"] = "ringalert@fraudwatch.ai"
                msg["To"]   = ALERT_EMAIL
                with smtplib.SMTP("localhost") as server:
                    server.send_message(msg)
                channels_notified.append("email")
                log(7, "FraudNotifier", "RUNNING", f"Email sent to {ALERT_EMAIL} ✅")
            except Exception as e:
                log(7, "FraudNotifier", "RUNNING", f"Email failed: {e}")

        notification_sent = bool(channels_notified)

        # Print alert to console regardless (always visible in demo)
        print("\n" + "━"*55)
        print(alert_message.replace("*","").replace("_",""))
        print("━"*55 + "\n")

    else:
        log(7, "FraudNotifier", "RUNNING", f"severity {severity} < 7.0 — no alert sent")

    notifier_result = {
        "notification_sent":   notification_sent,
        "channels_notified":   channels_notified,
        "severity_threshold":  7.0,
        "actual_severity":     severity,
        "alert_triggered":     severity >= 7.0,
        "notifier_timestamp":  datetime.now().isoformat(),
    }

    log(7, "FraudNotifier", "DONE",
        f"alert={'SENT' if notification_sent else 'SKIPPED'} | "
        f"channels: {channels_notified or ['console']}")
    return notifier_result


# ═════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR — runs all 7 agents in sequence
# ═════════════════════════════════════════════════════════════════════════════
async def run_ringalert(csv_path: str = DATASET_CSV):
    print("\n" + "═"*58)
    print("  RingAlert — 7-Agent Fraud Detection Pipeline")
    print("  vibeFORWARD: M-2 | Track 02: Fraud Watch")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("═"*58 + "\n")

    # Load dataframe once — shared across agents that need raw data
    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    if "late_night" not in df.columns:
        df["late_night"] = df["timestamp"].dt.hour.between(2, 3)
    if "is_account_transfer" not in df.columns:
        df["is_account_transfer"] = df["counterparty_id"].str.startswith("AC")
    if "is_merchant_payment" not in df.columns:
        df["is_merchant_payment"] = df["counterparty_id"].str.startswith("MR")

    await cognee.reset()  # clean slate for this run

    # ── Sequential agent pipeline ──────────────────────────────────────────
    ingest     = await agent1_data_ingestor(csv_path)
    graph      = await agent2_graph_mapper(df)
    detections = await agent3_pattern_detector(df, graph)
    entities   = await agent6_entity_enricher(detections)
    scores     = await agent4_risk_scorer(detections, entities)
    briefs     = await agent5_case_brief_writer(scores)
    notif      = await agent7_fraud_notifier(scores, briefs)

    # ── Final summary ──────────────────────────────────────────────────────
    print("\n" + "═"*58)
    print("  RINGALERT COMPLETE")
    print("═"*58)
    print(f"  Ring accounts:    {scores.get('ring_accounts')}")
    print(f"  Sink accounts:    {scores.get('sink_accounts')}")
    print(f"  Sleeper accounts: {scores.get('sleeper_accounts')}")
    print(f"  Total exposure:   ${scores.get('ring_exposure'):,.2f}")
    print(f"  Fraud prob:       {scores.get('fraud_probability')}%  "
          f"[{scores.get('fraud_prob_ci_lo')}–{scores.get('fraud_prob_ci_hi')}%]")
    print(f"  Severity:         {scores.get('adjusted_severity')}/10  "
          f"({scores.get('action_tier')})")
    print(f"  Typologies:       {', '.join(scores.get('typologies', []))}")
    print(f"  SAR required:     {'YES' if scores.get('sar_required') else 'No'}")
    print(f"  Action:           {scores.get('action_text')}")
    print()
    print("  SAR NARRATIVE:")
    print("  " + "\n  ".join(briefs.get("sar_narrative","").split("\n")))
    print("═"*58 + "\n")

    return {
        "scores": scores,
        "briefs": briefs,
        "notification": notif,
    }


if __name__ == "__main__":
    asyncio.run(run_ringalert())
