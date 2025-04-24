# System Architecture

## Database Schema

### Core Tables

1. **apparel_items**
   - Primary table for storing clothing measurements
   - Links to brands, categories, and fits
   - Stores measurement ranges (min/max) for various body parts

2. **brands**
   - Stores brand information
   - Includes default unit system (inches/cm)

3. **categories** and **subcategories**
   - Hierarchical organization of clothing types
   - Categories: tops, bottoms, outerwear, etc.
   - Subcategories: dress shirts, t-shirts, jeans, etc.

4. **fits**
   - Stores different fit types (slim, regular, relaxed)
   - Includes descriptions and gender associations

5. **size_guides**
   - Brand-specific size guide information
   - Similar structure to apparel_items
   - Includes source URLs and ingestion metadata

6. **size_aliases**
   - Maps different size labels to standardized sizes
   - Helps with cross-brand size comparison

### Supporting Tables

1. **genders**
   - Basic gender categorization

2. **units**
   - Measurement unit systems

3. **ingestion_log**
   - Tracks data ingestion processes
   - Stores metadata about source files

## Data Flow

1. **Data Ingestion**
   - Source files → ingestion_log
   - Parsed data → size_guides
   - Processed data → apparel_items

2. **Size Processing**
   - Raw measurements → standardized units
   - Brand-specific sizes → size_aliases
   - Category/fit assignment

## Current Issues and TODOs

1. **Database Improvements Needed**
   - Add foreign key constraints
   - Create missing indexes
   - Add data validation constraints
   - Implement proper unit conversion

2. **Data Quality**
   - Standardize measurement units
   - Validate size ranges
   - Ensure consistent category hierarchy

3. **Performance Considerations**
   - Index optimization
   - Query optimization
   - Data partitioning strategy

## API Structure

[To be documented]

## Frontend Components

[To be documented] 