"""API routes: investment memo generation."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from api.schemas import InvestmentMemo, AssetType
from agents.orchestrator.orchestrator_agent import OrchestratorAgent

router = APIRouter(prefix="/memos", tags=["Memos"])


class MemoRequest(BaseModel):
    city: str
    state: str
    locality: str
    pin_code: Optional[str] = None
    project_name: Optional[str] = None
    holding_years: int = 5
    use_llm: bool = False


@router.post("/generate", response_model=dict)
async def generate_memo(req: MemoRequest):
    """
    Generate a full investment memo for a location.
    Set use_llm=true to enable LLM narrative generation (requires ANTHROPIC_API_KEY).
    """
    from config.settings import get_settings
    settings = get_settings()

    llm_client = None
    if req.use_llm and settings.anthropic_api_key:
        import anthropic
        llm_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    agent = OrchestratorAgent(llm_client=llm_client)
    output = await agent.run(
        city=req.city,
        state=req.state,
        locality=req.locality,
        pin_code=req.pin_code,
        project_name=req.project_name,
        holding_years=req.holding_years,
    )

    if not output.success:
        raise HTTPException(status_code=500, detail=output.error)

    return {
        "memo": output.result,
        "agent_run_id": str(output.run_id),
        "processing_time_ms": output.processing_time_ms,
        "llm_used": output.llm_used,
        "disclaimer": settings.disclaimer,
    }
