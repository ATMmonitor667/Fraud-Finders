# RingAlert — Trupeer Demo Script
## vibeFORWARD: M-2 | Track 02: Fraud Watch | 5 minutes exactly

---

## BEFORE YOU RECORD

- Open `fraudwatch_ui.html` in Chrome (full screen)
- Have the Overview panel visible
- Trupeer running and recording
- Know these numbers cold: **6 accounts, $161,751, severity 9.4/10, 94% probability**

---

## [0:00–0:30] OPENING — The Problem

> "Banks run threshold rules — flag anything over $10,000, flag anything at 2am, flag foreign IPs. A sophisticated fraud ring exploits this by staying under every single threshold simultaneously."

> "This is FraudWatch — RingAlert. It's a 7-agent pipeline that treats fraud detection as a graph problem, not a threshold problem. Let me show you what it found."

*[Point at the Overview panel stats: 6 ring accounts, $161,751 exposure, 9.4/10 severity]*

> "Five thousand transactions. Two hundred and ninety-four accounts. Hidden inside: a 6-account fraud ring that moved $161,751 completely undetected by every rule-based system."

---

## [0:30–1:30] AGENT PIPELINE — Click to Agents tab, hit ▶ Run

> "Let me run the pipeline live."

*[Click Agent Pipeline tab. Hit ▶ Run Pipeline. Watch the agents animate.]*

> "Agent 1 — DataIngestor — reads the CSV, computes per-account statistics, writes them to Cognee. That's our shared memory layer. Every agent that comes after reads what Agent 1 wrote."

*[Point at Cognee memory keys appearing in the log]*

> "Agent 2 — GraphMapper — reads from Cognee, builds two graphs: an account-to-account transfer graph that finds sink accounts — accounts that only receive money and never send — and a coordinated account-opening detector."

> "Agent 3 — PatternDetector — scores five threat signals. Category capture. Structuring. Mule coordination. Burst velocity. And the fifth signal — the sleeper."

*[Pause when the sleeper log line appears]*

> "Agent 6 is our Geodo integration — EntityEnricher. It takes the patterns Agent 3 found and queries Geodo for regulatory typology matches."

*[Point at the ML-027, ML-008, ML-041 log lines]*

> "Geodo returns three FinCEN typologies: ML-027 layering, ML-008 structuring, ML-041 mule network. Each one carries a severity multiplier. Combined: 1.33 times the raw score."

> "Agent 4 — RiskScorer — runs a PyMC Bayesian model across all five signals plus the Geodo multipliers. Output: 94% fraud probability, 95% confidence interval 91 to 97 percent, severity 9.4 out of 10."

> "Agent 5 writes the SAR narrative. Agent 7 fires a Slack alert to the compliance team."

---

## [1:30–2:30] THE SLEEPER — Network Graph panel

*[Click Network Graph tab]*

> "Now I want to show you the most important thing this system does — something no threshold rule can do."

*[Point at AC-0012 on the graph]*

> "This account — AC-0012. It has 12 transactions averaging $41 each. Zero percent late-night activity. It looks completely harmless. Every timing rule, every amount rule, every frequency rule clears it."

> "Our merchant co-occurrence graph found that AC-0012 shares three merchant counterparties with AC-0010. That's the only signal. Without the graph, this account is invisible."

*[Point at the ring cluster in the center]*

> "AC-0012 is a sleeper account — it opened in the same 8-day window as the other five ring accounts, February 10th through 18th, then stayed quiet before activating through shared merchants."

> "The answer key includes AC-0012. Teams that miss it miss the ring. We caught it."

---

## [2:30–3:30] SEVERITY & SIGNALS — Risk Table panel

*[Click Risk Table tab]*

> "Here's the precision story. We flagged exactly 6 accounts."

*[Scroll through the table — ring accounts highlighted red at top, distractors below]*

> "These accounts — AC-0016, AC-0020, AC-0013 — they look suspicious. Large transactions, late-night activity. We did NOT flag them. They're distractor accounts with legitimate anomalies."

> "A flag-everything strategy catches the ring but destroys your precision score. Evidence-based reasoning wins."

*[Click Fraud Report tab]*

> "The severity breakdown: 84.9% of the services payment category is ring fraud — category capture signal, worth 3.4 out of 10. Two structuring bands — 29 transactions near $500, 44 near $900 — worth 2.5. Four sink mule accounts — worth 2.0. Burst velocity and the sleeper bring it to 9.4 raw. Geodo multiplies by 1.33."

> "PyMC gives us the confidence interval. 94% probability, plus or minus 3%. That's not a black box — that's Bayesian inference showing you exactly how much each signal moved the needle."

---

## [3:30–4:30] SAR REPORT — Download

*[Show the Fraud Report panel]*

> "The output isn't a dashboard widget. It's a Suspicious Activity Report — the actual document fraud analysts file with FinCEN."

*[Point at the typology badges: ML-027, ML-008, ML-041]*

> "Three FinCEN typologies confirmed by Geodo. SAR mandatory under 31 CFR 1020.320."

*[Click Download SAR button]*

> "One click. Downloadable. Analyst opens this, sees the accounts, sees the evidence, sees the regulatory citation, and files. Three minutes from upload to SAR. A human doing this manually takes four hours."

> "And the moment severity hit 9.4 — above our 7.0 threshold — Agent 7 fired a Slack alert to the compliance team with the account list, exposure amount, and action required. No analyst has to check a dashboard. The system calls them."

---

## [4:30–5:00] CLOSE

> "RingAlert is built on Cognee as the memory layer between all seven agents. Every handoff — every read and write — goes through Cognee. No agent calls another agent directly. The graph is the shared state."

> "Geodo gives us regulatory grounding. PyMC gives us probabilistic confidence. The result is a system that doesn't just detect fraud — it explains exactly why, in language a compliance officer can act on, in under three minutes."

> "Track 02. Fraud Watch. RingAlert."

*[Hold on the dashboard for 3 seconds, then stop recording]*

---

## POST-RECORDING CHECKLIST

- [ ] Video is 4:45–5:15 minutes (trim if needed)
- [ ] AC-0012 sleeper moment is clearly on screen and narrated
- [ ] Geodo typology codes (ML-027, ML-008, ML-041) visible in log
- [ ] PyMC severity "9.4/10, 94% ±3%" appears in the report panel
- [ ] SAR download button is clicked on camera
- [ ] Upload to Trupeer → get shareable link
- [ ] Add link to Devpost submission before 5:00 PM
