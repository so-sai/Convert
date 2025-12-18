"""
Test suite for Command Dispatcher (Router Logic).

RED PHASE: These tests WILL FAIL until dispatcher.py is implemented.
"""
import pytest


class TestDispatcher:
    """Test command routing and delegation."""

    def test_dispatcher_routes_backup_command(self, mock_dispatcher_envelope):
        """
        GIVEN a valid backup.start command envelope
        WHEN dispatcher processes it
        THEN it should route to backup service and return success
        """
        from core.dispatcher import Dispatcher
        
        dispatcher = Dispatcher()
        result = dispatcher.handle(mock_dispatcher_envelope)
        
        assert result["status"] == "success"
        assert "task_id" in result

    def test_dispatcher_rejects_invalid_command(self):
        """
        GIVEN an invalid command envelope
        WHEN dispatcher processes it
        THEN it should return error status
        """
        from core.dispatcher import Dispatcher
        
        dispatcher = Dispatcher()
        invalid_envelope = {"cmd": "invalid.command", "payload": {}}
        result = dispatcher.handle(invalid_envelope)
        
        assert result["status"] == "error"
        assert "message" in result

    def test_dispatcher_validates_payload_schema(self):
        """
        GIVEN a command with missing required fields
        WHEN dispatcher processes it
        THEN it should return validation error
        """
        from core.dispatcher import Dispatcher
        
        dispatcher = Dispatcher()
        incomplete_envelope = {"cmd": "backup.start", "payload": {}}  # Missing target_dir
        result = dispatcher.handle(incomplete_envelope)
        
        assert result["status"] == "error"
        assert "validation" in result["message"].lower()
