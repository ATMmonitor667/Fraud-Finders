import { ACCOUNTS } from '../data.js'

function color(score) {
  if (score > 60) return 'var(--red)'
  if (score > 30) return 'var(--amber)'
  return 'var(--blue)'
}

export default function RiskTable() {
  return (
    <div className="panel">
      <div className="topbar">
        <div>
          <div className="page-title">Risk Table</div>
          <div className="page-subtitle">Top accounts by composite anomaly score</div>
        </div>
        <div className="cognee-badge"><span className="cognee-dot" />agent_1 output → cognee:account_stats</div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">Account risk ranking</div>
          <div style={{ fontSize: 11, color: 'var(--muted)' }}>
            Score = late-night % + account age + structuring + volume + avg amount
          </div>
        </div>
        <div className="table-wrap">
          <table className="risk-table">
            <thead>
              <tr>
                <th>Account</th>
                <th>Risk Score</th>
                <th>Txns</th>
                <th>Total $</th>
                <th>Avg $</th>
                <th>Late-night %</th>
                <th>Days old</th>
                <th>Structuring</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {ACCOUNTS.map((a) => {
                const sleeper = a.id === 'AC-0012'
                return (
                  <tr key={a.id} className={a.isRing ? 'ring' : ''}>
                    <td><span className="acct-id">{a.id}</span></td>
                    <td>
                      <div className="risk-bar-wrap">
                        <div className="risk-bar-bg">
                          <div
                            className="risk-bar-fill"
                            style={{ width: `${(a.riskScore / 100) * 78}px`, background: color(a.riskScore) }}
                          />
                        </div>
                        <span className="score-val" style={{ color: color(a.riskScore) }}>
                          {a.riskScore}
                        </span>
                      </div>
                    </td>
                    <td>{a.txns}</td>
                    <td>${a.total.toLocaleString('en-US', { maximumFractionDigits: 0 })}</td>
                    <td>${a.avg.toLocaleString('en-US', { maximumFractionDigits: 0 })}</td>
                    <td style={{ color: a.lateNight > 0.8 ? 'var(--red)' : a.lateNight > 0.4 ? 'var(--amber)' : 'var(--muted)' }}>
                      {(a.lateNight * 100).toFixed(0)}%
                    </td>
                    <td style={{ color: a.daysOld < 30 ? 'var(--red)' : 'var(--muted)' }}>{a.daysOld}d</td>
                    <td style={{ color: a.near500 > 0 ? 'var(--amber)' : 'var(--muted)' }}>
                      {a.near500 + a.near1000} txns
                    </td>
                    <td>
                      <span className={`badge ${sleeper ? 'badge-sleeper' : a.isRing ? 'badge-ring' : 'badge-clear'}`}>
                        {sleeper ? 'Sleeper' : a.isRing ? 'Ring' : 'Clear'}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
