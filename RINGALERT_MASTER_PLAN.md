# RingAlert — Master Project Plan
## vibeFORWARD: M-2 | Track 02: Fraud Watch | June 7, 2026

---

## THE IDEA

**Product:** RingAlert  
**One sentence:** A multi-agent fraud detection tool that maps 5,000 bank transactions into a knowledge graph and surfaces a hidden 12-account fraud ring that threshold-based rules missed — giving analysts a 3-minute visual case brief with a Bayesian risk score.

**The problem:** A bank's fraud ring stayed under every alert threshold. Small transactions. Circular flows. Coordinated accounts. No single rule catches it — but the pattern is obvious once you see the graph.

**End user:** The fraud analyst with 3 minutes per case. No SQL. No code. Just: upload CSV → run → see the ring → flag or dismiss.

**Why we win:** Cognee is a graph-native memory engine. Fraud rings ARE a graph problem. The fit is exact. The judging rubric literally says "via Cognee" for criterion #2.

---

## THE DATASET

**Source:** https://www.kaggle.com/datasets/quantologist/track02-vibeforward-m-agents  
**Contents:** 5,000 bank transactions with a 12-account fraud ring hidden inside  
**Target:** Surface all 12 accounts — judges hold a hidden answer key (bonus credibility)  
**Download as:** `track02_transactions.csv`

---

## THE FIVE-AGENT PIPELINE

All agents hand off through **Cognee**. No exceptions. This is what criterion #2 scores.

```
CSV File
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│                    COGNEE MEMORY LAYER                      │
│   (Every agent reads from and writes to this — R02)        │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────┐
│  AGENT 1 — DataIngestor             │  Step 1: Find It
│  Input:  track02_transactions.csv   │
│  Action: Normalize fields, parse    │
│  Output: Entities + transactions    │
│  Cognee: cognee.remember(payload)   │
└──────────────────────────────────────┘
   │ (reads from Cognee)
   ▼
┌──────────────────────────────────────┐
│  AGENT 2 — GraphMapper              │  Step 2: Rank It
│  Input:  Entities from Cognee       │
│  Action: Build directed graph       │
│          Score each edge pair       │
│          Flag micro-transactions    │
│  Output: Enriched graph + scores    │
│  Cognee: recall() → process → remember()
└──────────────────────────────────────┘
   │ (reads from Cognee)
   ▼
┌──────────────────────────────────────┐
│  AGENT 3 — PatternDetector          │  Step 3: Act On It
│  Input:  Graph from Cognee          │
│  Action: DFS cycle detection        │
│          Circular flow finder       │
│          Coordinated timing check   │
│  Output: Flagged fraud rings        │
│  Cognee: recall() → detect → remember()
└──────────────────────────────────────┘
   │ (reads from Cognee)
   ▼
┌──────────────────────────────────────┐
│  AGENT 4 — RiskScorer               │  Step 4: Explain It
│  Input:  Flagged rings from Cognee  │
│  Action: PyMC Bayesian inference    │
│          "94% fraud prob ±3%"       │
│          Generate downloadable PDF  │  ← R08 REQUIRED
│  Output: Scored rings + narrative   │
│  Cognee: recall() → score → remember()
└──────────────────────────────────────┘
   │ (reads from Cognee)
   ▼
┌──────────────────────────────────────┐
│  AGENT 5 — CaseBriefWriter          │  Step 5: Show It
│  Input:  All results from Cognee    │
│  Action: Claude API → plain English │
│          3-sentence case brief      │
│  Output: Brief → UI right panel     │
│  Cognee: recall() → write briefs    │
└──────────────────────────────────────┘
   │
   ▼
UI Dashboard (Lovable)
  Left panel: Network graph (fraud ring highlighted red)
  Right panel: Case brief + risk score + Flag/Dismiss buttons
```

---

## WHAT EACH AGENT DETECTS

**Agent 3 finds three fraud patterns:**

1. **Circular flows** — Money moving in a loop: A→B→C→A. The accounts rotate funds so no single transfer looks large. DFS cycle detection catches it.

2. **Micro-transactions** — Repeated transactions just below the $500 alert threshold (e.g. $482, $491, $478). Each is individually harmless. The pattern across 12 accounts is fraud.

3. **Coordinated timing** — Unrelated accounts transacting in synchronized bursts. A fraudster controls multiple accounts and moves money at the same time to obscure the pattern.

---

## TECH STACK SETUP

### Install everything
```bash
pip install cognee anthropic pymc pandas numpy --break-system-packages
```

### API keys needed
```bash
export ANTHROPIC_API_KEY="sk-ant-..."     # from console.anthropic.com
export COGNEE_API_KEY="your-key-here"     # from cognee.ai after signup
```

### Run the pipeline
```bash
python ringalert_agents.py
```

### UI
Paste `lovable_ui_prompt.md` into https://lovable.dev — generates the full dashboard.

### IDE
Use https://lingcode.dev/try — browser-based, Claude Code + Codex built in, no install.

---

## MANDATORY TOOLS (submission invalid without these)

| Tool | What it does | Where |
|------|-------------|-------|
| **Cognee** | Memory layer between ALL agents | cognee.ai · pip install cognee |
| **Trupeer** | 5-minute demo video (NO VIDEO = DQ) | app.trupeer.ai/auth |
| **Geodo** | Domain Expert researches real entities | geodo.ai (request access first) |

---

## TEAM ROLES

| Role | Owns | What to do RIGHT NOW |
|------|------|---------------------|
| **Builder** | Agents 1–5, GitHub | Install packages, add API keys, run pipeline |
| **Designer** | Step 0 PDF, Lovable UI | Submit brief to Devpost, paste Lovable prompt |
| **Domain Expert** | Geodo research, Agent 4 narrative | Sign up for Geodo, start entity research |
| **Presenter** | Trupeer video, live demo | Set up Trupeer trial, read demo script |

---

## BUILD ORDER (11 AM → 5 PM)

| Time | Task | Owner |
|------|------|-------|
| 11:00 | **Submit Step 0 to Devpost FIRST** | Designer |
| 11:20 | Download Kaggle CSV, install packages, run Agent 1 | Builder |
| 11:50 | Agent 2 — GraphMapper, verify Cognee handoff | Builder |
| 12:00 | Sign up Geodo, start entity research | Domain Expert |
| 12:30 | Lunch — Agent 3 running | Everyone |
| 1:00 | Verify Agent 3 flags fraud rings | Builder |
| 1:00 | Paste Lovable prompt, build UI | Designer |
| 2:00 | Agent 4 — PyMC scoring live | Builder |
| 2:00 | Write Agent 4 downloadable narrative | Domain Expert |
| 2:30 | Connect UI to real pipeline output | Builder + Designer |
| 2:45 | Agent 5 — CaseBriefWriter, full end-to-end test | Builder |
| 3:15 | Polish: add "why" labels, cold-use test with teammate | All |
| 3:45 | **Record Trupeer demo (5 min)** | Presenter |
| 4:00 | Science fair — judges walk room | Presenter |
| **4:30** | **Final Devpost submission** | Designer |
| **5:00** | **SUBMISSIONS CLOSE — NO EXTENSIONS** | — |

---

## JUDGING — HOW TO SCORE 5/5 ON EACH

**Criterion 1 — Agents that work (5 pts)**  
Agent 1 must run on the real Kaggle CSV. Build ingestion first. Nothing else matters if this fails.

**Criterion 2 — Real collaboration via Cognee (5 pts)**  
Every agent uses `cognee.remember()` to write and `cognee.recall()` to read. The handoff IS Cognee. Not a function call between agents — Cognee.

**Criterion 3 — Matches your brief (5 pts)**  
Submit the Product Brief PDF (already built) before writing code. Write it conservatively. You're judged against your OWN promises.

**Criterion 4 — End user can use it cold (5 pts)**  
Upload CSV → Run → Fraud ring appears → Read brief → Flag or Dismiss. A judge at 4 PM with zero context must be able to do this in under 3 minutes.

**Criterion 5 — Explainable (5 pts)**  
Every output has a visible reason. Risk score shows "why" (3 circular flows, 47 micro-transactions, coordinated timing). No black box outputs. Labels on every node and edge.

---

## DEVPOST SUBMISSION CHECKLIST

- [ ] Product Brief PDF (`RingAlert_Step0_ProductBrief.pdf`)
- [ ] GitHub repo link (public, with README)
- [ ] Trupeer video URL (5 minutes, narrated)
- [ ] Track selection: Track 02 — Fraud Watch
- [ ] Written product description

Submit at: https://vibeforward-m2-agents.devpost.com  
Team verification: https://forms.gle/HGoa9fKruQEHazLAA

---

## PRIZE TARGETS

| Prize | Amount | How to get it |
|-------|--------|--------------|
| 1st Place | $1,500 cash | Score 25/25, find all 12 fraud accounts |
| PyMC Special | $2,000 course | Use PyMC in Agent 4 for Bayesian scoring |
| Best Trupeer | $200 cash | Best 5-min demo video |
| Geodo Top Team | $3,000 (3 Pro accounts) | Domain Expert uses Geodo for entity research |
| **Best possible haul** | **$4,700+** | All of the above |

---

## FILES IN THIS FOLDER

| File | What it is |
|------|-----------|
| `RingAlert_Step0_ProductBrief.pdf` | Submit to Devpost first |
| `ringalert_agents.py` | Full 5-agent Python pipeline |
| `lovable_ui_prompt.md` | Paste into Lovable to build the UI |
| `trupeer_demo_script.md` | 5-minute narrated demo script |
| `ringalert_workflow.html` | Open in browser — full visual workflow |
| `RINGALERT_MASTER_PLAN.md` | This file |

---

## KEY LINKS

| Resource | URL |
|----------|-----|
| Hackathon resources | https://vibe-forward.vercel.app/ |
| Devpost submission | https://vibeforward-m2-agents.devpost.com/ |
| Track 02 dataset | https://www.kaggle.com/datasets/quantologist/track02-vibeforward-m-agents |
| Cognee | https://cognee.ai |
| Cognee Discord | https://discord.gg/5SHNNhe7t |
| Trupeer | https://app.trupeer.ai/auth |
| Geodo | https://geodo.ai |
| LingCode IDE | https://lingcode.dev/try |
| Decision Hub (PyMC skills) | https://hub.decision.ai |
| PyMC Discord | https://discord.com/invite/tUSMHWJEyR |
| Lovable UI builder | https://lovable.dev |

---

*RingAlert · vibeFORWARD: M-2 · Track 02: Fraud Watch · June 7, 2026*
