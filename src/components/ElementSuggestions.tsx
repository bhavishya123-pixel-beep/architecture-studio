import { useState } from 'react';
import type { DesignElement, FacadeCategory } from '../types/house';

const CATEGORY_ICONS: Record<FacadeCategory, string> = {
  Exterior: '🏠',
  Interior: '🛋',
  Structural: '🏗',
  Landscape: '🌿',
  Roof: '🔺',
};

const CATEGORY_COLORS: Record<FacadeCategory, string> = {
  Exterior: '#3b82f6',
  Interior: '#8b5cf6',
  Structural: '#f59e0b',
  Landscape: '#10b981',
  Roof: '#ef4444',
};

interface ElementSuggestionsProps {
  elements: DesignElement[];
}

export function ElementSuggestions({ elements }: ElementSuggestionsProps) {
  const [activeCategory, setActiveCategory] = useState<FacadeCategory | 'All'>('All');

  const categories = ['All', ...Array.from(new Set(elements.map(e => e.category)))] as (FacadeCategory | 'All')[];
  const filtered = activeCategory === 'All' ? elements : elements.filter(e => e.category === activeCategory);

  return (
    <div className="elements-panel">
      <h3 className="elements-title">Suggested Design Elements</h3>

      <div className="category-tabs">
        {categories.map(cat => (
          <button
            key={cat}
            className={`cat-tab ${activeCategory === cat ? 'active' : ''}`}
            style={activeCategory === cat && cat !== 'All'
              ? { borderColor: CATEGORY_COLORS[cat as FacadeCategory], color: CATEGORY_COLORS[cat as FacadeCategory] }
              : {}}
            onClick={() => setActiveCategory(cat)}
          >
            {cat !== 'All' ? CATEGORY_ICONS[cat as FacadeCategory] : '⊞'} {cat}
          </button>
        ))}
      </div>

      <div className="elements-grid">
        {filtered.map(el => (
          <div key={el.id} className="element-card">
            <div
              className="element-category-badge"
              style={{ background: CATEGORY_COLORS[el.category] }}
            >
              {CATEGORY_ICONS[el.category]} {el.category}
            </div>
            <h4 className="element-name">{el.name}</h4>
            <p className="element-description">{el.description}</p>
            <div className="element-why">
              <span className="why-label">Why it fits</span>
              <p>{el.whyItFits}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
