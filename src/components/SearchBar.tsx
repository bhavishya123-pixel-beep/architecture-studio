import { type ArchitecturalStyle, type RoofType } from '../types/house';

interface SearchBarProps {
  query: string;
  onQueryChange: (q: string) => void;
  styleFilter: ArchitecturalStyle | 'All';
  onStyleChange: (s: ArchitecturalStyle | 'All') => void;
  roofFilter: RoofType | 'All';
  onRoofChange: (r: RoofType | 'All') => void;
  bedroomFilter: number | 'All';
  onBedroomChange: (b: number | 'All') => void;
  resultCount: number;
}

const STYLES: (ArchitecturalStyle | 'All')[] = [
  'All', 'Ranch', 'Craftsman', 'Prairie', 'Mid-Century Modern',
  'Mediterranean', 'Colonial', 'Contemporary',
];

const ROOFS: (RoofType | 'All')[] = ['All', 'Hip', 'Gable', 'Flat', 'Shed', 'Butterfly', 'Cross-Gable'];
const BEDROOMS: (number | 'All')[] = ['All', 3, 4, 5];

export function SearchBar({
  query, onQueryChange,
  styleFilter, onStyleChange,
  roofFilter, onRoofChange,
  bedroomFilter, onBedroomChange,
  resultCount,
}: SearchBarProps) {
  return (
    <div className="search-bar">
      <div className="search-input-wrap">
        <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>
        <input
          type="text"
          placeholder="Search by name, location, style or tag…"
          value={query}
          onChange={e => onQueryChange(e.target.value)}
          className="search-input"
        />
        {query && (
          <button className="clear-btn" onClick={() => onQueryChange('')} aria-label="Clear search">
            ×
          </button>
        )}
      </div>

      <div className="filters">
        <div className="filter-group">
          <label>Style</label>
          <select value={styleFilter} onChange={e => onStyleChange(e.target.value as ArchitecturalStyle | 'All')}>
            {STYLES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div className="filter-group">
          <label>Roof</label>
          <select value={roofFilter} onChange={e => onRoofChange(e.target.value as RoofType | 'All')}>
            {ROOFS.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>

        <div className="filter-group">
          <label>Bedrooms</label>
          <select value={bedroomFilter} onChange={e => {
            const v = e.target.value;
            onBedroomChange(v === 'All' ? 'All' : Number(v));
          }}>
            {BEDROOMS.map(b => <option key={b} value={b}>{b === 'All' ? 'All' : `${b}+`}</option>)}
          </select>
        </div>
      </div>

      <p className="result-count">
        Showing <strong>{resultCount}</strong> long-side plan house{resultCount !== 1 ? 's' : ''}
      </p>
    </div>
  );
}
