"""
SANDBOX.PY - Zero-Trust Process Sandbox for IndexerStorage
Task 6.4 - Sprint 6 Background Services

T20: Timeout Enforcement (10 seconds)
T22: Memory Limit (512MB)
"""

import asyncio
import os
import sys
from typing import List, Optional


class SandboxError(Exception):
    """Error raised when sandbox constraint is violated"""
    pass


class SandboxExecutor:
    """
    T20/T22: Isolated Process Execution with Resource Limits
    
    Runs extraction commands in sandboxed subprocess with:
    - Timeout enforcement (kills after N seconds)
    - Memory limit (kills if exceeds MB limit)
    - Isolation (no state sharing between executions)
    """
    
    DEFAULT_TIMEOUT_SECONDS = 10
    DEFAULT_MEMORY_LIMIT_MB = 512
    
    def __init__(
        self,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        memory_limit_mb: int = DEFAULT_MEMORY_LIMIT_MB
    ):
        self.timeout_seconds = timeout_seconds
        self.memory_limit_mb = memory_limit_mb
    
    async def execute(self, command: List[str], cwd: Optional[str] = None) -> bytes:
        """
        Execute command in sandboxed subprocess.
        
        Args:
            command: Command and arguments to execute
            cwd: Working directory (optional)
            
        Returns:
            stdout as bytes
            
        Raises:
            SandboxError: If timeout or memory limit exceeded
        """
        process = None
        
        try:
            # Create subprocess with resource pre-configuration
            if sys.platform == "win32":
                # Windows: Use CREATE_NEW_PROCESS_GROUP for job control
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    creationflags=0x00000200  # CREATE_NEW_PROCESS_GROUP
                )
                
                # Apply memory limit via Windows Job Object
                self._apply_windows_job_limits(process)
            else:
                # Unix: Use preexec_fn to set resource limits
                def set_unix_limits():
                    import resource
                    # Set memory limit (virtual memory)
                    mem_bytes = self.memory_limit_mb * 1024 * 1024
                    resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
                    # Set CPU time limit as backup
                    resource.setrlimit(resource.RLIMIT_CPU, 
                        (self.timeout_seconds + 5, self.timeout_seconds + 5))
                
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    preexec_fn=set_unix_limits
                )
            
            # Wait for completion with timeout AND memory monitoring
            try:
                # Create memory monitor task for Windows (Job Objects may fail)
                if sys.platform == "win32":
                    stdout, stderr = await self._execute_with_memory_monitor(
                        process, self.timeout_seconds, self.memory_limit_mb
                    )
                else:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=self.timeout_seconds
                    )
            except asyncio.TimeoutError:
                # Kill the process on timeout
                self._force_kill(process)
                raise SandboxError(
                    f"Process timeout: exceeded {self.timeout_seconds} seconds"
                )
            
            # Check for memory-related exit codes
            if process.returncode == -9 or process.returncode == 137:
                raise SandboxError(
                    f"Process killed by memory limit ({self.memory_limit_mb}MB)"
                )
            
            # Check for other memory error indicators
            stderr_str = stderr.decode('utf-8', errors='replace').lower()
            if 'memory' in stderr_str and ('error' in stderr_str or 'killed' in stderr_str):
                raise SandboxError(
                    f"Process memory error: {stderr_str[:200]}"
                )
            
            return stdout
            
        except SandboxError:
            raise
        except Exception as e:
            if process:
                self._force_kill(process)
            raise SandboxError(f"Sandbox execution failed: {e}")
    
    async def _execute_with_memory_monitor(
        self, 
        process, 
        timeout_seconds: int, 
        memory_limit_mb: int
    ) -> tuple:
        """
        Execute with active memory monitoring using psutil.
        
        This is the fallback for Windows when Job Objects fail.
        Polls process memory every 100ms and kills if exceeded.
        """
        import psutil
        
        memory_limit_bytes = memory_limit_mb * 1024 * 1024
        memory_exceeded = False
        
        async def monitor_memory():
            nonlocal memory_exceeded
            try:
                ps_process = psutil.Process(process.pid)
                while process.returncode is None:
                    try:
                        mem_info = ps_process.memory_info()
                        if mem_info.rss > memory_limit_bytes:
                            memory_exceeded = True
                            self._force_kill(process)
                            return
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        return
                    await asyncio.sleep(0.01)  # Check every 10ms (100Hz) for fast detection
            except Exception:
                pass
        
        # Start memory monitor
        monitor_task = asyncio.create_task(monitor_memory())
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout_seconds
            )
        finally:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        if memory_exceeded:
            raise SandboxError(
                f"Process killed by memory limit ({memory_limit_mb}MB)"
            )
        
        return stdout, stderr
    
    def _apply_windows_job_limits(self, process) -> None:
        """Apply memory limits via Windows Job Object (if available)"""
        try:
            # Try to use win32job if available
            import win32job
            import win32process
            
            # Create job object
            hJob = win32job.CreateJobObject(None, "")
            
            # Set memory limit
            info = win32job.QueryInformationJobObject(
                hJob, win32job.JobObjectExtendedLimitInformation
            )
            info['BasicLimitInformation']['LimitFlags'] = (
                win32job.JOB_OBJECT_LIMIT_PROCESS_MEMORY
            )
            info['ProcessMemoryLimit'] = self.memory_limit_mb * 1024 * 1024
            
            win32job.SetInformationJobObject(
                hJob, 
                win32job.JobObjectExtendedLimitInformation,
                info
            )
            
            # Assign process to job
            win32job.AssignProcessToJobObject(hJob, int(process._transport.get_pid()))
            
        except ImportError:
            # win32job not available - memory limit not enforced on Windows
            # T22 test will handle this gracefully
            pass
        except Exception:
            # Job object setup failed - continue without memory limit
            pass
    
    def _force_kill(self, process) -> None:
        """Force kill the process"""
        try:
            process.kill()
        except:
            pass
        
        # On Windows, also try taskkill for stubborn processes
        if sys.platform == "win32":
            try:
                os.system(f"taskkill /F /PID {process.pid} 2>nul")
            except:
                pass
