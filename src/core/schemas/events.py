# File: src/core/schemas/events.py
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class BaseEvent(BaseModel):
    """Mô hình sự kiện cơ sở."""
    id: str = Field(default_factory=lambda: f"evt-{uuid4().hex[:12]}")
    timestamp: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    type: str

class DomainEvent(BaseEvent):
    """Sự kiện ghi lại thay đổi trạng thái dữ liệu (cái 'gì')."""
    type: Literal["domain"] = "domain"
    payload: Dict[str, Any]

class InteractionEvent(BaseEvent):
    """Sự kiện ghi lại tương tác người dùng (cái 'như thế nào')."""
    type: Literal["interaction"] = "interaction"
    payload: Dict[str, Any]

class MemoryPayload(BaseModel):
    """Cấu trúc chi tiết của một quyết định được ghi lại."""
    rationale: str = Field(..., description="Why the decision/reasoning occurred")
    alternatives: List[str] = Field(..., description="Alternative options considered")
    impact: str = Field(..., description="Expected or observed impact")
    decision_framework: List[str] = Field(..., description="Framework/criteria used for decision")
    notes: Optional[str] = Field(None, description="Optional freeform note")

class MemoryEvent(BaseEvent):
    """Sự kiện ghi lại quyết định của hệ thống (cái 'tại sao')."""
    type: Literal["memory"] = "memory"
    payload: Dict[Literal["memory"], MemoryPayload]