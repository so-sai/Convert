from enum import Enum
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class StreamType(str, Enum):
    DOMAIN = "domain"
    INTERACTION = "interaction" 
    MEMORY = "memory"

class BaseEvent(BaseModel):
    """Base Event Schema"""
    event_id: str
    timestamp: int
    model_config = ConfigDict(extra="forbid", frozen=True)

class DomainEvent(BaseEvent):
    stream_type: StreamType
    stream_id: str
    event_type: str
    stream_sequence: int
    global_sequence: int
    timestamp: int
    payload: Any
    prev_event_hash: Optional[str] = None
    event_hash: str
    enc_algorithm: str = "pass-through"
    enc_key_id: Optional[str] = None
    enc_nonce: Optional[str] = None
    event_hmac: str
    model_config = ConfigDict(extra="forbid", frozen=True)

class MemoryEvent(DomainEvent): pass
class InteractionEvent(DomainEvent): pass

class SystemHealth(BaseModel):
    status: str = Field(..., pattern="^(connected|disconnected|initializing|degraded)$")
    backend_version: str
    uptime_seconds: int
    last_check: datetime
    database_connected: bool
    chain_integrity: bool
    mds_compliant: bool = True
    model_config = ConfigDict(extra="forbid")

class SystemStats(BaseModel):
    total_notes: int
    total_events: int
    last_sync: datetime | None = None
    mds_version: str
    crypto_integrity: str
    model_config = ConfigDict(extra="forbid")

class RecentNote(BaseModel):
    id: str
    title: str
    updated_at: datetime
    excerpt: str
    model_config = ConfigDict(extra="forbid")

class MemoryPayload(BaseModel):
    """Schema for AI Memory Bridge events"""
    decision_id: str
    rationale: str
    alternatives: list[str]
    confidence: float
    model_config = ConfigDict(extra="forbid")
