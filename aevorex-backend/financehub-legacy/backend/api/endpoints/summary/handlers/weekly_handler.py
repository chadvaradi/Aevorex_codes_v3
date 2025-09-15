import asyncio
from typing import List

async def generate_weekly_summary(ai_service, http_client, cache, tickers: List[str]):
    cache_key = f"weekly_summary:{','.join(tickers)}"
    cached_summary = await cache.get(cache_key)
    if cached_summary:
        return {
            "status": "success",
            "type": "weekly_summary",
            "data": cached_summary,
            "cached": True
        }

    prompt = f"Generate a weekly summary for the following tickers: {', '.join(tickers)}."

    summary = ""
    async for token in ai_service.stream_chat(prompt):
        summary += token

    await cache.set(cache_key, summary, ttl=86400)  # Cache for 24 hours

    return {
        "status": "success",
        "type": "weekly_summary",
        "data": summary,
        "cached": False
    }
