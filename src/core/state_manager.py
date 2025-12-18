from pydantic import BaseModel, Field
from typing import Dict, Any, Union
import time

class AppNavigation(BaseModel):
    active_module: str = "convert"
    last_route: str = "/"
    ui_depth: int = 0

class PanelConfig(BaseModel):
    split: Dict[str, float] = Field(default_factory=lambda: {"left": 0.5, "right": 0.5})

class AppState(BaseModel):
    version: int = 1
    timestamp: float = Field(default_factory=time.time)
    navigation: AppNavigation = Field(default_factory=AppNavigation)
    modules: Dict[str, Any] = Field(default_factory=dict)
    panels: Dict[str, PanelConfig] = Field(default_factory=dict)

def init_state() -> Dict[str, Any]:
    """Initialize default application state following MDS v3.14 schema."""
    state = AppState()
    # Ensure default panels exist for core modules
    if "notes" not in state.panels:
        state.panels["notes"] = PanelConfig(split={"left": 0.33, "right": 0.67})
    
    return state.model_dump()
