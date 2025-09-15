"""
This file now serves as the public entry point for the chat API module.

It has been refactored into a modular structure:
- `router.py`: Contains all FastAPI endpoint definitions.
- `handlers/`: Contains the business logic for each endpoint.

This file simply re-exports the router object from the new `router.py` file
to maintain backward compatibility for imports in the application's main router inclusion logic.
"""

from .router import router

__all__ = ["router"]
