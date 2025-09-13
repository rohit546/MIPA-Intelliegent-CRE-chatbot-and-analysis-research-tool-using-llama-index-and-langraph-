-- Simple database optimizations for Georgia Properties
-- Optimized for transaction-safe execution

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =================================================================
-- BASIC INDEXES FOR CORE QUERIES
-- =================================================================

-- County searches (JSONB field)
CREATE INDEX IF NOT EXISTS idx_georgia_properties_address_county
ON "Georgia Properties" USING gin ((address->>'county') gin_trgm_ops);

-- Property type fuzzy matching
CREATE INDEX IF NOT EXISTS idx_georgia_properties_property_type_trgm
ON "Georgia Properties" USING gin (property_type gin_trgm_ops);

-- Property subtype fuzzy matching  
CREATE INDEX IF NOT EXISTS idx_georgia_properties_property_subtype_trgm
ON "Georgia Properties" USING gin (property_subtype gin_trgm_ops);

-- Status exact matches
CREATE INDEX IF NOT EXISTS idx_georgia_properties_status
ON "Georgia Properties" (status);

-- =================================================================
-- SIZE AND PRICE RANGE INDEXES
-- =================================================================

-- Size acres for range queries
CREATE INDEX IF NOT EXISTS idx_georgia_properties_size_acres
ON "Georgia Properties" (size_acres)
WHERE size_acres IS NOT NULL AND size_acres > 0;

-- Building square footage
CREATE INDEX IF NOT EXISTS idx_georgia_properties_building_sqft
ON "Georgia Properties" (building_sqft)
WHERE building_sqft IS NOT NULL AND building_sqft > 0;

-- Lot square footage
CREATE INDEX IF NOT EXISTS idx_georgia_properties_size_sqft
ON "Georgia Properties" (size_sqft)
WHERE size_sqft IS NOT NULL AND size_sqft > 0;

-- Asking price for range queries
CREATE INDEX IF NOT EXISTS idx_georgia_properties_asking_price
ON "Georgia Properties" (asking_price)
WHERE asking_price IS NOT NULL AND asking_price > 0;

-- =================================================================
-- COMPOSITE INDEXES FOR COMMON PATTERNS
-- =================================================================

-- County + property type (most common combination)
CREATE INDEX IF NOT EXISTS idx_georgia_properties_county_type
ON "Georgia Properties" ((address->>'county'), property_type)
WHERE address->>'county' IS NOT NULL;

-- Update table statistics
VACUUM ANALYZE "Georgia Properties";