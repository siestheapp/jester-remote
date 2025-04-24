import pytest
from hypothesis import given, strategies as st
from typing import List, Dict, Any
from app.utils.vector_mapper import VectorMapper

@pytest.fixture
def vector_mapper():
    # Initialize with some test data
    test_data = {
        "chest": ["chest", "bust", "chest circumference"],
        "waist": ["waist", "midsection", "waist circumference"],
        "inseam": ["inseam", "inside leg", "leg length"],
        "shoulder": ["shoulder", "shoulder width", "across shoulder"]
    }
    return VectorMapper(measurement_mappings=test_data)

class TestVectorMapper:
    def test_exact_match(self, vector_mapper):
        """Test exact matches for measurement terms."""
        assert vector_mapper.map_measurement("chest") == "chest"
        assert vector_mapper.map_measurement("waist") == "waist"
        assert vector_mapper.map_measurement("inseam") == "inseam"

    def test_common_variations(self, vector_mapper):
        """Test common variations of measurement terms."""
        assert vector_mapper.map_measurement("bust") == "chest"
        assert vector_mapper.map_measurement("chest circumference") == "chest"
        assert vector_mapper.map_measurement("inside leg") == "inseam"

    def test_case_insensitivity(self, vector_mapper):
        """Test case-insensitive matching."""
        assert vector_mapper.map_measurement("CHEST") == "chest"
        assert vector_mapper.map_measurement("Waist") == "waist"
        assert vector_mapper.map_measurement("InSeam") == "inseam"

    def test_whitespace_handling(self, vector_mapper):
        """Test handling of extra whitespace."""
        assert vector_mapper.map_measurement("  chest  ") == "chest"
        assert vector_mapper.map_measurement("waist\t") == "waist"
        assert vector_mapper.map_measurement(" chest circumference ") == "chest"

    def test_semantic_matching(self, vector_mapper):
        """Test semantic matching with similarity threshold."""
        # These should match with high similarity
        assert vector_mapper.map_measurement("chest measurement") == "chest"
        assert vector_mapper.map_measurement("waistline") == "waist"

    def test_non_matching(self, vector_mapper):
        """Test behavior with non-matching terms."""
        assert vector_mapper.map_measurement("xyz123") is None
        assert vector_mapper.map_measurement("") is None
        assert vector_mapper.map_measurement("   ") is None

    def test_threshold_behavior(self, vector_mapper):
        """Test behavior with different similarity thresholds."""
        # Test with custom threshold
        result = vector_mapper.map_measurement(
            "chest area", similarity_threshold=0.7
        )
        assert result == "chest"

        # Test with stricter threshold
        result = vector_mapper.map_measurement(
            "chest area", similarity_threshold=0.95
        )
        assert result is None

    def test_get_measurement_categories(self, vector_mapper):
        """Test retrieval of measurement categories."""
        categories = vector_mapper.get_measurement_categories()
        assert isinstance(categories, list)
        assert "chest" in categories
        assert "waist" in categories
        assert "inseam" in categories
        assert "shoulder" in categories

    @given(st.text(min_size=1, max_size=50))
    def test_property_based_input(self, vector_mapper, input_text):
        """Property-based test for input handling."""
        try:
            result = vector_mapper.map_measurement(input_text)
            assert isinstance(result, str) or result is None
        except Exception as e:
            pytest.fail(f"Failed with input {input_text}: {str(e)}")

    def test_batch_mapping(self, vector_mapper):
        """Test batch mapping of multiple measurements."""
        inputs = ["chest", "waistline", "leg length", "invalid"]
        expected = ["chest", "waist", "inseam", None]
        results = vector_mapper.batch_map_measurements(inputs)
        assert results == expected

    def test_data_structure_integrity(self, vector_mapper):
        """Test the integrity of internal data structures."""
        # Test that internal mappings are properly maintained
        internal_mappings = vector_mapper.get_measurement_mappings()
        assert isinstance(internal_mappings, dict)
        assert all(isinstance(k, str) for k in internal_mappings.keys())
        assert all(isinstance(v, list) for v in internal_mappings.values())

    def test_update_mappings(self, vector_mapper):
        """Test updating measurement mappings."""
        new_mappings = {"neck": ["neck", "neck circumference"]}
        vector_mapper.update_mappings(new_mappings)
        assert vector_mapper.map_measurement("neck") == "neck"
        assert vector_mapper.map_measurement("neck circumference") == "neck"

    @pytest.mark.asyncio
    async def test_async_batch_mapping(self, vector_mapper):
        """Test asynchronous batch mapping functionality."""
        inputs = ["chest", "waist", "invalid"]
        results = await vector_mapper.async_batch_map_measurements(inputs)
        assert results == ["chest", "waist", None]

    def test_error_handling(self, vector_mapper):
        """Test error handling for invalid inputs."""
        with pytest.raises(ValueError):
            vector_mapper.map_measurement(None)
        
        with pytest.raises(TypeError):
            vector_mapper.map_measurement(123)

        with pytest.raises(ValueError):
            vector_mapper.update_mappings(None)

    @pytest.mark.parametrize("input_term,expected", [
        ("chest", "chest"),
        ("bust", "chest"),
        ("waistline", "waist"),
        ("leg length", "inseam"),
        ("invalid_term", None),
    ])
    def test_parametrized_mapping(self, vector_mapper, input_term, expected):
        """Parametrized test for various input terms."""
        assert vector_mapper.map_measurement(input_term) == expected 