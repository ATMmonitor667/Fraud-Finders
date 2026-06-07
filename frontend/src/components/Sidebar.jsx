import { IconOverview, IconAgents, IconTable, IconGraph, IconReport } from './icons.jsx'

const NAV = [
  { id: 'overview', label: 'Overview', icon: IconOverview, group: 'Investigation' },
  { id: 'agents', label: 'Agent Pipeline', icon: IconAgents, group: 'Investigation' },
  { id: 'risk', label: 'Risk Table', icon: IconTable, group: 'Investigation' },
  { id: 'graph', label: 'Network Graph', icon: IconGraph, group: 'Investigation' },
  { id: 'report', label: 'Fraud Report', icon: IconReport, group: 'Output' },
]

export default function Sidebar({ active, onNavigate }) {
  let lastGroup = null
  return (
    <aside className="sidebar">
      <div className="logo">
        <div className="logo-mark">
          <span className="logo-dot" />
          Ring<span>Alert</span>
        </div>
        <div className="logo-sub">Crestline Community Bank</div>
      </div>
      <nav className="nav">
        {NAV.map((item) => {
          const Icon = item.icon
          const header = item.group !== lastGroup ? <div className="nav-section" key={item.group}>{item.group}</div> : null
          lastGroup = item.group
          return (
            <div key={item.id}>
              {header}
              <div
                className={`nav-item ${active === item.id ? 'active' : ''}`}
                onClick={() => onNavigate(item.id)}
              >
                <Icon className="nav-ico" />
                {item.label}
              </div>
            </div>
          )
        })}
      </nav>
      <div className="sidebar-foot">
        <div className="status-badge">
          <span className="pulse" />
          LIVE · 5,000 txns loaded
        </div>
      </div>
    </aside>
  )
}
