"""
RingAlert — Multi-Agent Fraud Detection Pipeline
vibeFORWARD: M-2 | Track 02: Fraud Watch | June 7, 2026

Architecture (all handoffs via Cognee):
  Agent 1 — DataIngestor    → reads CSV, stores entities to Cognee
  Agent 2 — GraphMapper     → reads Cognee, builds relationship graph
  Agent 3 — PatternDetector → reads graph, flags circular flows & rings
  Agent 4 — RiskScorer      → reads flags, scores with PyMC Bayesian inference
  Agent 5 — CaseBriefWriter → reads scores, writes plain-English case briefs

Requirements:
  pip install cognee anthropic pandas numpy pymc --break-system-packages
"""

import os
import json
import asyncio
import pandas as pd
import numpy as np
from collections import defaultdict
from datetime import datetime
import anthropic

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION — fill in your keys
# ─────────────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-key-here")
COGNEE_API_KEY    = os.getenv("COGNEE_API_KEY", "your-cognee-key-here")
DATASET_CSV       = "track02_transactions.csv"   # path to the Kaggle CSV

# ─────────────────────────────────────────────────────────────────────────────
# Cognee setup
# ─────────────────────────────────────────────────────────────────────────────
import cognee
cognee.config.set_llm_provider("anthropic")
cognee.config.set_llm_api_key(ANTHROPIC_API_KEY)

# ─────────────────────────────────────────────────────────────────────────────
# STATUS PRINTER — shows live agent progress (mirrors the UI status bar)
# ─────────────────────────────────────────────────────────────────────────────
def status(agent_num: int, name: str, state: str, detail: str = ""):
    icon = {"RUNNING": "🟡", "DONE": "🟢", "ERROR": "🔴"}.get(state, "⚪")
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {icon} Agent {agent_num} — {name}: {state}  {detail}")


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 1 — DataIngestor
# Step 1: Find It
# Reads the raw CSV, normalises fields, stores every entity & transaction to Cognee
# ═════════════════════════════════════════════════════════════════════════════
async def agent1_data_ingestor(csv_path: str) -> dict:
    status(1, "DataIngestor", "RUNNING", "loading CSV")
    df = pd.read_csv(csv_path)

    # Normalise column names to lowercase snake_case
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Expected columns: transaction_id, sender_account, receiver_account, amount, timestamp
    # Rename common variants
    rename_map = {
        "from": "sender_account", "to": "receiver_account",
        "from_account": "sender_account", "to_account": "receiver_account",
        "value": "amount", "date": "timestamp", "time": "timestamp",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # Convert amount to float, drop nulls
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df.dropna(subset=["sender_account", "receiver_account", "amount"], inplace=True)

    # Build structured payload for Cognee
    payload = {
        "dataset": "track02_fraud_transactions",
        "total_rows": len(df),
        "accounts": list(set(df["sender_account"].tolist() + df["receiver_account"].tolist())),
        "transactions": df.to_dict(orient="records"),
        "ingestion_timestamp": datetime.now().isoformat(),
    }

    # Store to Cognee memory layer
    await cognee.add(json.dumps(payload), dataset_name="ringalert")
    await cognee.cognify()

    status(1, "DataIngestor", "DONE", f"{len(df)} transactions | {len(payload['accounts'])} accounts → Cognee")
    return payload


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 2 — GraphMapper
# Step 2: Rank It
# Retrieves from Cognee, builds directed relationship graph, stores enriched graph
# ═════════════════════════════════════════════════════════════════════════════
async def agent2_graph_mapper() -> dict:
    status(2, "GraphMapper", "RUNNING", "reading from Cognee")

    # Recall the ingested data from Cognee
    results = await cognee.search("track02_fraud_transactions ingestion", query_type="GRAPH_COMPLETION")
    raw = results[0] if results else {}

    # Re-parse transactions from stored payload
    transactions = raw.get("transactions", [])
    if not transactions:
        raise RuntimeError("GraphMapper: no transactions found in Cognee — did Agent 1 run?")

    # Build directed graph: edge_key → {count, total_amount, timestamps}
    graph = defaultdict(lambda: {"count": 0, "total_amount": 0.0, "timestamps": []})
    for tx in transactions:
        src = str(tx.get("sender_account", ""))
        dst = str(tx.get("receiver_account", ""))
        amt = float(tx.get("amount", 0))
        ts  = str(tx.get("timestamp", ""))
        if src and dst:
            graph[f"{src}→{dst}"]["count"] += 1
            graph[f"{src}→{dst}"]["total_amount"] += amt
            graph[f"{src}→{dst}"]["timestamps"].append(ts)

    # Suspicion heuristic: high frequency + small amounts → micro-transaction flag
    MICRO_THRESHOLD = 500.0
    for edge, data in graph.items():
        avg_amount = data["total_amount"] / max(data["count"], 1)
        data["avg_amount"] = round(avg_amount, 2)
        data["micro_flag"] = avg_amount < MICRO_THRESHOLD and data["count"] > 3
        data["suspicion_score"] = (
            (1.0 if data["micro_flag"] else 0.0) +
            min(data["count"] / 10.0, 1.0)
        )

    enriched_graph = {
        "edges": dict(graph),
        "total_edges": len(graph),
        "mapper_timestamp": datetime.now().isoformat(),
    }

    await cognee.add(json.dumps(enriched_graph), dataset_name="ringalert_graph")
    await cognee.cognify()

    top_edges = sorted(graph.items(), key=lambda x: x[1]["suspicion_score"], reverse=True)[:5]
    status(2, "GraphMapper", "DONE", f"{len(graph)} edges mapped | top suspicious: {[e[0] for e in top_edges]} → Cognee")
    return enriched_graph


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 3 — PatternDetector
# Step 3: Act On It
# Reads graph from Cognee, detects circular flows, micro-tx, coordinated timing
# ═════════════════════════════════════════════════════════════════════════════
async def agent3_pattern_detector() -> dict:
    status(3, "PatternDetector", "RUNNING", "reading graph from Cognee")

    results = await cognee.search("ringalert_graph edges suspicion", query_type="GRAPH_COMPLETION")
    raw = results[0] if results else {}
    edges = raw.get("edges", {})

    if not edges:
        raise RuntimeError("PatternDetector: no graph edges found in Cognee — did Agent 2 run?")

    # Build adjacency list
    adj = defaultdict(set)
    for edge_key in edges:
        parts = edge_key.split("→")
        if len(parts) == 2:
            adj[parts[0]].add(parts[1])

    # ── Detect circular flows (DFS cycle detection, max depth 5) ──
    def find_cycles(start, node, path, visited_edges, depth=0):
        if depth > 5:
            return []
        cycles = []
        for neighbor in adj.get(node, set()):
            edge = f"{node}→{neighbor}"
            if neighbor == start and len(path) >= 2:
                cycles.append(path + [neighbor])
            elif neighbor not in path and edge not in visited_edges:
                cycles.extend(find_cycles(start, neighbor, path + [neighbor],
                                          visited_edges | {edge}, depth + 1))
        return cycles

    all_cycles = []
    for account in list(adj.keys())[:200]:  # cap for performance
        found = find_cycles(account, account, [account], set())
        all_cycles.extend(found)

    # Deduplicate cycles (canonicalise by sorted tuple)
    unique_cycles = []
    seen = set()
    for cycle in all_cycles:
        key = tuple(sorted(cycle))
        if key not in seen:
            seen.add(key)
            unique_cycles.append(cycle)

    # ── Detect micro-transaction clusters ──
    micro_accounts = set()
    for edge_key, data in edges.items():
        if data.get("micro_flag"):
            parts = edge_key.split("→")
            micro_accounts.update(parts)

    # ── Build fraud ring candidates ──
    ring_accounts = set()
    for cycle in unique_cycles:
        ring_accounts.update(cycle)
    ring_accounts.update(micro_accounts)

    flagged_rings = []
    for i, cycle in enumerate(unique_cycles[:20]):  # top 20
        ring_edges = []
        for j in range(len(cycle) - 1):
            edge_key = f"{cycle[j]}→{cycle[j+1]}"
            ring_edges.append({
                "edge": edge_key,
                "data": edges.get(edge_key, {}),
            })
        flagged_rings.append({
            "ring_id": f"RING-{i+1:03d}",
            "accounts": cycle,
            "num_accounts": len(set(cycle)),
            "edges": ring_edges,
            "pattern_type": "circular_flow",
            "evidence": f"Circular flow: {' → '.join(cycle)}",
        })

    detection_result = {
        "flagged_rings": flagged_rings,
        "total_rings_detected": len(flagged_rings),
        "ring_accounts": list(ring_accounts),
        "micro_transaction_accounts": list(micro_accounts),
        "detector_timestamp": datetime.now().isoformat(),
    }

    await cognee.add(json.dumps(detection_result), dataset_name="ringalert_detections")
    await cognee.cognify()

    status(3, "PatternDetector", "DONE",
           f"{len(flagged_rings)} rings flagged | {len(ring_accounts)} suspicious accounts → Cognee")
    return detection_result


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 4 — RiskScorer
# Step 4: Explain It
# Reads flags from Cognee, applies PyMC Bayesian scoring with confidence intervals
# ═════════════════════════════════════════════════════════════════════════════
async def agent4_risk_scorer() -> dict:
    status(4, "RiskScorer", "RUNNING", "reading detections from Cognee")

    results = await cognee.search("ringalert_detections flagged_rings", query_type="GRAPH_COMPLETION")
    raw = results[0] if results else {}
    flagged_rings = raw.get("flagged_rings", [])

    if not flagged_rings:
        status(4, "RiskScorer", "DONE", "no rings to score")
        return {"scored_rings": [], "scorer_timestamp": datetime.now().isoformat()}

    import pymc as pm

    scored_rings = []
    for ring in flagged_rings:
        num_edges      = len(ring.get("edges", []))
        num_accounts   = ring.get("num_accounts", 2)
        micro_count    = sum(1 for e in ring.get("edges", [])
                             if e.get("data", {}).get("micro_flag"))

        # Bayesian model: fraud probability given evidence features
        with pm.Model() as fraud_model:
            # Prior: base fraud rate in dataset ~3%
            p_base = pm.Beta("p_base", alpha=1.5, beta=48.5)

            # Evidence lifts
            edge_lift    = pm.Deterministic("edge_lift",    pm.math.sigmoid(num_edges / 5.0))
            account_lift = pm.Deterministic("account_lift", pm.math.sigmoid(num_accounts / 4.0))
            micro_lift   = pm.Deterministic("micro_lift",   pm.math.sigmoid(micro_count / 3.0))

            p_fraud = pm.Deterministic(
                "p_fraud",
                pm.math.clip(p_base + 0.4 * edge_lift + 0.3 * account_lift + 0.3 * micro_lift, 0, 1)
            )

            trace = pm.sample(500, tune=500, progressbar=False, random_seed=42,
                              nuts_sampler="nutpie" if False else "pymc")

        p_samples = trace.posterior["p_fraud"].values.flatten()
        mean_prob = float(np.mean(p_samples))
        ci_low    = float(np.percentile(p_samples, 5))
        ci_high   = float(np.percentile(p_samples, 95))
        ci_half   = round((ci_high - ci_low) / 2 * 100, 1)

        risk_level = "CRITICAL" if mean_prob > 0.85 else "HIGH" if mean_prob > 0.65 else "MEDIUM"

        scored_ring = {
            **ring,
            "fraud_probability": round(mean_prob * 100, 1),
            "confidence_interval": f"±{ci_half}%",
            "ci_low": round(ci_low * 100, 1),
            "ci_high": round(ci_high * 100, 1),
            "risk_level": risk_level,
            "score_explanation": (
                f"{round(mean_prob*100,1)}% fraud probability (90% CI: "
                f"{round(ci_low*100,1)}%–{round(ci_high*100,1)}%). "
                f"Evidence: {num_edges} transaction edges, {num_accounts} accounts in ring, "
                f"{micro_count} micro-transactions below threshold."
            ),
        }
        scored_rings.append(scored_ring)

    # Sort by fraud probability descending
    scored_rings.sort(key=lambda x: x["fraud_probability"], reverse=True)

    score_result = {
        "scored_rings": scored_rings,
        "scorer_timestamp": datetime.now().isoformat(),
    }

    await cognee.add(json.dumps(score_result), dataset_name="ringalert_scores")
    await cognee.cognify()

    top = scored_rings[0] if scored_rings else {}
    status(4, "RiskScorer", "DONE",
           f"top ring: {top.get('ring_id')} at {top.get('fraud_probability')}% ±{top.get('confidence_interval')} → Cognee")
    return score_result


# ═════════════════════════════════════════════════════════════════════════════
# AGENT 5 — CaseBriefWriter
# Step 5: Show It
# Reads everything from Cognee, writes plain-English 3-line case briefs
# ═════════════════════════════════════════════════════════════════════════════
async def agent5_case_brief_writer() -> list[dict]:
    status(5, "CaseBriefWriter", "RUNNING", "reading all results from Cognee")

    results = await cognee.search("ringalert_scores scored_rings fraud_probability", query_type="GRAPH_COMPLETION")
    raw = results[0] if results else {}
    scored_rings = raw.get("scored_rings", [])

    if not scored_rings:
        status(5, "CaseBriefWriter", "DONE", "no rings to write briefs for")
        return []

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    briefs = []

    for ring in scored_rings[:12]:  # top 12 (matching the 12-account ring in dataset)
        prompt = f"""You are a fraud analyst assistant. Write a 3-sentence case brief for an analyst
who has 3 minutes to decide whether to escalate this case. Be direct, specific, and actionable.
Use plain English — no jargon. The analyst is NOT technical.

Ring ID: {ring['ring_id']}
Accounts involved: {', '.join(str(a) for a in ring.get('accounts', []))}
Pattern: {ring.get('pattern_type', 'unknown')}
Evidence: {ring.get('evidence', 'N/A')}
Fraud probability: {ring.get('fraud_probability')}% {ring.get('confidence_interval', '')}
Risk level: {ring.get('risk_level', 'UNKNOWN')}
Score explanation: {ring.get('score_explanation', '')}

Write exactly 3 sentences:
1. What is happening (describe the money movement in plain English)
2. Why it looks like fraud (the specific suspicious pattern)
3. Recommended action with urgency"""

        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        brief_text = message.content[0].text.strip()

        brief = {
            "ring_id": ring["ring_id"],
            "risk_level": ring.get("risk_level"),
            "fraud_probability": ring.get("fraud_probability"),
            "confidence_interval": ring.get("confidence_interval"),
            "accounts": ring.get("accounts", []),
            "brief": brief_text,
            "score_explanation": ring.get("score_explanation"),
            "evidence": ring.get("evidence"),
        }
        briefs.append(brief)
        status(5, "CaseBriefWriter", "RUNNING",
               f"  Brief written for {ring['ring_id']} ({ring.get('fraud_probability')}%)")

    # Store final briefs to Cognee
    await cognee.add(json.dumps({"briefs": briefs}), dataset_name="ringalert_briefs")
    await cognee.cognify()

    status(5, "CaseBriefWriter", "DONE", f"{len(briefs)} case briefs written → Cognee")
    return briefs


# ═════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR — runs all 5 agents in sequence
# ═════════════════════════════════════════════════════════════════════════════
async def run_ringalert(csv_path: str = DATASET_CSV) -> list[dict]:
    print("\n" + "═"*60)
    print("  RingAlert — Multi-Agent Fraud Detection")
    print("  vibeFORWARD: M-2 | Track 02: Fraud Watch")
    print("═"*60 + "\n")

    await cognee.reset()  # fresh run

    payload     = await agent1_data_ingestor(csv_path)
    graph       = await agent2_graph_mapper()
    detections  = await agent3_pattern_detector()
    scores      = await agent4_risk_scorer()
    briefs      = await agent5_case_brief_writer()

    print("\n" + "─"*60)
    print(f"  Pipeline complete. {len(briefs)} fraud ring(s) surfaced.")
    print("─"*60)

    for b in briefs:
        print(f"\n{'━'*50}")
        print(f"  {b['ring_id']} | {b['risk_level']} | {b['fraud_probability']}% {b['confidence_interval']}")
        print(f"  Accounts: {', '.join(str(a) for a in b['accounts'])}")
        print(f"\n{b['brief']}")

    return briefs


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(run_ringalert())
