import asyncio
from typing import List

async def generate_daily_summary(ai_service, http_client, cache, tickers: List[str]):
    cache_key = f"daily_summary:{','.join(tickers)}"
    cached_summary = await cache.get(cache_key)
    if cached_summary:
        return {
            "status": "success",
            "type": "daily_summary",
            "data": cached_summary,
            "cached": True
        }

    prompt = f"Generate a daily summary for the following tickers: {', '.join(tickers)}."

    summary = ""
    async for token in ai_service.stream_chat(prompt):
        summary += token

    await cache.set(cache_key, summary, ttl=3600)  # Cache for 1 hour (shorter for daily)

    return {
        "status": "success",
        "type": "daily_summary",
        "data": summary,
        "cached": False
    }

