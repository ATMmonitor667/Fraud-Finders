import { useEffect, useRef, useState } from 'react'
import { AGENTS, COGNEE_KEYS, LOGS } from '../data.js'
import { IconPlay } from './icons.jsx'

function pad(n) {
  return String(n).padStart(2, '0')
}

export default function AgentPipeline({ runSignal }) {
  const [statuses, setStatuses] = useState({}) // { [num]: 'running' | 'done' }
  const [lines, setLines] = useState([])
  const [running, setRunning] = useState(false)
  const termRef = useRef(null)
  const timers = useRef([])

  const start = () => {
    timers.current.forEach(clearTimeout)
    timers.current = []
    setStatuses({})
    setLines([])
    setRunning(true)

    const t0 = new Date()
    LOGS.forEach((log) => {
      const timer = setTimeout(() => {
        const d = new Date(t0.getTime() + log.delay)
        const time = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
        setLines((prev) => [...prev, { ...log, time, id: `${log.delay}-${log.msg.slice(0, 8)}` }])

        if (log.event) {
          const [kind, num] = log.event.split('-')
          setStatuses((prev) => ({ ...prev, [num]: kind === 'start' ? 'running' : 'done' }))
        }
        if (log.delay === LOGS[LOGS.length - 1].delay) setRunning(false)
      }, log.delay)
      timers.current.push(timer)
    })
  }

  // Trigger run when the parent signals (also covers the Overview "Run Analysis" button)
  useEffect(() => {
    if (runSignal > 0) start()
    return () => timers.current.forEach(clearTimeout)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runSignal])

  useEffect(() => {
    if (termRef.current) termRef.current.scrollTop = termRef.current.scrollHeight
  }, [lines])

  return (
    <div className="panel">
      <div className="topbar">
        <div>
          <div className="page-title">Agent Pipeline</div>
          <div className="page-subtitle">
            7 agents · Cognee memory layer · Geodo typology enrichment · PyMC Bayesian scoring
          </div>
        </div>
        <button className="btn btn-primary" onClick={start} disabled={running}>
          <IconPlay /> {running ? 'Running…' : 'Run Pipeline'}
        </button>
      </div>

      <div className="pipeline">
        {AGENTS.map((a) => {
          const st = statuses[a.num] || 'idle'
          return (
            <div key={a.num} className={`agent-step ${st}`}>
              <div className="agent-icon">{a.num}</div>
              <div className="agent-name">{a.name}</div>
              <div className="agent-role">{a.role}</div>
              <div className={`agent-status ${st}`}>
                {st === 'idle' ? 'Idle' : st === 'running' ? 'Running' : 'Done'}
              </div>
            </div>
          )
        })}
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">Cognee Memory Layer — Named Datasets</div>
          <div className="cognee-badge"><span className="cognee-dot" />shared state across all agents</div>
        </div>
        <div className="card-body">
          <div className="cognee-flow">
            {COGNEE_KEYS.map((k) => (
              <div className="cognee-key" key={k.key}>
                <div className="ck-agent">{k.agent}</div>
                <div className="ck-key">{k.key}</div>
                <div className="ck-desc">{k.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><div className="card-title">Agent Log</div></div>
        <div className="terminal" ref={termRef}>
          {lines.length === 0 && (
            <div className="log-line">
              <span className="log-time">--:--:--</span>
              <span className="log-agent log-sys">[system]</span>
              <span className="log-msg">
                RingAlert pipeline ready. Press ▶ Run to begin.<span className="cursor" />
              </span>
            </div>
          )}
          {lines.map((l) => (
            <div className="log-line" key={l.id}>
              <span className="log-time">{l.time}</span>
              <span className={`log-agent log-${l.cls}`}>{l.agent}</span>
              <span className={`log-msg ${l.type || ''}`}>{l.msg}</span>
            </div>
          ))}
          {running && (
            <div className="log-line">
              <span className="log-time" />
              <span className="log-agent" />
              <span className="log-msg"><span className="cursor" /></span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
