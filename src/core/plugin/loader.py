# Copyright (c) 2025 Project CONVERT. PolyForm Noncommercial 1.0.0
import importlib.util
import sys
import logging
from pathlib import Path
from typing import Dict, Type, Optional
from src.core.plugin.interface import IPlugin

logger = logging.getLogger(__name__)

class PluginLoader:
    """
    Securely loads plugins from a directory.
    Enforces 'PolyForm Noncommercial' header check.
    """
    
    def __init__(self):
        self._loaded_plugins: Dict[str, IPlugin] = {}

    def load_plugin(self, file_path: Path) -> Optional[IPlugin]:
        """
        Load a plugin from a file path.
        
        Args:
            file_path: Path to the plugin python file.
            
        Returns:
            The initialized plugin instance, or None if loading failed.
            
        Raises:
            SecurityError: If the plugin is missing the required license header.
            ImportError: If the plugin cannot be imported or is invalid.
        """
        file_path = Path(file_path).resolve()
        
        if not file_path.exists():
            raise FileNotFoundError(f"Plugin file not found: {file_path}")
            
        # 1. Security Check: Verify Header
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "PolyForm Noncommercial" not in content:
                logger.critical(f"Security Violation: Plugin {file_path.name} missing required license header.")
                raise SecurityError(f"Plugin {file_path.name} rejected: Missing 'PolyForm Noncommercial' header.")

        # 2. Import Module
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            raise ImportError(f"Could not create module spec for {file_path}")
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise ImportError(f"Failed to execute plugin module {module_name}: {e}") from e
            
        # 3. Find Plugin Class
        plugin_class: Optional[Type[IPlugin]] = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            # Check if it's a class defined in this module (not imported)
            if isinstance(attr, type) and attr.__module__ == module.__name__:
                # Manual duck-typing check because issubclass fails on Protocols with properties
                if hasattr(attr, 'initialize') and hasattr(attr, 'shutdown') and hasattr(attr, 'manifest'):
                    plugin_class = attr
                    break
                
        if not plugin_class:
            raise ImportError(f"No IPlugin implementation found in {file_path}")
            
        # 4. Instantiate
        try:
            plugin_instance = plugin_class()
            self._loaded_plugins[plugin_instance.manifest.name] = plugin_instance
            logger.info(f"Loaded plugin: {plugin_instance.manifest.name} v{plugin_instance.manifest.version}")
            return plugin_instance
        except Exception as e:
            raise ImportError(f"Failed to instantiate plugin {module_name}: {e}") from e

    def get_plugin(self, name: str) -> Optional[IPlugin]:
        return self._loaded_plugins.get(name)

class SecurityError(Exception):
    """Raised when a security check fails."""
    pass
