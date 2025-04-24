import pytest
from app.utils.vector_mapper import (
    match_to_standard,
    get_measurement_categories,
    MEASUREMENT_CATEGORIES
)

def test_exact_matches():
    """Test exact matches for standard measurement names."""
    assert match_to_standard("chest") == "chest"
    assert match_to_standard("waist") == "waist"
    assert match_to_standard("hip") == "hip"
    assert match_to_standard("inseam") == "inseam"

def test_common_variations():
    """Test common variations of measurement names."""
    variations = [
        ("chest width", "chest"),
        ("bust measurement", "chest"),
        ("natural waist", "waist"),
        ("waist circumference", "waist"),
        ("hip size", "hip"),
        ("seat measurement", "hip"),
        ("inside leg", "inseam"),
    ]
    
    for input_name, expected in variations:
        assert match_to_standard(input_name) == expected

def test_case_insensitivity():
    """Test that matching is case insensitive."""
    variations = [
        ("CHEST WIDTH", "chest"),
        ("Waist Circumference", "waist"),
        ("Hip Size", "hip"),
        ("INSEAM LENGTH", "inseam"),
    ]
    
    for input_name, expected in variations:
        assert match_to_standard(input_name) == expected

def test_whitespace_handling():
    """Test handling of extra whitespace."""
    variations = [
        ("  chest width  ", "chest"),
        ("waist  size", "waist"),
        ("hip   measurement  ", "hip"),
        (" inseam ", "inseam"),
    ]
    
    for input_name, expected in variations:
        assert match_to_standard(input_name) == expected

def test_semantic_matching():
    """Test semantic matching for similar but non-exact terms."""
    variations = [
        ("torso width", "chest"),
        ("midsection", "waist"),
        ("thigh circumference", None),  # Should not match any category
        ("arm span", "sleeve"),
    ]
    
    for input_name, expected in variations:
        assert match_to_standard(input_name) == expected

def test_threshold_filtering():
    """Test that matches below threshold are rejected."""
    non_matches = [
        "random text",
        "not a measurement",
        "something else",
        "12345",
    ]
    
    for input_name in non_matches:
        assert match_to_standard(input_name, threshold=0.75) is None

def test_get_measurement_categories():
    """Test retrieval of measurement categories."""
    categories = get_measurement_categories()
    
    # Check that all standard categories are present
    assert set(categories.keys()) == set(MEASUREMENT_CATEGORIES.keys())
    
    # Check that variations are returned as lists
    for variations in categories.values():
        assert isinstance(variations, list)
        assert len(variations) > 0

def test_threshold_sensitivity():
    """Test different threshold values."""
    measurement = "torso width"
    
    # Should match with lower threshold
    assert match_to_standard(measurement, threshold=0.7) == "chest"
    
    # Should not match with very high threshold
    assert match_to_standard(measurement, threshold=0.99) is None

def test_measurement_category_consistency():
    """Test that all measurement categories are properly structured."""
    for category, variations in MEASUREMENT_CATEGORIES.items():
        # Category should be a string
        assert isinstance(category, str)
        
        # Variations should be a set
        assert isinstance(variations, set)
        
        # Each variation should be a string
        for variation in variations:
            assert isinstance(variation, str)
            
        # Category should be included in its own variations
        assert category in variations 