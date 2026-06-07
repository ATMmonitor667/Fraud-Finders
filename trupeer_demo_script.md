# RingAlert — Trupeer Demo Script
## vibeFORWARD: M-2 | Track 02: Fraud Watch
### 5-Minute Narrated Walkthrough

---

**BEFORE YOU RECORD:**
- Open RingAlert in browser (full screen, no other tabs visible)
- Have `track02_transactions.csv` on your desktop
- Have your terminal open with the agent pipeline ready to run
- Trupeer settings: auto-zoom ON, filler-word removal ON, click indicators ON

---

## SCRIPT (speak naturally, don't read word-for-word)

---

**[0:00 – 0:30] — The Problem**

*(Open on the RingAlert dashboard, empty state)*

> "This is RingAlert — a fraud detection tool built for the vibeFORWARD hackathon.
>
> Here's the problem we're solving: a bank's fraud ring stayed under every alert. Small transactions, circular flows, coordinated accounts. The analyst has three minutes per case. No time for SQL. No time for graph traversals. The tool needs to do all of that automatically.
>
> Let me show you how."

---

**[0:30 – 1:00] — Upload the Data**

*(Click "Upload CSV" button — Trupeer will zoom in)*

> "I'm uploading the real dataset — 5,000 bank transactions provided by the hackathon organizers. This is Track 02's live data."

*(Select the CSV file — file name appears in the top bar)*

> "Agent 1 — the DataIngestor — is about to read every transaction and store each account and flow into Cognee, our graph memory layer. Cognee is why this works at scale — instead of querying a database every time, our agents build a persistent knowledge graph once and retrieve from it intelligently."

---

**[1:00 – 2:00] — Run the Analysis**

*(Click the red "Run Analysis" button)*

> "Watch the agent status bar at the top."

*(Point to agent pills as they light up)*

> "Agent 1 — DataIngestor — reading the CSV, normalizing fields, storing to Cognee. Done.
>
> Agent 2 — GraphMapper — it just read everything Agent 1 stored from Cognee, and built a directed relationship graph: who sent money to whom, how many times, how much. It's calculating suspicion scores for every account pair right now. Done.
>
> Agent 3 — PatternDetector — this is where the fraud ring gets found. It's looking for circular flows, micro-transactions just under alert thresholds, and coordinated timing. Done.
>
> Agent 4 — RiskScorer — instead of just a number, this uses PyMC Bayesian inference to give us a probability with a confidence interval. So we're not just saying 'suspicious' — we're saying '94% likely fraud, plus or minus 3%.' That's defensible in court. Done.
>
> Agent 5 — CaseBriefWriter — reads everything from Cognee, writes a plain-English brief for the analyst. Done."

---

**[2:00 – 3:00] — The Network Graph**

*(Point to the left panel — nodes and edges have appeared, red clusters visible)*

> "This is the transaction network. Every circle is an account. Every line is a money flow. The red ones — those are the fraud ring.
>
> You can see it immediately. Without this tool, an analyst would have to manually cross-reference hundreds of transactions to see what the graph makes obvious in seconds."

*(Click on the largest red cluster)*

> "I'll click this cluster."

---

**[3:00 – 4:00] — The Case Brief**

*(Right panel loads with case details — Trupeer will zoom in)*

> "Here's what the analyst sees. Ring 001. CRITICAL. 94% fraud probability, plus or minus 3%.
>
> The accounts involved — these are the actual account IDs from the dataset.
>
> And here's the brief — three sentences, plain English, written by Agent 5 for someone who has never opened a database:
>
> *(Read the first 2 sentences of the brief aloud)*
>
> Every number has an explanation. The confidence interval comes from the Bayesian model. The circular flow pattern is explained in plain English. There is no black box here — criterion 5, explainability, is baked into the architecture.
>
> And notice this: the analyst doesn't need to understand any of this. Two buttons. Flag for Review. Dismiss. That's the whole interface."

---

**[4:00 – 4:30] — Flag the Case**

*(Click "Flag for Review" button)*

> "Case flagged. The analyst just made a decision in under 3 minutes, on a fraud ring that had been invisible to every threshold-based system."

*(Trupeer will show the confirmation animation)*

> "The next ring loads automatically. The analyst moves on."

---

**[4:30 – 5:00] — Close**

*(Zoom out to show the full dashboard)*

> "RingAlert uses five agents — all handing off through Cognee's knowledge graph. PyMC for Bayesian risk scores. Claude API for case briefs. And a UI that requires zero training.
>
> The fraud ring that hid from every rule? It can't hide from a graph.
>
> This is RingAlert. vibeFORWARD: M-2, Track 02."

---

## POST-RECORDING CHECKLIST
- [ ] Video is under 5 minutes (Trupeer will trim if needed)
- [ ] All 5 agent status lights are visible going green
- [ ] Case brief is clearly readable
- [ ] Both action buttons are clicked on camera
- [ ] No terminal or code visible during the demo (judges see the product, not the code)
- [ ] Upload to Trupeer and copy the URL for Devpost submission

---

## TIPS FOR A GREAT TRUPEER RECORDING
- Speak at a natural pace — Trupeer removes filler words automatically
- Move your cursor deliberately to each element before clicking — Trupeer will auto-zoom
- If you make a mistake, pause 3 seconds and continue — Trupeer can cut it
- Record in Chrome, full screen, 1920×1080 if possible
