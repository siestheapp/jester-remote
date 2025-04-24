from typing import Dict, Any, Optional
import json
from datetime import datetime
from ..db.models import SizeGuide, MeasurementType, SizeGuideMeasurement, ValidationRule
from ..core.vision import run_vision_prompt
from ..utils.vector_mapper import match_to_standard

class SizeService:
    def __init__(self, db_session):
        self.db = db_session

    async def process_size_guide(
        self,
        image_path: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a size guide image and store normalized measurements.
        
        Args:
            image_path: Path to the uploaded size guide image
            metadata: Dictionary containing:
                - brand: Brand name
                - gender: Gender (Men, Women, Unisex)
                - size_guide_header: Category header
                - source_url: Source URL
                - unit: Unit of measurement
                - scope: Size guide scope
        
        Returns:
            Dictionary containing processing results and status
        """
        try:
            # Create size guide record
            size_guide = SizeGuide(
                brand=metadata["brand"],
                gender=metadata["gender"],
                category=metadata["size_guide_header"],
                source_url=metadata["source_url"],
                status="processing"
            )
            self.db.add(size_guide)
            await self.db.flush()  # Get the ID without committing

            # Extract measurements using GPT-4 Vision
            gpt_output = run_vision_prompt(image_path)
            
            # Parse JSON from GPT output
            try:
                json_start = gpt_output.index("{")
                json_end = gpt_output.rindex("}") + 1
                measurements_data = json.loads(gpt_output[json_start:json_end])
            except (ValueError, json.JSONDecodeError) as e:
                size_guide.status = "error"
                size_guide.error_message = f"Failed to parse GPT output: {str(e)}"
                await self.db.commit()
                return {"success": False, "error": str(e)}

            # Get unit ID for the specified unit
            unit_id = await self._get_unit_id(metadata["unit"])
            
            # Process each measurement
            for size_label, measurements in measurements_data.items():
                for measure_name, value in measurements.items():
                    # Match the measurement name to our standard types
                    standard_name = match_to_standard(measure_name)
                    if not standard_name:
                        continue  # Skip unrecognized measurements
                    
                    # Get or create measurement type
                    measurement_type = await self._get_measurement_type(standard_name)
                    
                    # Create measurement record
                    measurement = SizeGuideMeasurement(
                        size_guide_id=size_guide.id,
                        measurement_type_id=measurement_type.id,
                        unit_id=unit_id,
                        min_value=value if isinstance(value, (int, float)) else None,
                        max_value=value if isinstance(value, (int, float)) else None
                    )
                    self.db.add(measurement)

            # Validate measurements against rules
            validation_errors = await self._validate_measurements(size_guide.id)
            if validation_errors:
                size_guide.status = "error"
                size_guide.error_message = "Validation errors: " + ", ".join(validation_errors)
            else:
                size_guide.status = "active"
            
            size_guide.processed_at = datetime.utcnow()
            await self.db.commit()

            return {
                "success": True,
                "size_guide_id": size_guide.id,
                "status": size_guide.status,
                "measurements": measurements_data
            }

        except Exception as e:
            if size_guide:
                size_guide.status = "error"
                size_guide.error_message = str(e)
                await self.db.commit()
            return {"success": False, "error": str(e)}

    async def _get_unit_id(self, unit_name: str) -> int:
        """Get the ID for a unit of measurement."""
        unit = await self.db.query("SELECT id FROM units WHERE name = :name", 
                                 {"name": unit_name}).first()
        if not unit:
            raise ValueError(f"Unknown unit: {unit_name}")
        return unit.id

    async def _get_measurement_type(self, name: str) -> MeasurementType:
        """Get or create a measurement type."""
        measurement_type = await self.db.query(MeasurementType).filter(
            MeasurementType.name == name
        ).first()
        
        if not measurement_type:
            # Determine category based on name
            category = "upper_body" if name in ["chest", "shoulder", "sleeve", "neck"] else "lower_body"
            measurement_type = MeasurementType(
                name=name,
                description=f"Measurement for {name}",
                category=category
            )
            self.db.add(measurement_type)
            await self.db.flush()
        
        return measurement_type

    async def _validate_measurements(self, size_guide_id: int) -> list[str]:
        """
        Validate measurements against rules.
        Returns a list of validation error messages.
        """
        errors = []
        measurements = await self.db.query(SizeGuideMeasurement).filter(
            SizeGuideMeasurement.size_guide_id == size_guide_id
        ).all()
        
        for measurement in measurements:
            rules = await self.db.query(ValidationRule).filter(
                ValidationRule.measurement_type_id == measurement.measurement_type_id,
                ValidationRule.unit_id == measurement.unit_id
            ).first()
            
            if rules:
                # Convert values to float for comparison
                min_value = float(measurement.min_value) if measurement.min_value is not None else None
                max_value = float(measurement.max_value) if measurement.max_value is not None else None
                min_allowed = float(rules.min_allowed) if rules.min_allowed is not None else None
                max_allowed = float(rules.max_allowed) if rules.max_allowed is not None else None
                
                if min_value is not None and min_allowed is not None and min_value < min_allowed:
                    errors.append(f"{measurement.measurement_type.name} below minimum allowed value")
                if max_value is not None and max_allowed is not None and max_value > max_allowed:
                    errors.append(f"{measurement.measurement_type.name} above maximum allowed value")
        
        return errors
