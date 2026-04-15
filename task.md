# Task List - Lab Day 10: Data Pipeline & Data Observability

## 0. Preparation & Setup
- [ ] Create virtual environment: `python -m venv .venv`
- [ ] Activate virtual environment: `.venv\Scripts\activate` (Windows)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Setup environment variables: `cp .env.example .env` and configure it.
- [ ] Verify baseline run: `python etl_pipeline.py run` (ensure it downloads the model and runs successfully).

## 1. Sprint 1: Ingestion & Schema (60')
- [ ] **Data Source:** Read `data/raw/policy_export_dirty.csv` (or add custom raw data).
- [ ] **Documentation:** Fill in the source map in `docs/data_contract.md`.
    - [ ] At least 2 sources.
    - [ ] Define failure modes and metrics for each.
- [ ] **Execution:** Run `python etl_pipeline.py run --run-id sprint1`.
- [ ] **Validation (DoD):** Ensure logs and manifests contain `raw_records`, `cleaned_records`, `quarantine_records`, and `run_id`.

## 2. Sprint 2: Transformation, Quality & Embedding (60')
- [ ] **Transformation:** Extend `transform/cleaning_rules.py` with **≥ 3 new rules**.
    - [ ] Rules must have impact (documented in `metric_impact` table in `reports/group_report.md`).
- [ ] **Quality:** Extend `quality/expectations.py` with **≥ 2 new expectations**.
    - [ ] Differentiate between `warn` and `halt` severity.
- [ ] **Embedding:** Ensure idempotent embedding.
    - [ ] Verify `chunk_id` stability.
    - [ ] Verify pruning of removed IDs (baseline feature).
- [ ] **Execution:** Run `python etl_pipeline.py run` (should exit 0 with expectations passing).
- [ ] **Validation (DoD):** Verify logs for `embed_prune_removed` and consistent vector counts.

## 3. Sprint 3: Corruption Injection & Evaluation (60')
- [ ] **Injection:** Intentionally corrupt data or use flags like `--no-refund-fix --skip-validate`.
- [ ] **Execution (Bad Run):** `python etl_pipeline.py run --run-id inject-bad --no-refund-fix --skip-validate`.
- [ ] **Evaluation:**
    - [ ] Run evaluation: `python eval_retrieval.py --out artifacts/eval/after_inject_bad.csv`.
    - [ ] Compare with clean run results (Before/After evidence).
- [ ] **Reporting:** Complete `docs/quality_report.md` (interpreting the results and linking to `run_id`).
- [ ] **Validation (DoD):** Provide clear evidence (logs/CSV) that retrieval is better after the fix.

## 4. Sprint 4: Monitoring, Documentation & Reporting (60')
- [ ] **Monitoring:** Run freshness check: `python etl_pipeline.py freshness --manifest artifacts/manifests/manifest_<run-id>.json`.
- [ ] **Documentation:** Finalize all mandatory docs:
    - [ ] `docs/pipeline_architecture.md` (include diagram/ASCII/Mermaid).
    - [ ] `docs/data_contract.md` (Schema, Owner, SLA).
    - [ ] `docs/runbook.md` (Symptom → Detection → Diagnosis → Mitigation → Prevention).
- [ ] **Reporting:**
    - [ ] Complete `reports/group_report.md` (include Peer Review feedback from slide Part E).
    - [ ] Complete individual reports in `reports/individual/[name].md` (400-650 words).
- [ ] **Final README:** Ensure `README.md` has a single command to run the entire pipeline.

## 5. Final Submission & Grading
- [ ] **Grading Run:** Run `python grading_run.py --out artifacts/eval/grading_run.jsonl` (usually after 17:00).
- [ ] **Sanity Check:** Use `python instructor_quick_check.py` to verify `grading_run.jsonl` and manifests.
- [ ] **Submission:** Commit all required files by 18:00 deadline.
    - [ ] `.py` files, `contracts/*.yaml`
    - [ ] `artifacts/eval/grading_run.jsonl`, CSV eval, `artifacts/manifests/*.json`
    - [ ] `docs/*.md`
    - [ ] `reports/*.md`

## Extra Goals (Merit / Distinction)
- [ ] **Merit:** Ensure `gq_d10_03` passes perfectly (contains expected, no forbidden, top-1 matches).
- [ ] **Distinction:** Implement one "beyond baseline" feature:
    - [ ] (a) Real GE or Pydantic validation on cleaned schema.
    - [ ] (b) Freshness measurement at 2 boundaries (ingest + publish).
    - [ ] (c) Extended evaluation (LLM-judge or ≥5 question slice).
    - [ ] (d) Non-hardcoded versioning rules (reading cutoff from contract/env).
