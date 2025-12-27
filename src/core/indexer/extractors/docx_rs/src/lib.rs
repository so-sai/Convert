//! DOCX Extractor - Rust Native Implementation
//! Task 6.4 - Sprint 6 Background Services
//!
//! Uses docx-rs for high-performance DOCX text extraction.
//! Exposes to Python via PyO3 bindings.

use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::fs::File;
use std::io::Read;
use std::time::Instant;

/// Text segment with metadata
#[pyclass]
#[derive(Clone)]
struct TextSegment {
    #[pyo3(get)]
    text: String,
    #[pyo3(get)]
    page: Option<i32>,
    #[pyo3(get)]
    section: Option<String>,
    #[pyo3(get)]
    confidence: f64,
}

#[pymethods]
impl TextSegment {
    #[new]
    #[pyo3(signature = (text, page=None, section=None, confidence=1.0))]
    fn new(text: String, page: Option<i32>, section: Option<String>, confidence: f64) -> Self {
        TextSegment {
            text,
            page,
            section,
            confidence,
        }
    }
}

/// Extraction error details
#[pyclass]
#[derive(Clone)]
struct ExtractionError {
    #[pyo3(get)]
    code: String,
    #[pyo3(get)]
    message: String,
    #[pyo3(get)]
    recoverable: bool,
}

#[pymethods]
impl ExtractionError {
    #[new]
    fn new(code: String, message: String, recoverable: bool) -> Self {
        ExtractionError {
            code,
            message,
            recoverable,
        }
    }
}

/// Extraction result
#[pyclass]
struct ExtractionResult {
    #[pyo3(get)]
    segments: Vec<TextSegment>,
    #[pyo3(get)]
    metadata: Py<PyDict>,
    #[pyo3(get)]
    processing_time_ms: f64,
    #[pyo3(get)]
    file_size_bytes: i64,
    #[pyo3(get)]
    errors: Vec<ExtractionError>,
    #[pyo3(get)]
    truncated: bool,
    #[pyo3(get)]
    extractor: String,
    #[pyo3(get)]
    version: String,
}

/// Extract text from DOCX file
///
/// Args:
///     file_path: Path to DOCX file
///
/// Returns:
///     ExtractionResult with text segments and metadata
#[pyfunction]
fn extract_docx(py: Python, file_path: String) -> PyResult<ExtractionResult> {
    let start_time = Instant::now();

    // Get file size
    let file_size = match std::fs::metadata(&file_path) {
        Ok(metadata) => metadata.len() as i64,
        Err(_) => 0,
    };

    // Create metadata dict
    let metadata = PyDict::new(py);

    // Try to read file
    let mut file = match File::open(&file_path) {
        Ok(f) => f,
        Err(e) => {
            // File not found or permission denied
            let error = ExtractionError::new(
                "FILE_NOT_FOUND".to_string(),
                format!("Failed to open file: {}", e),
                false,
            );

            return Ok(ExtractionResult {
                segments: vec![],
                metadata: metadata.unbind(),
                processing_time_ms: start_time.elapsed().as_secs_f64() * 1000.0,
                file_size_bytes: file_size,
                errors: vec![error],
                truncated: false,
                extractor: "docx_rust".to_string(),
                version: "1.0.0".to_string(),
            });
        }
    };

    // Read file content
    let mut buffer = Vec::new();
    if let Err(e) = file.read_to_end(&mut buffer) {
        let error = ExtractionError::new(
            "READ_ERROR".to_string(),
            format!("Failed to read file: {}", e),
            false,
        );

        return Ok(ExtractionResult {
            segments: vec![],
            metadata: metadata.unbind(),
            processing_time_ms: start_time.elapsed().as_secs_f64() * 1000.0,
            file_size_bytes: file_size,
            errors: vec![error],
            truncated: false,
            extractor: "docx_rust".to_string(),
            version: "1.0.0".to_string(),
        });
    }

    // Parse DOCX
    let docx = match docx_rs::read_docx(&buffer) {
        Ok(d) => d,
        Err(e) => {
            let error = ExtractionError::new(
                "CORRUPTED".to_string(),
                format!("Failed to parse DOCX: {}", e),
                false,
            );

            return Ok(ExtractionResult {
                segments: vec![],
                metadata: metadata.unbind(),
                processing_time_ms: start_time.elapsed().as_secs_f64() * 1000.0,
                file_size_bytes: file_size,
                errors: vec![error],
                truncated: false,
                extractor: "docx_rust".to_string(),
                version: "1.0.0".to_string(),
            });
        }
    };

    // Extract text from document
    let mut segments = Vec::new();
    let mut errors = Vec::new();

    // Extract paragraphs
    for (idx, child) in docx.document.children.iter().enumerate() {
        match child {
            docx_rs::DocumentChild::Paragraph(para) => {
                let mut para_text = String::new();

                for run_child in &para.children {
                    if let docx_rs::ParagraphChild::Run(run) = run_child {
                        for run_child in &run.children {
                            if let docx_rs::RunChild::Text(text) = run_child {
                                para_text.push_str(&text.text);
                            }
                        }
                    }
                }

                // Only add non-empty paragraphs
                if !para_text.trim().is_empty() {
                    segments.push(TextSegment::new(
                        para_text,
                        None,
                        Some(format!("paragraph_{}", idx)),
                        1.0,
                    ));
                }
            }
            docx_rs::DocumentChild::Table(table) => {
                // Extract text from tables
                let mut table_text = String::new();

                for row in &table.rows {
                    for cell in &row.cells {
                        for cell_child in &cell.children {
                            if let docx_rs::TableCellContent::Paragraph(para) = cell_child {
                                for run_child in &para.children {
                                    if let docx_rs::ParagraphChild::Run(run) = run_child {
                                        for run_child in &run.children {
                                            if let docx_rs::RunChild::Text(text) = run_child {
                                                table_text.push_str(&text.text);
                                                table_text.push(' ');
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        table_text.push('\t'); // Tab between cells
                    }
                    table_text.push('\n'); // Newline between rows
                }

                if !table_text.trim().is_empty() {
                    segments.push(TextSegment::new(
                        table_text,
                        None,
                        Some(format!("table_{}", idx)),
                        1.0,
                    ));
                }
            }
            _ => {
                // Other document children (bookmarks, etc.) - skip for now
            }
        }
    }

    // Add metadata
    if let Err(e) = metadata.set_item("paragraph_count", segments.len()) {
        eprintln!("Failed to set metadata: {}", e);
    }

    let processing_time = start_time.elapsed().as_secs_f64() * 1000.0;

    Ok(ExtractionResult {
        segments,
        metadata: metadata.unbind(),
        processing_time_ms: processing_time,
        file_size_bytes: file_size,
        errors,
        truncated: false,
        extractor: "docx_rust".to_string(),
        version: "1.0.0".to_string(),
    })
}

/// Python module definition
#[pymodule]
fn docx_extractor(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_docx, m)?)?;
    m.add_class::<TextSegment>()?;
    m.add_class::<ExtractionError>()?;
    m.add_class::<ExtractionResult>()?;
    Ok(())
}
