import { useState } from 'react'
import Sidebar from './components/Sidebar.jsx'
import Overview from './components/Overview.jsx'
import AgentPipeline from './components/AgentPipeline.jsx'
import RiskTable from './components/RiskTable.jsx'
import NetworkGraph from './components/NetworkGraph.jsx'
import FraudReport from './components/FraudReport.jsx'

export default function App() {
  const [active, setActive] = useState('overview')
  const [runSignal, setRunSignal] = useState(0)

  const runPipeline = () => {
    setActive('agents')
    setRunSignal((n) => n + 1)
  }

  return (
    <div className="shell">
      <Sidebar active={active} onNavigate={setActive} />
      <main className="main">
        {active === 'overview' && <Overview key="overview" onRun={runPipeline} />}
        {active === 'agents' && <AgentPipeline key="agents" runSignal={runSignal} />}
        {active === 'risk' && <RiskTable key="risk" />}
        {active === 'graph' && <NetworkGraph key="graph" />}
        {active === 'report' && <FraudReport key="report" />}
      </main>
    </div>
  )
}
