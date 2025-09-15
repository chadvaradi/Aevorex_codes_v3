"""
Chat Tools
==========

Tools that can be used by the LLM to answer user questions about trading hours and market status.
Now includes **dynamic EODHD API integration** for real-time trading hours data.
"""

import json
from typing import Dict, Any, List
from backend.core.services.trading_hours_service import TradingHoursService
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class ChatTools:
    """Tools available to the LLM for answering user questions."""
    
    @staticmethod
    async def get_market_status(exchange: str) -> Dict[str, Any]:
        """
        Get current market status for an exchange using dynamic EODHD API data.
        
        Args:
            exchange: Exchange code (e.g., 'US', 'LSE', 'TO')
            
        Returns:
            Dict containing market status information
        """
        try:
            status = await TradingHoursService.get_market_status(exchange.upper())
            return {
                "success": True,
                "data": status
            }
        except Exception as e:
            logger.error(f"Error getting market status for {exchange}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def get_trading_hours(exchange: str) -> Dict[str, Any]:
        """
        Get trading hours for an exchange using dynamic EODHD API data.
        
        Args:
            exchange: Exchange code (e.g., 'US', 'LSE', 'TO')
            
        Returns:
            Dict containing trading hours information
        """
        try:
            # Use the dynamic EODHD API integration
            eodhd_data = await TradingHoursService.fetch_exchange_details(exchange.upper())
            
            if eodhd_data:
                parsed_data = TradingHoursService.parse_eodhd_trading_hours(eodhd_data)
                if parsed_data:
                    return {
                        "success": True,
                        "data": parsed_data,
                        "source": "eodhd_api"
                    }
            
            # Fallback to hardcoded data
            from backend.api.endpoints.eodhd.exchanges_router import EXCHANGE_TRADING_HOURS
            
            exchange_upper = exchange.upper()
            if exchange_upper not in EXCHANGE_TRADING_HOURS:
                return {
                    "success": False,
                    "error": f"Exchange '{exchange}' not found. Supported exchanges: {list(EXCHANGE_TRADING_HOURS.keys())}"
                }
            
            return {
                "success": True,
                "data": EXCHANGE_TRADING_HOURS[exchange_upper],
                "source": "fallback_data"
            }
        except Exception as e:
            logger.error(f"Error getting trading hours for {exchange}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def is_market_open(exchange: str) -> Dict[str, Any]:
        """
        Check if a market is currently open.
        
        Args:
            exchange: Exchange code (e.g., 'US', 'LSE', 'TO')
            
        Returns:
            Dict containing market open status
        """
        try:
            is_open, session_type = TradingHoursService.is_market_open(exchange.upper())
            return {
                "success": True,
                "data": {
                    "is_open": is_open,
                    "session_type": session_type,
                    "exchange": exchange.upper()
                }
            }
        except Exception as e:
            logger.error(f"Error checking if market is open for {exchange}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_available_tools() -> List[Dict[str, Any]]:
        """
        Get list of available tools for the LLM.
        
        Returns:
            List of tool definitions
        """
        return [
            {
                "name": "get_market_status",
                "description": "Get current market status for an exchange including open/closed status, session type, and next open/close times",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "exchange": {
                            "type": "string",
                            "description": "Exchange code (e.g., 'US', 'LSE', 'TO')",
                            "enum": ["US", "LSE", "TO"]
                        }
                    },
                    "required": ["exchange"]
                }
            },
            {
                "name": "get_trading_hours",
                "description": "Get trading hours and holidays for an exchange",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "exchange": {
                            "type": "string",
                            "description": "Exchange code (e.g., 'US', 'LSE', 'TO')",
                            "enum": ["US", "LSE", "TO"]
                        }
                    },
                    "required": ["exchange"]
                }
            },
            {
                "name": "is_market_open",
                "description": "Check if a market is currently open",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "exchange": {
                            "type": "string",
                            "description": "Exchange code (e.g., 'US', 'LSE', 'TO')",
                            "enum": ["US", "LSE", "TO"]
                        }
                    },
                    "required": ["exchange"]
                }
            }
        ]


def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool by name with given parameters.
    
    Args:
        tool_name: Name of the tool to execute
        parameters: Parameters for the tool
        
    Returns:
        Tool execution result
    """
    if tool_name == "get_market_status":
        return ChatTools.get_market_status(parameters.get("exchange", ""))
    elif tool_name == "get_trading_hours":
        return ChatTools.get_trading_hours(parameters.get("exchange", ""))
    elif tool_name == "is_market_open":
        return ChatTools.is_market_open(parameters.get("exchange", ""))
    else:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }

