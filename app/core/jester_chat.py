"""
Jester Chat module for the Jester application.
This module provides the chat functionality for the application.
"""

import streamlit as st
import openai
from typing import List, Dict, Any, Optional
from .vector_search import JesterVectorSearch
import json
import os
from app.config import config

class JesterChat:
    """
    JesterChat class for handling chat interactions with the Jester AI.
    
    This class provides methods for generating responses to user queries,
    adding information to the knowledge base, and managing chat history.
    """
    
    def __init__(self):
        """Initialize Jester with vector search capabilities and expert knowledge."""
        self.vector_search = JesterVectorSearch(
            index_path=config.VECTOR_INDEX_PATH,
            chunks_path=config.VECTOR_METADATA_PATH
        )
        
        self.system_prompt = """You are Jester, an expert AI assistant specializing in apparel size guide analysis and standardization. Your core capabilities include:

1. INTELLIGENT INTERPRETATION
- You can analyze any size guide format and understand its structure
- You recognize common patterns in how brands present measurements
- You understand the context and purpose of each measurement

2. FLEXIBLE REASONING
- Instead of following rigid rules, you think critically about each size guide
- You understand when measurements need to be doubled (e.g., "1/2 chest") based on context
- You can infer missing information from available context
- You recognize when measurements refer to the same concept (e.g., "Belt" → "Waist")

3. CATEGORY UNDERSTANDING
- You understand apparel categories (Tops, Dress Shirts, Bottoms, etc.)
- You can correctly categorize items even when brands use non-standard terms
- You recognize when categories need to be adjusted (e.g., a polo listed under "Outerwear")

4. MEASUREMENT STANDARDIZATION
- You standardize measurements while preserving their original intent
- You handle unit conversions thoughtfully
- You maintain precision in numerical values
- You understand fit implications of measurements

5. QUALITY ASSURANCE
- You flag potential issues or ambiguities
- You explain your reasoning when making decisions
- You ask for clarification when needed
- You ensure data integrity in the standardization process

When processing a size guide:
1. First analyze and understand its complete structure
2. Explain your reasoning about any non-obvious decisions
3. Ask clarifying questions if critical information is ambiguous
4. Provide clear explanations of your standardization choices

Your goal is to ensure accurate, consistent size guide processing while being flexible enough to handle any format or edge case."""

    def analyze_size_guide(self, image_analysis: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a size guide using GPT-4's understanding and available context.
        
        Args:
            image_analysis: The raw analysis from GPT-4 Vision
            metadata: Basic metadata about the size guide
            
        Returns:
            Dict containing structured analysis and recommendations
        """
        # Get relevant context from our knowledge base
        context_results = self.vector_search.search(
            f"size guide processing for {metadata.get('brand', '')} {metadata.get('category', '')}",
            k=3
        )
        
        # Build context from search results
        context = "\n\n".join([
            f"Context {i+1}:\n{result['text']}"
            for i, result in enumerate(context_results)
        ])
        
        # Prepare the analysis request
        analysis_prompt = f"""
Brand: {metadata.get('brand')}
Category: {metadata.get('category')}
Original Analysis: {image_analysis}

Based on the size guide information above and this context:
{context}

Please provide:
1. Standardized measurements and their reasoning
2. Category confirmation or suggestion
3. Any potential issues or ambiguities
4. Recommendations for handling this size guide

Explain your reasoning for any non-obvious decisions."""

        # Get GPT-4's analysis
        response = openai.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.7
        )
        
        # Extract and structure the response
        analysis = response.choices[0].message.content
        
        # Add this analysis to our knowledge base for future reference
        self.add_to_knowledge_base(
            f"Size Guide Analysis - {metadata.get('brand')}:\n{analysis}",
            metadata=metadata
        )
        
        return {
            "analysis": analysis,
            "context_used": context_results,
            "metadata": metadata
        }

    def get_response(self, user_input: str, chat_history: List[Dict[str, str]] = None) -> str:
        """
        Generate a response using the chat history and vector search context.
        
        Args:
            user_input: The user's input query
            chat_history: Optional list of previous chat messages
            
        Returns:
            str: The AI's response
        """
        # Get relevant context from vector search
        search_results = self.vector_search.search(user_input, k=3)
        
        # Construct the context from search results
        context = "\n\n".join([
            f"Context {i+1}:\n{result['text']}"
            for i, result in enumerate(search_results)
        ])
        
        # Prepare messages for the API call
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": f"Relevant research context:\n{context}"}
        ]
        
        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history)
        
        # Add the current user input
        messages.append({"role": "user", "content": user_input})
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content

    def add_to_knowledge_base(self, text: str, metadata: Dict[str, Any] = None):
        """
        Add new information to the vector search knowledge base.
        
        Args:
            text: The text to add to the knowledge base
            metadata: Optional metadata associated with the text
        """
        self.vector_search.add_chunk(text, metadata)

    def batch_add_to_knowledge_base(self, texts: List[str], metadata_list: List[Dict[str, Any]] = None):
        """
        Add multiple pieces of information to the knowledge base at once.
        
        Args:
            texts: List of texts to add to the knowledge base
            metadata_list: Optional list of metadata associated with each text
        """
        self.vector_search.batch_add_chunks(texts, metadata_list)
        
    def get_relevant_chunks(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Get the k most relevant chunks for a query.
        
        Args:
            query: The query to search for
            k: The number of chunks to return
            
        Returns:
            List[Dict[str, Any]]: List of relevant chunks
        """
        return self.vector_search.search(query, k=k) 