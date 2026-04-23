import { useState, useMemo } from 'react';
import { longSidePlanHouses } from './data/houses';
import type { ArchitecturalStyle, RoofType } from './types/house';
import { SearchBar } from './components/SearchBar';
import { HouseCard } from './components/HouseCard';
import { SketchImprovement } from './components/SketchImprovement';
import './App.css';

type Tab = 'catalog' | 'sketch';

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('sketch');
  const [query, setQuery] = useState('');
  const [styleFilter, setStyleFilter] = useState<ArchitecturalStyle | 'All'>('All');
  const [roofFilter, setRoofFilter] = useState<RoofType | 'All'>('All');
  const [bedroomFilter, setBedroomFilter] = useState<number | 'All'>('All');

  const filtered = useMemo(() => {
    const q = query.toLowerCase();
    return longSidePlanHouses.filter(h => {
      const matchesQuery =
        !q ||
        h.name.toLowerCase().includes(q) ||
        h.location.toLowerCase().includes(q) ||
        h.style.toLowerCase().includes(q) ||
        h.tags.some(t => t.includes(q)) ||
        h.description.toLowerCase().includes(q);
      const matchesStyle = styleFilter === 'All' || h.style === styleFilter;
      const matchesRoof = roofFilter === 'All' || h.roofType === roofFilter;
      const matchesBed = bedroomFilter === 'All' || h.bedrooms >= bedroomFilter;
      return matchesQuery && matchesStyle && matchesRoof && matchesBed;
    });
  }, [query, styleFilter, roofFilter, bedroomFilter]);

  return (
    <div className="app">
      <header className="site-header">
        <div className="header-inner">
          <div className="header-brand">
            <svg viewBox="0 0 32 32" width="36" height="36" fill="none">
              <rect x="2" y="14" width="28" height="16" rx="2" fill="#3b82f6" opacity="0.15" />
              <path d="M2 16 L16 6 L30 16" stroke="#3b82f6" strokeWidth="2.5" strokeLinejoin="round" fill="none" />
              <rect x="12" y="20" width="8" height="10" rx="1" fill="#3b82f6" opacity="0.6" />
              <line x1="2" y1="30" x2="30" y2="30" stroke="#3b82f6" strokeWidth="2" />
            </svg>
            <div>
              <h1 className="site-title">Architecture Studio</h1>
              <p className="site-tagline">Long Side Plan House Finder &amp; Design Advisor</p>
            </div>
          </div>

          <nav className="header-tabs">
            <button
              className={`header-tab ${activeTab === 'sketch' ? 'active' : ''}`}
              onClick={() => setActiveTab('sketch')}
            >
              Your Sketch
            </button>
            <button
              className={`header-tab ${activeTab === 'catalog' ? 'active' : ''}`}
              onClick={() => setActiveTab('catalog')}
            >
              House Catalog
            </button>
          </nav>
        </div>
      </header>

      <main className="main">
        {activeTab === 'sketch' && (
          <div className="tab-panel">
            <SketchImprovement />

            <section className="sketch-notes">
              <h3>What was improved from your sketch</h3>
              <div className="notes-grid">
                <NoteCard
                  icon="📐"
                  title="Floor Plan Zones"
                  body="Your three-zone layout was formalized into a Living/Dining wing (left), central Entry + Staircase, and a Bedroom Wing (right) with bathroom and walk-in closet."
                />
                <NoteCard
                  icon="🏠"
                  title="Elevation Clarity"
                  body="The facade was resolved with a flat roof + deep overhang, continuous upper ribbon windows, a distinct covered entry canopy, and a ground-level garage — all consistent with a contemporary long-side plan."
                />
                <NoteCard
                  icon="📏"
                  title="Proportions"
                  body="The plan is scaled to 96 ft × 40 ft — a 2.4:1 width-to-depth ratio that defines the long-side plan character. Windows and structural bays are equally spaced for rhythm."
                />
                <NoteCard
                  icon="🌿"
                  title="Suggested Next Steps"
                  body="Consider adding a rear courtyard/atrium between wings, a green roof over the garage, and landscaping berms that follow the horizontal facade. Browse the catalog for full element suggestions."
                />
              </div>
            </section>
          </div>
        )}

        {activeTab === 'catalog' && (
          <div className="tab-panel">
            <div className="catalog-intro">
              <h2 className="catalog-title">Long Side Plan Houses</h2>
              <p className="catalog-desc">
                All homes below share the key characteristic of a <strong>long-side plan</strong> — the main street-facing
                facade is the widest dimension, creating a ground-hugging, horizontally dominant composition.
                Click any card to reveal tailored design element suggestions.
              </p>
            </div>

            <SearchBar
              query={query}
              onQueryChange={setQuery}
              styleFilter={styleFilter}
              onStyleChange={setStyleFilter}
              roofFilter={roofFilter}
              onRoofChange={setRoofFilter}
              bedroomFilter={bedroomFilter}
              onBedroomChange={setBedroomFilter}
              resultCount={filtered.length}
            />

            {filtered.length === 0 ? (
              <div className="empty-state">
                <svg viewBox="0 0 64 64" width="64" height="64" fill="none">
                  <rect x="8" y="24" width="48" height="32" rx="3" stroke="#94a3b8" strokeWidth="2" />
                  <path d="M8 28 L32 12 L56 28" stroke="#94a3b8" strokeWidth="2" fill="none" />
                  <line x1="26" y1="56" x2="38" y2="56" stroke="#94a3b8" strokeWidth="2" />
                  <circle cx="46" cy="20" r="10" fill="#f1f5f9" stroke="#94a3b8" strokeWidth="2" />
                  <line x1="43" y1="20" x2="49" y2="20" stroke="#94a3b8" strokeWidth="2" />
                  <line x1="54" y1="28" x2="58" y2="32" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" />
                </svg>
                <p>No houses match your filters. Try widening the search.</p>
                <button onClick={() => { setQuery(''); setStyleFilter('All'); setRoofFilter('All'); setBedroomFilter('All'); }}>
                  Clear all filters
                </button>
              </div>
            ) : (
              <div className="house-grid">
                {filtered.map(house => (
                  <HouseCard key={house.id} house={house} />
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="site-footer">
        <p>Architecture Studio — Long Side Plan Houses &amp; Design Elements</p>
      </footer>
    </div>
  );
}

function NoteCard({ icon, title, body }: { icon: string; title: string; body: string }) {
  return (
    <div className="note-card">
      <span className="note-icon">{icon}</span>
      <h4>{title}</h4>
      <p>{body}</p>
    </div>
  );
}
