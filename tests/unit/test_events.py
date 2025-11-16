"""
Unit Tests for Event Schemas - Sprint 1
Tests Triple-Stream Event architecture validation
FIXED for Python 3.14 + Pydantic 2.12.4
"""

import pytest
from pydantic import ValidationError

from src.core.schemas.events import (
    DomainEvent,
    InteractionEvent,
    MemoryEvent,
    MemoryPayload,
)


def test_create_domain_event_success():
    """Test successful DomainEvent creation."""
    event = DomainEvent(payload={"note_id": "n-abc", "action": "created"})
    
    assert event.id.startswith("evt-")
    assert len(event.id) == 16
    assert event.type == "domain"
    assert event.payload["note_id"] == "n-abc"


def test_create_interaction_event_success():
    """Test successful InteractionEvent creation."""
    event = InteractionEvent(payload={"action": "portal_opened", "target": "notes"})
    
    assert event.id.startswith("evt-")
    assert len(event.id) == 16
    assert event.type == "interaction"


def test_create_memory_event_success():
    """Test successful MemoryEvent creation with valid payload."""
    payload_data = {
        "rationale": "Valid rationale with sufficient length to pass validation.",
        "alternatives": ["alt1", "alt2"],
        "impact": "high",
        "decision_framework": ["rule1", "rule2"],
    }
    
    memory_payload = MemoryPayload(**payload_data)
    event = MemoryEvent(type="memory", payload=memory_payload)
    
    assert event.id.startswith("evt-")
    assert len(event.id) == 16
    assert event.type == "memory"
    assert event.payload.impact == "high"


def test_event_ids_are_unique():
    """Test that generated event IDs are unique."""
    events = [DomainEvent(payload={}) for _ in range(10)]
    event_ids = [e.id for e in events]
    assert len(event_ids) == len(set(event_ids))


def test_invalid_event_type_raises_validation_error():
    """Test that invalid event type raises ValidationError."""
    with pytest.raises(ValidationError):
        DomainEvent(type="wrong_type", payload={})


@pytest.mark.parametrize(
    "invalid_payload, expected_error_part",
    [
        (
            {
                "rationale": "short",
                "alternatives": ["alt1"],
                "impact": "high",
                "decision_framework": ["rule1"],
            },
            "20 characters",  # ✅ FIXED: Tìm cụm này trong error message
        ),
        (
            {
                "rationale": "This rationale is definitely long enough.",
                "alternatives": [],
                "impact": "high", 
                "decision_framework": ["rule1"],
            },
            "at least 1",  # ✅ FIXED: Tìm cụm này trong error message
        ),
        (
            {
                "rationale": "This rationale is definitely long enough.",
                "alternatives": ["alt1"],
                "impact": "invalid_impact",
                "decision_framework": ["rule1"],
            },
            "should be",  # ✅ FIXED: Tìm cụm này trong error message
        ),
        (
            {
                "rationale": "This rationale is definitely long enough.",
                "alternatives": ["alt1"],
                "impact": "high",
                "decision_framework": [],
            },
            "at least 1",  # ✅ FIXED: Tìm cụm này trong error message
        ),
    ],
)
def test_memory_payload_validation_fails(invalid_payload, expected_error_part):
    """Test that invalid MemoryPayload raises ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        MemoryPayload(**invalid_payload)
    
    error_str = str(excinfo.value).lower()
    assert expected_error_part in error_str


def test_memory_payload_forbids_extra_fields():
    """Test that MemoryPayload blocks extra fields (security validation)."""
    invalid_data = {
        "rationale": "Valid rationale with sufficient length to pass validation.",
        "alternatives": ["alt1"],
        "impact": "high",
        "decision_framework": ["rule1"],
        "malicious_field": "should_be_blocked",
    }
    
    with pytest.raises(ValidationError) as excinfo:
        MemoryPayload(**invalid_data)
    
    error_str = str(excinfo.value).lower()
    assert "extra" in error_str