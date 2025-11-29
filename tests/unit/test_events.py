"""
Unit Tests for Event Schemas - Sprint 1
Tests Triple-Stream Event architecture validation
FIXED for Python 3.14 + Pydantic 2.12.4 + Current Schema
"""

import pytest
from pydantic import ValidationError

from src.core.schemas.events import (
    DomainEvent,
    MemoryEvent,
    InteractionEvent,
    StreamType,
)


def test_create_domain_event_success():
    """Test successful DomainEvent creation."""
    event = DomainEvent(
        event_id="evt-test123",
        stream_type=StreamType.DOMAIN,
        stream_id="stream-1",
        event_type="note_created",
        stream_sequence=1,
        global_sequence=1,
        timestamp=1234567890,
        payload={"note_id": "n-abc", "action": "created"},
        event_hash="hash123",
        event_hmac="hmac123"
    )
    
    assert event.event_id == "evt-test123"
    assert event.stream_type == StreamType.DOMAIN
    assert event.payload["note_id"] == "n-abc"


def test_create_interaction_event_success():
    """Test successful InteractionEvent creation."""
    event = InteractionEvent(
        event_id="evt-test456",
        stream_type=StreamType.INTERACTION,
        stream_id="stream-2",
        event_type="portal_opened",
        stream_sequence=1,
        global_sequence=2,
        timestamp=1234567891,
        payload={"action": "portal_opened", "target": "notes"},
        event_hash="hash456",
        event_hmac="hmac456"
    )
    
    assert event.event_id == "evt-test456"
    assert event.stream_type == StreamType.INTERACTION


def test_create_memory_event_success():
    """Test successful MemoryEvent creation."""
    event = MemoryEvent(
        event_id="evt-test789",
        stream_type=StreamType.MEMORY,
        stream_id="stream-3",
        event_type="decision_made",
        stream_sequence=1,
        global_sequence=3,
        timestamp=1234567892,
        payload={"decision": "use_argon2id", "rationale": "OWASP 2025 compliant"},
        event_hash="hash789",
        event_hmac="hmac789"
    )
    
    assert event.event_id == "evt-test789"
    assert event.stream_type == StreamType.MEMORY


def test_event_immutability():
    """Test that events are frozen (immutable)."""
    event = DomainEvent(
        event_id="evt-immutable",
        stream_type=StreamType.DOMAIN,
        stream_id="stream-4",
        event_type="test",
        stream_sequence=1,
        global_sequence=4,
        timestamp=1234567893,
        payload={},
        event_hash="hash",
        event_hmac="hmac"
    )
    
    with pytest.raises(ValidationError):
        event.event_id = "new-id"


def test_extra_fields_forbidden():
    """Test that extra fields are forbidden."""
    with pytest.raises(ValidationError):
        DomainEvent(
            event_id="evt-extra",
            stream_type=StreamType.DOMAIN,
            stream_id="stream-5",
            event_type="test",
            stream_sequence=1,
            global_sequence=5,
            timestamp=1234567894,
            payload={},
            event_hash="hash",
            event_hmac="hmac",
            malicious_field="should_fail"
        )