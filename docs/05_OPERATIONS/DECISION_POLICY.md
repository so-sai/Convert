# Decision Policy v1.0

**Status**: Active  
**Effective Date**: Sprint 1 (November 2025)  
**Review Cycle**: Every Sprint milestone  
**Owner**: Technical Manager (Gemini 3.0 Pro)

---

## 1. Purpose

This policy governs **what decisions** should be recorded as Memory Events and **when** they should be recorded, ensuring the Memory Stream remains valuable without becoming noisy.

---

## 2. Core Principle

> "Not every decision is worth remembering, but forgetting the right decisions is fatal."

Record decisions that have **lasting architectural impact**, not transient implementation details.

---

## 3. Recording Criteria

A decision **MUST** be recorded if it meets **ANY** of the following criteria:

### ✅ Criterion 1: Affects an Architectural Contract

**Definition**: Changes or creates a schema, API specification, or interface contract.

**Examples:**
- ✅ "Switch from WebSocket to SSE for event streaming"
- ✅ "Add `notes` field to MemoryPayload schema"
- ❌ "Rename variable `user_id` to `userId`" (no contract change)

**Why Record:** Contracts define system boundaries and must be traceable.

---

### ✅ Criterion 2: Introduces a New Dependency

**Definition**: Adds a library, framework, tool, or external service.

**Examples:**
- ✅ "Choose llama-cpp-python over transformers for local AI"
- ✅ "Add Scrypt for key derivation (new crypto dependency)"
- ❌ "Update pytest from 7.4.0 to 7.4.1" (patch update)

**Why Record:** Dependencies have security, maintenance, and licensing implications.

---

### ✅ Criterion 3: Resolves a Significant Trade-off

**Definition**: Makes a deliberate choice between competing concerns with lasting impact.

**Examples:**
- ✅ "Accept 4-hour setup cost for Triple-Stream to gain long-term auditability"
- ✅ "Use 12-char hex IDs (not full UUID) for storage efficiency"
- ❌ "Use List comprehension instead of for-loop" (micro-optimization)

**Why Record:** Trade-offs reveal system priorities and prevent repeated debates.

---

### ✅ Criterion 4: Sets a Precedent

**Definition**: Establishes a pattern, convention, or principle for future decisions.

**Examples:**
- ✅ "Always use `WITHOUT ROWID` for TEXT primary keys in SQLite"
- ✅ "Prefix all event IDs with type indicator (evt-, mem-, etc.)"
- ❌ "Format this specific SQL query with line breaks" (one-off style)

**Why Record:** Precedents create consistency and guide future development.

---

## 4. Non-Recording Criteria

**DO NOT** record Memory Events for:

### ❌ Routine Implementation Details
- Variable naming choices
- Code formatting decisions
- Minor refactorings without architectural impact
- Obvious choices with no alternatives

### ❌ Temporary Workarounds
- Planned refactorings with clear tech debt tickets
- Short-term fixes pending proper solution
- Experimental code marked for cleanup

### ❌ Trivial Bug Fixes
- Typo corrections
- Null pointer fixes
- Off-by-one errors
- Unless the bug reveals a design flaw

### ❌ Standard Practices
- Using Python for a Python project
- Following REST conventions for REST APIs
- Applying common design patterns (Factory, Strategy, etc.)

---

## 5. Decision Record Quality Standards

All recorded decisions must include:

### 📝 Rationale (Required)

**Format:** Minimum 20 characters, plain English

**Must Answer:**
- What problem does this solve?
- Why is this approach chosen?
- What constraints influenced the choice?

**Good Example:**
```
"Chose SQLite over PostgreSQL because offline-first principle 
requires zero-config database, and our data model fits 
single-user schema well."
```

**Bad Examples:**
- ❌ "Because it's better" (too vague)
- ❌ "Using library X" (no context)
- ❌ "Picked the fastest option" (no constraints mentioned)

---

### 🔀 Alternatives (Required)

**Format:** List of at least 1 considered alternative

**Must Include:**
- Name of alternative approach
- Why it was considered
- Why it was rejected (optional but recommended)

**Good Example:**
```
alternatives:
  - "PostgreSQL (more features but requires server)"
  - "DuckDB (columnar but less mature ecosystem)"
```

**Bad Examples:**
- ❌ `alternatives: []` (empty list)
- ❌ `alternatives: ["other options"]` (too vague)

---

### 📊 Impact Assessment (Required)

**Format:** Must be `low`, `medium`, or `high`

**Classification Guide:**
- **Low**: Affects 1-2 modules, easy to change later
- **Medium**: Affects multiple modules, moderate effort to change
- **High**: Affects core architecture, expensive to change

**Examples:**
- High: Choosing event sourcing pattern
- Medium: Selecting FTS5 over FTS4 for search
- Low: Choosing variable naming convention

---

### 🎯 Decision Framework (Required)

**Format:** List of at least 1 principle or criterion used

**Must Include:**
- Principles that guided the decision
- Priorities that influenced trade-offs
- Rules that constrained choices

**Good Example:**
```
decision_framework:
  - "offline-first principle"
  - "minimize-deployment-complexity"
  - "performance > features for MVP"
```

**Bad Examples:**
- ❌ `decision_framework: []` (empty)
- ❌ `decision_framework: ["best practice"]` (too generic)

---

### 📌 Notes (Optional)

**Format:** Free-form text, max 1000 characters

**Use For:**
- Future considerations
- Edge cases to watch
- Related decisions to revisit
- Implementation warnings

**Example:**
```
notes: "Will revisit if multi-user sync needed in v2.0. 
        Monitor SQLite 3.9.0+ requirement for FTS5."
```

---

## 6. Helper Method Usage

Use `MemoryBridge.should_record()` to check if a decision warrants recording:
```python
bridge = MemoryBridge(event_bus)

# Quick check before detailed recording
if bridge.should_record("Switching from FTS4 to FTS5"):
    decision = DecisionRecord(
        component="NoteService",
        category="implementation",
        rationale="...",
        alternatives=["FTS4", "External Elasticsearch"],
        impact="medium",
        decision_framework=["unicode-correctness", "offline-first"]
    )
    bridge.record_decision(decision)
```

**Keywords Detected:**
- architecture, contract, interface
- dependency, library, framework
- trade-off, vs, instead of
- pattern, convention, policy

---

## 7. Enforcement Mechanisms

### 🔧 Pre-commit Hook (Planned for Sprint 2)
- Warns if PR touches `src/core/schemas/` without decision record
- Checks for orphaned TODO comments referencing decisions

### 👁️ Code Review Checklist
Reviewers must verify:
- [ ] Architectural changes have corresponding decision record
- [ ] Decision meets quality standards (rationale, alternatives, etc.)
- [ ] Decision follows this policy's criteria

### 📊 Retrospective Analysis
- **Monthly**: Review Memory Stream for decision patterns/gaps
- **Per-Sprint**: Analyze decision velocity and quality trends
- **Quarterly**: Update policy based on learnings

---

## 8. Governance & Updates

### Policy Updates
- **Minor changes** (clarifications, examples): Technical Manager approval
- **Major changes** (new criteria, removal of criteria): Team consensus required
- **Emergency updates**: Security Architect can fast-track

### Audit Trail
All policy changes must be:
1. Documented in git commit with rationale
2. Announced in team channel with 48-hour notice
3. Reflected in updated version number

### Violation Handling
- **First violation**: Reminder + education (not punitive)
- **Repeated violations**: 1-on-1 discussion to understand friction
- **Systemic violations**: Policy is too strict, needs revision

---

## 9. Examples

### ✅ Should Record

**Example 1: Architectural Change**
```yaml
component: "EventBus"
category: "architectural"
rationale: "Switch from WebSocket to SSE because SSE is simpler for 
           unidirectional event streaming and has better browser support"
alternatives: ["WebSocket (bidirectional but overkill)", 
               "Long-polling (inefficient)"]
impact: "medium"
decision_framework: ["simplicity > features", "browser-compatibility"]
```

**Example 2: Dependency Introduction**
```yaml
component: "SearchEngine"
category: "implementation"
rationale: "Use FTS5 over FTS4 for better Unicode support, critical for 
           Vietnamese language correctness"
alternatives: ["FTS4 (simpler but limited Unicode)", 
               "External Elasticsearch (powerful but offline-incompatible)"]
impact: "medium"
decision_framework: ["unicode-correctness", "offline-first"]
```

**Example 3: Significant Trade-off**
```yaml
component: "SecurityLayer"
category: "implementation"
rationale: "Accept Scrypt N=2^20 (~1sec delay) for brute-force resistance, 
           trading UX smoothness for security"
alternatives: ["PBKDF2 (faster but weaker)", 
               "Argon2 (strongest but not in stdlib)"]
impact: "high"
decision_framework: ["security > convenience", "stdlib-only for MVP"]
notes: "May add Argon2 in v1.1 if user complaints about unlock delay"
```

---

### ❌ Should NOT Record

**Example 1: Trivial Naming**
```python
# ❌ Don't record
user_id = request.get("userId")  # vs userId = request.get("userId")
```

**Example 2: Obvious Choice**
```python
# ❌ Don't record
import json  # Obviously use stdlib json, no decision needed
```

**Example 3: Temporary Fix**
```python
# ❌ Don't record (has TODO)
# TODO: Replace with proper cache implementation in Sprint 3
temp_cache = {}
```

---

## 10. Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-20 | Initial release for Sprint 1 | System Architect |

---

## 11. Related Documents

- [DEC-ARCH-001: Triple-Stream Event Sourcing](../decisions/DEC-ARCH-001.yaml)
- [Memory Event Schema v0.1](../schemas/memory_events.yaml)
- [CONTEXT_PACKAGE_v2.2_Final.md](../architecture/CONTEXT_PACKAGE_v2.2_Final.md)

---

**Questions?** Contact: Technical Manager (Gemini 3.0 Pro)
