# Sprint 2 Completion Checklist - Nhóm 3 Người

**Sprint:** 2 - Cleaning, Expectations & Embed  
**Ngày hoàn thành:** 2026-04-15  
**Status:** ✅ COMPLETED

---

## 1. Member 2 (M2) - Data Quality Engineer

### Nhiệm vụ Sprint 2:
- [x] Implement ≥3 cleaning rules mới
- [x] Implement ≥2 expectations mới
- [x] Test pipeline với rules mới
- [x] Document metric impact
- [x] (Distinction) Implement Pydantic validation

### Deliverables:
- ✅ **4 Cleaning Rules** (vượt yêu cầu 3):
  1. BOM/Special Character Removal
  2. Text Length Validation (8-500 chars)
  3. Font/Character Normalization
  4. Metadata Consistency Check
  
- ✅ **3 Expectations** (vượt yêu cầu 2):
  1. No Null in Critical Fields (HALT)
  2. Date Range Validation (WARN)
  3. Pydantic Schema Validation (HALT) - **Distinction**

- ✅ **Test Results:**
  - 9/9 expectations PASSED
  - 60% clean rate (6/10 dòng)
  - 4 dòng quarantine với reasons rõ ràng

- ✅ **Documentation:**
  - `lab/docs/m2_sprint2_implementation.md`
  - `lab/docs/sprint2_m2_summary.md`

### Status: ✅ COMPLETED - Merit + Distinction

---

## 2. Member 3 (M3) - AI/Embed Engineer

### Nhiệm vụ Sprint 2:
- [x] Implement idempotent embedding
- [x] Test upsert behavior (chạy 2 lần)
- [x] Test prune logic
- [x] Verify embedding model load
- [x] Test retrieval quality

### Deliverables:
- ✅ **Idempotency Test:**
  - Run 1: 6 vectors, prune 1 old
  - Run 2: 6 vectors, no prune
  - Conclusion: ✅ Idempotent

- ✅ **Prune Logic:**
  - Verified: Removed 1 old vector
  - Strategy: Snapshot (vector store = cleaned data)

- ✅ **Embedding Model:**
  - Model: all-MiniLM-L6-v2
  - Dimension: 384
  - Status: ✅ Loaded successfully

- ✅ **Retrieval Quality:**
  - Test: 4 queries
  - Result: 3/4 PASSED (75%)
  - Threshold: >70% ✅

- ✅ **Documentation:**
  - `lab/docs/m3_sprint2_implementation.md`
  - `lab/docs/sprint2_m3_summary.md`
  - `lab/test_retrieval_m3.py`

### Status: ✅ COMPLETED - Merit

---

## 3. Member 1 (M1) - Data Engineer (Support Role)

### Nhiệm vụ Sprint 2:
- [x] Hỗ trợ M2 & M3 test pipeline
- [x] Theo dõi logs
- [x] Verify artifacts generated correctly

### Deliverables:
- ✅ Pipeline runs successful (2 test runs)
- ✅ Logs collected:
  - `run_sprint2-m2-test.log`
  - `run_sprint2-m3-test1.log`
  - `run_sprint2-m3-test2.log`
- ✅ Artifacts verified:
  - Cleaned CSV (6 rows)
  - Quarantine CSV (4 rows)
  - Manifests (complete metadata)

### Status: ✅ COMPLETED - Support

---

## 4. Team Coordination (Sprint 2)

### Cross-team Integration:
- ✅ M2 → M3: Cleaned data quality excellent
  - No BOM, normalized text
  - Optimal chunk length (8-500)
  - All expectations passed

- ✅ M3 → M2: Embedding feedback
  - Cleaning rules working well
  - 75% retrieval accuracy
  - Suggestion: Consider multilingual model

- ✅ M1 → M2 & M3: Log format confirmed
  - run_id, raw_records, cleaned_records
  - embed_upsert_count, embed_prune_removed
  - expectation results

### Shared Understanding:
- ✅ Pipeline flow: Raw → Clean → Validate → Embed
- ✅ Idempotency: Chạy lại an toàn, không duplicate
- ✅ Prune: Xóa vectors cũ không còn trong cleaned
- ✅ Quality: 60% clean rate, 9/9 expectations passed

---

## 5. Sprint 2 Metrics

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| M2: Cleaning Rules | ≥3 | 4 | ✅ Vượt |
| M2: Expectations | ≥2 | 3 | ✅ Vượt |
| M2: Pydantic Validation | Optional | Yes | ✅ Distinction |
| M2: Test Pass Rate | 100% | 100% | ✅ Perfect |
| M3: Idempotency | Yes | Yes | ✅ Confirmed |
| M3: Prune Logic | Working | Working | ✅ Verified |
| M3: Retrieval Accuracy | >70% | 75% | ✅ Pass |
| Pipeline Integration | Seamless | Seamless | ✅ Success |

---

## 6. Evidence Summary

### M2 Evidence:
- ✅ Code: `lab/transform/cleaning_rules.py` (4 rules)
- ✅ Code: `lab/quality/expectations.py` (3 expectations)
- ✅ Log: `run_sprint2-m2-test.log` (9/9 passed)
- ✅ CSV: `cleaned_sprint2-m2-test.csv` (6 rows)
- ✅ CSV: `quarantine_sprint2-m2-test.csv` (4 rows)

### M3 Evidence:
- ✅ Log: `run_sprint2-m3-test1.log` (prune 1, upsert 6)
- ✅ Log: `run_sprint2-m3-test2.log` (upsert 6, no prune)
- ✅ Manifest: `manifest_sprint2-m3-test1.json`
- ✅ Test script: `test_retrieval_m3.py`
- ✅ Test result: 75% accuracy (3/4 queries)

---

## 7. Risks Identified & Mitigations

| Risk | Owner | Mitigation | Status |
|------|-------|------------|--------|
| Pydantic v2 API changes | M2 | Updated to use `pattern` instead of `regex` | ✅ Resolved |
| Model not optimal for Vietnamese | M3 | 75% accuracy acceptable for Merit | ✅ Acceptable |
| Freshness check failing | M1 | Expected (data 5 days old) | ✅ Not a bug |
| Retrieval quality < 70% | M3 | Achieved 75%, above threshold | ✅ Pass |

---

## 8. Ready for Sprint 3?

### M1 Readiness: ✅ READY
- Pipeline stable
- Logs format confirmed
- Ready to support Sprint 3 (inject corruption)

### M2 Readiness: ✅ READY
- Cleaning rules working
- Expectations all passing
- Ready to write Quality Report (Sprint 3)
- Evidence collected for report

### M3 Readiness: ✅ READY
- Idempotent embedding working
- Retrieval test script ready
- Baseline quality established (75%)
- Ready for inject corruption test (Sprint 3)

---

## 9. Sprint 3 Preview

### M1 (Ingestion & Ops):
- Run inject corruption test (`--no-refund-fix --skip-validate`)
- Collect logs for before/after comparison
- Support M2 & M3 with evidence

### M2 (Quality):
- Receive evaluation results from M3
- Write Quality Report (`docs/quality_report.md`)
- Explain inject corruption → retrieval failure
- Explain fix → retrieval success
- Use Sprint 2 evidence in report

### M3 (Embed):
- Run evaluation before inject (baseline)
- Run evaluation after inject (corrupted)
- Run evaluation after fix (clean)
- Compare retrieval quality across 3 scenarios
- Document findings for M2's report

---

## 10. Level Achievement Summary

### M2 (Data Quality Engineer):
**Level:** Merit + Distinction ✅
- ✅ 4 cleaning rules (required 3)
- ✅ 3 expectations (required 2)
- ✅ Pydantic validation (Distinction)
- ✅ 100% test pass rate
- ✅ Evidence-driven documentation

### M3 (AI/Embed Engineer):
**Level:** Merit ✅ (Distinction opportunities in Sprint 3)
- ✅ Idempotency confirmed
- ✅ Prune logic working
- ✅ 75% retrieval accuracy (>70% threshold)
- ✅ Pipeline integration seamless
- ⏳ Distinction: Multilingual model (Sprint 3)

### Team Overall:
**Level:** Merit ✅ (on track for Distinction)
- ✅ All Sprint 2 requirements met
- ✅ Evidence comprehensive
- ✅ Code quality high
- ✅ Documentation complete

---

## 11. Key Achievements

1. ✅ **M2 vượt yêu cầu:** 4 rules (not 3), 3 expectations (not 2)
2. ✅ **M2 Distinction:** Pydantic type-safe validation
3. ✅ **M3 Idempotency:** Verified with 2 runs, stable at 6 vectors
4. ✅ **M3 Prune:** Working correctly (removed 1 old vector)
5. ✅ **Pipeline seamless:** Cleaning → Validation → Embedding
6. ✅ **Quality high:** 9/9 expectations passed, 75% retrieval accuracy
7. ✅ **Evidence complete:** Logs, CSV, manifests, test scripts

---

## 12. Next Steps

1. **Kick-off Sprint 3 meeting:**
   - Review Sprint 2 achievements
   - Plan inject corruption test
   - Agree on evaluation metrics

2. **M3 runs inject test:**
   - Baseline: Normal run (clean)
   - Inject: `--no-refund-fix --skip-validate`
   - After fix: Normal run again

3. **M3 evaluates retrieval:**
   - Compare accuracy: baseline vs inject vs after fix
   - Document findings

4. **M2 writes Quality Report:**
   - Use M3's evaluation results
   - Explain why inject → fail, fix → success
   - Use Sprint 2 evidence

5. **M1 supports:**
   - Collect logs for all 3 scenarios
   - Verify artifacts generated
   - Help with evidence extraction

---

**Sprint 2 Status: ✅ COMPLETED**  
**Team Readiness: ✅ ALL MEMBERS READY FOR SPRINT 3**  
**Next Sprint: Sprint 3 - Inject Corruption & Before/After**  
**Level Achieved: Merit (M2 + M3), on track for Distinction**
