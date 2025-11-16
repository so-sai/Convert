"""
Memory Bridge Interface v0.1
Contract for recording AI decision metadata across CONVERT v2
Optimized for Python 3.14
"""

from abc import ABC, abstractmethod
from typing import Literal
from pydantic import BaseModel, Field

from src.core.schemas.events import MemoryEvent, MemoryPayload


class EventBus(ABC):
    """Abstract Event Bus interface - implementations in Sprint 2+."""
    
    @abstractmethod
    def publish(self, event: MemoryEvent) -> None:
        """Publish an event to the bus."""
        pass


class DecisionRecord(BaseModel):
    """High-level decision record that gets transformed into MemoryEvent."""
    
    component: str = Field(
        ..., description="Component making the decision (e.g., 'NoteService')"
    )
    category: Literal["architectural", "implementation", "ux"]
    rationale: str = Field(..., min_length=20)
    alternatives: list[str] = Field(..., min_items=1)
    impact: Literal["low", "medium", "high"]
    decision_framework: list[str] = Field(..., min_items=1)
    notes: str | None = Field(None)


class MemoryBridge:
    """
    Single point of entry for recording decisions.
    Enforces Decision Policy v1.0 and transforms DecisionRecords into MemoryEvents.
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
    
    def record_decision(self, decision: DecisionRecord) -> str:
        """
        Record a decision that meets Decision Policy v1.0 criteria.
        
        Args:
            decision: A validated DecisionRecord
            
        Returns:
            event_id: The unique ID of the created MemoryEvent
        """
        memory_payload = MemoryPayload(
            rationale=decision.rationale,
            alternatives=decision.alternatives,
            impact=decision.impact,
            decision_framework=decision.decision_framework,
            notes=decision.notes,
        )
        
        memory_event = MemoryEvent(
            type="memory",
            payload=memory_payload
        )
        
        self.event_bus.publish(memory_event)
        return memory_event.id
    
    def should_record(self, decision_description: str) -> bool:
        """
        Helper to check if a decision meets Decision Policy v1.0 criteria.
        
        Decision Policy Criteria (ANY must be true):
        1. Affects an Architectural Contract
        2. Introduces a new dependency
        3. Resolves a significant trade-off
        4. Sets a precedent for future decisions
        """
        keywords = [
            "architecture",
            "contract",
            "interface",
            "dependency",
            "trade-off",
            "pattern",
            "policy",
        ]
        desc_lower = decision_description.lower()
        return any(kw in desc_lower for kw in keywords)
    