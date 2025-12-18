import pytest
import time
from src.core.state_manager import init_state, AppState

@pytest.mark.unit
def test_state_manager_init():
    """Test 2.1.0: init_state() returns default schema matching MDS."""
    state = init_state()
    
    # Verify Schema Structure
    assert isinstance(state, dict)
    assert "version" in state
    assert "timestamp" in state
    assert "navigation" in state
    assert "modules" in state
    assert "panels" in state
    
    # Verify Default Values
    assert state["version"] == 1
    assert isinstance(state["timestamp"], (int, float))
    assert state["navigation"]["ui_depth"] == 0
    
    # Verify Pydantic Model (Strict)
    # This ensures we are using the Pydantic model for validation even if returning dict
    model = AppState(**state)
    assert model.version == 1
