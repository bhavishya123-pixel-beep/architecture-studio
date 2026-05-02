"""
Base agent class. All specialized agents inherit from this.
Enforces the evidence-citation contract and structured JSON output.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    agent_name: str
    run_id: UUID = Field(default_factory=uuid4)
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    success: bool
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    evidence_ids: list[UUID] = Field(default_factory=list)
    sources_used: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    llm_used: bool = False
    llm_tokens_used: Optional[int] = None
    processing_time_ms: Optional[float] = None


class BaseAgent(ABC):
    """
    All agents must:
    1. Accept only typed inputs
    2. Return AgentOutput with evidence_ids populated
    3. Never invent facts — return data_gap=True if data is missing
    4. Catch and log exceptions rather than propagating them
    """

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agents.{name}")

    @abstractmethod
    async def run(self, **kwargs) -> AgentOutput:
        ...

    def _ok(
        self,
        result: dict,
        evidence_ids: list[UUID] = None,
        sources: list[str] = None,
        confidence: float = 0.8,
        llm_used: bool = False,
        llm_tokens: Optional[int] = None,
        processing_ms: Optional[float] = None,
    ) -> AgentOutput:
        return AgentOutput(
            agent_name=self.name,
            success=True,
            result=result,
            evidence_ids=evidence_ids or [],
            sources_used=sources or [],
            confidence=confidence,
            llm_used=llm_used,
            llm_tokens_used=llm_tokens,
            processing_time_ms=processing_ms,
        )

    def _fail(self, error: str) -> AgentOutput:
        self.logger.error(f"Agent {self.name} failed: {error}")
        return AgentOutput(
            agent_name=self.name,
            success=False,
            error=error,
            confidence=0.0,
        )
