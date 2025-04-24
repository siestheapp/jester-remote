-- Migration: Fix foreign keys and data consistency
-- Created at: 2025-04-15

-- Up Migration
BEGIN;

-- 1. Fix units first (as other tables depend on it)
ALTER TABLE public.units
    ADD CONSTRAINT units_name_unique UNIQUE (name);

-- 2. Fix brands unit reference
ALTER TABLE public.brands
    ADD COLUMN default_unit_id integer;

UPDATE public.brands b
SET default_unit_id = (
    SELECT id FROM public.units u 
    WHERE u.name = b.default_unit
);

ALTER TABLE public.brands
    ALTER COLUMN default_unit_id SET NOT NULL,
    ADD CONSTRAINT fk_default_unit FOREIGN KEY (default_unit_id) REFERENCES public.units(id),
    DROP COLUMN default_unit;

-- 3. Fix ingestion_log gender reference and add unique constraint
ALTER TABLE public.ingestion_log
    ADD COLUMN gender_id integer,
    ADD CONSTRAINT ingestion_uuid_unique UNIQUE (ingestion_uuid);

UPDATE public.ingestion_log il
SET gender_id = (
    SELECT id FROM public.genders g 
    WHERE g.name = il.gender
);

ALTER TABLE public.ingestion_log
    ALTER COLUMN gender_id SET NOT NULL,
    ADD CONSTRAINT fk_gender FOREIGN KEY (gender_id) REFERENCES public.genders(id),
    DROP COLUMN gender;

-- 4. Add missing foreign key constraints
ALTER TABLE public.apparel_items
    ADD CONSTRAINT fk_brand FOREIGN KEY (brand_id) REFERENCES public.brands(id),
    ADD CONSTRAINT fk_gender FOREIGN KEY (gender_id) REFERENCES public.genders(id),
    ADD CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES public.categories(id),
    ADD CONSTRAINT fk_subcategory FOREIGN KEY (subcategory_id) REFERENCES public.subcategories(id),
    ADD CONSTRAINT fk_fit FOREIGN KEY (fit_id) REFERENCES public.fits(id),
    ADD CONSTRAINT fk_unit FOREIGN KEY (unit_id) REFERENCES public.units(id),
    ADD CONSTRAINT fk_ingestion FOREIGN KEY (ingestion_uuid) REFERENCES public.ingestion_log(ingestion_uuid);

ALTER TABLE public.size_guides
    ADD CONSTRAINT fk_brand FOREIGN KEY (brand_id) REFERENCES public.brands(id);

ALTER TABLE public.size_aliases
    ADD CONSTRAINT fk_brand FOREIGN KEY (brand_id) REFERENCES public.brands(id),
    ADD CONSTRAINT fk_gender FOREIGN KEY (gender_id) REFERENCES public.genders(id);

-- 5. Add indexes for foreign keys for better performance
CREATE INDEX idx_apparel_brand ON public.apparel_items(brand_id);
CREATE INDEX idx_apparel_gender ON public.apparel_items(gender_id);
CREATE INDEX idx_apparel_category ON public.apparel_items(category_id);
CREATE INDEX idx_apparel_subcategory ON public.apparel_items(subcategory_id);
CREATE INDEX idx_apparel_fit ON public.apparel_items(fit_id);
CREATE INDEX idx_apparel_unit ON public.apparel_items(unit_id);
CREATE INDEX idx_apparel_ingestion ON public.apparel_items(ingestion_uuid);

CREATE INDEX idx_sizeguides_brand ON public.size_guides(brand_id);
CREATE INDEX idx_sizealiases_brand ON public.size_aliases(brand_id);
CREATE INDEX idx_sizealiases_gender ON public.size_aliases(gender_id);

COMMIT;

-- Down Migration (in case we need to rollback)
BEGIN;

-- Remove indexes
DROP INDEX IF EXISTS public.idx_apparel_brand;
DROP INDEX IF EXISTS public.idx_apparel_gender;
DROP INDEX IF EXISTS public.idx_apparel_category;
DROP INDEX IF EXISTS public.idx_apparel_subcategory;
DROP INDEX IF EXISTS public.idx_apparel_fit;
DROP INDEX IF EXISTS public.idx_apparel_unit;
DROP INDEX IF EXISTS public.idx_apparel_ingestion;
DROP INDEX IF EXISTS public.idx_sizeguides_brand;
DROP INDEX IF EXISTS public.idx_sizealiases_brand;
DROP INDEX IF EXISTS public.idx_sizealiases_gender;

-- Remove foreign key constraints
ALTER TABLE public.apparel_items
    DROP CONSTRAINT IF EXISTS fk_brand,
    DROP CONSTRAINT IF EXISTS fk_gender,
    DROP CONSTRAINT IF EXISTS fk_category,
    DROP CONSTRAINT IF EXISTS fk_subcategory,
    DROP CONSTRAINT IF EXISTS fk_fit,
    DROP CONSTRAINT IF EXISTS fk_unit,
    DROP CONSTRAINT IF EXISTS fk_ingestion;

ALTER TABLE public.size_guides
    DROP CONSTRAINT IF EXISTS fk_brand;

ALTER TABLE public.size_aliases
    DROP CONSTRAINT IF EXISTS fk_brand,
    DROP CONSTRAINT IF EXISTS fk_gender;

-- Restore ingestion_log gender column and remove unique constraint
ALTER TABLE public.ingestion_log
    ADD COLUMN gender text,
    DROP CONSTRAINT IF EXISTS ingestion_uuid_unique;

UPDATE public.ingestion_log il
SET gender = (
    SELECT name FROM public.genders g 
    WHERE g.id = il.gender_id
);

ALTER TABLE public.ingestion_log
    DROP CONSTRAINT IF EXISTS fk_gender,
    DROP COLUMN gender_id;

-- Restore brands default_unit column
ALTER TABLE public.brands
    ADD COLUMN default_unit text DEFAULT 'inches'::text;

UPDATE public.brands b
SET default_unit = (
    SELECT name FROM public.units u 
    WHERE u.id = b.default_unit_id
);

ALTER TABLE public.brands
    DROP CONSTRAINT IF EXISTS fk_default_unit,
    DROP COLUMN default_unit_id;

-- Remove units unique constraint
ALTER TABLE public.units
    DROP CONSTRAINT IF EXISTS units_name_unique;

COMMIT; 