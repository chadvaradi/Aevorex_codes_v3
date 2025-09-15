from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json  
import logging

from api.llm.schemas import ChatRequest, ChatResponse, ModelsResponse
from api.llm.catalogue import get_models_response, is_allowed, resolve_model, MODELS
from api.llm.providers.openrouter import OpenRouterProvider

logger = logging.getLogger(__name__)

router = APIRouter()
provider = OpenRouterProvider()

@router.get("/models", response_model=ModelsResponse)
def list_models():
    return get_models_response()

def _validate(model: str | None):
    if model is None:
        return
    if not is_allowed(model) and not is_allowed(resolve_model(model)):
        raise HTTPException(status_code=400, detail="Invalid model")

@router.post("/completions", response_model=ChatResponse)
async def completions(req: ChatRequest):
    _validate(req.model)
    # Convert Pydantic models to dict for provider
    messages_dict = [m.model_dump() for m in req.messages]
    content = await provider.generate(messages_dict, req.model)
    return ChatResponse(content=content, usage=None)

@router.post("/stream")
async def stream(req: ChatRequest):
    _validate(req.model)
    # Convert Pydantic models to dict for provider
    messages_dict = [m.model_dump() for m in req.messages]
    async def gen():
        try:
            async for chunk in provider.stream(messages_dict, req.model):
                yield "data: " + json.dumps({"content": chunk}) + "\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield "data: " + json.dumps({"error": f"Stream failed: {str(e)}"}) + "\n\n"
            yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
