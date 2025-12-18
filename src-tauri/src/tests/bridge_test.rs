//! Rust integration tests for PyO3 bridge.
//!
//! RED PHASE: These tests verify MDS v3.14 compliance (no subprocess, embedded Python only).

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyModule};

#[test]
fn test_python_interpreter_initializes() {
    // GIVEN: Rust application starts
    // WHEN: We attempt to initialize Python interpreter
    // THEN: Python should initialize successfully without spawning subprocess

    Python::with_gil(|py| {
        // If we get here, Python interpreter is embedded successfully
        let version = py.version_info();
        assert!(version.major >= 3);
        println!(
            "Python {}.{} initialized successfully",
            version.major, version.minor
        );
    });
}

#[test]
fn test_can_import_sys_module() {
    // GIVEN: Python interpreter is initialized
    // WHEN: We attempt to import sys module
    // THEN: Import should succeed (basic sanity check)

    Python::with_gil(|py| {
        let sys = py.import_bound("sys");
        assert!(sys.is_ok(), "Failed to import sys module");
    });
}

#[test]
fn test_can_add_to_python_path() {
    // GIVEN: Python interpreter is initialized
    // WHEN: We add a directory to sys.path
    // THEN: The path should be added successfully

    Python::with_gil(|py| {
        let sys = py.import_bound("sys").expect("Failed to import sys");
        let path = sys.getattr("path").expect("Failed to get path");

        // Add test path
        let result = path.call_method1("insert", (0, "C:\\Test"));
        assert!(result.is_ok(), "Failed to insert path");
    });
}

#[test]
fn test_can_create_python_dict() {
    // GIVEN: Python interpreter is initialized
    // WHEN: We create a Python dictionary from Rust
    // THEN: Dictionary should be created with correct data

    Python::with_gil(|py| {
        let dict = PyDict::new_bound(py);
        dict.set_item("cmd", "backup.start")
            .expect("Failed to set cmd");

        let payload = PyDict::new_bound(py);
        payload
            .set_item("target_dir", "C:\\Test")
            .expect("Failed to set target_dir");
        dict.set_item("payload", payload)
            .expect("Failed to set payload");

        // Verify
        let cmd = dict.get_item("cmd").expect("Failed to get cmd");
        assert!(cmd.is_some());
    });
}
