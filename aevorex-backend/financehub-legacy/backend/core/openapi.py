"""
Custom OpenAPI Schema Configuration

Provides custom OpenAPI schema generation for Aevorex FinanceHub API
with branded metadata, contact information, and logo configuration.
"""

from typing import Dict, Any, Optional
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import functools


@functools.lru_cache(maxsize=1)
def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """
    Generate custom OpenAPI schema for Aevorex FinanceHub API.
    
    This function overrides the default FastAPI OpenAPI schema with
    Aevorex-specific branding, contact information, and metadata.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Dict containing the custom OpenAPI schema
        
    Note:
        The schema is cached using lru_cache to avoid regenerating
        it on every request for better performance.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    # Generate base OpenAPI schema using FastAPI's utility
    openapi_schema = get_openapi(
        title="Aevorex FinanceHub API",
        version="0.1.0",
        description=(
            "Bloomberg-grade AI-driven financial data API with macro, fundamentals, "
            "technical analysis and multi-source integration. "
            "Professional equity research experience combining trading platform depth "
            "with intuitive LLM-powered conversational interface."
        ),
        routes=app.routes,
    )
    
    # Override metadata with Aevorex branding
    openapi_schema["info"].update({
        "title": "Aevorex FinanceHub API",
        "version": "0.1.0",
        "description": (
            "Bloomberg-grade AI-driven financial data API with macro, fundamentals, "
            "technical analysis and multi-source integration. "
            "Professional equity research experience combining trading platform depth "
            "with intuitive LLM-powered conversational interface."
        ),
        "termsOfService": "https://aevorex.com/terms",
        "contact": {
            "name": "Aevorex Team",
            "url": "https://aevorex.com",
            "email": "support@aevorex.com"
        },
        "license": {
            "name": "Proprietary – Aevorex",
            "url": "https://aevorex.com/license"
        }
    })
    
    # Add custom logo extension
    openapi_schema["x-logo"] = {
        "url": "https://aevorex.com/static/logo.png",
        "altText": "Aevorex Logo"
    }
    
    # Add custom extensions for Aevorex branding
    openapi_schema["x-branding"] = {
        "company": "Aevorex",
        "product": "FinanceHub",
        "tagline": "Premium Equity Research Platform",
        "website": "https://aevorex.com",
        "documentation": "https://docs.aevorex.com"
    }
    
    # Add server information
    openapi_schema["servers"] = [
        {
            "url": "https://api.aevorex.com",
            "description": "Production server"
        },
        {
            "url": "https://staging-api.aevorex.com", 
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8084",
            "description": "Development server"
        }
    ]
    
    # Cache the schema
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def get_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """
    Get the custom OpenAPI schema for the FastAPI application.
    
    This is a convenience function that calls custom_openapi()
    and returns the schema dictionary.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Dict containing the custom OpenAPI schema
    """
    return custom_openapi(app)


__all__ = ["custom_openapi", "get_openapi_schema"]
