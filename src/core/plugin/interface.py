# Copyright (c) 2025 Project CONVERT. PolyForm Noncommercial 1.0.0
from typing import Protocol, runtime_checkable, Any, Dict
from dataclasses import dataclass

@dataclass
class PluginManifest:
    """Metadata for a plugin."""
    name: str
    version: str
    description: str
    author: str
    license: str = "PolyForm Noncommercial 1.0.0"

@runtime_checkable
class IPlugin(Protocol):
    """
    Interface that all plugins must implement.
    """
    
    @property
    def manifest(self) -> PluginManifest:
        """Return plugin metadata."""
        ...

    def initialize(self, context: Dict[str, Any]) -> None:
        """
        Initialize the plugin with the given context.
        
        Args:
            context: A dictionary containing system services/config.
        """
        ...

    def shutdown(self) -> None:
        """Clean up resources before plugin unload."""
        ...
