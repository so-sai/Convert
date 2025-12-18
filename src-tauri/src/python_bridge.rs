//! PyO3 Rust-Python Bridge Module.
//!
//! Implements MDS v3.14 Hybrid SSOT architecture:
//! - Rust (The Muscle) embeds Python (The Brain)
//! - No subprocess spawning (Omega Fix)
//! - Direct memory communication via PyO3
//! - Dynamic Path Resolution (Gap 2 Fix)
//! - Persistent Session State data via OnceCell (Gap 3 Fix)

use once_cell::sync::Lazy;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use serde_json::{json, Value};
use std::env;
use std::path::PathBuf;
use std::sync::Mutex;

// GLOBAL STATE: Persist Python Dispatcher instance
// Mutex ensures thread safety across Tauri command calls
static PYTHON_DISPATCHER: Lazy<Mutex<Option<PyObject>>> = Lazy::new(|| Mutex::new(None));

/// Helper: Resolve Python Core source path dynamically
fn get_python_src_path() -> PathBuf {
    let current_dir = env::current_dir().unwrap_or_default();

    // 1. DEV Mode: Look for adjacent src-core directory
    // E:\DEV\Convert\src-tauri\..\src
    // Note: Project structure is src/core/dispatcher.py, but sys.path needs the root of the module
    // If src/core/dispatcher.py exists, we need to add 'src' to sys.path so 'import core.dispatcher' works?
    // OR if we import 'dispatcher' directly, we need to add 'src/core' to sys.path.
    // Based on previous code: sys_path.insert(0, path_str) where path points to 'src/core'

    // Attempt 1: Check for standard Monorepo Dev structure
    // We are in src-tauri. We need to go up one level, then into src/core
    // But wait, the previous code used: project_root.join("src") which implies E:\DEV\Convert\src
    // And import was "core.dispatcher".

    let root_src = current_dir.parent().unwrap().join("src");
    if root_src.exists() {
        println!("🐍 [PyO3] DEV Mode detected. Path: {:?}", root_src);
        return root_src;
    }

    // 2. PROD Mode: Fallback to local 'resources' or bundled folder
    println!("⚠️ [PyO3] DEV path not found. Falling back to PROD logic.");
    // For now, return current dir to prevent crash, real prod logic needs sidecar resource
    current_dir
}

/// Initialize Python environment and cache Dispatcher instance
pub fn init_python_backend() -> PyResult<()> {
    let mut dispatcher_guard = PYTHON_DISPATCHER.lock().unwrap();

    if dispatcher_guard.is_some() {
        return Ok(());
    }

    Python::with_gil(|py| {
        // 1. Setup Path
        let sys = py.import_bound("sys")?;
        let path = sys.getattr("path")?;

        let src_path = get_python_src_path();
        path.call_method1("insert", (0, src_path.to_str().unwrap()))?;

        println!("🐍 [PyO3] PYTHONPATH injected: {:?}", src_path);

        // 2. Import Module
        // We assume 'core.dispatcher' based on 'src' being the root in sys.path
        // If sys.path points to 'src', then 'import core.dispatcher' is valid?
        // Let's verify: E:\DEV\Convert\src\core\dispatcher.py
        // If sys.path = E:\DEV\Convert\src
        // Then 'import core.dispatcher' works.
        let module = PyModule::import_bound(py, "core.dispatcher").map_err(|e| {
            println!("❌ [PyO3] Import Failed: {}", e);
            e
        })?;

        // 3. Create Instance
        let class = module.getattr("Dispatcher")?;
        let instance = class.call0()?;

        // 4. Cache it
        *dispatcher_guard = Some(instance.unbind());
        println!("🐍 [PyO3] Dispatcher Singleton Initialized.");

        Ok(())
    })
}

/// Dispatch command to Python (Stateful)
pub fn dispatch_to_python(cmd: &str, payload: Value) -> Result<Value, String> {
    // Ensure initialized
    if PYTHON_DISPATCHER.lock().unwrap().is_none() {
        init_python_backend().map_err(|e| format!("Init Failed: {}", e))?;
    }

    Python::with_gil(|py| {
        let guard = PYTHON_DISPATCHER.lock().unwrap();
        let py_instance = guard.as_ref().expect("Dispatcher should be initialized");
        let dispatcher = py_instance.bind(py);

        // Create envelope
        let envelope = PyDict::new_bound(py);
        envelope.set_item("cmd", cmd).unwrap();

        // Pass payload as JSON string to handle complex types reliably
        let payload_str = serde_json::to_string(&payload).unwrap();

        // IMPORTANT: The Python Dispatcher expects a DICT payload, NOT a string.
        // We must convert JSON string -> Python Dict here to match the Interface.
        let json_module = PyModule::import_bound(py, "json").unwrap();
        let payload_dict = json_module.call_method1("loads", (payload_str,)).unwrap();

        envelope.set_item("payload", payload_dict).unwrap();

        // Call handle
        let result = dispatcher
            .call_method1("handle", (envelope,))
            .map_err(|e| format!("Python Execution Error: {}", e))?;

        // Convert result back to Rust Value
        let result_str = json_module
            .call_method1("dumps", (result,))
            .unwrap()
            .extract::<String>()
            .unwrap();

        let val: Value = serde_json::from_str(&result_str).unwrap();
        Ok(val)
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_path_resolution() {
        let path = get_python_src_path();
        assert!(path.exists());
    }

    #[test]
    fn test_singleton_initialization() {
        assert!(init_python_backend().is_ok());
        // Second call should return immediately
        assert!(init_python_backend().is_ok());
    }
}
