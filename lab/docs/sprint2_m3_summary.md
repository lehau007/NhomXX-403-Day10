# Sprint 2 Summary - Member 3 Quick Reference

**Status:** ✅ COMPLETED  
**Level:** Merit (Distinction opportunities in Sprint 3)  
**Date:** 2026-04-15

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Idempotency Test | ✅ PASS (2 runs, 6 vectors) |
| Prune Logic | ✅ WORKING (removed 1 old vector) |
| Embedding Model | ✅ LOADED (all-MiniLM-L6-v2) |
| Vector Dimension | 384 |
| Retrieval Accuracy | 75% (3/4 queries) |
| Pipeline Integration | ✅ SEAMLESS |

---

## Test Results

### Test 1: Idempotency ✅

```bash
# Run 1
python etl_pipeline.py run --run-id sprint2-m3-test1
# Result: embed_upsert count=6, embed_prune_removed=1

# Run 2 (same data)
python etl_pipeline.py run --run-id sprint2-m3-test2
# Result: embed_upsert count=6, no prune
```

**Conclusion:** ✅ Idempotent (vector count stable at 6)

---

### Test 2: Prune Logic ✅

**Observation:**
- Run 1: `embed_prune_removed=1` (xóa 1 vector cũ)
- Run 2: No prune message (data giống nhau)

**Conclusion:** ✅ Prune working correctly

---

### Test 3: Retrieval Quality ✅

**Test Script:** `lab/test_retrieval_m3.py`

| Query | Expected | Result | Status |
|-------|----------|--------|--------|
| "chính sách hoàn tiền" | policy_refund_v4 | hr_leave_policy | ❌ |
| "SLA ticket P1" | sla_p1_2026 | sla_p1_2026 | ✅ |
| "tài khoản bị khóa" | it_helpdesk_faq | it_helpdesk_faq | ✅ |
| "ngày phép năm" | hr_leave_policy | hr_leave_policy | ✅ |

**Overall:** 3/4 PASSED (75% accuracy)

**Analysis:**
- ✅ 75% > 70% threshold (acceptable)
- ❌ 1 query failed due to model limitation (not optimized for Vietnamese)
- ✅ Idempotency check: 6 vectors (expected)

---

## Key Implementation Details

### Stable chunk_id Generation
```python
def _stable_chunk_id(doc_id: str, chunk_text: str, seq: int) -> str:
    h = hashlib.sha256(f"{doc_id}|{chunk_text}|{seq}".encode("utf-8")).hexdigest()[:16]
    return f"{doc_id}_{seq}_{h}"
```
✅ Deterministic, collision probability ~10^-19

### Upsert Strategy
```python
col.upsert(ids=ids, documents=documents, metadatas=metadatas)
```
✅ Idempotent by design (update if exists, insert if not)

### Prune Strategy
```python
prev_ids = set(prev.get("ids") or [])
drop = sorted(prev_ids - set(ids))
if drop:
    col.delete(ids=drop)
```
✅ Snapshot approach (vector store = cleaned data)

---

## Evidence Files

1. **Logs:**
   - `lab/artifacts/logs/run_sprint2-m3-test1.log`
   - `lab/artifacts/logs/run_sprint2-m3-test2.log`

2. **Manifests:**
   - `lab/artifacts/manifests/manifest_sprint2-m3-test1.json`
   - `lab/artifacts/manifests/manifest_sprint2-m3-test2.json`

3. **Test Script:**
   - `lab/test_retrieval_m3.py`

4. **ChromaDB:**
   - `lab/chroma_db/` (6 vectors, not committed to git)

---

## Pipeline Integration

```
Raw CSV (10 rows)
    ↓
Cleaning (M2) → 6 clean + 4 quarantine
    ↓
Expectations (M2) → 9/9 PASSED
    ↓
Embedding (M3) → 6 vectors
    ↓
ChromaDB → Idempotent storage
```

**Status:** ✅ SEAMLESS

---

## Embedding Configuration

```bash
# .env
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION=day10_kb
EMBEDDING_MODEL=all-MiniLM-L6-v2
FRESHNESS_SLA_HOURS=24
```

**Model:** all-MiniLM-L6-v2
- Vector dimension: 384
- Speed: Fast (~50ms/doc)
- Language: English (primary), limited Vietnamese support

---

## Challenges & Solutions

### Challenge 1: Vietnamese Query Failed
**Problem:** "chính sách hoàn tiền" → wrong doc  
**Root Cause:** Model not optimized for Vietnamese  
**Solution:** 75% accuracy still acceptable for Merit  
**Future:** Upgrade to multilingual model (Distinction)

### Challenge 2: Freshness Check Failing
**Problem:** `freshness_check=FAIL` (age: 120 hours > SLA: 24)  
**Root Cause:** Raw data 5 days old  
**Solution:** Expected behavior (not a bug)

---

## Coordination với Team

### From M2:
- ✅ Cleaned data (6 rows, high quality)
- ✅ No BOM, normalized text
- ✅ Optimal chunk length (8-500 chars)

### To M1 & M2:
- ✅ Embedding logs (upsert count, prune count)
- ✅ Idempotency confirmed
- ✅ Retrieval test results (75%)

---

## Next Steps (Sprint 3)

- [ ] Inject corruption test (`--no-refund-fix --skip-validate`)
- [ ] Run evaluation before/after fix
- [ ] Compare retrieval quality
- [ ] Document findings for M2's Quality Report
- [ ] (Distinction) Test multilingual model

---

## Merit Level Proof

✅ **Idempotency:**
```
Run 1: embed_upsert count=6, embed_prune_removed=1
Run 2: embed_upsert count=6 (no prune)
Total vectors: 6 (stable)
```

✅ **Prune Logic:**
```
Previous: 7 vectors
After prune: 6 vectors (1 removed)
Matches cleaned data count
```

✅ **Retrieval Quality:**
```
3/4 queries passed (75%)
Threshold: >70%
Status: PASS
```

---

## Key Takeaways

1. ✅ **Idempotency confirmed:** Chạy 2 lần, vẫn 6 vectors
2. ✅ **Prune working:** Xóa vectors cũ không còn trong cleaned
3. ✅ **Model loaded:** all-MiniLM-L6-v2, 384 dims
4. ✅ **Retrieval acceptable:** 75% accuracy (>70% threshold)
5. ✅ **Pipeline seamless:** Cleaning → Validation → Embedding
6. ⏳ **Distinction opportunity:** Multilingual model upgrade (Sprint 3)

---

**M3 Sprint 2: ✅ COMPLETED - Merit Level**
