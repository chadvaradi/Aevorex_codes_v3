"""
Base LLM provider interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> str:
        """Generate a single response"""
        pass
    
    @abstractmethod
    async def stream(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> AsyncGenerator[str, None]:
        """Stream response chunks"""
        pass
