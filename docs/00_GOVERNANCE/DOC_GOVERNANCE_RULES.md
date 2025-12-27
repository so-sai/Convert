# 📜 DOCUMENTATION GOVERNANCE RULES v1.0

**Status:** ACTIVE  
**Effective Date:** 2025-12-27  
**Owner:** Chief Architect  
**Scope:** All documentation in `docs/` directory

---

## 🎯 CORE PRINCIPLES

### 1. SPEC as Artifact
- Each Task has its own SPEC document
- SPECs are **frozen after approval** (not after implementation)
- SPECs are versioned by task completion, not by file edits
- SPECs serve as **immutable contracts** for that task's scope

### 2. Single Source of Truth (SST)
- Each type of information has **exactly one authoritative source**
- All other documents **reference** the SST, never duplicate it
- Changes to a topic require updating only the SST

### 3. Reference, Don't Repeat
- Use explicit references: `"See SPEC 6.4 §3.2"` or `"Per ADL-015"`
- Link to source documents instead of copying content
- Summarize only when necessary, always with source attribution

### 4. Version by Task, Not by File
- SPEC versions align with task milestones (e.g., `SPEC_TASK_6_4_v2.0`)
- File edits within a task don't increment version
- Major version change = new task or significant scope change

---

## 📊 SST MAPPING

| Information Type              | Source of Truth                    | Reference Style              |
|-------------------------------|------------------------------------|-----------------------------|
| **Technical Requirements**    | `SPEC_TASK_X_X.md`                | `"See SPEC 6.4 §3.2"`       |
| **Architecture Decisions**    | `ARCHITECTURE_DECISIONS.md`       | `"Per ADL-015"`             |
| **Tech Stack & Comparisons**  | `TECHNOLOGY_MATRIX.md`            | `"Ref: TM2025/DOCX"`        |
| **Timeline & Evolution**      | `MDS_v3.14_Pi.md`                 | `"As per MDS §2025-12"`     |
| **API Contracts**             | `SPEC_TASK_X_X.md` (relevant)     | `"Contract: SPEC 6.4 §4.1"` |
| **Test Definitions**          | `SPEC_TASK_X_X.md` (test section) | `"Tests: SPEC 6.4 §5"`      |

---

## 🚫 ANTI-DRIFT RULE

**If a SPEC is FROZEN, any behavior change requires:**

1. **New SPEC** (for next task), OR
2. **Explicit AMENDMENT** section with:
   - Date of amendment
   - Rationale for change
   - Impact analysis
   - Link to original frozen section

**Amendment Format:**
```markdown
## AMENDMENT_20251227

**Original Frozen Section:** §3.2 (Extraction Result Contract)  
**Change:** Added `file_hash` field to result schema  
**Rationale:** Required for deduplication in Sprint 7  
**Impact:** Non-breaking addition, backward compatible  
**Approved By:** Chief Architect  
```

---

## 🔄 REVIEW CYCLE

### Post-Sprint Consolidation
- **When:** After each sprint completion
- **What:** Remove duplication, verify SST alignment
- **Checklist:**
  - [ ] No content duplicated between SPECs
  - [ ] ADL entries reference SPECs, don't repeat details
  - [ ] MDS contains narrative only, no spec details
  - [ ] TECHNOLOGY_MATRIX contains facts only, no rationale

### Monthly SST Alignment Check
- **When:** First week of each month
- **What:** Verify all references are valid and up-to-date
- **Action:** Update broken links, consolidate orphaned content

### Quarterly Governance Review
- **When:** End of each quarter
- **What:** Review and update governance rules based on lessons learned
- **Action:** Update this document if needed

---

## 📝 DOCUMENT TYPE DEFINITIONS

### SPEC (Specification)
- **Purpose:** Technical contract for a specific task
- **Lifecycle:** Created → Reviewed → Frozen → Implemented → Archived
- **Frozen When:** After approval, before implementation starts
- **Content:** Requirements, contracts, test definitions, acceptance criteria
- **Mutation:** Only via AMENDMENT section after freeze

### ADL (Architecture Decision Log)
- **Purpose:** Record of architectural choices and rationale
- **Lifecycle:** Living document, entries added but rarely modified
- **Content:** Decision, context, alternatives considered, consequences
- **Mutation:** New entries added; existing entries marked SUPERSEDED if needed

### MDS (Master Design Specification)
- **Purpose:** High-level narrative and timeline
- **Lifecycle:** Living document, updated with major milestones
- **Content:** Vision, roadmap, evolution story, strategic context
- **Mutation:** Continuous updates, narrative-focused

### TECHNOLOGY_MATRIX
- **Purpose:** Factual comparison of technology choices
- **Lifecycle:** Living document, updated when new tech is evaluated
- **Content:** Features, performance metrics, compatibility, versions
- **Mutation:** Add new rows/columns; update facts when verified

---

## ✅ COMPLIANCE CHECKLIST

Use this checklist when creating or updating documentation:

- [ ] **SST Identified:** Is this the authoritative source for this information?
- [ ] **No Duplication:** Have I checked that this content doesn't exist elsewhere?
- [ ] **References Used:** Have I linked to SST instead of copying?
- [ ] **SPEC Frozen:** If this is a SPEC, is it frozen after approval?
- [ ] **Amendment Protocol:** If changing frozen content, did I use AMENDMENT section?
- [ ] **Version Correct:** Does the version reflect task milestone, not file edits?

---

## 🎓 EXAMPLES

### ❌ BAD: Duplication
**In SPEC_TASK_6_4.md:**
> We chose Rust for DOCX extraction because it provides native performance, memory safety, and parallel processing capabilities.

**In ARCHITECTURE_DECISIONS.md:**
> ADL-015: Use Rust for DOCX extraction. Rationale: Native performance, memory safety, parallel processing.

**Problem:** Same rationale in two places. If we discover new reasons, we'd need to update both.

### ✅ GOOD: Reference
**In SPEC_TASK_6_4.md:**
> DOCX extraction uses Rust-native bindings (per ADL-015).

**In ARCHITECTURE_DECISIONS.md:**
> **ADL-015:** Rust Native DOCX Extraction  
> **Status:** ACTIVE — LOCKED BY SPEC_TASK_6_4_EXTRACTION.md  
> **Decision:** Use docx-rs (Rust) via PyO3 bindings  
> **Rationale:** Native performance (3-5x faster), memory safety (no GIL), parallel processing support  
> **Alternatives Considered:** python-docx (rejected: GIL bottleneck), unoconv (rejected: LibreOffice dependency)  
> **Consequences:** Requires Rust toolchain, PyO3 ≥0.23, maturin build pipeline

---

## 🔒 GOVERNANCE ENFORCEMENT

### Who Can Freeze a SPEC?
- Chief Architect (primary authority)
- Tech Lead (with Chief Architect approval)

### Who Can Amend a Frozen SPEC?
- Chief Architect (direct authority)
- Tech Lead (with documented rationale and Chief Architect review)

### Who Can Update Living Documents (ADL, MDS, TECH_MATRIX)?
- Any team member (with peer review)
- Changes must follow SST principles

---

## 📌 VERSION HISTORY

| Version | Date       | Changes                          | Author           |
|---------|------------|----------------------------------|------------------|
| v1.0    | 2025-12-27 | Initial governance rules created | Chief Architect  |

---

**Next Review:** 2026-01-27 (Monthly SST Alignment Check)
