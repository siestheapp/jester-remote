#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.core.vector_search import JesterVectorSearch

def main():
    """Initialize vector search with research data."""
    research_file = project_root / "data" / "research" / "size_guide_analysis.md"
    
    if not research_file.exists():
        print(f"Error: Research file not found at {research_file}")
        sys.exit(1)
    
    try:
        # Read research document
        print(f"Reading research document from {research_file}...")
        with open(research_file, "r") as f:
            research_content = f.read()
        
        # Initialize vector search
        print("Initializing vector search...")
        vector_search = JesterVectorSearch()
        
        # Add research content to vector store
        print("Adding research content to vector store...")
        vector_search.add_text(research_content, metadata={"source": "size_guide_analysis.md"})
        
        print("Successfully initialized vector search with research data!")
        
    except Exception as e:
        print(f"Error initializing vector search: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 