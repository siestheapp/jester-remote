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
    
    def __init__(self, vector_search=None):
        """
        Initialize the JesterChat instance.
        
        Args:
            vector_search: Optional JesterVectorSearch instance. If not provided,
                          a new instance will be created.
        """
        self.vector_search = vector_search or JesterVectorSearch()
        self.system_prompt = """You are Jester, an AI assistant specialized in menswear size guide standardization and analysis.
Your expertise includes:
1. Analyzing size charts and measurement tables
2. Identifying measurement patterns and inconsistencies
3. Suggesting standardized measurement approaches
4. Handling edge cases in size guide interpretation
5. Providing clear explanations of measurement methodologies

When responding:
- Be precise and technical in your analysis
- Reference specific measurements and standards
- Explain your reasoning clearly
- Ask clarifying questions when needed
- Suggest improvements to measurement methodologies
- Consider international size standards when relevant"""

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