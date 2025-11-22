# Copyright (c) 2025 Project CONVERT. PolyForm Noncommercial 1.0.0
import pytest
from pathlib import Path
from src.core.plugin.loader import PluginLoader, SecurityError
from src.core.plugin.interface import IPlugin, PluginManifest

# Mock Plugin Content
VALID_PLUGIN_CODE = """
# Copyright (c) 2025 Project CONVERT. PolyForm Noncommercial 1.0.0
from src.core.plugin.interface import IPlugin, PluginManifest

class TestPlugin(IPlugin):
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="test_plugin",
            version="1.0.0",
            description="A test plugin",
            author="Tester"
        )

    def initialize(self, context):
        pass

    def shutdown(self):
        pass
"""

INVALID_HEADER_PLUGIN_CODE = """
# Missing License Header
from src.core.plugin.interface import IPlugin, PluginManifest

class BadPlugin(IPlugin):
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(name="bad", version="1", description="", author="")
    def initialize(self, ctx): pass
    def shutdown(self): pass
"""

@pytest.fixture
def plugin_loader():
    return PluginLoader()

@pytest.fixture
def valid_plugin_file(tmp_path):
    p = tmp_path / "valid_plugin.py"
    p.write_text(VALID_PLUGIN_CODE, encoding='utf-8')
    return p

@pytest.fixture
def invalid_header_plugin_file(tmp_path):
    p = tmp_path / "invalid_plugin.py"
    p.write_text(INVALID_HEADER_PLUGIN_CODE, encoding='utf-8')
    return p

def test_load_valid_plugin(plugin_loader, valid_plugin_file):
    plugin = plugin_loader.load_plugin(valid_plugin_file)
    assert plugin is not None
    assert plugin.manifest.name == "test_plugin"
    assert plugin_loader.get_plugin("test_plugin") == plugin

def test_reject_invalid_header(plugin_loader, invalid_header_plugin_file):
    with pytest.raises(SecurityError, match="Missing 'PolyForm Noncommercial' header"):
        plugin_loader.load_plugin(invalid_header_plugin_file)

def test_plugin_not_found(plugin_loader):
    with pytest.raises(FileNotFoundError):
        plugin_loader.load_plugin(Path("non_existent.py"))
