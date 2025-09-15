"""
Summary API domain package.

Provides scheduled and on-demand summary endpoints:
- Daily summaries
- Weekly summaries
- Monthly summaries
- Quarterly summaries
"""

from .summary_router import router

__all__ = ["router"]
