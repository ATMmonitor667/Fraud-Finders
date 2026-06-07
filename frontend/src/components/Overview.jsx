import { useEffect, useRef, useState } from 'react'
import { HOURLY_RING, HOURLY_NORM } from '../data.js'
import { IconPlay } from './icons.jsx'

function useCountUp(target, duration = 1100, decimals = 0) {
  const [val, setVal] = useState(0)
  useEffect(() => {
    let raf
    const start = performance.now()
    const tick = (now) => {
      const t = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - t, 3)
      setVal(target * eased)
      if (t < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [target, duration])
  return decimals ? val.toFixed(decimals) : Math.round(val)
}

function Metric({ kind, label, value, sub, valueClass }) {
  return (
    <div className={`metric ${kind}`}>
      <div className="metric-label">{label}</div>
      <div className={`metric-value ${valueClass}`}>{value}</div>
      <div className="metric-sub">{sub}</div>
    </div>
  )
}

function HourChart({ data, late, normal }) {
  const max = Math.max(...Object.values(data))
  return (
    <div>
      <div className="bar-chart">
        {Array.from({ length: 24 }, (_, h) => {
          const v = data[h] || 0
          const isLate = h < 6 || h === 23
          let bg = 'var(--muted2)'
          if (normal) bg = isLate ? 'rgba(255,71,87,.35)' : 'var(--muted2)'
          else bg = isLate ? 'var(--red)' : 'var(--border2)'
          return (
            <div
              key={h}
              className="bar"
              style={{ height: `${(v / max) * 100}%`, background: bg }}
              data-tip={`${h}:00 → ${v} txns`}
            />
          )
        })}
      </div>
      <div className="chart-axis">
        <span>0h</span><span>6h</span><span>12h</span><span>18h</span><span>23h</span>
      </div>
    </div>
  )
}

export default function Overview({ onRun }) {
  const ring = useCountUp(6)
  const exposure = useCountUp(161751)
  const txns = useCountUp(292)
  const avg = useCountUp(561)
  const late = useCountUp(91)
  const mounted = useRef(false)
  useEffect(() => { mounted.current = true }, [])

  return (
    <div className="panel">
      <div className="topbar">
        <div>
          <div className="page-title">Overview</div>
          <div className="page-subtitle">Crestline Community Bank · 90-day window · March–June 2026</div>
        </div>
        <button className="btn btn-primary" onClick={onRun}>
          <IconPlay /> Run Analysis
        </button>
      </div>

      <div className="metric-grid">
        <Metric kind="danger" label="Confirmed Ring" value={ring} valueClass="danger" sub="accounts identified" />
        <Metric kind="danger" label="Total Exposure" value={`$${exposure.toLocaleString('en-US')}`} valueClass="danger" sub="matches hint $161,751" />
        <Metric kind="warn" label="Ring Transactions" value={txns} valueClass="amber" sub="of 5,000 total" />
        <Metric kind="warn" label="Alert Threshold Hits" value={0} valueClass="amber" sub="zero rule triggers" />
        <Metric kind="info" label="Avg Ring Txn" value={`$${avg}`} valueClass="blue" sub="vs $63 baseline" />
        <Metric kind="info" label="Late-Night Rate" value={`${late}%`} valueClass="blue" sub="ring txns 11pm–5am" />
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">Transaction timing — ring vs normal</div>
          <div className="cognee-badge"><span className="cognee-dot" />agent_1 → cognee</div>
        </div>
        <div className="card-body">
          <div className="hours">
            <div>
              <div className="hours-label" style={{ color: 'var(--red)' }}>
                <span className="dot" style={{ background: 'var(--red)' }} /> Ring accounts
              </div>
              <HourChart data={HOURLY_RING} />
              <div style={{ marginTop: 10, fontSize: 11.5, color: 'var(--muted)' }}>
                91.4% of transactions occur midnight–6am
              </div>
            </div>
            <div>
              <div className="hours-label" style={{ color: 'var(--muted)' }}>
                <span className="dot" style={{ background: 'var(--muted2)' }} /> Normal accounts
              </div>
              <HourChart data={HOURLY_NORM} normal />
              <div style={{ marginTop: 10, fontSize: 11.5, color: 'var(--muted)' }}>
                Evenly distributed across all hours
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="two-col">
        <div className="card">
          <div className="card-header"><div className="card-title">Why rules missed this</div></div>
          <div className="card-body">
            <ul className="signal-list">
              {[
                ['All transactions below $1,000', 'Max txn: $898.89 — under every common alert threshold'],
                ['Individual accounts look low-volume', 'Each account alone: 12–83 txns over 90 days'],
                ['No single large transfer', 'Ring used many small txns: avg $561, distributed'],
                ['Spread across categories', 'Used grocery, retail, electronics — nothing unusual alone'],
              ].map(([t, d]) => (
                <li key={t}>
                  <span className="signal-ico bad">✕</span>
                  <div>
                    <div className="signal-title">{t}</div>
                    <div className="signal-detail">{d}</div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="card">
          <div className="card-header"><div className="card-title">What the agents caught</div></div>
          <div className="card-body">
            <ul className="signal-list">
              {[
                ['Coordinated account opening', 'All 6 accounts opened within 8 days (Feb 10–18, 2026)'],
                ['Exclusive late-night activity', '91.4% of transactions between 11pm–5am'],
                ['Structuring below $500/$900', '73 txns clustered just below these psychological ceilings'],
                ['Shared merchant network', '35+ counterparties used across ring accounts simultaneously'],
              ].map(([t, d]) => (
                <li key={t}>
                  <span className="signal-ico good">✓</span>
                  <div>
                    <div className="signal-title">{t}</div>
                    <div className="signal-detail">{d}</div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
