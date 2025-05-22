import logging
from sqlalchemy import select
from app.db.models import Brand, Category, Unit, SizeGuide, SizeGuideMeasurement, MeasurementType, Gender
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
import re

logger = logging.getLogger(__name__)

def parse_range(value):
    """Parse a value like '32-34' or '32 - 34' into (32, 34). If not a range, return (value, value)."""
    if isinstance(value, (int, float)):
        return value, value
    if isinstance(value, str):
        match = re.match(r"\s*(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*", value)
        if match:
            return float(match.group(1)), float(match.group(2))
        try:
            return float(value), float(value)
        except Exception:
            return None, None
    return None, None

async def get_or_create(session, model, defaults=None, **kwargs):
    instance = await session.scalar(select(model).filter_by(**kwargs))
    if instance:
        return instance
    params = dict((k, v) for k, v in kwargs.items())
    if defaults:
        params.update(defaults)
    instance = model(**params)
    session.add(instance)
    await session.flush()
    return instance

async def get_measurement_type_id(session, name):
    mt = await session.scalar(select(MeasurementType).filter_by(name=name))
    if mt:
        return mt.id
    # Create if not exists
    mt = MeasurementType(name=name, description=f"Auto-created for {name}")
    session.add(mt)
    await session.flush()
    return mt.id

async def ingest_size_guide(data: dict, session: AsyncSession):
    """
    Ingests a standardized size guide dict into the database.
    Assumes data is already validated and approved.
    """
    # Support both top-level and metadata dict for all key fields
    metadata_dict = data.get("metadata") or {}
    brand_name = data.get("brand") or metadata_dict.get("brand")
    category_name = data.get("category") or metadata_dict.get("category")
    unit_name = data.get("unit", "inches") or metadata_dict.get("unit", "inches")
    header = data.get("header") or metadata_dict.get("header")
    source_url = data.get("source_url") or metadata_dict.get("source_url")
    scope = data.get("scope") or metadata_dict.get("scope")
    gender_name = data.get("gender") or metadata_dict.get("gender")

    # Debug logging
    print(f"[IngestionService] Extracted brand_name: {brand_name}")
    print(f"[IngestionService] metadata_dict: {metadata_dict}")
    print(f"[IngestionService] data: {data}")

    # Fail fast if brand_name is missing
    if not brand_name:
        raise ValueError(f"Brand name is missing in data: {data}")

    # Normalize sizes to a list of dicts
    sizes = data.get("sizes")
    if isinstance(sizes, dict):
        sizes = [{"size": k, **v} for k, v in sizes.items()]
    elif not isinstance(sizes, list):
        sizes = []
    print(f"[IngestionService] brand_name: {brand_name}, sizes: {sizes}")

    # 1. Get or create brand, category, unit, gender
    unit = await get_or_create(session, Unit, name=unit_name)
    brand = await get_or_create(session, Brand, name=brand_name, defaults={"default_unit_id": unit.id})
    gender = await get_or_create(session, Gender, name=gender_name) if gender_name else None
    category = await get_or_create(session, Category, name=category_name, gender_id=gender.id if gender else None)

    # 2. Create size guide (fill all required fields)
    size_guide = SizeGuide(
        brand_id=brand.id,
        category_id=category.id if category else None,
        size_guide_header=header,
        source_url=source_url,
        scope=scope,
        gender_id=gender.id if gender else None,
        # You may want to add ingestion_uuid, subcategory_id, etc.
        size_label="",  # Placeholder, as your schema requires it
    )
    session.add(size_guide)
    await session.flush()

    # 3. Insert size/measurement rows
    for size_row in sizes:
        size_label = size_row.get("size")
        for field, value in size_row.items():
            if field == "size":
                continue
            measurement_type_id = await get_measurement_type_id(session, field)
            min_value, max_value = parse_range(value)
            measurement = SizeGuideMeasurement(
                size_guide_id=size_guide.id,
                measurement_type_id=measurement_type_id,
                min_value=min_value,
                max_value=max_value,
                unit_id=unit.id
            )
            session.add(measurement)
    await session.commit()
    logger.info(f"Ingested size guide for brand={brand_name}, category={category_name}")
    return size_guide.id

class IngestService:
    def __init__(self):
        pass

    def process_size_guide(self, size_data, metadata):
        """
        Process a size guide with its metadata.
        
        Args:
            size_data (dict): The extracted size guide data
            metadata (dict): Metadata about the size guide including brand, gender, etc.
            
        Returns:
            bool: True if processing was successful
        """
        try:
            # For now, just return success
            # TODO: Implement actual processing logic
            return True
        except Exception as e:
            print(f"Error processing size guide: {str(e)}")
            return False
