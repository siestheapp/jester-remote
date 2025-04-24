# Database Changelog

This document tracks all significant changes to the database schema.

## [002] - 2025-04-15 - Measurement Normalization

### Added
- `measurement_types` table
  - Standardizes measurement names and descriptions
  - Includes common measurements like chest, waist, sleeve, neck, etc.
  - Enforces unique measurement names

- `size_guide_measurements` table
  - Links measurements to size guides
  - Stores min/max values for each measurement
  - References measurement types and units
  - Ensures unique measurements per size guide

- `validation_rules` table
  - Defines allowed ranges for measurements
  - Links to measurement types and units
  - Initial rules added for chest, waist, and neck measurements

### Modified
- `size_guides` table
  - Added `status` column (values: draft, processing, active, error)
  - Added `error_message` column for tracking issues
  - Added `processed_at` timestamp

### Indexes
- Created index on `size_guide_measurements(size_guide_id)`
- Created index on `size_guide_measurements(measurement_type_id)`
- Created index on `size_guide_measurements(unit_id)`

### Data Migration
- Migrated existing measurement data from the `size_guides` table to the new normalized structure
- Preserved all existing measurement values
- Defaulted to inches for unit where not specified

### Purpose
This migration normalizes the storage of measurements in the database, making it easier to:
- Validate measurement data during ingestion
- Support multiple measurement systems
- Track the status of size guide processing
- Ensure data consistency through proper constraints

### Rollback
The migration includes a down script that will:
- Remove the validation_rules table
- Remove new columns from size_guides
- Remove the size_guide_measurements table
- Remove the measurement_types table

### Migration File
- Location: `data/migrations/002_measurement_normalization.sql`
- Execution Script: `scripts/run_migration.py` 