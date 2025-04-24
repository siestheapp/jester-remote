-- Reset sequences
ALTER SEQUENCE public.genders_id_seq RESTART WITH 1;
ALTER SEQUENCE public.units_id_seq RESTART WITH 1;
ALTER SEQUENCE public.measurement_types_id_seq RESTART WITH 1;
ALTER SEQUENCE public.brands_id_seq RESTART WITH 1;
ALTER SEQUENCE public.categories_id_seq RESTART WITH 1;
ALTER SEQUENCE public.subcategories_id_seq RESTART WITH 1;
ALTER SEQUENCE public.fits_id_seq RESTART WITH 1;

-- Seed Genders
INSERT INTO public.genders (name) VALUES
    ('Men''s'),
    ('Women''s'),
    ('Unisex');

-- Seed Units
INSERT INTO public.units (name, abbreviation, description) VALUES
    ('inches', 'in', 'Imperial measurement unit commonly used in US and UK'),
    ('centimeters', 'cm', 'Metric measurement unit used internationally');

-- Seed Measurement Types
INSERT INTO public.measurement_types (name, description) VALUES
    ('Chest', 'Circumference measurement around the fullest part of the chest'),
    ('Waist', 'Circumference measurement around the natural waistline'),
    ('Hip', 'Circumference measurement around the fullest part of the hips'),
    ('Neck', 'Circumference measurement around the base of the neck'),
    ('Shoulder', 'Measurement across the back from shoulder point to shoulder point'),
    ('Sleeve Length', 'Measurement from shoulder point to wrist'),
    ('Inseam', 'Measurement from crotch to bottom of leg'),
    ('Outseam', 'Measurement from waist to bottom of leg along the outside'),
    ('Rise', 'Measurement from crotch to waistband'),
    ('Thigh', 'Circumference measurement around the fullest part of the thigh'),
    ('Bicep', 'Circumference measurement around the fullest part of the upper arm'),
    ('Wrist', 'Circumference measurement around the wrist');

-- Seed Brands
INSERT INTO public.brands (name, website, description) VALUES
    ('Banana Republic', 'https://bananarepublic.gap.com', 'American clothing and accessories retailer owned by Gap Inc.'),
    ('J.Crew', 'https://www.jcrew.com', 'American multi-brand, multi-channel, specialty retailer'),
    ('Uniqlo', 'https://www.uniqlo.com', 'Japanese casual wear designer, manufacturer and retailer'),
    ('Zara', 'https://www.zara.com', 'Spanish apparel retailer'),
    ('H&M', 'https://www.hm.com', 'Swedish multinational clothing retail company');

-- Seed Categories
INSERT INTO public.categories (name, description) VALUES
    ('Tops', 'Upper body garments including shirts, t-shirts, and sweaters'),
    ('Bottoms', 'Lower body garments including pants, shorts, and skirts'),
    ('Outerwear', 'Outdoor and cold weather garments'),
    ('Suits', 'Formal wear and business attire'),
    ('Activewear', 'Athletic and sports clothing');

-- Seed Subcategories
INSERT INTO public.subcategories (category_id, name, description) VALUES
    (1, 'Dress Shirts', 'Formal button-up shirts'),
    (1, 'T-Shirts', 'Casual short-sleeved shirts'),
    (1, 'Sweaters', 'Knitted upper body garments'),
    (2, 'Chinos', 'Casual cotton twill pants'),
    (2, 'Jeans', 'Denim pants'),
    (2, 'Shorts', 'Short pants'),
    (3, 'Jackets', 'Light to medium weight outerwear'),
    (3, 'Coats', 'Heavy weight outerwear'),
    (4, 'Suit Jackets', 'Formal suit upper pieces'),
    (4, 'Suit Pants', 'Formal suit lower pieces'),
    (5, 'Athletic Shirts', 'Performance tops for sports and exercise'),
    (5, 'Athletic Pants', 'Performance bottoms for sports and exercise');

-- Seed Fits
INSERT INTO public.fits (name, description) VALUES
    ('Regular', 'Standard fit with moderate room throughout'),
    ('Slim', 'Tailored fit with less room throughout'),
    ('Relaxed', 'Generous fit with more room throughout'),
    ('Athletic', 'Extra room in chest and thighs, tapered waist'),
    ('Skinny', 'Very close-fitting throughout');

-- Seed Validation Rules
INSERT INTO public.validation_rules (measurement_type_id, min_value, max_value, unit_id, description) VALUES
    (1, 30, 60, 1, 'Valid chest measurement range in inches'),
    (1, 76, 152, 2, 'Valid chest measurement range in centimeters'),
    (2, 24, 54, 1, 'Valid waist measurement range in inches'),
    (2, 61, 137, 2, 'Valid waist measurement range in centimeters'),
    (3, 30, 60, 1, 'Valid hip measurement range in inches'),
    (3, 76, 152, 2, 'Valid hip measurement range in centimeters'),
    (4, 13, 22, 1, 'Valid neck measurement range in inches'),
    (4, 33, 56, 2, 'Valid neck measurement range in centimeters');

-- Add some common size aliases
INSERT INTO public.size_aliases (brand_id, gender_id, size_label, mapped_size) VALUES
    (1, 1, 'S', 'Small'),
    (1, 1, 'M', 'Medium'),
    (1, 1, 'L', 'Large'),
    (1, 1, 'XL', 'Extra Large'),
    (2, 1, 'S', 'Small'),
    (2, 1, 'M', 'Medium'),
    (2, 1, 'L', 'Large'),
    (2, 1, 'XL', 'Extra Large'); 