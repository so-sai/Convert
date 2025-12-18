"""
Command Dispatcher - Routes commands to appropriate services.

Implements routing logic for Hybrid SSOT architecture.
"""
from typing import Dict, Any


class Dispatcher:
    """
    Central command router for Python Core.
    
    Routes incoming commands from Rust/Tauri to appropriate service handlers.
    """
    
    def __init__(self):
        """Initialize dispatcher with service registry."""
        self._services = {
            "backup": self._handle_backup,
            "restore": self._handle_restore,
        }
    
    def handle(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route command to appropriate handler.
        
        Args:
            envelope: Command envelope with 'cmd' and 'payload' keys
            
        Returns:
            Result dictionary with 'status' and additional data
        """
        try:
            # Validate envelope structure
            if not isinstance(envelope, dict):
                return self._error("Invalid envelope: must be a dictionary")
            
            if "cmd" not in envelope:
                return self._error("Missing 'cmd' field in envelope")
            
            if "payload" not in envelope:
                return self._error("Missing 'payload' field in envelope")
            
            # Parse command
            cmd = envelope["cmd"]
            if not isinstance(cmd, str):
                return self._error("Command must be a string")
            
            # Route to service
            parts = cmd.split(".", 1)
            if len(parts) != 2:
                return self._error(f"Invalid command format: {cmd}")
            
            service_name, action = parts
            
            if service_name not in self._services:
                return self._error(f"Unknown service: {service_name}")
            
            # Delegate to service handler
            return self._services[service_name](action, envelope["payload"])
            
        except Exception as e:
            return self._error(f"Dispatcher error: {str(e)}")
    
    def _handle_backup(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle backup service commands."""
        if action == "start":
            # Validate payload
            if "target_dir" not in payload:
                return self._error("Backup validation failed: missing target_dir")
            
            # Simulate successful backup initiation
            return {
                "status": "success",
                "task_id": "backup_001",
                "message": "Backup initiated"
            }
        
        return self._error(f"Unknown backup action: {action}")
    
    def _handle_restore(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle restore service commands."""
        if action == "start":
            # Validate payload (FIXED: match Rust parameter name 'file_path')
            if "file_path" not in payload:
                return self._error("Restore validation failed: missing file_path")
            
            path = payload["file_path"]  # FIXED: use correct key
            print(f"🐍 [PYTHON] Restore command received! Path: {path}")
            
            # TODO: Implement actual restore logic in Sprint 6
            # For now, return success to confirm E2E connection works
            return {
                "status": "success",
                "task_id": "restore_001",
                "message": f"Restore initiated for {path}",
                "file_path": path
            }
        
        return self._error(f"Unknown restore action: {action}")
    
    def _error(self, message: str) -> Dict[str, Any]:
        """Create error response."""
        return {
            "status": "error",
            "message": message
        }
