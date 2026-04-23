import { useState } from 'react';

type View = 'floor-plan' | 'elevation';

export function SketchImprovement() {
  const [view, setView] = useState<View>('floor-plan');

  return (
    <section className="sketch-section">
      <div className="sketch-header">
        <div>
          <h2 className="sketch-title">Your Sketch — Improved</h2>
          <p className="sketch-subtitle">
            Your rough drawing interpreted as a long-side plan house with three zones and a contemporary elevation.
          </p>
        </div>
        <div className="view-toggle">
          <button
            className={`toggle-btn ${view === 'floor-plan' ? 'active' : ''}`}
            onClick={() => setView('floor-plan')}
          >
            Floor Plan
          </button>
          <button
            className={`toggle-btn ${view === 'elevation' ? 'active' : ''}`}
            onClick={() => setView('elevation')}
          >
            Elevation
          </button>
        </div>
      </div>

      <div className="sketch-canvas">
        {view === 'floor-plan' ? <FloorPlanSVG /> : <ElevationSVG />}
      </div>

      <div className="sketch-legend">
        {view === 'floor-plan' ? (
          <div className="legend-items">
            <LegendItem color="#dbeafe" label="Living / Dining Zone (Left Wing)" />
            <LegendItem color="#fef9c3" label="Entry Foyer & Staircase (Centre)" />
            <LegendItem color="#dcfce7" label="Bedroom Wing (Right Wing)" />
            <LegendItem color="#f3f4f6" label="Circulation / Corridor" />
          </div>
        ) : (
          <div className="legend-items">
            <LegendItem color="#334155" label="Flat Roof with Deep Overhang" />
            <LegendItem color="#93c5fd" label="Ribbon / Floor-to-Ceiling Windows" />
            <LegendItem color="#d1d5db" label="Horizontal Concrete / Stucco Bands" />
            <LegendItem color="#fbbf24" label="Covered Entry Canopy" />
            <LegendItem color="#6b7280" label="Garage Door (Ground Level)" />
          </div>
        )}
      </div>
    </section>
  );
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="legend-item">
      <span className="legend-swatch" style={{ background: color }} />
      <span>{label}</span>
    </div>
  );
}

function FloorPlanSVG() {
  return (
    <svg
      viewBox="0 0 800 420"
      xmlns="http://www.w3.org/2000/svg"
      className="plan-svg"
      aria-label="Improved floor plan"
    >
      {/* ── Background ── */}
      <rect width="800" height="420" fill="#f8fafc" />

      {/* ── Compass ── */}
      <g transform="translate(750, 30)">
        <circle cx="0" cy="0" r="18" fill="white" stroke="#94a3b8" strokeWidth="1" />
        <text x="0" y="-6" textAnchor="middle" fontSize="11" fontWeight="700" fill="#1e293b">N</text>
        <path d="M0,-14 L3,-4 L0,-8 L-3,-4 Z" fill="#1e293b" />
        <path d="M0,14 L3,4 L0,8 L-3,4 Z" fill="#94a3b8" />
      </g>

      {/* ── Scale bar ── */}
      <g transform="translate(30, 390)">
        <line x1="0" y1="0" x2="100" y2="0" stroke="#64748b" strokeWidth="1.5" />
        <line x1="0" y1="-5" x2="0" y2="5" stroke="#64748b" strokeWidth="1.5" />
        <line x1="50" y1="-3" x2="50" y2="3" stroke="#64748b" strokeWidth="1.5" />
        <line x1="100" y1="-5" x2="100" y2="5" stroke="#64748b" strokeWidth="1.5" />
        <text x="0" y="-10" fontSize="9" fill="#64748b">0</text>
        <text x="44" y="-10" fontSize="9" fill="#64748b">10ft</text>
        <text x="90" y="-10" fontSize="9" fill="#64748b">20ft</text>
      </g>

      {/* ── Outer wall ── */}
      <rect x="40" y="40" width="720" height="340" fill="white" stroke="#1e293b" strokeWidth="3" />

      {/* ── Left Wing — Living / Dining (blue tint) ── */}
      <rect x="40" y="40" width="220" height="340" fill="#dbeafe" stroke="#1e293b" strokeWidth="1.5" />
      <text x="150" y="30" textAnchor="middle" fontSize="11" fill="#1e40af" fontWeight="600">LIVING / DINING</text>

      {/* Sofa group */}
      <rect x="60" y="80" width="80" height="35" rx="6" fill="#93c5fd" stroke="#3b82f6" strokeWidth="1.5" />
      <rect x="60" y="80" width="80" height="10" rx="3" fill="#60a5fa" />
      <rect x="145" y="80" width="10" height="35" rx="4" fill="#93c5fd" stroke="#3b82f6" strokeWidth="1.5" />
      <rect x="155" y="80" width="10" height="35" rx="4" fill="#93c5fd" stroke="#3b82f6" strokeWidth="1.5" />
      {/* Coffee table */}
      <rect x="75" y="125" width="55" height="30" rx="3" fill="white" stroke="#3b82f6" strokeWidth="1.5" />
      {/* Armchair */}
      <rect x="170" y="90" width="40" height="40" rx="5" fill="#bfdbfe" stroke="#3b82f6" strokeWidth="1.5" />
      <rect x="170" y="90" width="40" height="10" rx="3" fill="#93c5fd" />

      {/* Dining table */}
      <rect x="60" y="220" width="90" height="55" rx="4" fill="white" stroke="#3b82f6" strokeWidth="1.5" />
      {/* Chairs around table */}
      {[0, 1, 2].map(i => (
        <rect key={`dc-top-${i}`} x={65 + i * 28} y={208} width={22} height={14} rx={3} fill="#bfdbfe" stroke="#3b82f6" strokeWidth="1" />
      ))}
      {[0, 1, 2].map(i => (
        <rect key={`dc-bot-${i}`} x={65 + i * 28} y={274} width={22} height={14} rx={3} fill="#bfdbfe" stroke="#3b82f6" strokeWidth="1" />
      ))}
      <rect x={47} y={228} width={14} height={22} rx={3} fill="#bfdbfe" stroke="#3b82f6" strokeWidth="1" />
      <rect x={149} y={228} width={14} height={22} rx={3} fill="#bfdbfe" stroke="#3b82f6" strokeWidth="1" />

      {/* Kitchen counter (bottom of left wing) */}
      <rect x="50" y="330" width="200" height="30" rx="3" fill="#e0e7ff" stroke="#6366f1" strokeWidth="1.5" />
      <text x="150" y="350" textAnchor="middle" fontSize="9" fill="#4338ca">KITCHEN COUNTER</text>
      <circle cx="90" cy="344" r="7" fill="white" stroke="#6366f1" strokeWidth="1" />
      <circle cx="110" cy="344" r="7" fill="white" stroke="#6366f1" strokeWidth="1" />
      <circle cx="130" cy="344" r="7" fill="white" stroke="#6366f1" strokeWidth="1" />

      {/* ── Centre — Entry Foyer & Staircase (yellow tint) ── */}
      <rect x="260" y="40" width="280" height="340" fill="#fef9c3" stroke="#1e293b" strokeWidth="1.5" />
      <text x="400" y="30" textAnchor="middle" fontSize="11" fill="#854d0e" fontWeight="600">ENTRY / STAIRCASE</text>

      {/* Entry door (bottom of centre) */}
      <rect x="360" y="360" width="80" height="20" fill="#fbbf24" stroke="#92400e" strokeWidth="1.5" />
      <text x="400" y="374" textAnchor="middle" fontSize="9" fill="#78350f" fontWeight="600">ENTRY DOOR</text>
      {/* Door swing arc */}
      <path d="M360,360 Q360,330 390,340" fill="none" stroke="#92400e" strokeWidth="1" strokeDasharray="4,3" />

      {/* Foyer tiles */}
      {[0, 1, 2, 3].map(row =>
        [0, 1, 2, 3, 4, 5].map(col => (
          <rect
            key={`tile-${row}-${col}`}
            x={270 + col * 44}
            y={290 + row * 18}
            width={42}
            height={16}
            fill={((row + col) % 2 === 0) ? '#fef3c7' : '#fde68a'}
            stroke="#f59e0b"
            strokeWidth="0.5"
          />
        ))
      )}

      {/* Staircase */}
      <rect x="280" y="80" width="240" height="180" rx="4" fill="#fef3c7" stroke="#b45309" strokeWidth="2" />
      <text x="400" y="72" textAnchor="middle" fontSize="10" fill="#b45309" fontWeight="600">STAIRCASE</text>
      {/* Stair treads */}
      {Array.from({ length: 12 }, (_, i) => (
        <rect key={`stair-${i}`} x="290" y={88 + i * 14} width="220" height="13"
          fill={i % 2 === 0 ? '#fde68a' : '#fef3c7'} stroke="#f59e0b" strokeWidth="0.8" />
      ))}
      {/* Stair direction arrow */}
      <path d="M400,240 L400,200 M395,207 L400,200 L405,207" fill="none" stroke="#92400e" strokeWidth="1.5" />
      <text x="415" y="225" fontSize="9" fill="#92400e">UP</text>

      {/* ── Right Wing — Bedrooms (green tint) ── */}
      <rect x="540" y="40" width="220" height="340" fill="#dcfce7" stroke="#1e293b" strokeWidth="1.5" />
      <text x="650" y="30" textAnchor="middle" fontSize="11" fill="#166534" fontWeight="600">BEDROOM WING</text>

      {/* Bedroom 1 */}
      <rect x="550" y="50" width="200" height="100" fill="#bbf7d0" stroke="#16a34a" strokeWidth="1.5" rx="2" />
      <text x="650" y="65" textAnchor="middle" fontSize="9" fill="#15803d" fontWeight="600">BEDROOM 1</text>
      {/* Bed */}
      <rect x="575" y="80" width="60" height="55" rx="4" fill="white" stroke="#16a34a" strokeWidth="1.5" />
      <rect x="575" y="80" width="60" height="15" rx="3" fill="#86efac" />
      <rect x="640" y="85" width="15" height="15" rx="3" fill="#86efac" stroke="#16a34a" strokeWidth="1" />
      <rect x="660" y="85" width="20" height="30" rx="3" fill="#d1fae5" stroke="#16a34a" strokeWidth="1" />

      {/* Bedroom 2 */}
      <rect x="550" y="160" width="200" height="100" fill="#bbf7d0" stroke="#16a34a" strokeWidth="1.5" rx="2" />
      <text x="650" y="175" textAnchor="middle" fontSize="9" fill="#15803d" fontWeight="600">BEDROOM 2</text>
      {/* Bed */}
      <rect x="575" y="190" width="55" height="50" rx="4" fill="white" stroke="#16a34a" strokeWidth="1.5" />
      <rect x="575" y="190" width="55" height="14" rx="3" fill="#86efac" />
      <rect x="635" y="193" width="14" height="14" rx="3" fill="#86efac" stroke="#16a34a" strokeWidth="1" />

      {/* Bathroom */}
      <rect x="550" y="270" width="95" height="100" fill="#e0f2fe" stroke="#0284c7" strokeWidth="1.5" rx="2" />
      <text x="597" y="285" textAnchor="middle" fontSize="8" fill="#0369a1" fontWeight="600">BATH</text>
      {/* WC */}
      <ellipse cx="570" cy="345" rx="14" ry="10" fill="white" stroke="#0284c7" strokeWidth="1.2" />
      <rect x="562" y="330" width="16" height="15" rx="2" fill="white" stroke="#0284c7" strokeWidth="1.2" />
      {/* Bathtub */}
      <rect x="560" y="295" width="65" height="30" rx="8" fill="white" stroke="#0284c7" strokeWidth="1.2" />
      <ellipse cx="617" cy="310" rx="5" ry="4" fill="#bae6fd" stroke="#0284c7" strokeWidth="1" />

      {/* Walk-in closet */}
      <rect x="645" y="270" width="115" height="100" fill="#f0fdf4" stroke="#16a34a" strokeWidth="1.5" rx="2" />
      <text x="702" y="285" textAnchor="middle" fontSize="8" fill="#15803d" fontWeight="600">WALK-IN CLOSET</text>
      {[0, 1, 2].map(i => (
        <rect key={`rod-${i}`} x={658} y={295 + i * 24} width={90} height={18} rx={3}
          fill="#dcfce7" stroke="#16a34a" strokeWidth="1" />
      ))}

      {/* ── Corridor / Hall ── */}
      <rect x="260" y="40" width="15" height="340" fill="#f1f5f9" stroke="#1e293b" strokeWidth="1" />
      <rect x="525" y="40" width="15" height="340" fill="#f1f5f9" stroke="#1e293b" strokeWidth="1" />

      {/* ── Windows (long side — top) ── */}
      {[60, 160, 310, 420, 530, 590, 670].map((x, i) => (
        <g key={`win-${i}`}>
          <rect x={x} y={38} width={55} height={8} fill="#93c5fd" stroke="#3b82f6" strokeWidth="1.2" />
          <line x1={x + 18} y1={38} x2={x + 18} y2={46} stroke="#3b82f6" strokeWidth="0.8" />
          <line x1={x + 37} y1={38} x2={x + 37} y2={46} stroke="#3b82f6" strokeWidth="0.8" />
        </g>
      ))}

      {/* ── Dimension annotations ── */}
      <line x1="40" y1="20" x2="760" y2="20" stroke="#94a3b8" strokeWidth="1" markerEnd="url(#arrow)" markerStart="url(#arrow)" />
      <text x="400" y="15" textAnchor="middle" fontSize="10" fill="#64748b" fontWeight="600">96 ft (Long Side)</text>
      <line x1="770" y1="40" x2="770" y2="380" stroke="#94a3b8" strokeWidth="1" />
      <text x="785" y="210" fontSize="10" fill="#64748b" fontWeight="600" transform="rotate(90,785,210)">40 ft (Depth)</text>

      <defs>
        <marker id="arrow" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
          <path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8" />
        </marker>
      </defs>
    </svg>
  );
}

function ElevationSVG() {
  return (
    <svg
      viewBox="0 0 800 480"
      xmlns="http://www.w3.org/2000/svg"
      className="plan-svg"
      aria-label="Improved front elevation"
    >
      {/* ── Sky & ground ── */}
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#e0f2fe" />
          <stop offset="100%" stopColor="#f8fafc" />
        </linearGradient>
        <linearGradient id="concrete" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#e2e8f0" />
          <stop offset="100%" stopColor="#cbd5e1" />
        </linearGradient>
      </defs>
      <rect width="800" height="480" fill="url(#sky)" />
      {/* Ground */}
      <rect x="0" y="420" width="800" height="60" fill="#d1fae5" />
      <line x1="0" y1="420" x2="800" y2="420" stroke="#6b7280" strokeWidth="1.5" />

      {/* ── Trees (flanking) ── */}
      <g opacity="0.7">
        <rect x="15" y="320" width="12" height="100" fill="#6b7280" />
        <ellipse cx="21" cy="290" rx="30" ry="50" fill="#16a34a" opacity="0.8" />
        <ellipse cx="21" cy="280" rx="22" ry="38" fill="#15803d" />
      </g>
      <g opacity="0.7">
        <rect x="775" y="320" width="12" height="100" fill="#6b7280" />
        <ellipse cx="781" cy="290" rx="30" ry="50" fill="#16a34a" opacity="0.8" />
        <ellipse cx="781" cy="280" rx="22" ry="38" fill="#15803d" />
      </g>

      {/* ── Main building mass ── */}
      <rect x="40" y="100" width="720" height="320" fill="url(#concrete)" />

      {/* ── Flat roof with deep overhang ── */}
      <rect x="20" y="88" width="760" height="22" fill="#334155" rx="2" />
      <rect x="20" y="98" width="760" height="6" fill="#1e293b" />

      {/* ── Fascia / soffit detail ── */}
      <rect x="22" y="108" width="756" height="8" fill="#475569" />

      {/* ── Horizontal cladding bands ── */}
      {[130, 155, 180, 205, 230, 255, 280, 305, 330, 355, 380].map((y, i) => (
        <rect key={`band-${i}`} x="40" y={y} width="720" height="18"
          fill={i % 2 === 0 ? '#e2e8f0' : '#cbd5e1'} />
      ))}

      {/* ── Upper floor ribbon windows ── */}
      <rect x="55" y="115" width="690" height="50" fill="#1e293b" rx="2" />
      {/* Window panes — upper ribbon */}
      {Array.from({ length: 12 }, (_, i) => (
        <rect key={`uw-${i}`} x={60 + i * 57} y={117} width={52} height={46}
          fill="#93c5fd" stroke="#60a5fa" strokeWidth="1" opacity="0.85" />
      ))}
      {/* Reflection lines */}
      {Array.from({ length: 12 }, (_, i) => (
        <line key={`ur-${i}`} x1={62 + i * 57} y1={119} x2={78 + i * 57} y2={135}
          stroke="white" strokeWidth="1" opacity="0.4" />
      ))}

      {/* ── Mid floor horizontal window band ── */}
      <rect x="55" y="230" width="390" height="40" fill="#1e293b" rx="2" />
      {Array.from({ length: 7 }, (_, i) => (
        <rect key={`mw-${i}`} x={60 + i * 55} y={232} width={50} height={36}
          fill="#7dd3fc" stroke="#38bdf8" strokeWidth="1" opacity="0.8" />
      ))}
      {Array.from({ length: 7 }, (_, i) => (
        <line key={`mr-${i}`} x1={62 + i * 55} y1={234} x2={76 + i * 55} y2={248}
          stroke="white" strokeWidth="1" opacity="0.35" />
      ))}

      {/* ── Entry canopy ── */}
      <rect x="300" y="195" width="200" height="14" fill="#fbbf24" rx="2" />
      <rect x="310" y="207" width="6" height="55" fill="#92400e" />
      <rect x="484" y="207" width="6" height="55" fill="#92400e" />
      {/* Canopy shadow */}
      <rect x="300" y="207" width="200" height="6" fill="#d97706" opacity="0.5" />

      {/* ── Entry door ── */}
      <rect x="345" y="260" width="110" height="160" rx="4" fill="#1e293b" />
      {/* Door panels */}
      <rect x="352" y="268" width="44" height="65" rx="2" fill="#374151" />
      <rect x="404" y="268" width="44" height="65" rx="2" fill="#374151" />
      <rect x="352" y="342" width="44" height="65" rx="2" fill="#374151" />
      <rect x="404" y="342" width="44" height="65" rx="2" fill="#374151" />
      {/* Door handles */}
      <circle cx="393" cy="322" r="4" fill="#fbbf24" />
      <circle cx="407" cy="322" r="4" fill="#fbbf24" />
      {/* Sidelights */}
      <rect x="325" y="265" width="22" height="110" rx="2" fill="#7dd3fc" opacity="0.7" />
      <rect x="453" y="265" width="22" height="110" rx="2" fill="#7dd3fc" opacity="0.7" />
      {/* Transom */}
      <rect x="325" y="255" width="150" height="12" rx="2" fill="#7dd3fc" opacity="0.6" />

      {/* ── Entry steps ── */}
      <rect x="310" y="418" width="180" height="8" fill="#94a3b8" />
      <rect x="315" y="410" width="170" height="8" fill="#9ca3af" />
      <rect x="322" y="402" width="156" height="8" fill="#a1a1aa" />

      {/* ── Garage (right side, ground level) ── */}
      <rect x="460" y="270" width="290" height="150" fill="#1e293b" rx="2" />
      {/* Garage door panels */}
      {[0, 1, 2, 3].map(row =>
        [0, 1, 2].map(col => (
          <rect key={`gd-${row}-${col}`}
            x={468 + col * 92} y={278 + row * 34}
            width={88} height={30}
            rx={2} fill="#374151" stroke="#4b5563" strokeWidth="1" />
        ))
      )}
      {/* Garage window strip */}
      {[0, 1, 2].map(col => (
        <rect key={`gw-${col}`} x={475 + col * 92} y={284} width={74} height={10}
          rx={1} fill="#7dd3fc" opacity="0.6" />
      ))}

      {/* ── Left side — lower windows ── */}
      {[0, 1].map(col => (
        <rect key={`lw-${col}`} x={60 + col * 110} y={280} width={95} height={90}
          rx={2} fill="#7dd3fc" stroke="#38bdf8" strokeWidth="1.5" opacity="0.8" />
      ))}
      {[0, 1].map(col => (
        <line key={`lr-${col}`} x1={65 + col * 110} y1={283} x2={90 + col * 110} y2={305}
          stroke="white" strokeWidth="1.5" opacity="0.4" />
      ))}

      {/* ── Dimension lines ── */}
      <line x1="40" y1="72" x2="760" y2="72" stroke="#94a3b8" strokeWidth="1" strokeDasharray="5,3" />
      <line x1="40" y1="66" x2="40" y2="78" stroke="#94a3b8" strokeWidth="1.5" />
      <line x1="760" y1="66" x2="760" y2="78" stroke="#94a3b8" strokeWidth="1.5" />
      <text x="400" y="67" textAnchor="middle" fontSize="10" fill="#64748b" fontWeight="600">96 ft — Long Side Facade</text>

      {/* ── Floor level lines ── */}
      <line x1="20" y1="110" x2="36" y2="110" stroke="#94a3b8" strokeWidth="1" />
      <text x="15" y="113" textAnchor="end" fontSize="8" fill="#94a3b8">Lvl 2</text>
      <line x1="20" y1="260" x2="36" y2="260" stroke="#94a3b8" strokeWidth="1" />
      <text x="15" y="263" textAnchor="end" fontSize="8" fill="#94a3b8">Lvl 1</text>
      <line x1="20" y1="420" x2="36" y2="420" stroke="#94a3b8" strokeWidth="1" />
      <text x="15" y="423" textAnchor="end" fontSize="8" fill="#94a3b8">GL</text>

      {/* ── Labels ── */}
      <text x="400" y="145" textAnchor="middle" fontSize="9" fill="#1e40af" fontWeight="600" opacity="0.8">
        RIBBON WINDOWS — UPPER FLOOR
      </text>
      <text x="215" y="194" textAnchor="middle" fontSize="8" fill="#b45309">LIVING WING</text>
      <text x="605" y="194" textAnchor="middle" fontSize="8" fill="#166534">BEDROOM WING</text>
      <text x="400" y="190" textAnchor="middle" fontSize="8" fill="#92400e">COVERED ENTRY CANOPY</text>
      <text x="605" y="265" textAnchor="middle" fontSize="8" fill="#374151">GARAGE</text>
    </svg>
  );
}
