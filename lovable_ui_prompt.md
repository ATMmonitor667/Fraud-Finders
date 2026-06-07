# RingAlert — Lovable UI Prompt

Paste this entire prompt into Lovable.dev to generate the dashboard.

---

Build a single-page fraud detection dashboard called **RingAlert** for a bank fraud analyst.

**Tech stack:** React, Tailwind CSS, recharts for any charts. Dark professional color scheme: navy (#0D1B2A) background, white text, red (#C0392B) for danger states, amber (#E67E22) for warnings, green (#27AE60) for safe.

**Layout — one screen, no scrolling:**

---

**TOP BAR (full width, navy, 56px tall)**
- Left: "RingAlert" logo in bold white, with a small red ring/target icon
- Center: 5 agent status pills in a row, each showing:
  - Agent number + name (e.g. "1 DataIngestor")
  - Status dot: gray (idle) → yellow pulsing (running) → green (done) → red (error)
  - Animate the dot with a CSS pulse when running
- Right: "Upload CSV" button (navy outline, white text) and a "Run Analysis" red button

---

**MAIN AREA (below top bar, full remaining height, two panels side by side):**

**LEFT PANEL — Network Graph (60% width)**
- Title: "Transaction Network" in small gray uppercase
- Show a force-directed network graph using a simple SVG/canvas simulation:
  - Nodes = account IDs (circles, white outline, navy fill)
  - Edges = transactions (gray lines)
  - Suspicious clusters highlighted: nodes in red, edges in red dashed lines
  - Clicking a cluster selects it and loads its case in the right panel
  - A subtle animated pulsing glow on the red nodes
- Below the graph: small legend — "○ Normal account  ● Suspicious account  — Transaction  ╌ Suspicious flow"
- If no data loaded yet: centered placeholder text "Upload a CSV and run analysis to see the fraud network"

**RIGHT PANEL — Case Brief (40% width, dark gray #1A252F background)**
- When a ring is selected, show:
  
  **Header row:**
  - Ring ID badge (e.g. "RING-001") in red on dark background
  - Risk level badge: "CRITICAL" in red / "HIGH" in amber / "MEDIUM" in yellow
  
  **Risk Score block (prominent):**
  - Large number: e.g. "94%" in white bold 48px
  - Below it: "fraud probability" in small gray
  - Below that: "±3% confidence (PyMC Bayesian)" in small amber text
  
  **Accounts involved:**
  - Row of account ID chips (small rounded rectangles, red background)
  
  **Case Brief:**
  - Section title "Analyst Brief" in gray uppercase
  - 3 sentences of plain-English brief text, white, readable font size
  
  **Evidence:**
  - Small collapsible section "Evidence" showing the technical pattern description
  
  **Action buttons — full width, prominent:**
  - "🚩 Flag for Review" — red background, white text, large
  - "✓ Dismiss" — dark gray background, white text, large
  - Both buttons should show a brief confirmation animation when clicked

- When nothing is selected: "← Select a cluster from the network graph to view its case brief"

---

**BOTTOM STATUS BAR (full width, 32px, very dark)**
- Left: connection status "● Cognee connected" in green
- Center: last run timestamp or "No analysis run yet"
- Right: "Submissions close 5:00 PM · Devpost: vibeforward-m2-agents.devpost.com"

---

**Interactions to implement:**
1. Upload CSV → file name shown in top bar, "Run Analysis" button becomes enabled
2. "Run Analysis" → agents animate one by one left to right (yellow pulse → green check)
3. After run: nodes appear in graph with suspicious ones highlighted red
4. Click red cluster → right panel populates with that ring's data
5. "Flag for Review" → button turns green with checkmark, brief fades to green tint
6. "Dismiss" → brief fades out, next ring loads automatically

**Dummy data to show on first load (so judges see a working product immediately):**
Pre-load with 3 sample fraud rings:
- RING-001: accounts ACC-1042, ACC-2891, ACC-3304, ACC-4017 | 94% ±3% | CRITICAL
  Brief: "Four accounts moved $2,300 in a tight circle over 72 hours, each transaction just under the $500 alert threshold. This is a textbook micro-transaction fraud ring — the circular flow is unmistakable once mapped as a graph. Recommend immediate freeze of all four accounts and escalation to compliance within the hour."
- RING-002: accounts ACC-7721, ACC-8830, ACC-9102 | 87% ±4% | HIGH  
  Brief: "Three accounts exchanged funds 23 times in 48 hours with identical transaction timing, suggesting automated coordination. The average transaction of $312 appears designed to stay below detection thresholds. Flag for investigation — the timing pattern is the clearest signal."
- RING-003: accounts ACC-5519, ACC-6648 | 71% ±6% | HIGH
  Brief: "Two accounts traded $45,000 back and forth across 18 transactions over one week. While bilateral flows can be legitimate, the consistent below-threshold amounts and identical timing intervals are suspicious. Review account ownership and relationship before deciding."

Make the UI polished, professional, and immediately usable by someone who has never seen it before. No instructions needed. Big obvious buttons. Every number explained.
