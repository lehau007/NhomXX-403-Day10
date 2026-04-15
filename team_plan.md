# Kế hoạch thực hiện Lab 10 - Nhóm 3 người

Tài liệu này cung cấp kế hoạch chi tiết, phân công nhiệm vụ, tech stack và quy chuẩn output cho nhóm 3 người nhằm hoàn thành Lab 10 đạt tối thiểu mức **Merit** (mục tiêu **Distinction** nếu hoàn thành tốt các mục tiêu mở rộng).

---

## 1. Phân công vai trò (3 Thành viên)

| Thành viên | Vai trò | Trách nhiệm chính |
|---|---|---|
| **Member 1 (M1)** | Data Engineer (Ingestion & Ops) | Ingestion pipeline, Data contract (sources), Monitoring (freshness), Final Integration (run bash). |
| **Member 2 (M2)** | Data Quality Engineer | Cleaning rules, Expectations, Quarantine logic, Data Contract (schema), Quality Report. |
| **Member 3 (M3)** | AI/Embed Engineer | Idempotent Embedding (Chroma), Retrieval Evaluation, Inject Corruption, Runbook, Architecture Docs. |

---

## 2. Tech Stack & Công cụ

*   **Ngôn ngữ:** Python 3.9+
*   **Môi trường:** `venv`, các dependency quản lý qua `requirements.txt`.
*   **Data Processing:** Cấu trúc dữ liệu Python tiêu chuẩn (Dict, List) hoặc `pandas` (nếu cần xử lý phức tạp).
*   **Vector Database:** `chromadb` (Local, lưu tại `day10/lab/artifacts/...` nhưng KHÔNG commit DB).
*   **Embedding Model:** Google api `gemini-embedding-2`. (Dùng google.genai python client).
*   **Validation (Tùy chọn cho Distinction):** `pydantic` (khuyên dùng để validate schema thật) hoặc `great_expectations`.
*   **Document format:** Markdown (`.md`), YAML (`.yaml`), JSON (`.jsonl` cho grading).

---

## 3. Quy định Format của Output (DoD - Definition of Done)

### 3.1. Source Code (`.py`)
*   **Logging:** Mọi script chạy phải log ra console có chứa `run_id`.
*   **Idempotency:** Code có thể chạy lại nhiều lần an toàn, không sinh rác hoặc duplicate data.
*   **Comment & Docstrings:** Bắt buộc có docstring cho các rule (`cleaning_rules.py`) và expectation (`expectations.py`) do nhóm tự thêm. Ghi rõ mục đích rule đó chặn lỗi gì.

### 3.2. Data Artifacts (Thư mục `artifacts/`)
*   **Manifest (`manifest_<run-id>.json`):** Chứa metadata của đợt chạy (số dòng raw, clean, thời gian, trạng thái pipeline).
*   **Quarantine (`quarantine_<run-id>.csv`):** Các dòng bị loại bỏ (do lỗi nghiệp vụ hoặc định dạng) phải nằm ở đây, không được drop im lặng.
*   **Eval (`eval/*.csv`):** Ghi rõ scenario đánh giá (ví dụ: `before_fix`, `after_fix`, `inject_bad`).

### 3.3. Documents & Reports (`docs/`, `reports/`)
*   **Format Markdown:** Tuân thủ template mẫu. Sử dụng bảng, checklist và highlight code block khi cần.
*   **Bằng chứng (Evidence-driven):** Mọi claim trong Report (chất lượng cải thiện, fix thành công) BẮT BUỘC kèm theo ảnh chụp màn hình log, hoặc trích dẫn vài dòng CSV/JSON.
*   **Tên file:** Tuân thủ đúng cấu trúc thư mục yêu cầu (`group_report.md`, thư mục `individual/tên_thành_viên.md`).

---

## 4. Kế hoạch Chi tiết theo Sprint

### Sprint 1: Setup, Ingestion & Schema (M1 dẫn dắt)
*   **M1 (Ingestion):**
    *   Setup môi trường ảo (`.venv`), cấp quyền và install thư viện.
    *   Review file `data/raw/policy_export_dirty.csv`.
    *   Chỉnh sửa `etl_pipeline.py` (nếu cần) để đảm bảo bước ingest đọc file tạo ra đúng chuẩn log gồm `raw_records`.
    *   Điền phần Source Map vào `docs/data_contract.md`.
*   **M2 (Quality - Chuẩn bị):** 
    *   Phân tích các loại "rác" trong dữ liệu raw (ngày sai format, duplicate, version cũ).
*   **M3 (Embed - Chuẩn bị):**
    *   Review `contracts/data_contract.yaml`, điền các thông tin Owner, SLA.

### Sprint 2: Cleaning, Expectations & Embed (M2 & M3 dẫn dắt)
*   **M2 (Cleaning & Validation):**
    *   Mở rộng `transform/cleaning_rules.py` (Thêm ≥ 3 rule mới: ví dụ chuẩn hóa font chữ, check độ dài policy, filter rác BOM). Đẩy các dòng lỗi vào quarantine.
    *   Mở rộng `quality/expectations.py` (Thêm ≥ 2 rules: ví dụ check format Date, check không có null quan trọng). Đảm bảo phân loại được Mức độ (Warn vs Halt).
    *   *(Distinction)*: Cài đặt Pydantic Model để validate thay vì dùng if/else thường.
*   **M3 (Embedding):**
    *   Đảm bảo logic tạo `chunk_id` ổn định (ví dụ hash content + doc_id).
    *   Viết code upsert vào Chroma, đảm bảo xóa (prune) các chunk_id cũ không còn tồn tại trong list clean mới.
    *   Kiểm tra tính Idempotent: Báo M1 chạy pipeline 2 lần, số vector không được tăng.

### Sprint 3: Inject Corruption & Before/After (M3 dẫn dắt)
*   **M3 (Inject & Eval):**
    *   Chạy pipeline bằng cờ cố ý làm sai: `python etl_pipeline.py run --run-id inject-bad --no-refund-fix --skip-validate`.
    *   Chạy evaluation ra CSV (`artifacts/eval/after_inject_bad.csv`).
    *   Chạy lại pipeline bình thường, eval lại để lấy evidence "sạch".
*   **M2 (Quality Report):**
    *   Nhận kết quả từ M3, viết `docs/quality_report.md` giải thích vì sao khi inject lỗi thì retrieval bị sai, và fix xong thì đúng lại thế nào.
*   **M1 (Hỗ trợ):**
    *   Theo dõi logs, trích xuất đoạn log fail/pass gửi cho M2 đưa vào report.

### Sprint 4: Monitoring, Runbook & Final Docs (Cả nhóm)
*   **M1 (Monitoring):**
    *   Chạy check freshness `python etl_pipeline.py freshness ...`.
    *   Bổ sung bảng `metric_impact` vào `reports/group_report.md`.
*   **M3 (Architecture & Runbook):**
    *   Hoàn thành sơ đồ `docs/pipeline_architecture.md`.
    *   Hoàn thành `docs/runbook.md` với chuỗi Symptom → Detection → Diagnosis → Mitigation → Prevention.
*   **M1, M2, M3 (Individual Reports & Review):**
    *   Mỗi người tự viết `reports/individual/[tên].md` (400-650 chữ). **Bắt buộc** trích log hoặc CSV chứng minh.
    *   Kiểm tra chéo (Peer Review): Trả lời 3 câu hỏi (Slide phần E) vào group report.
    *   Check output lần cuối bằng: `python instructor_quick_check.py --grading artifacts/eval/grading_run.jsonl`.
    *   Commit & Push (Chú ý file `.gitignore`, không commit `.env` hay `chroma_db`).

---

## 5. Checklist Bàn Giao Cuối Cùng (Tránh rớt hạng)
- [ ] Lệnh `python etl_pipeline.py run` kết thúc với Exit Code 0.
- [ ] Thư mục `artifacts/quarantine/` CÓ FILE dữ liệu lỗi (để chứng minh rule có tác dụng).
- [ ] Thư mục `artifacts/eval/` có file `before_after` và `grading_run.jsonl`.
- [ ] Đủ 3 Individual report (nếu thiếu, cá nhân 0 điểm).
- [ ] Report Nhóm có giải thích bằng số liệu và evidence.
- [ ] **Mục tiêu Merit:** Grading câu 3 (`gq_d10_03`) đúng hoàn toàn.
- [ ] **Mục tiêu Distinction:** Áp dụng pydantic hoặc đo freshness 2 biên (Ingest & Publish) và minh chứng bằng log.