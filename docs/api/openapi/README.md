# CONVERT - Private Cognitive Environment

**Version**: 0.1.0-sprint1  
**Status**: Sprint 1 Foundation Complete  
**Architecture**: Triple-Stream Event Sourcing with Self-Aware Memory

## Vision

Kiến tạo một Môi trường Nhận thức Riêng tư, nơi tri thức của bạn được sở hữu bởi bạn, được khuếch đại bởi AI chạy cục bộ, và được kết nối bởi một dòng chảy thời gian thông minh.

## Core Principles

1. **Data Sovereignty** - .md files as ground truth
2. **Offline-First** - Core features work without internet
3. **Event Sourcing** - Perfect memory & auditability
4. **Progressive Complexity** - UI evolves with user
5. **Hardware-Aware** - Adaptive performance
6. **Security-by-Design** - Zero-trust architecture

## Sprint 1: The Aware Foundation ✅

### Completed Deliverables

- ✅ Triple-Stream Event Bus architecture
- ✅ Event Schemas (Domain, Interaction, Memory)
- ✅ Memory Bridge interface for decision recording
- ✅ Pydantic validation with security guarantees
- ✅ REST API specification (OpenAPI 3.0.3)
- ✅ Decision Policy & governance framework
- ✅ Comprehensive test suite (7 tests, 100% coverage)

## Development Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/unit/test_events.py -v

# Expected output: 7 passed