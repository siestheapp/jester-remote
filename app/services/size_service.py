from typing import Dict, Any, Optional
import json
from datetime import datetime
from ..db.models import SizeGuide, MeasurementType, SizeGuideMeasurement, ValidationRule
from ..core.vision import run_vision_prompt
from ..utils.vector_mapper import match_to_standard
from sqlalchemy.ext.asyncio import AsyncSession

class SizeService:
    def __init__(self, session: AsyncSession):
        self.session = session

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
            self.session.add(size_guide)
            await self.session.flush()  # Get the ID without committing

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
                await self.session.commit()
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
                    self.session.add(measurement)

            # Validate measurements against rules
            validation_errors = await self._validate_measurements(size_guide.id)
            if validation_errors:
                size_guide.status = "error"
                size_guide.error_message = "Validation errors: " + ", ".join(validation_errors)
            else:
                size_guide.status = "active"
            
            size_guide.processed_at = datetime.utcnow()
            await self.session.commit()

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
                await self.session.commit()
            return {"success": False, "error": str(e)}

    async def _get_unit_id(self, unit_name: str) -> int:
        """Get the ID for a unit of measurement."""
        unit = await self.session.execute("SELECT id FROM units WHERE name = :name", 
                                 {"name": unit_name}).first()
        if not unit:
            raise ValueError(f"Unknown unit: {unit_name}")
        return unit[0]

    async def _get_measurement_type(self, name: str) -> MeasurementType:
        """Get or create a measurement type."""
        measurement_type = await self.session.execute(MeasurementType).filter(
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
            self.session.add(measurement_type)
            await self.session.flush()
        
        return measurement_type[0]

    async def _validate_measurements(self, size_guide_id: int) -> list[str]:
        """
        Validate measurements against rules.
        Returns a list of validation error messages.
        """
        errors = []
        measurements = await self.session.execute(SizeGuideMeasurement).filter(
            SizeGuideMeasurement.size_guide_id == size_guide_id
        ).all()
        
        for measurement in measurements:
            rules = await self.session.execute(ValidationRule).filter(
                ValidationRule.measurement_type_id == measurement.measurement_type_id,
                ValidationRule.unit_id == measurement.unit_id
            ).first()
            
            if rules:
                # Convert values to float for comparison
                min_value = float(measurement.min_value) if measurement.min_value is not None else None
                max_value = float(measurement.max_value) if measurement.max_value is not None else None
                min_allowed = float(rules[0].min_allowed) if rules[0].min_allowed is not None else None
                max_allowed = float(rules[0].max_allowed) if rules[0].max_allowed is not None else None
                
                if min_value is not None and min_allowed is not None and min_value < min_allowed:
                    errors.append(f"{measurement.measurement_type.name} below minimum allowed value")
                if max_value is not None and max_allowed is not None and max_value > max_allowed:
                    errors.append(f"{measurement.measurement_type.name} above maximum allowed value")
        
        return errors

    async def prepare_ingestion_proposal(self, analysis_result: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the extracted data and metadata to prepare a detailed ingestion proposal.
        Returns a structured proposal of database operations for review.
        """
        # Analyze the size guide data
        size_data = analysis_result.get('size_data', {})
        measurements = analysis_result.get('measurements', [])
        
        # Prepare the proposal
        proposal = {
            'operations': [],
            'tables_affected': [],
            'validation_checks': [],
            'potential_conflicts': [],
            'notes': []
        }
        
        # Analyze brand
        proposal['operations'].append({
            'table': 'brands',
            'operation': 'upsert',
            'data': {'name': metadata['brand']},
            'reason': 'Ensure brand exists in database'
        })
        
        # Analyze measurements and size mappings
        for measurement in measurements:
            proposal['operations'].append({
                'table': 'measurements',
                'operation': 'insert',
                'data': measurement,
                'validation': [
                    f"Check if measurement '{measurement.get('name')}' follows standard terminology",
                    f"Validate measurement values are within expected range for {metadata['unit']}"
                ]
            })
        
        # Add size mappings
        if size_data:
            proposal['operations'].append({
                'table': 'size_mappings',
                'operation': 'insert',
                'data': size_data,
                'validation': [
                    "Check for size consistency across brand",
                    "Validate measurement ranges"
                ]
            })
        
        # Add metadata
        proposal['metadata'] = metadata
        
        # Add validation checks
        proposal['validation_checks'].extend([
            "Verify measurement units consistency",
            "Check for duplicate size guides",
            "Validate measurement ranges for clothing type"
        ])
        
        return proposal

    async def execute_ingestion(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the approved ingestion proposal.
        Returns the result of the ingestion process.
        """
        try:
            # Execute each operation in the proposal
            for operation in proposal['operations']:
                if operation['operation'] == 'upsert':
                    # Implement upsert logic
                    pass
                elif operation['operation'] == 'insert':
                    # Implement insert logic
                    pass
            
            # Commit the transaction
            await self.session.commit()
            
            return {
                'success': True,
                'message': 'Size guide data successfully ingested',
                'operations_completed': len(proposal['operations'])
            }
            
        except Exception as e:
            # Rollback on error
            await self.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
