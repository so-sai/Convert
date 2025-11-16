"""
Event Schemas - Sprint 1 Foundation
Triple-Stream Architecture: Domain, Interaction, Memory
FIXED for Python 3.14 + Pydantic 2.12.4
"""

from typing import Any, Literal
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict


class BaseEvent(BaseModel):
    """Base event model for all event types."""
    
    model_config = ConfigDict(extra='forbid')

    id: str = Field(default_factory=lambda: f"evt-{uuid4().hex[:12]}")
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now(timezone.utc).timestamp())
    )
    type: str


class DomainEvent(BaseEvent):
    """Domain Event - captures state transitions (the 'what')."""
    
    type: Literal["domain"] = "domain"
    payload: dict[str, Any]


class InteractionEvent(BaseEvent):
    """Interaction Event - captures user behavior (the 'how')."""
    
    type: Literal["interaction"] = "interaction"
    payload: dict[str, Any]


class MemoryPayload(BaseModel):
    """Schema for Memory Event payload - AI decision metadata."""
    
    model_config = ConfigDict(extra='forbid')

    rationale: str = Field(..., min_length=20)
    alternatives: list[str] = Field(..., min_length=1)
    impact: Literal["low", "medium", "high"]
    decision_framework: list[str] = Field(..., min_length=1)
    notes: str | None = None


class MemoryEvent(BaseEvent):
    """Memory Event - captures system reasoning (the 'why')."""
    
    type: Literal["memory"] = "memory"
    payload: MemoryPayload