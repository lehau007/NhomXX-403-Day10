# Sprint 3 Summary - Member 3 Quick Reference

**Status:** ✅ COMPLETED  
**Level:** Merit + Evidence for Distinction  
**Date:** 2026-04-15

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Scenarios Tested | 3 (Baseline, Inject Bad, After Fix) |
| Questions Evaluated | 4 per scenario (12 total) |
| Baseline Quality | 100% (0/4 hits forbidden) |
| Inject Bad Quality | 75% (1/4 hits forbidden) ❌ |
| After Fix Quality | 100% (0/4 hits forbidden) ✅ |
| Corruption Detected | Yes (expectation failed) |
| Fix Verified | Yes (prune + re-embed) |

---

## Test Scenarios

### Scenario 1: Baseline (Clean) ✅
```bash
python etl_pipeline.py run --run-id sprint3-baseline
python eval_retrieval.py --out artifacts/eval/eval_baseline.csv
```

**Result:**
- ✅ 9/9 expectations PASSED
- ✅ 6 vectors embedded
- ✅ 4/4 questions: `hits_forbidden=no`
- ✅ **100% quality**

---

### Scenario 2: Inject Bad (Corrupted) ❌
```bash
python etl_pipeline.py run --run-id sprint3-inject-bad --no-refund-fix --skip-validate
python eval_retrieval.py --out artifacts/eval/eval_inject_bad.csv
```

**Result:**
- ❌ `refund_no_stale_14d_window] FAIL (halt) :: violations=1`
- ⚠️ Skipped validation (intentional for demo)
- ❌ 1/4 questions: `hits_forbidden=yes` (q_refund_window)
- ❌ **75% quality** (25% corrupted)

**Key Finding:** Stale chunk "14 ngày làm việc" embedded → wrong info retrieved

---

### Scenario 3: After Fix (Clean Again) ✅
```bash
python etl_pipeline.py run --run-id sprint3-after-fix
python eval_retrieval.py --out artifacts/eval/eval_after_fix.csv
```

**Result:**
- ✅ 9/9 expectations PASSED
- ✅ `embed_prune_removed=1` (removed corrupted chunk)
- ✅ 4/4 questions: `hits_forbidden=no`
- ✅ **100% quality** (restored)

---

## Comparison Table

| Metric | Baseline | Inject Bad | After Fix |
|--------|----------|------------|-----------|
| Expectations Passed | 9/9 | 8/9 | 9/9 |
| Vectors Embedded | 6 | 6 | 6 |
| Contains Expected | 4/4 | 4/4 | 4/4 |
| **Hits Forbidden** | **0/4** ✅ | **1/4** ❌ | **0/4** ✅ |
| **Quality Score** | **100%** | **75%** | **100%** |

---

## Key Findings

### Finding 1: Expectation Caught Corruption ✅
```
expectation[refund_no_stale_14d_window] FAIL (halt) :: violations=1
```
- ✅ Detected stale refund window (14 ngày)
- ✅ Would halt pipeline (if not `--skip-validate`)

### Finding 2: Corruption Propagated to Retrieval ❌
```
q_refund_window: hits_forbidden=yes
```
- ❌ Query retrieved chunk with "14 ngày làm việc"
- ❌ User receives wrong information (14 days instead of 7)

### Finding 3: Fix Restored Quality ✅
```
embed_prune_removed=1
q_refund_window: hits_forbidden=no
```
- ✅ Prune removed corrupted chunk
- ✅ Clean chunk embedded
- ✅ Query no longer hits forbidden content

---

## Question-by-Question Analysis

### q_refund_window (Refund Policy) 🔍

| Scenario | Hits Forbidden | Status |
|----------|----------------|--------|
| Baseline | no | ✅ Clean |
| Inject Bad | **yes** | ❌ Corrupted |
| After Fix | no | ✅ Clean |

**Impact:** 
- Inject Bad: User gets wrong refund window (14 days vs 7 days)
- After Fix: User gets correct information

---

### q_p1_sla, q_lockout, q_leave_version ✅

| Scenario | Hits Forbidden | Status |
|----------|----------------|--------|
| All 3 scenarios | no | ✅ Clean |

**Impact:** Not affected by refund corruption (isolated issue)

---

## Evidence Files

### Logs:
- `lab/artifacts/logs/run_sprint3-baseline.log`
- `lab/artifacts/logs/run_sprint3-inject-bad.log`
- `lab/artifacts/logs/run_sprint3-after-fix.log`

### Evaluations:
- `lab/artifacts/eval/eval_baseline.csv`
- `lab/artifacts/eval/eval_inject_bad.csv`
- `lab/artifacts/eval/eval_after_fix.csv`

### Cleaned Data:
- `lab/artifacts/cleaned/cleaned_sprint3-baseline.csv`
- `lab/artifacts/cleaned/cleaned_sprint3-inject-bad.csv`
- `lab/artifacts/cleaned/cleaned_sprint3-after-fix.csv`

---

## Key Insights for M2's Quality Report

### 1. Expectations Work ✅
**Evidence:** `refund_no_stale_14d_window] FAIL` caught corruption  
**Message:** "Quality gates prevent bad data from reaching users"

### 2. Data Quality Impacts Retrieval ❌
**Evidence:** 25% corruption rate (1/4 questions)  
**Message:** "Bad data → wrong information → user dissatisfaction"

### 3. Cleaning Rules Prevent Issues ✅
**Evidence:** Baseline & After Fix both 100% clean  
**Message:** "Cleaning rules + expectations = 100% quality"

### 4. Prune Removes Corruption ✅
**Evidence:** `embed_prune_removed=1` in After Fix  
**Message:** "Idempotent pipeline self-heals from corruption"

---

## Metrics for Report

### Quality Degradation (Inject Bad):
- **Before:** 100% clean (Baseline)
- **After Inject:** 75% clean (25% corrupted)
- **Impact:** 1 in 4 users receive wrong information

### Quality Restoration (After Fix):
- **Before Fix:** 75% clean
- **After Fix:** 100% clean
- **Recovery:** Full restoration (prune + re-embed)

---

## Recommendations for M2

### Visualize Impact:
```
Baseline:    [✅✅✅✅] 100% clean
Inject Bad:  [✅✅✅❌] 75% clean (1 corrupted)
After Fix:   [✅✅✅✅] 100% clean (restored)
```

### Emphasize Business Value:
- **Without pipeline:** 25% wrong information
- **With pipeline:** 0% wrong information
- **Value:** Compliance + user satisfaction

### Highlight Technical Excellence:
- Expectations catch issues early
- Cleaning rules fix known problems
- Prune removes stale data
- Idempotent design enables self-healing

---

## Sprint 3 Achievements

✅ **3 scenarios tested:** Baseline, Inject Bad, After Fix  
✅ **12 evaluations completed:** 4 questions x 3 scenarios  
✅ **Corruption demonstrated:** 25% quality degradation  
✅ **Fix verified:** 100% quality restoration  
✅ **Evidence comprehensive:** Logs, CSV, manifests  
✅ **Insights documented:** Ready for M2's Quality Report

---

## Next Steps

### For M2 (Quality Report):
- [ ] Use evaluation CSVs as evidence
- [ ] Explain why inject → fail (stale chunk embedded)
- [ ] Explain why fix → success (prune + clean chunk)
- [ ] Quantify business impact (25% → 0% corruption)
- [ ] Highlight pipeline value (expectations + cleaning + prune)

### For M1 (Monitoring):
- [ ] Review freshness check results
- [ ] Prepare for Sprint 4 monitoring tasks

---

## Key Takeaways

1. ✅ **Expectations work:** Caught corruption before it should reach users
2. ❌ **Corruption impacts retrieval:** 25% wrong information (1/4 questions)
3. ✅ **Fix restores quality:** Prune + re-embed → 100% clean
4. ✅ **Evidence comprehensive:** 3 scenarios, 12 evaluations, full logs
5. ✅ **Ready for Quality Report:** M2 has all evidence needed

---

**M3 Sprint 3: ✅ COMPLETED - Merit + Distinction Evidence**
