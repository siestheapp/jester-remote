-- Migration: 002_measurement_normalization
-- Created: 2025-04-15
-- Description: Normalizes measurement storage and adds validation support

-- Up Migration
BEGIN;

-- Create measurement_types table
CREATE TABLE measurement_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(30) NOT NULL, -- e.g., 'chest', 'waist', 'inseam'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create size_guide_measurements table
CREATE TABLE size_guide_measurements (
    id SERIAL PRIMARY KEY,
    size_guide_id INTEGER NOT NULL REFERENCES size_guides(id) ON DELETE CASCADE,
    measurement_type_id INTEGER NOT NULL REFERENCES measurement_types(id),
    unit_id INTEGER NOT NULL REFERENCES units(id),
    min_value DECIMAL(10,2),
    max_value DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(size_guide_id, measurement_type_id)
);

-- Create validation_rules table
CREATE TABLE validation_rules (
    id SERIAL PRIMARY KEY,
    measurement_type_id INTEGER NOT NULL REFERENCES measurement_types(id),
    unit_id INTEGER NOT NULL REFERENCES units(id),
    min_allowed DECIMAL(10,2),
    max_allowed DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(measurement_type_id, unit_id)
);

-- Modify size_guides table
ALTER TABLE size_guides
ADD COLUMN status VARCHAR(20) DEFAULT 'pending',
ADD COLUMN error_message TEXT,
ADD COLUMN processed_at TIMESTAMP WITH TIME ZONE;

-- Create indexes
CREATE INDEX idx_size_guide_measurements_size_guide_id ON size_guide_measurements(size_guide_id);
CREATE INDEX idx_size_guide_measurements_measurement_type_id ON size_guide_measurements(measurement_type_id);
CREATE INDEX idx_size_guide_measurements_unit_id ON size_guide_measurements(unit_id);

-- Insert common measurement types
INSERT INTO measurement_types (name, description, category) VALUES
('chest', 'Circumference of chest at widest point', 'upper_body'),
('waist', 'Natural waist circumference', 'lower_body'),
('inseam', 'Length from crotch to ankle', 'lower_body'),
('shoulder', 'Shoulder width point to point', 'upper_body'),
('sleeve', 'Length from shoulder to wrist', 'upper_body'),
('neck', 'Neck circumference', 'upper_body'),
('hip', 'Hip circumference at widest point', 'lower_body'),
('thigh', 'Thigh circumference', 'lower_body');

COMMIT;

-- Down Migration
BEGIN;

-- Remove added columns from size_guides
ALTER TABLE size_guides
DROP COLUMN status,
DROP COLUMN error_message,
DROP COLUMN processed_at;

-- Drop tables in reverse order of creation
DROP TABLE IF EXISTS validation_rules;
DROP TABLE IF EXISTS size_guide_measurements;
DROP TABLE IF EXISTS measurement_types;

COMMIT; 