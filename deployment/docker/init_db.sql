-- India Real Estate Intelligence OS — PostgreSQL + PostGIS Schema
-- Run once on DB initialization.

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Infrastructure projects ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS infrastructure_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id TEXT NOT NULL,
    source_url TEXT,
    source_tier SMALLINT NOT NULL CHECK (source_tier IN (1, 2, 3)),
    raw_snapshot_path TEXT,
    confidence NUMERIC(4,3) NOT NULL,
    freshness_score NUMERIC(4,3) DEFAULT 1.0,

    infra_type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    state TEXT NOT NULL,
    city TEXT,
    corridor TEXT,
    status TEXT NOT NULL,
    length_km NUMERIC(10,2),
    cost_crore NUMERIC(16,2),
    start_point TEXT,
    end_point TEXT,

    -- Spatial: store as geometry (SRID 4326 = WGS84)
    geo_line GEOMETRY(LINESTRING, 4326),
    geo_polygon GEOMETRY(POLYGON, 4326),
    geo_centroid GEOMETRY(POINT, 4326) GENERATED ALWAYS AS (
        CASE
            WHEN geo_line IS NOT NULL THEN ST_Centroid(geo_line)
            WHEN geo_polygon IS NOT NULL THEN ST_Centroid(geo_polygon)
            ELSE NULL
        END
    ) STORED,

    announcement_date DATE,
    approval_date DATE,
    tender_date DATE,
    construction_start_date DATE,
    expected_completion_date DATE,
    actual_completion_date DATE,
    executing_agency TEXT,
    project_id_official TEXT,

    published_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    data_gap BOOLEAN DEFAULT FALSE,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_infra_state ON infrastructure_records(state);
CREATE INDEX IF NOT EXISTS idx_infra_city ON infrastructure_records(city);
CREATE INDEX IF NOT EXISTS idx_infra_status ON infrastructure_records(status);
CREATE INDEX IF NOT EXISTS idx_infra_type ON infrastructure_records(infra_type);
CREATE INDEX IF NOT EXISTS idx_infra_geo ON infrastructure_records USING GIST(geo_centroid);
CREATE INDEX IF NOT EXISTS idx_infra_project_id ON infrastructure_records(project_id_official);


-- ── RERA projects ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS rera_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id TEXT NOT NULL,
    source_url TEXT,
    source_tier SMALLINT DEFAULT 1,
    raw_snapshot_path TEXT,
    confidence NUMERIC(4,3) NOT NULL,
    freshness_score NUMERIC(4,3) DEFAULT 1.0,

    rera_registration_number TEXT NOT NULL,
    rera_portal TEXT NOT NULL,
    project_name TEXT NOT NULL,
    developer_name TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    state TEXT NOT NULL,
    city TEXT NOT NULL,
    locality TEXT,
    pin_code TEXT,
    geo_point GEOMETRY(POINT, 4326),

    rera_status TEXT NOT NULL,
    registration_date DATE,
    registration_expiry DATE,
    promised_possession_date DATE,
    revised_possession_date DATE,
    actual_possession_date DATE,
    total_units INTEGER,
    units_sold INTEGER,
    units_remaining INTEGER,
    complaint_count INTEGER,
    active_complaints INTEGER,
    possession_delay_days INTEGER,

    published_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data_gap BOOLEAN DEFAULT FALSE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_rera_number ON rera_records(rera_registration_number, rera_portal);
CREATE INDEX IF NOT EXISTS idx_rera_city ON rera_records(city);
CREATE INDEX IF NOT EXISTS idx_rera_status ON rera_records(rera_status);
CREATE INDEX IF NOT EXISTS idx_rera_developer ON rera_records(developer_name);
CREATE INDEX IF NOT EXISTS idx_rera_geo ON rera_records USING GIST(geo_point);


-- ── Market price records ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS market_price_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id TEXT NOT NULL,
    source_url TEXT,
    source_tier SMALLINT NOT NULL,
    confidence NUMERIC(4,3) NOT NULL,
    freshness_score NUMERIC(4,3) DEFAULT 1.0,

    city TEXT NOT NULL,
    state TEXT NOT NULL,
    locality TEXT NOT NULL,
    pin_code TEXT,
    geo_point GEOMETRY(POINT, 4326),
    asset_type TEXT NOT NULL,
    segment TEXT NOT NULL,

    price_per_sqft NUMERIC(12,2),
    price_per_sqft_yoy_pct NUMERIC(8,2),
    price_per_sqft_qoq_pct NUMERIC(8,2),
    monthly_rent_per_sqft NUMERIC(10,2),
    gross_yield_pct NUMERIC(6,3),
    net_yield_pct NUMERIC(6,3),
    inventory_units INTEGER,
    absorption_rate_pct NUMERIC(6,2),
    days_on_market NUMERIC(8,1),
    new_launches_units INTEGER,
    unsold_inventory_months NUMERIC(6,1),
    observation_period TEXT NOT NULL,

    published_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data_gap BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_price_city_locality ON market_price_records(city, locality);
CREATE INDEX IF NOT EXISTS idx_price_period ON market_price_records(observation_period);
CREATE INDEX IF NOT EXISTS idx_price_geo ON market_price_records USING GIST(geo_point);


-- ── Macro signals ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS macro_signal_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id TEXT NOT NULL,
    source_tier SMALLINT DEFAULT 1,
    confidence NUMERIC(4,3) NOT NULL,
    signal_type TEXT NOT NULL,
    value NUMERIC(12,4) NOT NULL,
    unit TEXT NOT NULL,
    period TEXT NOT NULL,
    yoy_change NUMERIC(10,4),
    qoq_change NUMERIC(10,4),
    direction TEXT DEFAULT 'neutral',
    rbi_commentary TEXT,
    published_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_macro_type ON macro_signal_records(signal_type);
CREATE INDEX IF NOT EXISTS idx_macro_period ON macro_signal_records(period);


-- ── Developer records ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS developer_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id TEXT NOT NULL,
    confidence NUMERIC(4,3) NOT NULL,
    name TEXT NOT NULL,
    registered_name TEXT,
    state TEXT,
    total_projects INTEGER,
    completed_projects INTEGER,
    ongoing_projects INTEGER,
    delayed_projects INTEGER,
    rera_complaints_total INTEGER,
    avg_possession_delay_days NUMERIC(8,1),
    on_time_delivery_rate_pct NUMERIC(5,1),
    published_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_developer_name ON developer_records(name);


-- ── Location score cards ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS location_score_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    locality TEXT NOT NULL,
    pin_code TEXT,
    geo_point GEOMETRY(POINT, 4326),
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    infrastructure_uplift JSONB,
    connectivity JSONB,
    affordability JSONB,
    rental_yield JSONB,
    liquidity JSONB,
    regulatory_safety JSONB,
    developer_trust JSONB,
    execution_risk JSONB,
    appreciation_potential JSONB,

    final_score NUMERIC(5,2),
    final_confidence NUMERIC(4,3),
    data_completeness_pct NUMERIC(5,1),
    human_review_required BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scores_city ON location_score_cards(city);
CREATE INDEX IF NOT EXISTS idx_scores_final ON location_score_cards(final_score DESC);
CREATE INDEX IF NOT EXISTS idx_scores_geo ON location_score_cards USING GIST(geo_point);


-- ── Alerts ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    location TEXT,
    city TEXT,
    affected_project_ids UUID[],
    affected_infra_ids UUID[],
    evidence_ids UUID[],
    source_ids TEXT[],
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMPTZ,
    data JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_city ON alerts(city);
CREATE INDEX IF NOT EXISTS idx_alerts_triggered ON alerts(triggered_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged) WHERE acknowledged = FALSE;


-- ── Spatial helper functions ──────────────────────────────────────────────────

-- Find infrastructure within radius of a point (in km)
CREATE OR REPLACE FUNCTION find_infra_within_radius(
    p_lat FLOAT, p_lon FLOAT, p_radius_km FLOAT
)
RETURNS TABLE(
    id UUID, name TEXT, infra_type TEXT, status TEXT,
    distance_km FLOAT, city TEXT, state TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ir.id, ir.name, ir.infra_type, ir.status,
        ST_Distance(
            ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326)::geography,
            ir.geo_centroid::geography
        ) / 1000 AS distance_km,
        ir.city, ir.state
    FROM infrastructure_records ir
    WHERE ir.geo_centroid IS NOT NULL
      AND ST_DWithin(
            ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326)::geography,
            ir.geo_centroid::geography,
            p_radius_km * 1000
          )
    ORDER BY distance_km;
END;
$$ LANGUAGE plpgsql;
