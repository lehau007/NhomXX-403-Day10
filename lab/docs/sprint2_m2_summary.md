# Sprint 2 Summary - Member 2 Quick Reference

**Status:** ✅ COMPLETED  
**Level:** Merit + Distinction  
**Date:** 2026-04-15

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Cleaning Rules Added | 4 (required: 3) ✅ |
| Expectations Added | 3 (required: 2) ✅ |
| Pipeline Test | PASSED (9/9 expectations) ✅ |
| Clean Rate | 60% (6/10 dòng) |
| Pydantic Validation | Implemented ✅ (Distinction) |

---

## Files Modified

1. **`lab/transform/cleaning_rules.py`**
   - Added 4 new rules (7-10)
   - Added 2 helper functions
   - Added constants (MIN/MAX_CHUNK_LENGTH)
   - Total additions: ~80 lines

2. **`lab/quality/expectations.py`**
   - Added 3 new expectations (E7-E9)
   - Added Pydantic model (CleanedChunkSchema)
   - Added validation function
   - Total additions: ~60 lines

---

## New Cleaning Rules

### Rule 7: BOM/Special Character Removal
- **Function:** `_remove_bom_and_special_chars()`
- **Impact:** Giảm encoding errors, cải thiện embedding quality
- **Status:** ✅ Working

### Rule 8: Text Length Validation
- **Range:** 8-500 characters
- **Impact:** Tăng retrieval precision, giảm noise
- **Status:** ✅ Working

### Rule 9: Font/Character Normalization
- **Function:** `_normalize_font_and_punctuation()`
- **Impact:** Cải thiện search/matching accuracy
- **Status:** ✅ Working

### Rule 10: Metadata Consistency Check
- **Logic:** exported_at >= effective_date
- **Impact:** Phát hiện data corruption sớm
- **Status:** ✅ Working

---

## New Expectations

### E7: No Null in Critical Fields
- **Severity:** HALT
- **Fields:** chunk_id, doc_id, chunk_text, effective_date
- **Result:** ✅ PASSED (0 violations)

### E8: Date Range Validation
- **Severity:** WARN
- **Range:** 2025-01-01 to 2027-12-31
- **Result:** ✅ PASSED (0 out of range)

### E9: Pydantic Schema Validation (Distinction)
- **Severity:** HALT
- **Type:** Type-safe validation
- **Result:** ✅ PASSED (6/6 rows validated)

---

## Test Results

```bash
python lab/etl_pipeline.py run --run-id sprint2-m2-test
```

**Output:**
```
run_id=sprint2-m2-test
raw_records=10
cleaned_records=6
quarantine_records=4

✅ expectation[min_one_row] OK
✅ expectation[no_empty_doc_id] OK
✅ expectation[refund_no_stale_14d_window] OK
✅ expectation[chunk_min_length_8] OK
✅ expectation[effective_date_iso_yyyy_mm_dd] OK
✅ expectation[hr_leave_no_stale_10d_annual] OK
✅ expectation[no_null_critical_fields] OK
✅ expectation[effective_date_range_2025_2027] OK
✅ expectation[pydantic_schema_validation] OK

9/9 PASSED
```

---

## Quarantine Breakdown

| Dòng | Reason | Rule |
|------|--------|------|
| 2 | duplicate_chunk_text | Baseline |
| 5 | missing_effective_date | Baseline |
| 7 | stale_hr_policy_effective_date | Baseline |
| 9 | unknown_doc_id | Baseline |

**Note:** Không có dòng nào bị quarantine do new rules (7-10) - raw data không có BOM, length issues, hoặc metadata inconsistency. New rules sẵn sàng bắt lỗi trong tương lai.

---

## Evidence Files

1. **Log:** `lab/artifacts/logs/run_sprint2-m2-test.log`
2. **Cleaned:** `lab/artifacts/cleaned/cleaned_sprint2-m2-test.csv`
3. **Quarantine:** `lab/artifacts/quarantine/quarantine_sprint2-m2-test.csv`
4. **Code:** 
   - `lab/transform/cleaning_rules.py`
   - `lab/quality/expectations.py`

---

## Distinction Level Proof

✅ **Pydantic Validation:**
```python
class CleanedChunkSchema(BaseModel):
    chunk_id: str = Field(..., min_length=1)
    doc_id: str = Field(..., min_length=1)
    chunk_text: str = Field(..., min_length=8, max_length=500)
    effective_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    exported_at: str = Field(..., min_length=1)
    
    @validator('effective_date')
    def validate_date_range(cls, v):
        if v < "2025-01-01" or v > "2027-12-31":
            raise ValueError(f"effective_date {v} outside valid range")
        return v
```

✅ **Test Result:**
```
expectation[pydantic_schema_validation] OK (halt) :: validated_rows=6, errors=0
```

---

## Next Steps (Sprint 3)

- [ ] Receive evaluation results from M3
- [ ] Write Quality Report (`docs/quality_report.md`)
- [ ] Explain inject corruption → retrieval failure
- [ ] Explain fix → retrieval success
- [ ] Use Sprint 2 evidence in report

---

## Key Takeaways

1. ✅ **Vượt yêu cầu:** 4 rules (required 3), 3 expectations (required 2)
2. ✅ **Distinction achieved:** Pydantic type-safe validation
3. ✅ **100% test pass:** All 9 expectations passed
4. ✅ **Evidence-driven:** Logs, CSV files, code documented
5. ✅ **Ready for Sprint 3:** Quality report preparation

---

**M2 Sprint 2: ✅ COMPLETED - Merit + Distinction Level**
