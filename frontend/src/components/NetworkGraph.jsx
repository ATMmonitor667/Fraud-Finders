import { useEffect, useRef } from 'react'

const RING = ['AC-0001', 'AC-0005', 'AC-0009', 'AC-0010', 'AC-0011', 'AC-0012']
const HIGH = ['AC-0016', 'AC-0020', 'AC-0013', 'AC-0017', 'AC-0019', 'AC-0031', 'AC-0015']
const NORMAL = ['AC-0057', 'AC-0198', 'AC-0232', 'AC-0098', 'AC-0085']

const RING_EDGES = [
  ['AC-0001', 'AC-0005'], ['AC-0005', 'AC-0010'], ['AC-0010', 'AC-0011'],
  ['AC-0011', 'AC-0009'], ['AC-0009', 'AC-0001'], ['AC-0005', 'AC-0009'],
  ['AC-0001', 'AC-0010'], ['AC-0011', 'AC-0001'], ['AC-0010', 'AC-0012'], ['AC-0012', 'AC-0011'],
]
const CROSS_EDGES = [
  ['AC-0005', 'AC-0016'], ['AC-0010', 'AC-0031'], ['AC-0001', 'AC-0013'],
  ['AC-0011', 'AC-0019'], ['AC-0009', 'AC-0020'], ['AC-0010', 'AC-0015'],
]
const NORMAL_EDGES = [['AC-0016', 'AC-0057'], ['AC-0031', 'AC-0098'], ['AC-0013', 'AC-0232']]

export default function NetworkGraph() {
  const canvasRef = useRef(null)
  const raf = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const dpr = window.devicePixelRatio || 1

    function layout() {
      const W = canvas.clientWidth
      const H = canvas.clientHeight
      canvas.width = W * dpr
      canvas.height = H * dpr
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      const cx = W / 2
      const cy = H / 2
      const nodes = {}
      RING.forEach((id, i) => {
        const a = (i / RING.length) * Math.PI * 2 - Math.PI / 2
        nodes[id] = { x: cx + Math.cos(a) * 88, y: cy + Math.sin(a) * 88, type: 'ring' }
      })
      HIGH.forEach((id, i) => {
        const a = (i / HIGH.length) * Math.PI * 2 - Math.PI / 3
        nodes[id] = { x: cx + Math.cos(a) * 168, y: cy + Math.sin(a) * 168, type: 'high' }
      })
      NORMAL.forEach((id, i) => {
        const a = (i / NORMAL.length) * Math.PI * 2 + Math.PI / 5
        nodes[id] = { x: cx + Math.cos(a) * 240, y: cy + Math.sin(a) * 240, type: 'normal' }
      })
      return { W, H, cx, cy, nodes }
    }

    let geo = layout()

    function edge(a, b, color, alpha, width) {
      const na = geo.nodes[a]
      const nb = geo.nodes[b]
      if (!na || !nb) return
      ctx.beginPath()
      ctx.moveTo(na.x, na.y)
      ctx.lineTo(nb.x, nb.y)
      ctx.strokeStyle = color
      ctx.globalAlpha = alpha
      ctx.lineWidth = width
      ctx.stroke()
      ctx.globalAlpha = 1
    }

    function flowDot(a, b, t) {
      const na = geo.nodes[a]
      const nb = geo.nodes[b]
      if (!na || !nb) return
      const x = na.x + (nb.x - na.x) * t
      const y = na.y + (nb.y - na.y) * t
      ctx.beginPath()
      ctx.arc(x, y, 2.4, 0, Math.PI * 2)
      ctx.fillStyle = '#ff8a95'
      ctx.shadowColor = '#ff4757'
      ctx.shadowBlur = 8
      ctx.fill()
      ctx.shadowBlur = 0
    }

    function node(id, n, pulse) {
      const isRing = n.type === 'ring'
      const isHigh = n.type === 'high'
      const r = isRing ? 15 : isHigh ? 10 : 7
      const color = isRing ? '#ff4757' : isHigh ? '#4d9fff' : '#404a63'
      if (isRing) {
        ctx.beginPath()
        ctx.arc(n.x, n.y, r + 7 + pulse, 0, Math.PI * 2)
        ctx.fillStyle = 'rgba(255,71,87,0.12)'
        ctx.fill()
      }
      ctx.beginPath()
      ctx.arc(n.x, n.y, r, 0, Math.PI * 2)
      ctx.fillStyle = isRing ? '#2a1014' : isHigh ? '#0c1c33' : '#11151d'
      ctx.fill()
      ctx.strokeStyle = color
      ctx.lineWidth = isRing ? 2 : 1.4
      ctx.stroke()
      ctx.fillStyle = color
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      if (isRing) {
        ctx.font = '600 9px "DM Mono", monospace'
        ctx.fillText(id.replace('AC-', ''), n.x, n.y)
      } else {
        ctx.font = '9px "DM Mono", monospace'
        ctx.fillText(id.replace('AC-', ''), n.x, n.y - r - 8)
      }
    }

    function frame(now) {
      const { W, H, cx, cy, nodes } = geo
      ctx.clearRect(0, 0, W, H)
      NORMAL_EDGES.forEach(([a, b]) => edge(a, b, '#404a63', 0.5, 0.8))
      CROSS_EDGES.forEach(([a, b]) => edge(a, b, '#4d9fff', 0.22, 1))
      RING_EDGES.forEach(([a, b]) => edge(a, b, '#ff4757', 0.4, 1.6))

      const t = (now % 2200) / 2200
      RING_EDGES.forEach(([a, b], i) => flowDot(a, b, (t + i / RING_EDGES.length) % 1))

      const pulse = Math.sin(now / 600) * 2 + 2
      Object.entries(nodes).forEach(([id, n]) => node(id, n, pulse))

      ctx.fillStyle = 'rgba(255,71,87,0.55)'
      ctx.font = 'bold 10px "DM Mono", monospace'
      ctx.textAlign = 'center'
      ctx.fillText('RING CLUSTER', cx, cy + 120)

      raf.current = requestAnimationFrame(frame)
    }

    raf.current = requestAnimationFrame(frame)

    const onResize = () => { geo = layout() }
    window.addEventListener('resize', onResize)
    return () => {
      cancelAnimationFrame(raf.current)
      window.removeEventListener('resize', onResize)
    }
  }, [])

  return (
    <div className="panel">
      <div className="topbar">
        <div>
          <div className="page-title">Network Graph</div>
          <div className="page-subtitle">Account-to-account transfer flows between high-risk accounts</div>
        </div>
        <div className="cognee-badge"><span className="cognee-dot" />agent_3 output → cognee:ring_findings</div>
      </div>

      <div className="card">
        <div className="card-header"><div className="card-title">Account–merchant co-occurrence network</div></div>
        <canvas ref={canvasRef} className="graph-canvas" />
        <div className="legend">
          <span><span className="dot" style={{ background: 'var(--red)' }} />Ring account</span>
          <span><span className="dot" style={{ background: 'var(--blue)' }} />High-risk account</span>
          <span><span className="dot" style={{ background: 'var(--muted2)' }} />Normal account</span>
          <span><span className="line-key" style={{ background: 'rgba(255,71,87,.5)' }} />Ring transfer flow</span>
        </div>
      </div>

      <div className="evidence-grid">
        <div className="evidence-block">
          <div className="ev-title">Ring cluster evidence</div>
          <div className="ev-row"><span className="ev-key">Accounts confirmed</span><span className="ev-val danger">AC-0001, 0005, 0009, 0010, 0011, 0012</span></div>
          <div className="ev-row"><span className="ev-key">Shared merchants</span><span className="ev-val warn">35 counterparties</span></div>
          <div className="ev-row"><span className="ev-key">Strongest link</span><span className="ev-val">MR-0157 (4 ring accts)</span></div>
          <div className="ev-row"><span className="ev-key">Total exposure</span><span className="ev-val danger">$161,751</span></div>
          <div className="ev-row"><span className="ev-key">Benchmark target</span><span className="ev-val ok">$161,751 ✓</span></div>
        </div>
        <div className="evidence-block">
          <div className="ev-title">Behavioral signatures</div>
          <div className="ev-row"><span className="ev-key">Txn timing</span><span className="ev-val danger">91.4% midnight–6am</span></div>
          <div className="ev-row"><span className="ev-key">Account age at start</span><span className="ev-val warn">8–21 days</span></div>
          <div className="ev-row"><span className="ev-key">Max single txn</span><span className="ev-val">$898.89 (below $900)</span></div>
          <div className="ev-row"><span className="ev-key">Structuring events</span><span className="ev-val warn">73 txns near $500/$900</span></div>
          <div className="ev-row"><span className="ev-key">Burst transactions</span><span className="ev-val warn">16 txns &lt;60s apart</span></div>
        </div>
      </div>
    </div>
  )
}
