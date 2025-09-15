"""
Chat Logic

Core logic for handling chat interactions with LLM providers.
Bridges between the Chat API endpoints and the LLM model catalogue.
"""

import logging
import json
from typing import Optional, Dict, Any
from fastapi import HTTPException

from backend.config.model_catalogue import get_models_response, resolve_model
from backend.api.endpoints.chat.schemas import ChatRequest, ChatResponse
from backend.api.endpoints.chat.provider import OpenRouterProvider
from backend.core.services.chat_tools import ChatTools, execute_tool

logger = logging.getLogger(__name__)

class ChatLogic:
    """
    Handles chat interactions and routes them to the selected LLM provider.
    """

    def __init__(self):
        self._provider = None

    @property
    def provider(self):
        """Lazy loading of provider to avoid initialization errors."""
        if self._provider is None:
            self._provider = OpenRouterProvider()
        return self._provider

    def get_models_response(self) -> Dict[str, Any]:
        """
        Return the available models for chat.
        """
        return get_models_response()
    
    def _detect_trading_hours_query(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Detect if the user is asking about trading hours or market status.
        
        Args:
            message: User message
            
        Returns:
            Dict with tool call info if detected, None otherwise
        """
        message_lower = message.lower()
        
        # Check for trading hours queries
        trading_hours_keywords = [
            "trading hours", "market hours", "exchange hours", "when does", "when is",
            "is the market open", "is nasdaq open", "is nyse open", "is lse open",
            "market status", "exchange status", "is open", "is closed"
        ]
        
        if any(keyword in message_lower for keyword in trading_hours_keywords):
            # Determine exchange from context
            exchange = "US"  # Default
            if "nasdaq" in message_lower or "nyse" in message_lower:
                exchange = "US"
            elif "lse" in message_lower or "london" in message_lower:
                exchange = "LSE"
            elif "toronto" in message_lower or "tsx" in message_lower:
                exchange = "TO"
            
            # Determine which tool to use
            if "hours" in message_lower or "schedule" in message_lower:
                return {
                    "tool": "get_trading_hours",
                    "parameters": {"exchange": exchange}
                }
            elif "status" in message_lower or "open" in message_lower or "closed" in message_lower:
                return {
                    "tool": "get_market_status", 
                    "parameters": {"exchange": exchange}
                }
            else:
                return {
                    "tool": "is_market_open",
                    "parameters": {"exchange": exchange}
                }
        
        return None
    
    def _enhance_system_message_with_tools(self, system_message: str, user_message: str) -> str:
        """
        Enhance system message with trading hours tools if relevant.
        
        Args:
            system_message: Original system message
            user_message: User's message
            
        Returns:
            Enhanced system message
        """
        tool_query = self._detect_trading_hours_query(user_message)
        
        if tool_query:
            tools_info = ChatTools.get_available_tools()
            tools_description = "\n".join([
                f"- {tool['name']}: {tool['description']}" 
                for tool in tools_info
            ])
            
            system_message += f"""
            
You have access to the following trading hours tools:
{tools_description}

If the user asks about market hours, trading status, or exchange schedules, use the appropriate tool to get accurate, real-time information.
"""
        
        return system_message

    async def handle_rapid_chat(
        self,
        request,
        cache_service,
        tier: str
    ) -> Dict[str, Any]:
        """
        Handle rapid chat requests with access to any data source.
        """
        try:
            body = await request.json()
            messages = body.get("messages", [])
            context = body.get("context", {})
            model = body.get("model", "gpt-4o-mini")
            
            # Extract ticker and data sources from context
            ticker = context.get("ticker")
            data_sources = context.get("data_sources", [])
            
            # Add system message with context
            system_message = "You are a financial analyst with access to multiple data sources."
            if ticker:
                system_message += f" The user is asking about {ticker}."
            if data_sources:
                system_message += f" Available data sources: {', '.join(data_sources)}."
            
            # Get the last user message for tool detection
            last_user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_message = msg.get("content", "")
                    break
            
            # Enhance system message with tools if needed
            system_message = self._enhance_system_message_with_tools(system_message, last_user_message)
            
            # Check if we need to call a tool
            tool_query = self._detect_trading_hours_query(last_user_message)
            tool_result = None
            
            if tool_query:
                try:
                    tool_result = execute_tool(tool_query["tool"], tool_query["parameters"])
                    if tool_result.get("success"):
                        system_message += f"\n\nTool Result: {json.dumps(tool_result['data'], indent=2)}"
                    else:
                        system_message += f"\n\nTool Error: {tool_result.get('error', 'Unknown error')}"
                except Exception as e:
                    logger.error(f"Tool execution error: {e}")
                    system_message += f"\n\nTool Error: {str(e)}"
            
            # Prepend system message
            messages.insert(0, {
                "role": "system",
                "content": system_message
            })
            
            # Generate response
            response = await self.provider.generate(messages, model)
            
            return {
                "id": f"chatcmpl-{int(__import__('time').time())}",
                "object": "chat.completion",
                "created": int(__import__('time').time()),
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.content
                    },
                    "finish_reason": "stop"
                }],
                "usage": response.usage
            }
            
        except Exception as e:
            logger.error(f"Rapid chat error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def handle_deep_chat(
        self,
        request,
        cache_service,
        tier: str
    ):
        """
        Handle deep chat requests with streaming and access to any data source.
        """
        try:
            body = await request.json()
            messages = body.get("messages", [])
            context = body.get("context", {})
            model = body.get("model", "gpt-4o-mini")
            
            # Extract ticker and data sources from context
            ticker = context.get("ticker")
            data_sources = context.get("data_sources", [])
            
            # Add comprehensive system message
            system_message = """You are an expert financial analyst providing deep, comprehensive analysis with access to multiple data sources.
            
            Provide detailed insights including:
            - Technical analysis
            - Fundamental analysis
            - Market sentiment
            - Risk assessment
            - Investment recommendations
            
            Be thorough and professional in your analysis."""
            
            if ticker:
                system_message += f" The user is asking about {ticker}."
            if data_sources:
                system_message += f" Available data sources: {', '.join(data_sources)}."
            
            # Prepend system message
            messages.insert(0, {
                "role": "system",
                "content": system_message
            })
            
            # Stream response
            async def generate():
                try:
                    async for chunk in self.provider.stream(messages, model):
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    logger.error(f"Stream error: {e}")
                    yield f"data: {json.dumps({'error': f'Stream failed: {str(e)}'})}\n\n"
                    yield "data: [DONE]\n\n"
            
            from fastapi.responses import StreamingResponse
            return StreamingResponse(generate(), media_type="text/event-stream")
            
        except Exception as e:
            logger.error(f"Deep chat error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat request using the selected model.
        """
        try:
            # Resolve model
            model_config = resolve_model(request.model)
            logger.info(f"Resolved model: {model_config}")

            # Send request to provider
            response = await self.provider.chat(
                model=model_config,
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=request.stream,
            )

            return ChatResponse(
                model=request.model,
                messages=request.messages,
                response=response,
            )
        except Exception as e:
            logger.error(f"Chat processing failed: {e}", exc_info=True)
            raise

    async def generate_rapid_chat(self, ticker: str, message: str, model_id: str) -> Dict[str, Any]:
        """
        Generate rapid chat response for a specific ticker.
        """
        try:
            # Simple implementation - return a basic response
            return {
                "ticker": ticker,
                "message": message,
                "response": f"Rapid analysis for {ticker}: {message}",
                "model": model_id,
                "timestamp": "2025-01-15T00:00:00Z"
            }
        except Exception as e:
            logger.error(f"Rapid chat generation failed: {e}", exc_info=True)
            raise

    async def stream_rapid_chat(self, ticker: str, message: str, model_id: str):
        """
        Stream rapid chat response for a specific ticker.
        """
        try:
            # Simple streaming implementation
            response_data = {
                "ticker": ticker,
                "message": message,
                "response": f"Streaming analysis for {ticker}: {message}",
                "model": model_id,
                "timestamp": "2025-01-15T00:00:00Z"
            }
            yield f"data: {json.dumps(response_data)}\n\n"
        except Exception as e:
            logger.error(f"Rapid chat streaming failed: {e}", exc_info=True)
            raise

# Create global instance
chat_logic = ChatLogic()

# Compatibility wrapper functions for chat endpoints

async def get_models_response():
    """
    Return available models (async wrapper).
    """
    from backend.config.model_catalogue import get_models_response as get_models
    return get_models()

async def handle_rapid_chat(request, cache_service=None, tier: str = "free"):
    """
    Compatibility wrapper for rapid chat endpoint.
    Delegates to ChatLogic.handle_rapid_chat.
    """
    return await chat_logic.handle_rapid_chat(request, cache_service, tier)

async def handle_deep_chat(request, cache_service=None, tier: str = "free"):
    """
    Compatibility wrapper for deep chat endpoint.
    Delegates to ChatLogic.handle_deep_chat.
    """
    return await chat_logic.handle_deep_chat(request, cache_service, tier)

# Export functions to module namespace for chat_router import
__all__ = ["get_models_response", "handle_rapid_chat", "handle_deep_chat", "generate_rapid_chat", "stream_rapid_chat"]