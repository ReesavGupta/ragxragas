"""
Query decomposition for complex sports analytics questions.
"""

import time
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from pydantic import SecretStr

from ..utils.logging import get_logger
from ..config import get_settings

logger = get_logger(__name__)


class QueryDecomposer:
    """Decompose complex sports analytics queries into sub-questions."""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = self._init_llm()
        self.prompt_template = self._init_prompt_template()
        
        logger.info("Query decomposer initialized")
    
    def _init_llm(self) -> ChatGroq:
        """Initialize Groq LLM."""
        if not self.settings:
            raise ValueError("Settings not available")
        
        return ChatGroq(
            api_key=SecretStr(self.settings.groq_api_key) if self.settings.groq_api_key else None,
            model=self.settings.groq_model,
            temperature=self.settings.temperature
        )
    
    def _init_prompt_template(self) -> PromptTemplate:
        """Initialize the decomposition prompt template."""
        template = """
You are a sports analytics expert. Your task is to decompose complex sports questions into simpler, atomic sub-questions that can be answered individually.

Given a complex sports question, break it down into 2-4 simpler sub-questions that together will help answer the original question.

Complex Question: {query}

Instructions:
1. Identify the main components of the question
2. Break down into logical sub-questions
3. Each sub-question should be specific and answerable
4. Sub-questions should be independent but related
5. Focus on sports analytics, statistics, and comparisons
6. DO NOT include any introductory text or explanations
7. ONLY provide the sub-questions, one per line starting with "- "

Sub-questions:
"""
        
        return PromptTemplate(
            input_variables=["query"],
            template=template
        )
    
    def decompose_query(self, query: str) -> List[str]:
        """Decompose a complex query into sub-questions."""
        try:
            # Add rate limiting delay
            time.sleep(0.5)  # 0.5 second delay between requests
            
            # Create the prompt
            prompt = self.prompt_template.format(query=query)
            
            # Get response from LLM with rate limiting protection
            try:
                response = self.llm.invoke(prompt)
            except Exception as e:
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    logger.warning(f"Rate limit hit in decomposition, waiting 3 seconds: {e}")
                    time.sleep(3)
                    response = self.llm.invoke(prompt)
                else:
                    raise e
            
            # Parse the response to extract sub-questions
            if hasattr(response, 'content'):
                response_content = str(response.content)
            else:
                response_content = str(response)
            sub_questions = self._parse_response(response_content)
            
            logger.info(f"Decomposed query into {len(sub_questions)} sub-questions")
            return sub_questions
            
        except Exception as e:
            logger.error(f"Error decomposing query: {e}")
            # Fallback: return the original query as a single sub-question
            return [query]
    
    def _parse_response(self, response: str) -> List[str]:
        """Parse LLM response to extract sub-questions."""
        try:
            # Ensure response is a string
            if not isinstance(response, str):
                response = str(response)
            
            lines = response.strip().split('\n')
            sub_questions = []
            
            for line in lines:
                line = line.strip()
                # Skip empty lines and common non-question content
                if not line or line.startswith('#') or line.startswith('Instructions:') or \
                   line.startswith('Complex Question:') or line.startswith('Sub-questions:') or \
                   'break down' in line.lower() or 'decompose' in line.lower():
                    continue
                
                if line.startswith('- '):
                    # Remove the "- " prefix
                    sub_question = line[2:].strip()
                    if sub_question and len(sub_question) > 10:  # Ensure it's a real question
                        sub_questions.append(sub_question)
                elif line.startswith('* '):
                    # Alternative bullet format
                    sub_question = line[2:].strip()
                    if sub_question and len(sub_question) > 10:
                        sub_questions.append(sub_question)
                elif line and len(line) > 10:
                    # If no bullet points, treat each non-empty line as a sub-question
                    sub_questions.append(line)
            
            # If no valid sub-questions found, return the original query
            if not sub_questions:
                return [response.strip()]
            
            return sub_questions
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return [str(response).strip()]
    
    def validate_decomposition(self, original_query: str, sub_questions: List[str]) -> Dict[str, Any]:
        """Validate the quality of query decomposition."""
        if not sub_questions:
            return {
                "valid": False,
                "reason": "No sub-questions generated",
                "sub_questions": []
            }
        
        # Basic validation
        validation = {
            "valid": True,
            "original_query": original_query,
            "sub_questions": sub_questions,
            "count": len(sub_questions),
            "avg_length": sum(len(q) for q in sub_questions) / len(sub_questions) if sub_questions else 0,
            "issues": []
        }
        
        # Check for issues
        if len(sub_questions) < 2:
            validation["issues"].append("Too few sub-questions")
        
        if len(sub_questions) > 5:
            validation["issues"].append("Too many sub-questions")
        
        # Check for very short or very long sub-questions
        for i, q in enumerate(sub_questions):
            if len(q) < 10:
                validation["issues"].append(f"Sub-question {i+1} too short")
            if len(q) > 200:
                validation["issues"].append(f"Sub-question {i+1} too long")
        
        if validation["issues"]:
            validation["valid"] = False
        
        return validation
    
    def get_decomposition_stats(self, query: str) -> Dict[str, Any]:
        """Get statistics about query decomposition."""
        try:
            sub_questions = self.decompose_query(query)
            validation = self.validate_decomposition(query, sub_questions)
            
            stats = {
                "original_query": query,
                "sub_questions": sub_questions,
                "sub_question_count": len(sub_questions),
                "validation": validation,
                "decomposition_successful": len(sub_questions) > 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting decomposition stats: {e}")
            return {
                "error": str(e),
                "decomposition_successful": False
            } 