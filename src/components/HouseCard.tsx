import { useState } from 'react';
import type { HousePlan } from '../types/house';
import { ElementSuggestions } from './ElementSuggestions';

interface HouseCardProps {
  house: HousePlan;
}

export function HouseCard({ house }: HouseCardProps) {
  const [expanded, setExpanded] = useState(false);
  const ratio = (house.width / house.depth).toFixed(1);

  return (
    <article className={`house-card ${expanded ? 'expanded' : ''}`}>
      <div className="house-image-wrap">
        <img src={house.imageUrl} alt={house.name} className="house-image" loading="lazy" />
        <span className="orientation-badge">Long-Side Plan</span>
        <span className="style-badge">{house.style}</span>
      </div>

      <div className="house-body">
        <div className="house-header">
          <div>
            <h2 className="house-name">{house.name}</h2>
            <p className="house-location">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              {house.location}
            </p>
          </div>
          <div className="year-badge">{house.yearBuilt}</div>
        </div>

        <p className="house-description">{house.description}</p>

        <div className="house-stats">
          <div className="stat">
            <span className="stat-value">{house.width}′</span>
            <span className="stat-label">Width</span>
          </div>
          <div className="stat">
            <span className="stat-value">{house.depth}′</span>
            <span className="stat-label">Depth</span>
          </div>
          <div className="stat">
            <span className="stat-value">{ratio}:1</span>
            <span className="stat-label">Ratio</span>
          </div>
          <div className="stat">
            <span className="stat-value">{house.squareFootage.toLocaleString()}</span>
            <span className="stat-label">Sq Ft</span>
          </div>
          <div className="stat">
            <span className="stat-value">{house.bedrooms}</span>
            <span className="stat-label">Bed</span>
          </div>
          <div className="stat">
            <span className="stat-value">{house.bathrooms}</span>
            <span className="stat-label">Bath</span>
          </div>
        </div>

        <div className="house-meta">
          <span className="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
            </svg>
            {house.roofType} Roof
          </span>
          <span className="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path d="M3 9h18M9 21V9" />
            </svg>
            {house.orientation === 'long-side' ? 'Long-Side Oriented' : house.orientation}
          </span>
        </div>

        <div className="house-tags">
          {house.tags.map(tag => (
            <span key={tag} className="tag">{tag}</span>
          ))}
        </div>

        <button
          className="expand-btn"
          onClick={() => setExpanded(prev => !prev)}
          aria-expanded={expanded}
        >
          {expanded ? 'Hide Design Elements ▲' : `View ${house.suggestedElements.length} Design Elements ▼`}
        </button>
      </div>

      {expanded && (
        <div className="house-elements">
          <ElementSuggestions elements={house.suggestedElements} />
        </div>
      )}
    </article>
  );
}
