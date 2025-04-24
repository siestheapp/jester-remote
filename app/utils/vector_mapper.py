import openai
import numpy as np
import os
from dotenv import load_dotenv
from typing import Optional, Dict, List, Set, Any
from sentence_transformers import SentenceTransformer
import asyncio
from difflib import SequenceMatcher
import re

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# You can expand this list as needed
STANDARD_FIELDS = ["chest", "waist", "sleeve", "neck", "hip"]

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define standard measurement categories and their common variations
MEASUREMENT_CATEGORIES: Dict[str, Set[str]] = {
    "chest": {
        "chest", "chest width", "chest circumference", "bust", 
        "chest measurement", "chest size", "bust measurement"
    },
    "waist": {
        "waist", "waist size", "waist circumference", 
        "waist measurement", "natural waist"
    },
    "hip": {
        "hip", "hip measurement", "hip circumference", 
        "hip size", "seat", "seat measurement"
    },
    "inseam": {
        "inseam", "inseam length", "inside leg", 
        "leg length", "inner leg measurement"
    },
    "neck": {
        "neck", "neck size", "collar", "collar size", 
        "neck circumference", "neck measurement"
    },
    "sleeve": {
        "sleeve", "sleeve length", "arm length", 
        "sleeve measurement", "arm measurement"
    },
    "shoulder": {
        "shoulder", "shoulder width", "across shoulder", 
        "shoulder measurement", "shoulder breadth"
    }
}

# Pre-compute embeddings for all standard measurements and variations
_embeddings_cache = {}
_standard_lookup = {}

def _initialize_embeddings():
    """Pre-compute embeddings for all measurement terms."""
    global _embeddings_cache, _standard_lookup
    
    all_terms = set()
    for standard, variations in MEASUREMENT_CATEGORIES.items():
        all_terms.add(standard)
        all_terms.update(variations)
        for variation in variations:
            _standard_lookup[variation.lower()] = standard
    
    # Compute embeddings for all terms
    terms_list = list(all_terms)
    embeddings = model.encode(terms_list)
    _embeddings_cache = dict(zip(terms_list, embeddings))

# Initialize embeddings on module load
_initialize_embeddings()

def get_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(
        input=[text],
        model=model
    )
    return np.array(response.data[0].embedding)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def match_to_standard(measurement: str, threshold: float = 0.75) -> Optional[str]:
    """
    Match a measurement name to its standard category using semantic similarity.
    
    Args:
        measurement: The measurement name to standardize
        threshold: Minimum similarity score to consider a match (0-1)
    
    Returns:
        The standard measurement category or None if no match found
    """
    measurement = measurement.lower().strip()
    
    # Check for exact matches first
    if measurement in _standard_lookup:
        return _standard_lookup[measurement]
    
    # Compute embedding for the input measurement
    measurement_embedding = model.encode(measurement)
    
    # Find the closest match
    max_similarity = -1
    best_match = None
    
    for term, embedding in _embeddings_cache.items():
        similarity = np.dot(measurement_embedding, embedding)
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = term
    
    # Return the standard category if similarity is above threshold
    if max_similarity >= threshold and best_match in _standard_lookup:
        return _standard_lookup[best_match]
    
    return None

def get_measurement_categories() -> Dict[str, List[str]]:
    """
    Get all standard measurement categories and their variations.
    
    Returns:
        Dictionary mapping standard categories to lists of variations
    """
    return {
        standard: list(variations)
        for standard, variations in MEASUREMENT_CATEGORIES.items()
    }

class VectorMapper:
    """
    A utility class for mapping measurement terms to standardized categories
    using semantic similarity and exact matching.
    """

    def __init__(self, measurement_mappings: Dict[str, List[str]]):
        """
        Initialize the VectorMapper with measurement mappings.

        Args:
            measurement_mappings: Dictionary mapping standard terms to their variations
        """
        if not isinstance(measurement_mappings, dict):
            raise ValueError("measurement_mappings must be a dictionary")
        
        self._mappings = measurement_mappings
        self._reverse_mappings = self._build_reverse_mappings()

    def _build_reverse_mappings(self) -> Dict[str, str]:
        """Build reverse mappings for quick lookup of variations."""
        reverse_mappings = {}
        for standard, variations in self._mappings.items():
            for variation in variations:
                reverse_mappings[variation.lower()] = standard
        return reverse_mappings

    def _normalize_text(self, text: str) -> str:
        """Normalize text by removing extra whitespace and converting to lowercase."""
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        return re.sub(r'\s+', ' ', text.strip().lower())

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity ratio between two strings."""
        return SequenceMatcher(None, text1, text2).ratio()

    def map_measurement(
        self, 
        measurement: str, 
        similarity_threshold: float = 0.85
    ) -> Optional[str]:
        """
        Map a measurement term to its standardized category.

        Args:
            measurement: The measurement term to map
            similarity_threshold: Minimum similarity score for semantic matching

        Returns:
            Mapped standard term or None if no match found
        """
        if measurement is None:
            raise ValueError("Measurement cannot be None")
        if not isinstance(measurement, str):
            raise TypeError("Measurement must be a string")
        
        # Normalize input
        normalized = self._normalize_text(measurement)
        if not normalized:
            return None

        # Check exact matches first
        if normalized in self._reverse_mappings:
            return self._reverse_mappings[normalized]

        # Try semantic matching
        best_match = None
        best_score = 0

        for variation, standard in self._reverse_mappings.items():
            score = self._calculate_similarity(normalized, variation)
            if score > best_score and score >= similarity_threshold:
                best_score = score
                best_match = standard

        return best_match

    def batch_map_measurements(
        self, 
        measurements: List[str]
    ) -> List[Optional[str]]:
        """
        Map multiple measurements in batch.

        Args:
            measurements: List of measurement terms to map

        Returns:
            List of mapped standard terms (None for unmatched terms)
        """
        return [self.map_measurement(m) for m in measurements]

    async def async_batch_map_measurements(
        self, 
        measurements: List[str]
    ) -> List[Optional[str]]:
        """
        Asynchronously map multiple measurements.

        Args:
            measurements: List of measurement terms to map

        Returns:
            List of mapped standard terms (None for unmatched terms)
        """
        async def map_single(measurement: str) -> Optional[str]:
            return self.map_measurement(measurement)

        tasks = [map_single(m) for m in measurements]
        return await asyncio.gather(*tasks)

    def get_measurement_categories(self) -> List[str]:
        """
        Get list of all standard measurement categories.

        Returns:
            List of standard measurement terms
        """
        return list(self._mappings.keys())

    def get_measurement_mappings(self) -> Dict[str, List[str]]:
        """
        Get the current measurement mappings.

        Returns:
            Dictionary of measurement mappings
        """
        return self._mappings.copy()

    def update_mappings(self, new_mappings: Dict[str, List[str]]) -> None:
        """
        Update measurement mappings with new entries.

        Args:
            new_mappings: Dictionary of new mappings to add/update
        """
        if new_mappings is None:
            raise ValueError("new_mappings cannot be None")
        
        self._mappings.update(new_mappings)
        self._reverse_mappings = self._build_reverse_mappings()
