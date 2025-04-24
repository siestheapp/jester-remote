#!/usr/bin/env python3
"""
Initialize the vector search with initial knowledge base data.
This script should be run once to set up the vector search index.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.core.vector_search import JesterVectorSearch

def main():
    """Initialize vector search with initial knowledge."""
    # Initial knowledge chunks about clothing and measurements
    initial_chunks = [
        {
            "text": "When measuring chest width, measure across the fullest part of your chest, keeping the tape measure parallel to the ground.",
            "metadata": {
                "measurement_type": "chest",
                "category": "measurement_instructions"
            }
        },
        {
            "text": "For waist measurements, measure around your natural waistline, keeping the tape measure snug but not tight.",
            "metadata": {
                "measurement_type": "waist",
                "category": "measurement_instructions"
            }
        },
        {
            "text": "To measure inseam length, measure from the crotch seam to the bottom of the leg where you want the pants to end.",
            "metadata": {
                "measurement_type": "inseam",
                "category": "measurement_instructions"
            }
        },
        {
            "text": "For sleeve length, measure from the center back of your neck, across your shoulder, and down to your wrist.",
            "metadata": {
                "measurement_type": "sleeve",
                "category": "measurement_instructions"
            }
        },
        {
            "text": "Hip measurements should be taken at the fullest part of your hips, usually about 8 inches below your waist.",
            "metadata": {
                "measurement_type": "hip",
                "category": "measurement_instructions"
            }
        },
        {
            "text": "Regular fit clothing provides a classic, comfortable cut with room for movement without being too loose.",
            "metadata": {
                "fit_type": "regular",
                "category": "fit_descriptions"
            }
        },
        {
            "text": "Slim fit clothing offers a more tailored silhouette that's closer to the body without being skin-tight.",
            "metadata": {
                "fit_type": "slim",
                "category": "fit_descriptions"
            }
        },
        {
            "text": "Relaxed fit provides extra room throughout for maximum comfort and ease of movement.",
            "metadata": {
                "fit_type": "relaxed",
                "category": "fit_descriptions"
            }
        }
    ]

    # Initialize vector search
    vector_search = JesterVectorSearch()
    
    # Add initial chunks
    vector_search.batch_add_chunks(initial_chunks)
    
    print("Vector search initialized with initial knowledge base.")
    print(f"Index saved to: {vector_search.index_path}")
    print(f"Chunks saved to: {vector_search.chunks_path}")

if __name__ == "__main__":
    main() 