# Sprint 1 Completion Checklist - Nhóm 3 Người

**Sprint:** 1 - Setup, Ingestion & Schema  
**Ngày hoàn thành:** 2026-04-15  
**Status:** ✅ COMPLETED

---

## 1. Member 1 (M1) - Data Engineer (Ingestion & Ops)

### Nhiệm vụ Sprint 1:
- [x] Setup môi trường ảo (`.venv`)
- [x] Install thư viện từ `requirements.txt`
- [x] Review file `data/raw/policy_export_dirty.csv`
- [x] Verify `etl_pipeline.py` ingest logic
- [x] Điền phần Source Map vào `docs/data_contract.md`

### Deliverables:
- ✅ Environment setup hoàn tất
- ✅ Raw data reviewed (9 dòng, nhiều lỗi)
- ✅ Source map documented trong `data_contract.md`

### Notes:
- Raw file có 9 dòng data với 6 loại lỗi khác nhau
- Pipeline ingest đọc được file và log `raw_records=9`
- Cần coordinate với M2 về quarantine reasons

---

## 2. Member 2 (M2) - Data Quality Engineer

### Nhiệm vụ Sprint 1:
- [x] Phân tích các loại "rác" trong dữ liệu raw
- [x] Identify failure modes (duplicate, empty, stale, invalid format)
- [x] Document findings cho Sprint 2

### Deliverables:
- ✅ **Tài liệu phân tích:** `lab/docs/m2_sprint1_analysis.md`
- ✅ **6 loại lỗi đã phát hiện:**
  1. Duplicate records (11.1%)
  2. Empty data (11.1%)
  3. Invalid date format (11.1%)
  4. Stale HR policy (11.1%)
  5. Stale refund window (11.1%)
  6. Unknown doc_id (11.1%)
- ✅ **Kế hoạch Sprint 2:** 3+ cleaning rules, 2+ expectations

### Key Findings:
- Chỉ 33.3% data clean (3/9 dòng)
- Cần implement BOM removal, length validation, font normalization
- Cần thêm null check và date range validation expectations

---

## 3. Member 3 (M3) - AI/Embed Engineer

### Nhiệm vụ Sprint 1:
- [x] Review `contracts/data_contract.yaml`
- [x] Điền thông tin Owner, SLA, Embedding config
- [x] Document idempotency strategy
- [x] Prepare cho Sprint 2 embedding implementation

### Deliverables:
- ✅ **Data contract updated:** `lab/contracts/data_contract.yaml`
  - Owner information
  - Embedding configuration (model, vector store, idempotency)
  - Data lineage (upstream/downstream)
  - SLA & monitoring metrics
  - Freshness measurement points (3 stages)
- ✅ **Tài liệu phân tích:** `lab/docs/m3_sprint1_analysis.md`
- ✅ **Test plan cho Sprint 2:** Idempotency, prune, retrieval tests

### Key Updates:
- Embedding model: all-MiniLM-L6-v2 (384 dims)
- chunk_id strategy: SHA256 hash-based
- Prune strategy: snapshot (xóa vectors cũ không còn trong cleaned)
- Freshness SLA: 24 hours (3 measurement points)

---

## 4. Team Coordination (Sprint 1)

### Documents Created:
1. ✅ `lab/docs/m2_sprint1_analysis.md` - M2 data quality analysis
2. ✅ `lab/docs/m3_sprint1_analysis.md` - M3 embedding & contract analysis
3. ✅ `lab/contracts/data_contract.yaml` - Updated with full details
4. ✅ `lab/docs/sprint1_completion_checklist.md` - This file

### Cross-team Dependencies Identified:
- **M1 → M2:** Log format, run_id convention
- **M1 → M3:** run_id format, metadata structure
- **M2 → M3:** Chunk_text quality (BOM, special chars)
- **M3 → M2:** chunk_id format, idempotency guarantee

### Shared Understanding:
- ✅ Raw data có 6 loại lỗi chính
- ✅ Expected clean rate: ~33-44% (3-4/9 dòng)
- ✅ Quarantine strategy: 5-6 dòng sẽ bị quarantine
- ✅ Idempotency: Dựa vào stable chunk_id (hash-based)
- ✅ Prune: Xóa vectors cũ không còn trong cleaned

---

## 5. Sprint 1 Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Raw records analyzed | 9 | ✅ |
| Error types identified | 6 | ✅ |
| Expected clean rate | 33.3% | ⚠️ Low (expected) |
| Documents created | 4 | ✅ |
| Data contract completeness | 100% | ✅ |
| Team coordination meetings | 1 | ✅ |

---

## 6. Risks Identified & Mitigations

| Risk | Owner | Mitigation | Status |
|------|-------|------------|--------|
| Low clean rate (33%) | M2 | Implement robust cleaning rules | ⏳ Sprint 2 |
| Embedding model load failure | M3 | Verify dependencies installed | ⏳ Sprint 2 |
| chunk_id collision | M3 | Use SHA256 (collision ~10^-19) | ✅ Low risk |
| Quarantine approval process unclear | M2 | Document in data_contract.md | ✅ Done |
| Freshness SLA breach | M1 | Implement monitoring in Sprint 4 | ⏳ Sprint 4 |

---

## 7. Ready for Sprint 2?

### M1 Readiness: ✅ READY
- Environment setup complete
- Ingest logic verified
- Ready to support M2 & M3 testing

### M2 Readiness: ✅ READY
- Error analysis complete
- Cleaning rules plan ready (3+ rules)
- Expectations plan ready (2+ rules)
- Ready to implement in Sprint 2

### M3 Readiness: ✅ READY
- Data contract complete
- Idempotency strategy documented
- Test plan ready (idempotency, prune, retrieval)
- Ready to implement embedding in Sprint 2

---

## 8. Sprint 2 Preview

### M1 (Ingestion & Ops):
- Hỗ trợ M2 test cleaning rules
- Theo dõi logs, trích xuất evidence
- Chuẩn bị cho monitoring (Sprint 4)

### M2 (Quality):
- **Implement 3+ cleaning rules:**
  1. BOM/special character removal
  2. Text length validation (min/max)
  3. Font/character normalization
  4. (Bonus) Metadata consistency check
- **Implement 2+ expectations:**
  1. No null in critical fields
  2. Date range validation
  3. (Distinction) Pydantic schema validation

### M3 (Embed):
- Implement idempotent embedding
- Test upsert behavior (run 2x, verify no duplicate)
- Test prune logic (remove chunks, verify vectors deleted)
- Verify embedding model load & vector dimensions

---

## 9. Evidence for Report (Sprint 1)

### M2 Evidence:
- ✅ Raw data analysis table (6 error types)
- ✅ Statistics: 33.3% clean, 66.7% errors
- ✅ Quarantine reasons mapping table

### M3 Evidence:
- ✅ Data contract YAML snippet (embedding section)
- ✅ chunk_id generation code snippet
- ✅ Prune logic code snippet

### Team Evidence:
- ✅ Sprint 1 completion checklist (this document)
- ✅ Cross-team coordination notes

---

## 10. Next Steps

1. **Kick-off Sprint 2 meeting:**
   - Review Sprint 1 deliverables
   - Sync on implementation approach
   - Agree on testing strategy

2. **M2 starts implementation:**
   - Create branch: `feature/cleaning-rules`
   - Implement 3+ rules in `transform/cleaning_rules.py`
   - Implement 2+ expectations in `quality/expectations.py`

3. **M3 starts implementation:**
   - Create branch: `feature/idempotent-embedding`
   - Test embedding flow
   - Verify idempotency & prune logic

4. **M1 supports testing:**
   - Run pipeline with M2's new rules
   - Collect logs for evidence
   - Verify quarantine files generated correctly

---

**Sprint 1 Status: ✅ COMPLETED**  
**Team Readiness: ✅ ALL MEMBERS READY FOR SPRINT 2**  
**Next Sprint: Sprint 2 - Cleaning, Expectations & Embed**
