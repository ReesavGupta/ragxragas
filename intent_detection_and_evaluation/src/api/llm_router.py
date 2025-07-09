"""
API wrapper for switching between local Ollama (gemma3:1b) and GROQ using LangChain integrations.
"""

# Placeholder imports (to be replaced with actual langchain-ollama and langchain-groq imports)
from typing import Literal
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain_groq import ChatGroq
from pydantic import SecretStr
from langchain_core.messages import BaseMessage

class LLMRouter:
    def __init__(self, backend: Literal['ollama', 'groq'] = 'ollama'):
        """
        Initialize the router with a default backend.
        backend: 'ollama' for local gemma3:1b, 'groq' for GROQ API
        """
        self.backend = backend
        # Set up Ollama (gemma3:1b)
        self.ollama_model = OllamaLLM(model="gemma3:1b")
        # Set up GROQ
        groq_api_key = os.getenv("GROQ_API_KEY")
        groq_model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")  # Default model
        if groq_api_key:
            self.groq_model = ChatGroq(api_key=SecretStr(groq_api_key), model=groq_model)
        else:
            self.groq_model = None

    def set_backend(self, backend: Literal['ollama', 'groq']):
        """Switch the backend (ollama or groq)."""
        self.backend = backend

    def generate(self, question: str, **kwargs) -> str:
        """
        Send a prompt to the selected backend and return the response as a string.
        """
        template = """Question: {question}\n\nAnswer: Let's think step by step."""
        prompt = ChatPromptTemplate.from_template(template)

        # model inference 
        if self.backend == 'ollama':
            chain = prompt | self.ollama_model
            result = chain.invoke({"question": question})
            
        elif self.backend == 'groq':
            if not self.groq_model:
                raise RuntimeError("GROQ API key not set in environment.")
            
            chain = prompt | self.groq_model
            result = chain.invoke({"question": question})
        else:
            raise ValueError(f"Unknown backend: {self.backend}")
       
        # Handle result type
        if isinstance(result, BaseMessage):
            return str(result.content)
        elif isinstance(result, list):
            # Join string elements or convert dicts to strings, then join as a single string
            return "\n".join(str(item) for item in result)
        elif isinstance(result, str):
            return result
        else:
            return str(result)