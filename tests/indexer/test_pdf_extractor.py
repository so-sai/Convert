"""
PDF Extractor Tests - TDD GREEN Phase
Task 6.4 Extraction Pipeline

Tests T24.01-T24.05 for PDF extraction using PyMuPDF.
"""

import pytest
from pathlib import Path
import time

# Try to import PyMuPDF for test data creation
try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


@pytest.fixture
def sample_pdf(tmp_path):
    """Create a valid multi-page PDF for testing"""
    if not PYMUPDF_AVAILABLE:
        pytest.skip("PyMuPDF not available")
    
    pdf_path = tmp_path / "test.pdf"
    
    # Create a simple PDF with 3 pages
    doc = fitz.open()
    
    # Page 1
    page1 = doc.new_page()
    page1.insert_text((72, 72), "Page 1: Introduction\n\nThis is a test document.")
    
    # Page 2
    page2 = doc.new_page()
    page2.insert_text((72, 72), "Page 2: Content\n\nThis page has some content.")
    
    # Page 3
    page3 = doc.new_page()
    page3.insert_text((72, 72), "Page 3: Conclusion\n\nThe end.")
    
    # Set metadata
    doc.set_metadata({
        "title": "Test Document",
        "author": "Test Author",
        "subject": "Testing",
    })
    
    doc.save(str(pdf_path))
    doc.close()
    
    return pdf_path


@pytest.fixture
def corrupted_pdf(tmp_path):
    """Create a corrupted PDF file"""
    pdf_path = tmp_path / "corrupted.pdf"
    # Write invalid PDF data
    pdf_path.write_bytes(b"%PDF-1.4\n%corrupted data that is not valid")
    return pdf_path


@pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF not installed")
def test_T24_01_basic_pdf_extraction(sample_pdf):
    """T24.01: Extract text from valid multi-page PDF"""
    from src.core.indexer.extractors.pdf_extractor import extract_pdf
    
    result = extract_pdf(sample_pdf)
    
    # Should extract all 3 pages
    assert len(result.segments) == 3, f"Expected 3 segments, got {len(result.segments)}"
    
    # Check page numbers
    assert result.segments[0].page == 1
    assert result.segments[1].page == 2
    assert result.segments[2].page == 3
    
    # Check text content
    assert "Introduction" in result.segments[0].text
    assert "Content" in result.segments[1].text
    assert "Conclusion" in result.segments[2].text
    
    # Should have no errors
    assert len(result.errors) == 0
    assert result.success
    assert not result.truncated
    
    # Should have processing time
    assert result.processing_time_ms > 0
    
    print(f"\n   ✅ T24.01: Extracted {len(result.segments)} pages in {result.processing_time_ms:.2f}ms")


@pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF not installed")
def test_T24_02_metadata_extraction(sample_pdf):
    """T24.02: Extract metadata from PDF"""
    from src.core.indexer.extractors.pdf_extractor import extract_pdf
    
    result = extract_pdf(sample_pdf)
    
    # Check metadata
    assert "page_count" in result.metadata
    assert result.metadata["page_count"] == 3
    
    assert "title" in result.metadata
    assert result.metadata["title"] == "Test Document"
    
    assert "author" in result.metadata
    assert result.metadata["author"] == "Test Author"
    
    print(f"\n   ✅ T24.02: Metadata extracted: {result.metadata}")


@pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF not installed")
def test_T24_03_corrupted_pdf_handling(corrupted_pdf):
    """T24.03: Handle corrupted PDF gracefully"""
    from src.core.indexer.extractors.pdf_extractor import extract_pdf
    
    result = extract_pdf(corrupted_pdf)
    
    # Should have errors
    assert len(result.errors) > 0
    assert not result.success
    
    # Error should indicate corruption
    assert any("corrupt" in err.message.lower() or "invalid" in err.message.lower() 
               for err in result.errors)
    
    # Should not crash, should return result
    assert result is not None
    
    print(f"\n   ✅ T24.03: Corrupted PDF handled gracefully: {result.errors[0].message}")


@pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF not installed")
def test_T24_04_performance_benchmark(sample_pdf):
    """T24.04: Verify extraction performance < 50ms P95"""
    from src.core.indexer.extractors.pdf_extractor import extract_pdf
    
    times = []
    for _ in range(100):
        start = time.perf_counter()
        result = extract_pdf(sample_pdf)
        elapsed_ms = (time.perf_counter() - start) * 1000
        times.append(elapsed_ms)
        
        # Sanity check
        assert result.success
    
    times.sort()
    p50 = times[49]  # Median
    p95 = times[94]  # 95th percentile
    p99 = times[98]  # 99th percentile
    
    print(f"\n   📊 T24.04 Performance:")
    print(f"      P50: {p50:.2f}ms")
    print(f"      P95: {p95:.2f}ms")
    print(f"      P99: {p99:.2f}ms")
    
    assert p95 < 50.0, f"P95 latency {p95:.2f}ms exceeds 50ms target"
    print(f"   ✅ T24.04: P95 latency = {p95:.2f}ms (target: <50ms)")


@pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF not installed")
def test_T24_05_file_not_found_handling(tmp_path):
    """T24.05: Handle missing file gracefully"""
    from src.core.indexer.extractors.pdf_extractor import extract_pdf
    
    nonexistent = tmp_path / "does_not_exist.pdf"
    
    result = extract_pdf(nonexistent)
    
    # Should have error
    assert len(result.errors) > 0
    assert not result.success
    
    # Error should indicate file not found
    assert any("not found" in err.message.lower() for err in result.errors)
    
    print(f"\n   ✅ T24.05: Missing file handled gracefully")


@pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF not installed")
def test_T24_06_empty_pdf_handling(tmp_path):
    """T24.06: Handle PDF with no text content"""
    pdf_path = tmp_path / "empty.pdf"
    
    # Create PDF with blank page
    doc = fitz.open()
    doc.new_page()  # Blank page
    doc.save(str(pdf_path))
    doc.close()
    
    from src.core.indexer.extractors.pdf_extractor import extract_pdf
    
    result = extract_pdf(pdf_path)
    
    # Should succeed but have no segments (blank page)
    assert result.success
    assert len(result.segments) == 0
    assert result.metadata["page_count"] == 1
    
    print(f"\n   ✅ T24.06: Empty PDF handled correctly")
