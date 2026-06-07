// Real dataset values computed from data/track02_clean.csv (Crestline Community Bank, Track 02).
// Ring accounts: AC-0001, AC-0005, AC-0009, AC-0010, AC-0011, AC-0012 (AC-0012 = sleeper).

export const RING_IDS = ['AC-0001', 'AC-0005', 'AC-0009', 'AC-0010', 'AC-0011', 'AC-0012']

export const SUMMARY = {
  ringAccounts: 6,
  totalExposure: 161751,
  ringTransactions: 292,
  thresholdHits: 0,
  avgRingTxn: 561,
  lateNightRate: 91,
  fraudProbability: 94,
  fraudProbCi: [91, 97],
  severity: 9.4,
  geodoMultiplier: 1.33,
}

export const ACCOUNTS = [
  { id: 'AC-0005', txns: 83, total: 53896.22, avg: 649.35, max: 898.89, lateNight: 1.0, daysOld: 13, near500: 5, near1000: 0, merchants: 2, regions: ['NJ'], isRing: true, riskScore: 79.2 },
  { id: 'AC-0009', txns: 42, total: 29120.71, avg: 693.35, max: 885.8, lateNight: 1.0, daysOld: 13, near500: 5, near1000: 0, merchants: 1, regions: ['NY'], isRing: true, riskScore: 79.2 },
  { id: 'AC-0001', txns: 42, total: 26985.76, avg: 642.52, max: 897.05, lateNight: 1.0, daysOld: 18, near500: 7, near1000: 0, merchants: 1, regions: ['PA'], isRing: true, riskScore: 79.0 },
  { id: 'AC-0011', txns: 52, total: 25919.11, avg: 498.44, max: 892.26, lateNight: 0.904, daysOld: 15, near500: 6, near1000: 0, merchants: 12, regions: ['NJ'], isRing: true, riskScore: 78.9 },
  { id: 'AC-0010', txns: 61, total: 27467.37, avg: 450.28, max: 893.33, lateNight: 0.836, daysOld: 21, near500: 6, near1000: 0, merchants: 20, regions: ['NJ'], isRing: true, riskScore: 71.3 },
  { id: 'AC-0016', txns: 20, total: 15977.29, avg: 798.86, max: 14941.26, lateNight: 0.45, daysOld: 226, near500: 0, near1000: 0, merchants: 20, regions: ['CA'], isRing: false, riskScore: 27.1 },
  { id: 'AC-0057', txns: 9, total: 919.16, avg: 102.13, max: 541.23, lateNight: 0.556, daysOld: 549, near500: 0, near1000: 0, merchants: 9, regions: ['CA'], isRing: false, riskScore: 26.1 },
  { id: 'AC-0020', txns: 15, total: 9048.86, avg: 603.26, max: 8644.86, lateNight: 0.4, daysOld: 640, near500: 0, near1000: 0, merchants: 15, regions: ['NY'], isRing: false, riskScore: 25.2 },
  { id: 'AC-0013', txns: 23, total: 12829.25, avg: 557.79, max: 12100.91, lateNight: 0.261, daysOld: 630, near500: 0, near1000: 0, merchants: 22, regions: ['PA'], isRing: false, riskScore: 24.9 },
  { id: 'AC-0019', txns: 18, total: 10728.03, avg: 596.0, max: 10052.89, lateNight: 0.389, daysOld: 778, near500: 0, near1000: 0, merchants: 18, regions: ['CT'], isRing: false, riskScore: 24.8 },
  { id: 'AC-0017', txns: 18, total: 13316.71, avg: 739.82, max: 12235.3, lateNight: 0.389, daysOld: 443, near500: 0, near1000: 0, merchants: 17, regions: ['PA'], isRing: false, riskScore: 24.8 },
  { id: 'AC-0031', txns: 23, total: 1029.33, avg: 44.75, max: 196.52, lateNight: 0.522, daysOld: 382, near500: 0, near1000: 0, merchants: 22, regions: ['NY'], isRing: false, riskScore: 24.8 },
  { id: 'AC-0015', txns: 16, total: 13261.3, avg: 828.83, max: 12672.95, lateNight: 0.375, daysOld: 683, near500: 0, near1000: 0, merchants: 16, regions: ['NY'], isRing: false, riskScore: 24.2 },
  { id: 'AC-0012', txns: 12, total: 488.45, avg: 40.7, max: 99.12, lateNight: 0.0, daysOld: 19, near500: 0, near1000: 0, merchants: 11, regions: ['CT'], isRing: true, riskScore: 20.8 },
  { id: 'AC-0198', txns: 22, total: 1341.3, avg: 60.97, max: 277.66, lateNight: 0.5, daysOld: 200, near500: 0, near1000: 0, merchants: 22, regions: ['PA'], isRing: false, riskScore: 24.0 },
  { id: 'AC-0232', txns: 24, total: 1032.49, avg: 43.02, max: 157.9, lateNight: 0.5, daysOld: 744, near500: 0, near1000: 0, merchants: 22, regions: ['CT'], isRing: false, riskScore: 24.0 },
  { id: 'AC-0098', txns: 24, total: 841.39, avg: 35.06, max: 163.58, lateNight: 0.458, daysOld: 106, near500: 0, near1000: 0, merchants: 24, regions: ['NY'], isRing: false, riskScore: 22.4 },
  { id: 'AC-0085', txns: 14, total: 375.16, avg: 26.8, max: 78.42, lateNight: 0.571, daysOld: 435, near500: 0, near1000: 0, merchants: 14, regions: ['NY'], isRing: false, riskScore: 21.7 },
  { id: 'AC-0183', txns: 11, total: 459.1, avg: 41.74, max: 117.45, lateNight: 0.545, daysOld: 446, near500: 0, near1000: 0, merchants: 11, regions: ['PA'], isRing: false, riskScore: 20.7 },
  { id: 'AC-0072', txns: 15, total: 720.8, avg: 48.05, max: 130.16, lateNight: 0.533, daysOld: 607, near500: 0, near1000: 0, merchants: 15, regions: ['CT'], isRing: false, riskScore: 20.3 },
]

export const HOURLY_RING = { 0: 48, 1: 52, 2: 56, 3: 51, 4: 49, 5: 8, 6: 2, 7: 1, 8: 2, 9: 1, 10: 2, 11: 2, 12: 2, 13: 1, 14: 1, 15: 1, 16: 0, 17: 1, 18: 1, 19: 2, 20: 1, 21: 2, 22: 2, 23: 10 }
export const HOURLY_NORM = { 0: 49, 1: 47, 2: 53, 3: 44, 4: 45, 5: 44, 6: 56, 7: 62, 8: 70, 9: 71, 10: 71, 11: 65, 12: 68, 13: 65, 14: 64, 15: 63, 16: 62, 17: 60, 18: 63, 19: 62, 20: 61, 21: 57, 22: 53, 23: 43 }

export const AGENTS = [
  { num: 1, name: 'DataIngestor', role: 'Statistical Analyst', dataset: 'ringalert', accent: 'blue' },
  { num: 2, name: 'GraphMapper', role: 'Sink + Co-occurrence', dataset: 'ringalert_graph', accent: 'violet' },
  { num: 3, name: 'PatternDetector', role: '5 Threat Signals', dataset: 'ringalert_detections', accent: 'orange' },
  { num: 6, name: 'EntityEnricher', role: 'Geodo Typology', dataset: 'ringalert_entities', accent: 'amber' },
  { num: 4, name: 'RiskScorer', role: 'PyMC Severity 0–10', dataset: 'ringalert_scores', accent: 'green' },
  { num: 5, name: 'CaseBriefWriter', role: 'SAR Narrative', dataset: 'ringalert_briefs', accent: 'violet' },
  { num: 7, name: 'FraudNotifier', role: 'Slack / Email Alert', dataset: 'external', accent: 'amber' },
]

export const COGNEE_KEYS = [
  { agent: 'Agent 1 → writes', key: 'ringalert{}', desc: 'account_stats, category_totals, coordinated_open_groups' },
  { agent: 'Agent 2 → reads ringalert, writes', key: 'ringalert_graph{}', desc: 'transfer_edges, sink_accounts, co_occurrence_pairs, merchant_cliques' },
  { agent: 'Agent 3 → reads graph, writes', key: 'ringalert_detections{}', desc: 'ring_accounts[], signals{}, raw_severity, sleeper_accounts' },
  { agent: 'Agent 6 → reads detections, writes', key: 'ringalert_entities{}', desc: 'typologies[ML-027, ML-008, ML-041], combined_multiplier, sar_required' },
  { agent: 'Agent 4 → reads entities, writes', key: 'ringalert_scores{}', desc: 'severity 9.4/10, fraud_prob 94%, action CRITICAL, CI [91–97%]' },
  { agent: 'Agent 5 → reads scores, writes', key: 'ringalert_briefs{}', desc: 'sar_narrative, one_liner, downloadable SAR document' },
]

// Live agent log timeline (delay in ms, relative to run start).
export const LOGS = [
  { delay: 0, agent: '[system]', cls: 'sys', msg: 'Initializing RingAlert — 7-agent pipeline · loading 5,000 transactions from Cognee' },
  { delay: 500, agent: '[agent-1]', cls: 'a1', msg: 'START: DataIngestor — computing per-account statistics (294 accounts)', event: 'start-1' },
  { delay: 900, agent: '[agent-1]', cls: 'a1', msg: 'Coordinated open window detected: 6 accounts opened Feb 10–18 2026 (8-day window)', type: 'warn' },
  { delay: 1200, agent: '[agent-1]', cls: 'a1', msg: 'Services category: $161,751 of $190,623 total = 84.9% account-to-account layering', type: 'warn' },
  { delay: 1500, agent: '[cognee]', cls: 'sys', msg: 'WRITE → Cognee:ringalert · account_stats{294}, category_totals{7}, coordinated_open_groups{1}' },
  { delay: 1800, agent: '[agent-1]', cls: 'a1', msg: 'DONE: 294 accounts profiled · 6 coordinated-open flagged → Cognee:ringalert', event: 'done-1' },
  { delay: 2200, agent: '[agent-2]', cls: 'a2', msg: 'START: GraphMapper — reading Cognee:ringalert · building transfer + co-occurrence graphs', event: 'start-2' },
  { delay: 2500, agent: '[cognee]', cls: 'sys', msg: 'READ ← Cognee:ringalert · account_stats{294}' },
  { delay: 2900, agent: '[agent-2]', cls: 'a2', msg: 'Transfer graph: sink accounts found — AC-0002, AC-0003, AC-0006, AC-0007 (receive only, never send)', type: 'warn' },
  { delay: 3200, agent: '[agent-2]', cls: 'a2', msg: 'Coordinated open group confirmed: [AC-0001, AC-0005, AC-0009, AC-0010, AC-0011, AC-0012]', type: 'alert' },
  { delay: 3500, agent: '[agent-2]', cls: 'a2', msg: 'AC-0012 SLEEPER: avg=$41, late_night=0% — invisible to timing/amount rules, visible only via graph' },
  { delay: 3800, agent: '[cognee]', cls: 'sys', msg: 'WRITE → Cognee:ringalert_graph · transfer_edges, sink_accounts[4], merchant_cliques[1]' },
  { delay: 4100, agent: '[agent-2]', cls: 'a2', msg: 'DONE: 4 sink accounts · 1 clique (6 members) → Cognee:ringalert_graph', event: 'done-2' },
  { delay: 4500, agent: '[agent-3]', cls: 'a3', msg: 'START: PatternDetector — reading Cognee:ringalert_graph · scoring 5 threat signals', event: 'start-3' },
  { delay: 4800, agent: '[cognee]', cls: 'sys', msg: 'READ ← Cognee:ringalert_graph · sink_accounts, merchant_cliques' },
  { delay: 5100, agent: '[agent-3]', cls: 'a3', msg: 'Signal 1 — Category capture: 84.9% services volume is ring fraud [score: 3.4/4.0]', type: 'warn' },
  { delay: 5400, agent: '[agent-3]', cls: 'a3', msg: 'Signal 2 — Structuring: 29 txns near $500, 44 near $900 — two bands [score: 2.5/2.5]', type: 'warn' },
  { delay: 5700, agent: '[agent-3]', cls: 'a3', msg: 'Signal 3 — Mule coordination: 4 sink accounts confirmed [score: 2.0/2.0]', type: 'warn' },
  { delay: 6000, agent: '[agent-3]', cls: 'a3', msg: 'Signal 4 — Burst velocity: 16 transactions under 60 seconds [score: 1.0/1.0]' },
  { delay: 6300, agent: '[agent-3]', cls: 'a3', msg: 'Signal 5 — Sleeper AC-0012 activated via merchant graph [score: 0.5/0.5]', type: 'alert' },
  { delay: 6600, agent: '[cognee]', cls: 'sys', msg: 'WRITE → Cognee:ringalert_detections · ring_accounts[6], raw_severity=9.4, signals{}' },
  { delay: 6900, agent: '[agent-3]', cls: 'a3', msg: 'DONE: raw_severity=9.4/10 · ring confirmed [AC-0001,0005,0009,0010,0011,0012]', event: 'done-3' },
  { delay: 7300, agent: '[agent-6]', cls: 'a6', msg: 'START: EntityEnricher — querying Geodo for FinCEN typology matching', event: 'start-6' },
  { delay: 7600, agent: '[cognee]', cls: 'sys', msg: 'READ ← Cognee:ringalert_detections · signals{}, ring_accounts[6]' },
  { delay: 8000, agent: '[agent-6]', cls: 'a6', msg: 'Geodo query: "layering peer-to-peer account transfers services category"' },
  { delay: 8300, agent: '[agent-6]', cls: 'a6', msg: 'Geodo → ML-027: Layering via P2P Transfers · SAR mandatory · multiplier ×1.15', type: 'alert' },
  { delay: 8600, agent: '[agent-6]', cls: 'a6', msg: 'Geodo query: "structuring sub-threshold dual-band $500 $900"' },
  { delay: 8900, agent: '[agent-6]', cls: 'a6', msg: 'Geodo → ML-008: Structuring (31 USC §5324) · multiplier ×1.10', type: 'alert' },
  { delay: 9200, agent: '[agent-6]', cls: 'a6', msg: 'Geodo → ML-041: Coordinated Mule Network · multiplier ×1.08', type: 'alert' },
  { delay: 9500, agent: '[cognee]', cls: 'sys', msg: 'WRITE → Cognee:ringalert_entities · typologies[ML-027,ML-008,ML-041] · combined_multiplier=1.33' },
  { delay: 9800, agent: '[agent-6]', cls: 'a6', msg: 'DONE: 3 typologies matched · sar_required=true · severity multiplier ×1.33', event: 'done-6' },
  { delay: 10200, agent: '[agent-4]', cls: 'a4', msg: 'START: RiskScorer — PyMC Bayesian inference on 5 signals + Geodo multipliers', event: 'start-4' },
  { delay: 10500, agent: '[cognee]', cls: 'sys', msg: 'READ ← Cognee:ringalert_entities · combined_multiplier=1.33' },
  { delay: 10900, agent: '[agent-4]', cls: 'a4', msg: 'PyMC: sampling posterior (1000 draws)... Beta(2,48) prior · 5 signal likelihoods' },
  { delay: 11400, agent: '[agent-4]', cls: 'a4', msg: 'PyMC result: fraud_prob=94% (95% CI: 91%–97%) · raw_severity=9.4 × 1.33 → 10.0', type: 'alert' },
  { delay: 11700, agent: '[agent-4]', cls: 'a4', msg: 'Action tier: CRITICAL · SAR mandatory · freeze accounts · law enforcement referral' },
  { delay: 12000, agent: '[cognee]', cls: 'sys', msg: 'WRITE → Cognee:ringalert_scores · severity=9.4, fraud_prob=94%, action=CRITICAL' },
  { delay: 12300, agent: '[agent-4]', cls: 'a4', msg: 'DONE: severity 9.4/10 CRITICAL → Cognee:ringalert_scores', event: 'done-4' },
  { delay: 12700, agent: '[agent-5]', cls: 'a5', msg: 'START: CaseBriefWriter — generating SAR narrative via Claude API', event: 'start-5' },
  { delay: 13000, agent: '[cognee]', cls: 'sys', msg: 'READ ← Cognee:ringalert_scores · all signals and typologies' },
  { delay: 13500, agent: '[agent-5]', cls: 'a5', msg: 'Claude API: writing FinCEN-format SAR narrative (4 sections)...' },
  { delay: 14200, agent: '[agent-5]', cls: 'a5', msg: 'SAR narrative complete · downloadable · 31 CFR 1020.320 compliant', type: 'alert' },
  { delay: 14500, agent: '[cognee]', cls: 'sys', msg: 'WRITE → Cognee:ringalert_briefs · sar_narrative, one_liner, pdf_ready=true' },
  { delay: 14800, agent: '[agent-5]', cls: 'a5', msg: 'DONE: SAR ready for download → Cognee:ringalert_briefs', event: 'done-5' },
  { delay: 15200, agent: '[agent-7]', cls: 'a7', msg: 'START: FraudNotifier — severity 9.4 ≥ 7.0 threshold · sending CRITICAL alert', event: 'start-7' },
  { delay: 15500, agent: '[agent-7]', cls: 'a7', msg: 'CRITICAL ALERT fired → Slack + email · ring_accounts[6] · exposure=$161,751', type: 'alert' },
  { delay: 15800, agent: '[agent-7]', cls: 'a7', msg: 'DONE: alert dispatched to compliance team', event: 'done-7' },
  { delay: 16200, agent: '[system]', cls: 'sys', msg: '━━ Pipeline complete ━━ Ring: AC-0001,0005,0009,0010,0011,0012 · $161,751 · SAR filed' },
]

export const TYPOLOGIES = [
  { code: 'ML-027', name: 'Layering via P2P Transfers', mult: '×1.15' },
  { code: 'ML-008', name: 'Sub-threshold Structuring', mult: '×1.10' },
  { code: 'ML-041', name: 'Coordinated Mule Network', mult: '×1.08' },
]

export const EVIDENCE_SIGNALS = [
  {
    n: 1,
    title: 'Coordinated account creation',
    source: 'Agent 1 · Cognee: account_stats.days_old',
    detail: 'All 6 accounts opened within an 8-day window (Feb 10–18 2026). Threshold: <30 days old at window start. Population baseline: 99% of 294 accounts were >90 days old.',
  },
  {
    n: 2,
    title: 'Late-night exclusivity',
    source: 'Agent 1 · Cognee: account_stats.late_night_pct',
    detail: 'Ring accounts: 91.4% of transactions between 11pm–5am. Normal population: 25% late-night rate. Threshold: >80% late-night = high anomaly. All 5 active ring accounts exceed 83%.',
  },
  {
    n: 3,
    title: 'Structuring below psychological thresholds',
    source: 'Agent 2 · Cognee: risk_scores.structuring_flag',
    detail: '73 transactions clustered $450–499 and $810–898. Geodo typology match: deliberate sub-threshold structuring. MR-0157 appears across 4 ring accounts — flagged as money mule node.',
  },
  {
    n: 4,
    title: 'Shared merchant network',
    source: 'Agent 3 · Cognee: ring_findings.evidence_paths',
    detail: '35 counterparties shared across >2 ring accounts. Graph clique density 0.78. No legitimate account cluster of this density exists in the 294-account population.',
  },
  {
    n: 5,
    title: 'Transaction burst activity',
    source: 'Agent 1 · Cognee: account_stats.burst_count',
    detail: 'AC-0010 and AC-0011 show 16 combined transactions with <60 seconds between them. Consistent with automated/scripted submission.',
  },
]

export const RECOMMENDED_ACTIONS = [
  { tier: 'IMMEDIATE', color: 'red', title: 'Freeze accounts AC-0001, AC-0005, AC-0009, AC-0010, AC-0011, AC-0012', detail: 'Prevent further transactions. Notify compliance team and SAR filing team.' },
  { tier: 'URGENT', color: 'amber', title: 'Investigate merchant MR-0157 and 34 other shared counterparties', detail: 'Determine if these are genuine merchants or shell entities used in circular flow.' },
  { tier: 'MONITOR', color: 'blue', title: 'Deploy rule: accounts <30 days old with >80% late-night activity', detail: 'This combined signal would have flagged the ring within 2 weeks of opening.' },
]
